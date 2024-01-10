from utils.screwdriver import WebController
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
# {"role": "assistant", "type": "code", "format": "python", "start": True}???

class ApiKey:
    def __init__(self, key: str = "selenium", engine: str = "google"):
        self.key = key
        self.engine = engine

    def __str__(self):
        return f'{self.engine}: {self.key}'
    
class SearchEngine:
    def __init__(self, key: ApiKey = ApiKey()):
        self.key = key
        self.engine = key.engine

        if self.key.key == "selenium":
            self.driver = WebController()
            self.browser = self.driver.webdriver()
            self.engines = {"google": {"engine":"https://www.google.com/search?q=",
                                       "search": {"title": (By.CLASS_NAME, "MBeuO"),
                                                  "description": (By.CLASS_NAME, "r025kc"),
                                                  "link": (By.CSS_SELECTOR, 'a[jsname="UWckNb"]')}}} 

    def search(self, query: str, complexity: int = 3):
        if self.key.key == 'selenium':
            return self.selenium_search(query, complexity)
        
    def wait_until(self, condition: tuple[By, str], timeout: int = 30):
        WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located(condition))
        
    def selenium_search(self, query: str, complexity: int = 3):
        engine = self.engines[self.engine]
        self.browser.get(engine["engine"] + query)

        keys = {key:None for key in engine["search"].keys()}
        results = [dict(keys) for _ in range(complexity)]
        for key, identifier in engine["search"].items():
            self.wait_until(identifier)
            elements = self.browser.find_elements(*identifier)[:complexity]

            for index, elem in enumerate(elements):
                results[index][key] = elem.get_attribute('href') if key == "link" else elem.text

        return results
    
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

            # lmao wtf is this
            if (items := data.get("items", [])):
                return self.results_filter(items)
            else:
                return "No results found."

        except requests.RequestException as e:
            return f"Error fetching search results: {e}"


