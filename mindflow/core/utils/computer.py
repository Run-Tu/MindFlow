import io
import os
import platform
import contextlib
import subprocess
from rich.syntax import Syntax
from ..utils.general import lazy_import
import threading

class Computer:
    def __init__(self, extensions) -> None:
        self.platform = platform.uname()
        self.user = os.getlogin()
        self.os = f"{self.platform.system} {self.platform.version}"
        
        self.globals = {"lazy_import": lazy_import,
                        "extensions": extensions}
        
        self.languages = {"cmd":[],
                          "powershell":["powershell", "-Command"],
                          "applescript":["osascript", "-e"],
                          "bash":[],
                          "js":["node", "-e"],
                          "r": ["Rscript", "-e"],
                          "java": ["java", "-e"]}
        
        self.supported = set(self.available())
    
    def available(self):
        os_languages = {
            "Windows": ["cmd", "powershell"],
            "Darwin": ["applescript"],
            "Linux": ["bash"]
        }
        
        languages = {
            "js": ["node", "-v"],
            "r": ["R", "--version"],
            "java": ["java", "-version"]
        }
        
        supported = ["python"] + os_languages.get(self.platform.system, [])
        for lang, command in languages.items():
            if self.check(command):
                supported.append(lang)
        
        return supported
    
    def check(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def md(self, code, format='python', theme="github-dark"):
        return Syntax(code, format, theme=theme, line_numbers=True)

    def run(self, code, language='python'):
        with ThreadContext(target=self.threaded_run, args=(code, language)) as context:
            pass # bro wtf is happening here??
        return context.result
    
    def threaded_run(self, code, language):
        if language == 'python':
            return self.run_python(code)
        return self.run_shell(code, language)
    
    def run_python(self, code):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            try:
                exec(code, self.globals.copy())
            except Exception as e:
                output.write(f"An error occurred: {e}")
        return (result 
                if (result := output.getvalue()) 
                else "The following code did not generate any console text output, but may generate other output.")
    
    def run_shell(self, code, language):
        try:
            command = self.languages.get(language, None)
            if command is None:
                return f"MindFlow does not support the language: {language}"
            
            result = subprocess.run(command + [f"{code}"], capture_output=True, text=True)
            return (result.stdout 
                    if result.stdout
                    else f"Command executed with exit code: {result.returncode}")
            
        except Exception as e:
            return f"An error occurred: {e}"


class ThreadContext:
    def __init__(self, target, args=()):
        self.result = None
        self.thread = threading.Thread(target=self.wrapper, args=(target,) + args)
        self.thread.daemon = True

    def wrapper(self, target, *args):
        self.result = target(*args)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.thread.join()
