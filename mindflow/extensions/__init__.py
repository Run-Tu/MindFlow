from ..core.utils.general import ROOT_DIR
from pathlib import Path
import toml
import os
import sys
import importlib

class Extensions:
    def __init__(self):
        self.extensions_dir = Path(ROOT_DIR, "extensions", "extensions")
        self.extensions = os.listdir(self.extensions_dir)
        
        for extension in self.extensions:
            module_path = Path(self.extensions_dir, extension)
            if module_path.is_dir() and '__init__.py' in os.listdir(module_path):
                try:
                    # Add the module's directory to sys.path
                    sys.path.insert(0, str(module_path))
                    
                    spec = importlib.util.spec_from_file_location(extension, module_path / '__init__.py')
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    setattr(self, extension, getattr(module, extension.title())())
                    
                    # Remove the module's directory from sys.path
                    sys.path.pop(0)
                except ImportError as e:
                    print(f"Failed to import {extension}: {e}")
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

