from pathlib import Path
from ..utils import ROOT_DIR
import importlib
import sys

def load(path: Path | str):
    if path is None:
        path = Path(ROOT_DIR, "profile", "template.py")
    module_name = "mindflow.apps"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    for variable in dir(module):
        if not variable.startswith("__"):
            globals()[variable] = getattr(module, variable)
