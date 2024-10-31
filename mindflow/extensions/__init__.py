from .browser import Browser
from .email import Email

from ..utils import ROOT_DIR
from pathlib import Path
import importlib

def load_extensions():
    with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "r") as f:
        extensions = f.read().splitlines()
    
    for module_name in extensions:
        globals()[module_name] = importlib.import_module(module_name)

load_extensions()
