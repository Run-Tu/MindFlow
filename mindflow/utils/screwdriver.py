import os
import logging
import json
import browsers
import importlib
from pathlib import Path
from selenium import webdriver
import random
import platform

class WebController:
    def __init__(self, 
                 headless: bool = True,
                 ignore: tuple[str] = ("images", "css"),
                 browser: str = None,
                 hierarchy: list = ["chrome", "firefox", "msedge"]):
        
        # select browser
        if not browser: 
            available = set(i["browser_type"] 
                            for i in browsers.browsers())

            for browser in hierarchy:
                if browser in available:
                    self.chosen_browser = browser
                    break
        else:
            self.chosen_browser = browser

        self.setup_browser(self.chosen_browser)
        self.setup_user_agent()
        self.headless = headless
        self.ignore = ignore

        if self.headless:
            self.browser_options.add_argument("--headless")

        if self.ignore:
            self.setup_ignore()

    def log(self, text: str) -> None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.info(text)

    def webdriver(self):
        self.driver = self.Browser(
            service=self.Service(self.DriverManager().install()),
            options=self.browser_options
            )
        return self.driver

    def setup_browser(self, browser: str = "chrome"):
        with open(Path(Path(__file__).parent, "supported.json"), "r") as f:
            config = json.loads(f.read())[browser]

        module = importlib.import_module(f"selenium.webdriver.{config['service']}.options")
        self.browser_options = getattr(module, 'Options')()

        module = importlib.import_module(f"selenium.webdriver.{config['service']}.service")
        self.Service = module.Service

        module = importlib.import_module(f"webdriver_manager.{config['manager']}")
        self.DriverManager = getattr(module, config["driver"] + "DriverManager")

        self.Browser = getattr(webdriver, config["service"].capitalize())

        if self.chosen_browser == "firefox":
            self.profile = webdriver.FirefoxProfile()


    def setup_ignore(self):
        if self.chosen_browser == "firefox":
            if "css" in self.ignore:
                self.profile.set_preference('permissions.default.stylesheet', 2)
            if "images" in self.ignore:
                self.profile.set_preference('permissions.default.image', 2)
            self.browser_options.profile = self.profile

        elif self.chosen_browser == "chrome":
            if "images" in self.ignore:
                prefs = {"profile.managed_default_content_settings.images": 2}
                self.browser_options.add_experimental_option("prefs", prefs)

    def setup_user_agent(self):
        # this system will be automated in the future
        # meaning it does not need to be updated.
        # this is a bad temporary fix lol

        browsers = {"chrome": ["AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
                               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.3"],
                    "firefox": ["Gecko/20100101 Firefox/127.",
                                "Gecko/20100101 Firefox/126."],
                    "edge": ["AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.",
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/125.0.0.",
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0."]}
        
        platforms = {"Windows": ["Windows NT 10.0; Win64; x64",
                            "Windows NT 10.0; Win64; x64; rv:127.0"],
                    "Darwin": ["Macintosh; Intel Mac OS X 10_15_7"],
                    "Linux": ["X11; Linux x86_64"]}
        
        os_platform = random.choice(platforms[platform.system()])
        browser = random.choice(browsers[self.chosen_browser])

        user_agent = f"Mozilla/5.0 ({os_platform}) {browser}"
        if self.chosen_browser == "firefox":
            self.profile.set_preference("general.useragent.override", user_agent)
        else:
            self.browser_options.add_argument(f"user-agent={user_agent}")

if __name__ == "__main__":
    driver = WebController()
    browser = driver.webdriver()
    os.system("pause")
