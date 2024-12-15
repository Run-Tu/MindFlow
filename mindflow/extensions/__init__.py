from .browser import Browser, BrowserKwargs
from .email import Email, EmailKwargs

from ..utils import ROOT_DIR, Kwargs
from pathlib import Path
import importlib

def load_extensions():
    with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "r") as f:
        extensions = f.read().splitlines()
    
    for module_name in extensions:
        module = importlib.import_module(module_name)
        globals()[module_name] = getattr(module, module_name.title())
        if (kwargs := getattr(module, module_name.title()+"Kwargs")):
            globals()[module_name+"Kwargs"] = kwargs

load_extensions()
