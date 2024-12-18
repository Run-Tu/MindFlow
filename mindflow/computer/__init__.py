import shutil
import subprocess
from typing import List, Dict
from functools import partial
from pathlib import Path
from ..utils import ROOT_DIR
import mindflow.extensions as extensions

class Computer:
    def __init__(self, 
                 profile_path: Path | str = None,
                 paths: Dict[str, list] = None,
                 extensions: Dict[str, object] = None):
        
        self.profile_path = profile_path or Path(ROOT_DIR, "profile", "template.py")
        self.extensions = extensions or {}
        self.custom_paths = paths or {}
        self.supported = self.available()
        
    def inject_kwargs(self, code):
        for extension, vals in self.extensions.items():
            if extension in code:
                kwarg_str = ', '.join(f'{kwarg}={val!r}' for kwarg, val in vals.items())
                code = code.replace(f"{extension}()", f"{extension}({kwarg_str})")
        return code
    
    def load_instructions(self):
        return "\n\n".join(
            getattr(extensions, extension).load_instructions()
            for extension in self.extensions.keys()
        )

    def available(self) -> Dict[str, str]:
        languages = {
            "python": ["py", "python", "python3"],
            "js": ["bun", "deno", "node"],
            "r": ["R", "rscript"],
            "java": ["java"],
            "cmd": ["cmd"],
            "powershell": ["powershell"],
            "applescript": ["osascript"],
            "bash": ["bash"],
        }
        
        args = {
            "python": "-c",
            "cmd": "/c",
            "powershell": "-Command",
            "applescript": "-e",
            "bash": "-c",
            "js": "-e",
            "r": "-e",
            "java": "-e"
        }
        
        supported = {}
        for lang, command in languages.items():
            if (path := self.check(command)):
                supported[lang] = [path, args[lang]]
        supported |= self.custom_paths
        
        return supported
    
    def check(self, exes) -> bool:
        for exe in exes:
            if (exe := shutil.which(exe)):
                return exe
    
    def run(self, code: str, language: str ='python') -> str:
        try:
            command = self.supported.get(language, None)
            if command is None: 
                return f"MindFlow does not support the language: {language}"
            
            if language == "python":
                code = self.inject_kwargs(code)

            result = subprocess.run(command + [code], capture_output=True, text=True)
            if result.stdout or result.stderr:
                return (result.stdout + "\n" + result.stderr).strip()
            if result.returncode == 0:
                return (f"The following code did not generate any console text output, but may generate other output.")
            return (f"Command executed with exit code: {result.returncode}")
            
        except Exception as e:
            return f"An error occurred: {e}"
