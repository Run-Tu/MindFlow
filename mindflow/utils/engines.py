import asyncio
import requests
from playwright.async_api import async_playwright
import time

class ApiKey:
    def __init__(self, key: str = "playwright", engine: str = "google"):
        self.key = key
        self.engine = engine

    def __str__(self):
        return f'{self.engine}: {self.key}'

class SearchEngine:
    def __init__(self, key: ApiKey = ApiKey()):
        self.key = key
        self.engine = key.engine

        if self.key.key == "playwright":
            self.engines = {"google": {"engine":"https://www.google.com/search?q=",
                                       "search": {"title": 'h3.LC20lb',
                                                  "description": 'div.r025kc',
                                                  "link": 'div.yuRUbf > div > span > a'}}}

    async def playwright_search(self, query: str, complexity: int = 3):
        async with async_playwright() as p:
            self.driver = await p.chromium.launch()
            start = time.time()
            self.page = await self.driver.new_page()
            engine = self.engines[self.engine]
            await self.page.goto(engine["engine"] + query)

            keys = {key:None for key in engine["search"].keys()}
            results = [dict(keys) for _ in range(complexity)]
            for key, selector in engine["search"].items():
                elements = await self.page.query_selector_all(selector)
                elements = elements[:complexity]

                for index, elem in enumerate(elements):
                    if key == "link":
                        results[index][key] = await elem.get_attribute('href')
                    else:   
                        results[index][key] = await elem.inner_text()

            print(f"completed in {time.time() - start} s")
            await self.driver.close()
            return results

    def search(self, query: str, complexity: int = 3):
        if self.key.key == 'playwright':
            return asyncio.run(self.playwright_search(query, complexity))
        elif self.engine == 'google':
            return self.google_search(query, complexity)

    def load_search(self, query: dict, clean: bool = True):
        site = self.load_site(query["link"], clean)
        return query | {"content": site}

    def results_filter(self, results: list):
        
        if self.engine == "google":
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
