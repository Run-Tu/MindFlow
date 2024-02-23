from .utils.computer import Computer
from .utils.llm import LLM, to_lmc
from pathlib import Path
import importlib
import json
import os

from .defaults import (LLM_DEFAULT, CODE_DEFAULT, VISION_DEFAULT)

class Apikey:
    def __init__(self, key: str = "playwright", name: str = "google"):
        self.key = key
        self.name = name

    def __str__(self):
        return f'{self.name}: {self.key}'

class Profile:
    """
    store apikeys here. this is temp since its a bad setup omg.
    """
    def __init__(
            self, 
            keys: dict = {"llm": LLM_DEFAULT,
                          "code": CODE_DEFAULT,
                          "vision": VISION_DEFAULT,
                          "browser": "playwright"}, 
            search_engine: str = "google",
            name: str = None):
        self.keys = keys
        self.search_engine = search_engine
        self.name = "User" if name is None else name

    def __str__(self):
        return f'Profile({self.name}, {self.keys})'

class MindFlow:
    """
    The core of all operations occurs here.
    Where the system breaks down requests from the user and executes them.
    """
    def __init__(
            self,
            messages: list | None = None,
            history_dir: Path | None = None,
            skills_dir: Path | None = None,
            prompts_dir: Path | None = None,
            extensions_dir: Path | None= None,
            verbose: bool = False,
            local: bool = False,
            computer = None,
            llm = None,
            tasks = False) -> None:
        
        # utils
        self.computer = Computer() if computer is None else computer
        self.llm = LLM(Profile(), messages=messages) if llm is None else llm

        self.tasks = tasks

        # logging + debugging
        self.verbose = verbose
        
        # memory + history
        self.history_dir = Path(Path(__file__).parent, "memory", "history") if history_dir is None else history_dir
        self.skills_dir = Path(Path(__file__).parent, "memory", "skills") if skills_dir is None else skills_dir
        self.prompts_dir = Path(Path(__file__).parent, "prompts") if prompts_dir is None else prompts_dir
        self.extensions_dir = Path(Path(__file__).parent.parent, "extensions") if extensions_dir is None else extensions_dir
        
        self.llm.messages = [] if messages is None else messages

        # experimental
        self.local = local
        
        # extensions including ['browser'] by default
        for extension in os.listdir(self.extensions_dir):
            module_path = os.path.join(self.extensions_dir, extension)
            if os.path.isdir(module_path) and '__init__.py' in os.listdir(module_path):
                try:
                    module = importlib.import_module(extension)
                    name = extension.title()
                    setattr(self, name, getattr(module, name)())
                except ImportError:
                    config_path = Path(self.extensions_dir, extension, "config.default.toml")
                    if config_path.exists():
                        with open(config_path, "r") as f:
                            # Handle the config file as needed
                            pass

        # prompts
        self.prompts = {}
        prompts = os.listdir(self.prompts_dir)
        for filename in prompts:
            with open(Path(self.prompts_dir, filename), "r") as f:
                self.prompts[filename.split('.')[0]] = f.read().strip()

    def chat(self, 
            message: str = None, 
            display: bool = True, 
            stream: bool = False,
            timeout=16):
        
        response = json.loads(self.llm.raw_chat(message, system=self.prompts["initial"]))
        for _ in range(timeout):
            if response == "The task is done.":
                return
            
            if response.get("type", None) == "code":
                #self.llm.messages.append(to_lmc(response.get("content", None), role="computer", type="code"))
                output = self.computer.run_python(response.get("content", None))
                self.llm.messages.append(to_lmc(output, role="computer", type="code", format="output"))
                
                
                response = json.loads(self.llm.raw_chat(message=output, role="computer", system=self.prompts["initial"]))
            else:
                return response.get("content", None)
            
        raise Warning("MindFlow has exceeded it's timeout stream of thoughts!")

