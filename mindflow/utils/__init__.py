import subprocess
import importlib.util

from pathlib import Path
import platform
import sys
import os
import re

import random
import string

# constants
ROOT_DIR = Path(__file__).resolve().parent.parent
PLATFORM = platform.uname()
USERNAME = os.getlogin()
SYSTEM = platform.system()
OS = f"{SYSTEM} {platform.version()}"

def is_installed(package):
    spec = importlib.util.find_spec(package)
    return spec is not None

def python_load_profile(path: Path | str):
    module_name = f"mindflow.parse_profile"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return getattr(module, "profile", {})

def load_profile(profile_path):
    if profile_path is None:
        return {}
    
    profile_path = Path(profile_path)
    if not profile_path.is_file():
        return {}
    
    suffix = profile_path.suffix.lower()
    with open(profile_path, "r") as f:
        if suffix == ".json":
            return lazy_import("json").load(f)
        elif suffix in {".yaml", ".yml"}:
            return lazy_import("yaml").safe_load(f)
        elif suffix == ".toml":
            return lazy_import("toml").load(f)
        elif suffix in {".py", ".pyw"}:
            return python_load_profile(profile_path)
        
    return {}

def re_format(text, replacements, pattern=r'\{([a-zA-Z0-9_]+)\}', strict=False):
    matches = set(re.findall(pattern, text))
    if strict and (missing := matches - set(replacements.keys())):
        raise ValueError(f"Missing replacements for: {', '.join(missing)}")

    for match in matches & set(replacements.keys()):
        text = re.sub(r'\{' + match + r'\}', str(replacements[match]), text)
    return text

def load_prompts(dir, 
                 info: dict = {},
                 conversational: bool = False):
    prompts = {}

    for filename in Path(dir).iterdir():
        if not filename.is_file():
            continue

        name = filename.stem
        with open(Path(dir, filename), "r") as f:
            prompts[name] = re_format(f.read().strip(), info)

    prompts['initial'] += "\n\n" + prompts['instructions']
    if conversational:
        prompts['initial'] += "\n\n" + prompts['conversational']

    return prompts

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

def generate_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
 
def get_relevant(document: dict, threshold: float = 1.125, clean=False):
    # temp, filter by distance
    # future, density based retrieval relevance 
    # https://github.com/chroma-core/chroma/blob/main/chromadb/experimental/density_relevance.ipynb
    
    np = lazy_import("numpy",
                     install=True,
                     optional=False)

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
