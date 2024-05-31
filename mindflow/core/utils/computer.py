import io
import os
import sys
import platform
from rich.console import Console
from rich.syntax import Syntax
from ..utils.general import lazy_import
import threading
from functools import partial

class Computer:
    def __init__(self) -> None:
        self.platform = platform.uname()
        self.user = os.getlogin()
        self.os = f"{self.platform.system} {self.platform.version}"
        self.supported = ["python", "js"]
        self.globals = {"lazy_import": lazy_import}
        
        if self.platform.system == "Windows":
            self.supported += ["cmd", "powershell"]
        elif self.platform.system == "Darwin":
            self.supported += ["applescript"]
        elif self.platform.system == "Linux":
            self.supported += ["bash"]
            
    def md(self, code, format='python', console=Console()):
        console.print(Syntax(code, format, theme="github-dark", line_numbers=True))
        print()
        

    def run(self, code, format='python'):
        console = Console()
        if format == 'pseudocode':
            console.print(f'[bold #4a4e54]{chr(0x1F785)} Task plan in `{format}`...[/bold #4a4e54]')
            self.md(code, format, console)
            return None

        console.print(f'[bold #4a4e54]{chr(0x1F785)} Running `{format}`...[/bold #4a4e54]')
        self.md(code, format, console)
        
        self.output = ""
        
        if format == 'python':
            run = self.run_python
        elif (format == 'bash') or (format == 'cmd') or (format == 'shell'):
            run = self.run_shell
        elif format == 'applescript' and platform.system() == 'Darwin':
            run = self.run_applescript
        elif format == 'js':
            run = self.run_js
        elif format == 'powershell':
            run = self.run_powershell
        else:
            return f"MindFlow does not support the format: {format}"
        
        # new thread, so main thread won't close
        thread = threading.Thread(target=partial(run, code))
        thread.start()
        thread.join()
        
        return (self.output 
                if self.output 
                else "The following code did not generate any console text output, but may generate other output.")
 

    def run_python(self, code):
        output = io.StringIO()
        stdout = sys.stdout
        sys.stdout = output
        try:
            exec(code, self.globals)
        except Exception as e:
            output.write(f"An error occurred: {e}")
        finally:
            sys.stdout = stdout
        self.output = output.getvalue()

    def run_shell(self, code):
        try:
            result = os.system(code)
            self.output = f"Command executed with exit code: {result}"
        except Exception as e:
            self.output = f"An error occurred: {e}"

    def run_applescript(self, code):
        try:
            result = os.system(f'osascript -e "{code}"')
            self.output = f"Command executed with exit code: {result}"
        except Exception as e:
            self.output = f"An error occurred: {e}"

    def run_js(self, code):
        try:
            result = os.system(f'node -e "{code}"')
            self.output = f"Command executed with exit code: {result}"
        except Exception as e:
            self.output = f"An error occurred: {e}"
        
    def run_powershell(self, code):
        try:
            result = os.system(f'powershell -Command "{code}"')
            self.output = f"Command executed with exit code: {result}"
        except Exception as e:
            self.output = f"An error occurred: {e}"
