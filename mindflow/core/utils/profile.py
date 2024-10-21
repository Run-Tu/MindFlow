from .general import load_settings
from typing import TypedDict

class Profile(TypedDict):
    def __init__(self, config_file= None):
        self.settings = load_settings(file=config_file) if config_file else {}
        if not self.settings.get("profile"):
            self.settings["profile"] = {"name": "default", "version": "1.0.0"}
        print(self.settings)
            
    def __str__(self):
        return f'Profile({self.settings})'
