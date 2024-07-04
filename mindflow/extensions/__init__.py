from ..core.utils.general import ROOT_DIR
from pathlib import Path
import toml
import os
import sys
import importlib

class Extensions:
    def __init__(self):
        self.extensions_dir = Path(ROOT_DIR, "extensions", "extensions")
        self.extensions = []
        
        for extension in self.extensions_dir.iterdir():
            if not extension.is_dir():
                continue
            
            file = '__init__.py'
            if not (extension / "__init__.py").exists():
                if not (config_path := extension / "omproject.toml").exists():
                    print(f"Failed to import {extension.name}: `omproject.toml` doesn't exist!")
                    continue
                    
                with open(config_path, "r") as f:
                    config = toml.load(f.read())["setup"]
                if not (file := config.get("init", None)):
                    print(f"Failed to import {extension.name}: `init` in `omproject.toml` not specified!")
                    continue

            try:
                spec = importlib.util.spec_from_file_location(extension.name, extension / file)
                module = importlib.util.module_from_spec(spec)
                sys.modules[extension.name] = module
                spec.loader.exec_module(module)

                setattr(self, extension.name, getattr(module, extension.name.title())())
                self.extensions.append(extension.name)
            
            except ImportError as e:
                print(f"Failed to import {extension.name}: {e}")

                        
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

