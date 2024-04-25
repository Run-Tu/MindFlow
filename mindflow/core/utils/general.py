import subprocess
import importlib.util
import toml
from pathlib import Path

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

def load_settings(settings=None, section=None, verbose=False):
    if settings is None:
        
        config = Path(ROOT_DIR, "config.toml")
        config_default = Path(ROOT_DIR, "config.default.toml")
        
        with open(config_default, "r") as file:
            settings = toml.load(file)
        
        if config.is_file():
            with open(config, "r") as file:
                settings |= toml.load(file)
        elif verbose:
            print("config.toml not found, using config.defaults.toml instead!")

    return settings.get(section, settings) if section else settings
