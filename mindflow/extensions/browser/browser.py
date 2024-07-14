import asyncio
import requests
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from functools import partial
import re

from .utils.google_snippets import (get_weather, 
                                   get_showtimes, 
                                   get_events, 
                                   get_reviews)

class Browser:
    def __init__(self,
                 ignore: tuple[str] = None):
        self.key = "playwright"
        self.name = "google"
        self.loop = asyncio.get_event_loop()
        
        self.ignore_words = frozenset(("main menu", "move to sidebar", "navigation", "contribute", "search", "appearance", "tools", "personal tools", "pages for logged out editors", "move to sidebar", "hide", "show", "toggle the table of contents", "general", "actions", "in other projects", "print/export"))

        if not ignore:
            self.ignore = ("png","jpg","jpeg","svg","gif", "css","woff","woff2","mp3","mp4")
        else:
            self.ignore = ignore
        self.ignore_regex = re.compile(r"\.(" + "|".join(self.ignore) + ")$")

        if self.key == "playwright":
            self.engines = {"google": {"engine":"https://www.google.com/search?q=",
                                       "search": {"title": 'h3.LC20lb',
                                                  "description": 'div.r025kc',
                                                  "link": 'div.yuRUbf > div > span > a'},
                                        # rich snippets (surface level searches)
                                       "widgets": {"weather": get_weather,
                                                   "showtimes": get_showtimes,
                                                   "events": get_events,
                                                   "reviews": get_reviews}}}
            
            self.loop.run_until_complete(self.init_playwright())

    async def playwright_search(self, 
                                query: str, 
                                n: int = 3, 
                                widget: str = None):

        page = await self.browser.new_page()
        # Abort css and other uneccesary requests
        await page.route(self.ignore_regex, lambda route: route.abort())

        engine = self.engines[self.name]
        await page.goto(engine["engine"] + query) 

        #results = {"searches": []}
        results = ()
        if widget and (function := engine["widgets"].get(widget, None)):
            results = ({"widget": await function(page)},)

        keys = {key: None for key in engine["search"].keys()}
        results += tuple(keys.copy() for _ in range(n))
        
        
        for key, selector in engine["search"].items():
            elements = (await page.query_selector_all(selector))[:n]
            for index, elem in enumerate(elements):
                if key == "link":
                    results[index][key] = await elem.get_attribute('href')
                else:
                    results[index][key] = await elem.inner_text()

        await page.close()
        return results


    async def init_playwright(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        
    async def close_playwright(self):
        await self.browser.close()
        await self.playwright.stop()

    def search(self, query: str, n: int = 3, parallel=False, widget=None):
        search = ""
        if self.key == 'playwright':
            search = self.playwright_search(query, n, widget)
        elif self.name == 'google':
            search = self.google_search(query, n, widget)
        
        if parallel:
            return search
        return self.loop.run_until_complete(search)
        
    def parallel(self, *funcs):
        return self.loop.run_until_complete(self.run_parallel(*funcs))
        
    async def run_parallel(self, *funcs):
        tasks = tuple(partial(func, *args, parallel=True)() for func, args in funcs)
        return tuple(await asyncio.gather(*tasks))

    def load_search(self, result: dict, clean: bool = True):
        site = self.loop.run_until_complete(self.load_site(result["link"], clean))
        return site
    
    
    # def load_searches(self, queries: dict):
    #     # must be a better way to do this in async than flattening it
    #     tasks = []
    #     for query in queries.values():
    #         tasks += [await self.load_site(site["link"], True) for site in query['searches']]
            
    #     loop = asyncio.get_event_loop()
    #     results = loop.run_until_complete(asyncio.gather(*tasks))
    #     n = len(queries)
    #     pairs = [results[i:i + n] for i in range(0, len(results), n)]

    #     # really bad algo :/
    #     i = 0
    #     for query in queries:
    #         for content in pairs:
    #             queries[query]['searches'][i] = content 
    #             i += 1
    #         i = 0
                
    #     return queries

    def results_filter(self, results: list):
        
        if self.name == "google":
            title, link, desc = "title", "link", "snippet"
            
        return [{"title": result[title],
                 "link": result[link],
                 "description": result[desc]} for result in results]

    def google_search(self, query: str, n: int = 3):
        base_url = "https://www.googleapis.com/customsearch/v1"
        cx = "65a4f09c14c4846ee"

        params = {
            "key": self.key,
            "cx": cx,
            "q": query,
            "num": n
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if (items := data.get("items", [])):
                return self.results_filter(items)
            else:
                return "No results found."

        except requests.RequestException as e:
            return f"Error fetching search results: {e}"

    async def to_markdown(self, html: str) -> str:
        alphabet = "abcdefghijklmnopqrztuvwxyz"
        markdown_content = md(html, heading_style="ATX")
            
        # Ensure new lines are at a max of 2 each time
        content = '\n\n'.join([line.strip() for line in markdown_content.split('\n')
                                if len(line.strip()) > 2 and not (line.strip().lower() in self.ignore_words) and not("*  *  *" in line) and any(i in {*line.lower()} for i in alphabet)])
        
        # Detect and remove weird patterns using regex
        return content

    async def load_site(self, site: str, clean: bool = True):
        page = await self.browser.new_page()
        await page.goto(site)
        if clean:
            body = await page.query_selector('body')
            html = await body.inner_html()
            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove footer and a tags
            for footer in soup.find_all('footer'):
                footer.decompose()
            for a in soup.find_all('a'):
                a.decompose()
            
            web_context = await self.to_markdown(str(soup))
            return web_context
        else:
            return await page.content()
