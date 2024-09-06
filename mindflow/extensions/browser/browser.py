import asyncio
from playwright.async_api import async_playwright

from pathlib import Path 
from .utils.general import to_markdown, get_relevant, uid
from snova import SnSdk
import importlib
import browsers
import random
import json
import toml

class Browser:
    def __init__(self, mindflow, headless=True):
        # Temp solution, loads widgets from ALL engines
        # Should only load widgets from chosen engine
        
        # points to current mindflow instance
        self.mindflow = mindflow        

        with open(Path(__file__).parent / "src" / "engines.json", "r") as f:
            self.engines = json.load(f)
        self.browser_engine = 'google'
        
        path = ".utils."
        for engine, data in self.engines.items():
            module = importlib.import_module(path + engine, package=__package__)
            self.engines[engine]["widgets"] = {widget: getattr(module, lib) for widget, lib in data["widgets"].items()}
            
        self.headless = True if (not headless) else (not mindflow.verbose)
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
    
    async def check_visibility_while_waiting(self, page, check_selector, wait_selector, timeout=30000):
        # start time
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # check if the element is visible
            is_visible = await page.is_visible(check_selector)
            
            # if the element is visible, return True
            if is_visible:
                return True
            
            # check if the wait_selector is visible
            try:
                return await page.wait_for_selector(wait_selector, state='visible', timeout=1000)
            except: pass  # wait_selector did not appear within the timeout
            
            # check if the timeout has been reached
            if asyncio.get_event_loop().time() - start_time > timeout / 1000:
                break
        
        return False  # Timeout reached, return False
    
    def perplexity_search(self, query: str): 
        return self.loop.run_until_complete(self.run_perplexity_search(query))
        
    async def run_perplexity_search(self, query: str): 
        page = await self.browser.new_page()
        text = ""
        try:
            await page.goto("https://www.perplexity.ai/search/new?q=" + query)
            copy = await self.check_visibility_while_waiting(page,
                                                            '.zone-name-title', # cloudflare
                                                            '.flex.items-center.gap-x-xs > button:first-child') # perplexity
            
            # cloudflare auth is blocking perplexity :(
            if copy is True:
                await page.close()  
                return ""
            
            await copy.click()
            
            text = await page.evaluate('navigator.clipboard.readText()')
        finally:
            await page.close() 
        return text
        
    
    async def playwright_search(self, 
                                query: str, 
                                n: int = 3,
                                engine: str = "google"):


        page = await self.browser.new_page()
        results = (f"Error: An error occured with {engine} search.",)
        try:
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
        finally:
            await page.close()
        return results
    
    async def playwright_load(self, url, clean: bool = False, to_context=False, void=False):
        page = await self.browser.new_page()
        try:
            await page.goto(url) 
            
            if not clean:
                return await page.content()
            
            body = await page.query_selector('body')
            html = await body.inner_html() 
        finally:
            await page.close()
        
        contents = to_markdown(html, 
                                ignore=['header', 'footer', 'nav', 'navbar'],
                                ignore_classes=['footer']).strip()
            
        # CONCEPT
        # add to short-term mindflow vectordb 
        # acts like a cache and local search engine
        # for previous web searches
        # uses embeddings to view relevant searches
        
        # will actually use a temp collection
        # stm should act like a cache
        
        if to_context:
            # temp, will improve
            contents = contents.split("###")
            self.mindflow.collection.add(
                documents=contents,
                metadatas=[{"source": "browser"} 
                           for _ in range(len(contents))], # filter on these!
                ids=[f"doc-{uid()}" 
                     for _ in range(len(contents))], # unique for each doc
            )
        
        if not void:
            return contents


    def search(self,
               query: str,
               n: int = 3,
               cite: bool = False,
               engine: str = "google",
               local: bool = False):
        
        # TODO: add a cache
        
        # search WITH perplexity.ai
        if not local:
            # what is this error handling ;^;
            try: 
                if (result := self.perplexity_search(query)):
                    return result
            except: pass
            
                
        # FALLBACK
        # search LIKE perplexity.ai (locally)
        # uses embeddings :D
        
        sites = self.loop.run_until_complete(self.playwright_search(query, n, engine))
        self.parallel(*(self.playwright_load(url=site["link"], 
                                             clean=True, 
                                             to_context=True, 
                                             void=True)
                        for site in sites))
                    
        relevant = get_relevant(self.mindflow.collection.query(query_texts=[query], 
                                                                n_results=3),
                                clean=True)
        
        prompt = self.settings["prompts"]["summarise"] + (self.settings["prompts"]["citations"] if cite else "")
        result = self.llm.chat(relevant, 
                               role="browser",
                               system=prompt)
        return result

    
    def widget_search(self,
                      query: str,
                      widget: str,
                      engine: str = "google") -> dict:

        try:
            results = self.loop.run_until_complete(self.run_widget_search(query, widget, engine))
        except:
            results = {"error": "An error occured, results are fallback from perplexity.ai."}
        
        # fallback to perplexityy
        if not results or results.get("error"):
            results |= {"results": self.loop.run_until_complete(self.run_perplexity_search(query))}
            
            if not results["results"]:
                return {"error": "It seems like your query does not show any widgets."}
            
        return results
    
    async def run_widget_search(self,
                            query: str,
                            widget: str,
                            engine: str = "google") -> dict:
        
        page = await self.browser.new_page()
        engine = self.engines.get(self.browser_engine, {})
        await page.goto(engine["engine"] + query) 
        try:
            if (function := engine.get("widgets", {}).get(widget, None)):
                results = (await function(self, page)) or {}
        except:
            results = {"error": "An error occured, results are fallback from perplexity.ai."}
        
        await page.close() 
        return results
    
    def parallel(self, *funcs, void=False):
        if not void:
            return self.loop.run_until_complete(self.run_parallel(*funcs)) 
        
    async def run_parallel(self, *funcs):
        return tuple(await asyncio.gather(*funcs))

