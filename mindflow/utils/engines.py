import asyncio
import requests
from playwright.async_api import async_playwright
from markdownify import markdownify as md
import re

class ApiKey:
    def __init__(self, key: str = "playwright", name: str = "google"):
        self.key = key
        self.name = name

    def __str__(self):
        return f'{self.name}: {self.key}'

class Search:
    def __init__(self, key: ApiKey = ApiKey(),
                 ignore: tuple[str] = None):
        self.key = key
        self.name = key.name
        self.loop = asyncio.get_event_loop()

        if (ignore is None or ignore is False):
            self.ignore = ("png","jpg","jpeg","svg","gif", "css","woff","woff2","mp3","mp4")
        else:
            self.ignore = ignore
        self.ignore_regex = re.compile(r"\.(" + "|".join(self.ignore) + ")$")

        if self.key.key == "playwright":
            self.engines = {"google": {"engine":"https://www.google.com/search?q=",
                                       "search": {"title": 'h3.LC20lb',
                                                  "description": 'div.r025kc',
                                                  "link": 'div.yuRUbf > div > span > a'}}}
            self.loop.run_until_complete(self.init_playwright())

    async def playwright_search(self, query: str, complexity: int = 3):
        page = await self.browser.new_page()

        # Abort css and other uneccesary requests
        await page.route(self.ignore_regex, lambda route: route.abort())

        engine = self.engines[self.name]
        await page.goto(engine["engine"] + query)  # Join the list into a string

        keys = {key: None for key in engine["search"].keys()}
        results = [dict(keys) for _ in range(complexity)]
        for key, selector in engine["search"].items():
            elements = await page.query_selector_all(selector)
            elements = elements[:complexity]

            for index, elem in enumerate(elements):
                if key == "link":
                    results[index][key] = await elem.get_attribute('href')
                else:
                    results[index][key] = await elem.inner_text()

        await page.close()
        return results


    async def init_playwright(self):
        self.playwright = await async_playwright().__aenter__()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def close_playwright(self):
        await self.browser.close()
        await self.playwright.__aexit__()

    def search(self, queries: list, complexity: int = 3):
        if self.key.key == 'playwright':
            return self.loop.run_until_complete(self.run_search(queries, complexity))
        elif self.name == 'google':
            return {query: self.google_search(query, complexity) for query in queries}

    async def run_search(self, queries: list, complexity: int = 3):
        tasks = tuple(self.playwright_search(query, complexity) for query in queries)
        results = await asyncio.gather(*tasks)
        return dict(zip(queries, results))

    def load_search(self, query: dict, clean: bool = True):
        site = self.load_site(query["link"], clean)
        return query | {"content": site}

    def results_filter(self, results: list):
        
        if self.name == "google":
            title, link, desc = "title", "link", "snippet"
            
        return [{"title": result[title],
                 "link": result[link],
                 "description": result[desc]} for result in results]

    def google_search(self, query: str, complexity: int = 3):
        base_url = "https://www.googleapis.com/customsearch/v1"
        cx = "65a4f09c14c4846ee"

        params = {
            "key": self.key.key,
            "cx": cx,
            "q": query,
            "num": complexity
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
        return md(html)

    async def load_site(self, site: str, clean: bool = True):
        page = await self.browser.new_page()
        await page.goto(site)
        if clean:
            body = await page.query_selector('body')
            html = await body.inner_html()
            web_context = await self.to_markdown(html)

            return web_context
        else:
            return await page.content()

    async def load_search(self, query: dict, clean: bool = True):
        site = await self.load_site(query["link"], clean)
        return query | {"content": site}

