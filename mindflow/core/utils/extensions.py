from .general import ROOT_DIR, lazy_import
from pathlib import Path
import toml
import re
import sys
import importlib

class Extensions:
    def __init__(self, mindflow):
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
            
            loading = True
            while loading:
                try:
                    spec = importlib.util.spec_from_file_location(extension.name, extension / file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[extension.name] = module
                    spec.loader.exec_module(module)

                    setattr(self, extension.name, getattr(module, extension.name.title())(mindflow=mindflow))
                    self.extensions.append(extension.name)
                    with open(extension / config["instructions"], "r") as f:
                        self.instructions[extension.name] = f.read()
                    loading = False
    
                except ModuleNotFoundError as e:
                    lib = re.search(r"'([^']*)'", str(e)).group(1)
                    print(f"No module named '{lib}', attempting to install")
                    module = lazy_import(lib, install=True, optional=False, verbose=False)
                    if module:
                        print(f"'{lib}' successfully installed")
                    else:
                        print(f"Unable to install '{lib}', ignoring extension")
                        loading = False
                        
                except Exception as e:
                    print(f"Failed to import extension '{extension.name}': {e}")
                    loading = False
            
    def load_instructions(self) -> str:
        return "\n".join(f"# {name} EXTENSION\n{instructions}" for name, instructions in self.instructions.items())
        
