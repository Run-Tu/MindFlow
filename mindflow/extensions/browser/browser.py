import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from markdownify import markdownify as md
from bs4 import BeautifulSoup

from pathlib import Path 
from snova import SnSdk
import importlib
import browsers
import random
import json
import toml
import re


# might publish as a new module
def filter_markdown(markdown):
    filtered_lines = []
    consecutive_new_lines = 0
    rendered  = re.compile(r'.*\]\(http.*\)')
    embed_line = re.compile(r'.*\]\(.*\)')

    for line in markdown.split('\n'):
        line: str = line.strip()
        
        if embed_line.match(line) and not rendered.match(line):
            continue
        
        if '[' in line and ']' not in line:
            line = line.replace('[', '')
        elif ']' in line and '[' not in line:
            line = line.replace(']', '')
        
        if len(line) > 2:
            filtered_lines.append(line)
            consecutive_new_lines = 0
        elif line == '' and consecutive_new_lines < 1:
            filtered_lines.append('')
            consecutive_new_lines += 1
    
    return '\n'.join(filtered_lines)

def to_markdown(html, ignore=[], ignore_ids=[], ignore_classes=[], strip=[]): 
    #html = html.encode('utf-8', 'replace').decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove elements based on tags
    for tag in ignore:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove elements based on IDs
    for id_ in ignore_ids:
        for element in soup.find_all(id=id_):
            element.decompose()
    
    # Remove elements based on classes
    for class_ in ignore_classes:
        for element in soup.find_all(class_=class_):
            element.decompose()
    
    markdown = filter_markdown(md(str(soup), strip=strip))
    return markdown

class Browser:
    def __init__(self, mindflow, headless=False):
        # Temp solution, loads widgets from ALL engines
        # Should only load widgets from chosen engine
        
        # points to current mindflow instance
        self.mindflow = mindflow
        self.context = mindflow.context_memory.global_collection

        with open(Path(__file__).parent / "src" / "engines.json", "r") as f:
            self.engines = json.load(f)
        self.browser_engine = 'google'
        
        path = ".utils."
        for engine, data in self.engines.items():
            module = importlib.import_module(path + engine, package=__package__)
            self.engines[engine]["widgets"] = {widget: getattr(module, lib) for widget, lib in data["widgets"].items()}
            
        self.headless = headless
        self.llm = SnSdk("Meta-Llama-3.1-405B-Instruct")
        
        default_path = Path(__file__).parent / "config.default.toml"
        if (config_path := Path(__file__).parent / "config.toml").is_file():
            default_path = config_path
            
        with open(default_path, "r") as f:
            self.settings = toml.load(f)
            
        for key, value in self.settings['search'].items():
            self.settings['search'][key] = frozenset(value)
    
        # Init browser at runtime for faster speeds in the future
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.init_playwright())

    async def close_playwright(self):
        await self.browser.close()
        await self.playwright.stop()
        
    async def init_playwright(self):
        installed_browsers = {browser['display_name']:browser
                              for browser in browsers.browsers()}
         
        supported = ("Google Chrome", "Mozilla Firefox", "Microsoft Edge")
        for browser in supported:
            if (selected := installed_browsers.get(browser, {})):
                break
            
        self.playwright = await async_playwright().start()
        with open(Path(Path(__file__).parent, "src", "user_agents.txt"), "r") as f:
            self.user_agent = random.choice(f.read().split('\n'))
        
        path, browser_type = selected.get("path"), selected.get("browser_type", "unknown")
        self.browser_type = browser_type
        if (browser_type == "firefox" 
            or browser_type == "unknown" 
            or not selected):

            await self.init_gecko()
        else:
            await self.init_chromium(browser, path, browser_type)
    
        if not self.browser:
            raise Exception("Browser initialization failed.")
        
    async def init_chromium(self, browser, local_browser, browser_type): 
        # supports user profiles (for saved logins)      
        # temp solution, use default profile
        
        profile_path = Path(Path.home(), "AppData", "Local", *browser.split(), "User Data", "Default")
        self.browser = await self.playwright.chromium.launch_persistent_context(executable_path=local_browser,
                                                                                channel=browser_type,
                                                                                headless=self.headless, 
                                                                                user_agent=self.user_agent,
                                                                                user_data_dir=profile_path)
        
    async def init_gecko(self): 
        # doesn't support user profiles
        # because of playwright bug with gecko based browsers 
        
        self.browser = await self.playwright.firefox.launch_persistent_context(headless=self.headless,
                                                                               user_agent=self.user_agent)
        
    async def playwright_search(self, 
                                query: str, 
                                n: int = 3,
                                engine: str = "google"):

        page = await self.browser.new_page()
        await stealth_async(page)
        
        engine = self.engines.get(self.browser_engine, engine)
        await page.goto(engine["engine"] + query) 

        # wacky ahh searching here
        results = ()
        keys = {key: None for key in engine["search"].keys()}
        results += tuple(keys.copy() for _ in range(n))
        
        for key, selector in engine["search"].items():
            elements = (await page.query_selector_all(selector))[:n]
            for index, elem in enumerate(elements):
                results[index][key] = (await elem.get_attribute('href') 
                                       if key == "link" 
                                       else await elem.inner_text())

        await page.close()
        return results
    
    async def playwright_load(self, url, clean: bool = False, to_context=False):
        page = await self.browser.new_page()
        await stealth_async(page)
        await page.goto(url) 
        
        if not clean:
            return await page.content()
        
        body = await page.query_selector('body')
        html = await body.inner_html() 
        
        contents = to_markdown(html, 
                                ignore=['header', 'footer', 'nav', 'navbar'],
                                ignore_classes=['footer']).strip()
            
        # CONCEPT
        # add to short-term mindflow vectordb 
        # acts like a cache and local search engine
        # for previous web searches
        # uses embeddings to view relevant searches
        if to_context:
            # temp, will improve
            contents = contents.split("###")
            self.context.add(
                documents=contents,
                metadatas=[{"source": "browser"} for _ in range(len(contents))], # filter on these!
                ids=[f"doc{i}" for i in range(len(contents))], # unique for each doc
            )
            
        return contents


    def search(self,
               query: str,
               n: int = 3,
               cite: bool = False,
               engine: str = "google"):
        
        # search like perplexity.ai
        # v1, will use embeddings in future 
        # versions to save money
        
        sites = self.loop.run_until_complete(self.playwright_search(query, n, engine))
        results = self.parallel(*(self.playwright_load(url=site["link"], clean=True, to_context=True) for site in sites))
        
        prompt = self.settings["prompts"]["summarise"] + (self.settings["prompts"]["citations"] if cite else "")
        result = self.llm.chat("\n\n".join(results), 
                               role="browser",
                               system=prompt)
        return result
    
    def widget_search(self,
                      query: str,
                      widget: str,
                      engine: str = "google") -> dict:
        return self.loop.run_until_complete(self.run_widget_search(query, widget, engine))
    
    async def run_widget_search(self,
                            query: str,
                            widget: str,
                            engine: str = "google") -> dict:
        
        page = await self.browser.new_page()
        await stealth_async(page)
        
        engine = self.engines.get(self.browser_engine, {})
        await page.goto(engine["engine"] + query) 
        
        results = {"error": "Requested widget is unsupported."}
        if (function := engine.get("widgets", {}).get(widget, None)):
            results = await function(self, page)
        
        await page.close() 
        return results
    
    def parallel(self, *funcs):
        return self.loop.run_until_complete(self.run_parallel(*funcs))
        
    async def run_parallel(self, *funcs):
        return tuple(await asyncio.gather(*funcs))

