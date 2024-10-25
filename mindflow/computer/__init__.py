import shutil
import subprocess
from typing import List, Dict

class Computer:
    def __init__(self, 
                 paths: Dict[str, list] = None,
                 extensions: Dict[str, object] = None):
        self.extensions = extensions or {}
        self.custom_paths = paths or {}
        self.supported = self.available()
    
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

        return supported | self.custom_paths
    
    def check(self, exes) -> bool:
        for exe in exes:
            if (exe := shutil.which(exe)):
                return exe
    
    def run(self, code: str, language: str ='python') -> str:
        try:
            command = self.supported.get(language, None)
            if command is None: 
                return f"MindFlow does not support the language: {language}"
        
            result = subprocess.run(command + [code], capture_output=True, text=True)
            return (result.stdout.strip()
                    if result.stdout
                    else f"Command executed with exit code: {result.returncode}")
            
        except Exception as e:
            return f"An error occurred: {e}"
