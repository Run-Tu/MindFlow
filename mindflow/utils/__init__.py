import subprocess
import importlib.util
import toml
import sys
from pathlib import Path
import os
import platform

import random
import string
from functools import partial as config
import numpy as np

# constants
ROOT_DIR = Path(__file__).resolve().parent.parent
PLATFORM = platform.uname()
USERNAME = os.getlogin()
SYSTEM = platform.system()
OS = f"{SYSTEM} {platform.version()}"

def is_installed(package):
    spec = importlib.util.find_spec(package)
    return spec is not None

def load_profile(path: Path | str):
    module_name = f"mindflow.parse_profile"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return getattr(module, "profile", {})

def Kwargs(**kwargs):
    return kwargs

def lazy_import(package,
                name: str = '', 
                install_name: str = '',
                prefixes: tuple = ("pip install ", "py -m pip install "),
                install= False,
                void = False,
                verbose = False,
                optional=True):
    
    name = name or package
    if package in sys.modules:
        return sys.modules[package]

    spec = importlib.util.find_spec(name or package)
    if spec is None:
        if optional:
            return None
        elif install:
            if verbose:
                print(f"Module '{package}' is missing, proceeding to install.")
            
            success = False
            for prefix in prefixes:
                try: 
                    subprocess.run(prefix + install_name or package, shell=True, check=True)
                    success = True
                    break
                except subprocess.CalledProcessError: 
                    continue
            if not success:
                raise ImportError(f"Failed to install module '{name}'")
            spec = importlib.util.find_spec(name)
            if spec is None:
                raise ImportError(f"Failed to install module '{name}'")
        else:
            raise ImportError(f"Module '{name}' cannot be found")
    elif verbose:
        print(f"Module '{name}' is already installed.")
        
    if void:
        return None

    if not install:
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[name or package] = module
    
    if install:
        spec.loader.exec_module(module)
    
    importlib.reload(module) 

    return module

def lazy_imports(packages: list[str | tuple[str]], 
                 prefix: str = "pip install ",
                 user_install = False,
                 void = False):
    
    libs = []
    for package in packages:
        if not isinstance(package, str):
            package = (package[0], None) if len(package) == 1 else package
        else:
            package = (package, None)
            
        if (pack := lazy_import(*package, prefix=prefix, user_install=user_install, void=void)):
            libs.append(pack)

    if void:
        return None
    
    return tuple(libs)

def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                merge_dicts(dict1[key], value)
            else:
                dict1[key] = value
        else:
            dict1[key] = value  
    return dict1

def load_settings(file: str | Path = None, settings=None, section=None, verbose=False):
    if settings is None:
        config_default = Path(ROOT_DIR, "profile.template.toml")
        with open(config_default, "r") as f:
            settings = toml.load(f)
            
        if file:
            config = Path(file)
            if config.is_file():
                with open(config, "r") as f:
                    if (setting := toml.load(f)):
                        settings = merge_dicts(settings, setting)
            elif verbose:
                print("config.toml not found, using config.defaults.toml instead!")

    return settings.get(section, settings) if section else settings

def generate_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
 
def get_relevant(document: dict, threshold: float = 1.125, clean=False):
    # temp, filter by distance
    # future, density based retrieval relevance 
    # https://github.com/chroma-core/chroma/blob/main/chromadb/experimental/density_relevance.ipynb

    mask = np.array(document['distances']) <= threshold
    keys = tuple(set(document) & set(('distances', 'documents', 'metadatas', 'ids')))
    for key in keys:
        document[key] = np.array(document[key])[mask].tolist()
        
    if document.get('ids'):
        _, unique_indices = np.unique(document['ids'], return_index=True)
        for key in ('distances', 'documents', 'metadatas', 'ids'):
            document[key] = np.array(document[key])[unique_indices].tolist()
            
    if clean:
        document = "\n\n".join(np.array(document["documents"]).flatten().tolist())
    return document
