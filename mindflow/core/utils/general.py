import subprocess
import importlib.util
import toml
from pathlib import Path
from functools import lru_cache

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

def is_installed(package):
    spec = importlib.util.find_spec(package)
    return spec is not None

def lazy_import(package: str, 
                name: str = '', 
                prefix: str = "pip install ",
                user_install = False,
                void = False) -> None:

    user_option = " --user" if user_install else ""
    name = name or package

    if not is_installed(name):
        print(f"`{package}` package is missing, proceeding to install.")
        try:
            subprocess.run(prefix + package + user_option, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to install `{package}`.")
            return None
    
    if void:
        return None
    
    return importlib.import_module(package)

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

@lru_cache(maxsize=None)
def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                merge_dicts(dict1[key], value)  # Recursively merge child dictionaries
            else:
                dict1[key] = value  # Overwrite with the new value
        else:
            dict1[key] = value  # Add new key-value pairs
    return dict1

def load_settings(file: str | Path = None, settings=None, section=None, verbose=False):
    if settings is None:
        config_default = Path(ROOT_DIR, "config.default.toml")
        with open(config_default, "r") as file:
            settings = toml.load(file)
            
        if file:
            config = Path(file)
            if config.is_file():
                with open(config, "r") as file:
                    settings = merge_dicts(settings, toml.load(file))
            elif verbose:
                print("config.toml not found, using config.defaults.toml instead!")

    return settings.get(section, settings) if section else settings
