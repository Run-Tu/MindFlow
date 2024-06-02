from ..core.utils.general import ROOT_DIR
from pathlib import Path
import toml
import os
import importlib

class Extensions:
    def __init__(self):
        # questionable setup but will improve it in the future
        self.extensions_dir = Path(ROOT_DIR, "extensions", "extensions")
        self.extensions = os.listdir(self.extensions_dir)
        
        # extensions including ['browser'] by default
        for extension in self.extensions:
            module_path = Path(self.extensions_dir, extension)
            if os.path.isdir(module_path) and '__init__.py' in os.listdir(module_path):
                try:
                    module = importlib.import_module(extension)
                    name = extension.lower()
                    setattr(self, name, getattr(module, name)())
                    print(getattr(self, name))
                except ImportError:
                    config_path = Path(self.extensions_dir, extension, "omproject.toml")
                    if config_path.exists():
                        with open(config_path, "r") as f:
                            # Handle the config file as needed
                            pass
            
def instructions(extension):
    extensions = os.listdir(Path(ROOT_DIR, "extensions", "extensions"))
    if not (extension in extensions):
        print("Extension does not exists.")
        return
    
    root = Path(ROOT_DIR, "extensions", "extensions", extension)
    path = toml.load(Path(root, "omproject.toml"))["setup"]["instructions"]
    
    with open(Path(root, path), "r") as f:
        instructions = f.read()
        
    return instructions

