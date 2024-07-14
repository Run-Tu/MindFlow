from .general import ROOT_DIR
from pathlib import Path
import toml
import os
import sys
import importlib

class Extensions:
    def __init__(self):
        self.extensions_dir = Path(ROOT_DIR, "extensions")
        self.extensions = []
        self.instructions = {}
        
        for extension in self.extensions_dir.iterdir():
            if not extension.is_dir():
                continue
            
            file = '__init__.py' if (extension / "__init__.py").exists() else None
                
            if not (config_path := extension / "omproject.toml").exists():
                print(f"Failed to import {extension.name}: `omproject.toml` doesn't exist!")
                continue
                
            with open(config_path, "r") as f:
                config = toml.loads(f.read())["setup"]
                
            if not file and not (file := config.get("init", None)):
                print(f"Failed to import {extension.name}: `init` in `omproject.toml` not specified!")
                continue

            try:
                spec = importlib.util.spec_from_file_location(extension.name, extension / file)
                module = importlib.util.module_from_spec(spec)
                sys.modules[extension.name] = module
                spec.loader.exec_module(module)

                setattr(self, extension.name, getattr(module, extension.name.title())())
                self.extensions.append(extension.name)
                with open(extension / config["instructions"], "r") as f:
                    self.instructions[extension.name] = f.read()
            
            except Exception as e:
                print(f"Failed to import {extension.name}: {e}")
                
    def load_instructions(self) -> str:
        return "\n".join(f"# {name} EXTENSION\n{instructions}" for name, instructions in self.instructions.items())
        
