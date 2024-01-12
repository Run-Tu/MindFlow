from utils.engines import ApiKey, SearchEngine

class Task:
    def __init__(self, name: str):
        self.name = name

class Browser(Task):
    def __init__(self, 
                 api_key: ApiKey = ApiKey("selenium")):
        
        self.api_key = api_key
        self.engine = SearchEngine(api_key)

        self.driver = self.engine.driver
        self.browser = self.engine.browser

    def to_searches(self, text: str) -> tuple[str]:
        # ai function to generate 
        search = None
        return search
    
    def web_search(self, text: str):
        return self.engine.search(text)

    def load_site(self, url: str):
        return 

class Computer:
    def __init__(self):
        

        

class Model:
    def __init__(self):
        # self.pipelines = {browser: browser, brrowser}
        pass

    def run(self, task: Task):

        pass
