import asyncio
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from pathlib import Path
from functools import partial
from playwright_stealth import stealth_async
import random
import time
import re

from .utils.google_snippets import (get_weather, 
                                   get_showtimes, 
                                   get_events, 
                                   get_reviews)

class Browser:
    def __init__(self,
                 ignore: tuple[str] = None,
                 headless=True,
                 bot=True,
                 mode="perplexity"):
        
        self.engines = {"google": {"engine": "https://www.google.com/search?q=",
                                   "search": {"title": 'h3.LC20lb',
                                              "description": 'div.r025kc',
                                              "link": 'div.yuRUbf > div > span > a'},
                                   # rich snippets (surface level searches)
                                   "widgets": {"weather": get_weather,
                                               "showtimes": get_showtimes,
                                               "events": get_events,
                                               "reviews": get_reviews}}}
        
        self.browser_engine = "google"
        self.headless = headless
        self.bot = bot
        self.mode = mode
        self.loop = asyncio.get_event_loop()
        
        # ignores        
        self.ignore_words = frozenset(("main menu", "move to sidebar", "navigation", "contribute", "search", "appearance", "tools", "personal tools", "pages for logged out editors", "move to sidebar", "hide", "show", "toggle the table of contents", "general", "actions", "in other projects", "print/export"))
        self.ignore = ignore if ignore else ("png", "jpg", "jpeg", "svg", "gif", "css", "woff", "woff2", "mp3", "mp4")
        self.ignore_regex = re.compile(r"\.(" + "|".join(self.ignore) + ")$")
            
        # init browser at runtime
        # for faster speeds in the future
        self.loop.run_until_complete(self.init_playwright())
        
    async def init_playwright(self):
        self.playwright = await async_playwright().start()
        
        # Get user profile path
        # user_data_dir = self.get_user_data_dir('chrome')  # Change 'chrome' to 'firefox' or 'msedge' as needed
        #print(f"User profile path: {user_data_dir}")
        
        with open(Path(Path(__file__).parent, "src", "user_agents.txt"), "r") as f:
            agent = random.choice(f.read().split('\n'))
        
        # Launch browser with user profile
        self.browser = await self.playwright.chromium.launch(#user_data_dir=user_data_dir,
                                                             headless=self.headless)
        self.context = self.browser.new_context(user_agent=agent)

    def get_user_data_dir(self, browser_type):
        if browser_type == 'firefox':
            return str(Path.home() / 'AppData' / 'Roaming' / 'Mozilla' / 'Firefox' / 'Profiles')
        elif browser_type == 'chrome':
            return str(Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default')
        elif browser_type == 'msedge':
            return str(Path.home() / 'AppData' / 'Local' / 'Microsoft' / 'Edge' / 'User Data')
        else:
            raise Exception(f"Unsupported browser type: {browser_type}")
        
    async def close_playwright(self):
        await self.browser.close()
        await self.playwright.stop()

    async def playwright_search(self, 
                                query: str, 
                                results: int = 3, 
                                widget: str = None):

        page = await self.browser.new_page()
        
        # Abort uneccesary requests
        await page.route(self.ignore_regex, lambda route: route.abort())

        engine = self.engines.get(self.browser_engine, "google")
        await page.goto(engine["engine"] + query) 

        results = ()
        if widget and (function := engine["widgets"].get(widget, None)):
            results = ({"widget": await function(page)},)

        keys = {key: None for key in engine["search"].keys()}
        results += tuple(keys.copy() for _ in range(results))
        
        for key, selector in engine["search"].items():
            elements = (await page.query_selector_all(selector))[:results]
            for index, elem in enumerate(elements):
                if key == "link":
                    results[index][key] = await elem.get_attribute('href')
                else:
                    results[index][key] = await elem.inner_text()

        await page.close()
        return results if len(results) > 1 else results[0]
    
    async def perplexity_search(self, query):
        page = await self.context.new_page()
        await stealth_async(page)
        await page.goto("https://www.perplexity.ai/")
        
        #  await asyncio.sleep(300)
        
        
        # Enter query
        print("ATTEMPTING!")
        await page.wait_for_selector('textarea[placeholder="Ask anything..."]')
        print("PASSED!")
        await page.fill('textarea[placeholder="Ask anything..."]', query)
        await page.click('button[aria-label="Submit"]')
        
        # Extract results
        await page.click('button[data-icon="clipboard"]')
        results = await page.evaluate('navigator.clipboard.readText()')
        
        # Close the browser
        await page.close()
        return results

    def search(self, query: str, n: int = 3, parallel=False, mode="perplexity", widget=None):
        if mode == "playwright":
            search = self.playwright_search(query, n, widget)

        elif mode == "perplexity":
            search = self.perplexity_search(query)
            
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
    
    def results_filter(self, results: list):
        if self.browser_engine == "google":
            title, link, desc = "title", "link", "snippet"
            
        return [{"title": result[title],
                 "link": result[link],
                 "description": result[desc]} for result in results]

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
