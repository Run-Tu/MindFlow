import io
import os
import sys
import platform
from rich.console import Console
from rich.syntax import Syntax

class Computer:
    def __init__(self) -> None:
        self.platform = platform.uname()
        self.user = os.getlogin()
        self.os = f"{self.platform.system} {self.platform.version}"
        
    def run(self, code, format='python'):
        console = Console()
        syntax = Syntax(code, format, theme="github-dark", line_numbers=True)
        
        console.print(f'[bold #4a4e54]{chr(0x1F785)} Running `{format}`...[/bold #4a4e54]')
        console.print(syntax)
        print()
        
        output = ""
        
        if format == 'python':
            output = self.run_python(code)
        elif format == 'shell':
            output = self.run_shell(code)
        elif format == 'applescript' and platform.system() == 'Darwin':
            output = self.run_applescript(code)
        elif format == 'js':
            output = self.run_js(code)
        else:
            output = f"MindFlow does not support the format: {format}"
        
        return output if output else "The following code did not generate any console text output, but may generate other output."
 

    def run_python(self, code):
        output = io.StringIO()
        stdout = sys.stdout
        sys.stdout = output
        try:
            exec(code, {})
        except Exception as e:
            output.write(f"An error occurred: {e}")
        finally:
            sys.stdout = stdout
        return output.getvalue()

    def run_shell(self, code):
        try:
            result = os.system(code)
            return f"Command executed with exit code: {result}"
        except Exception as e:
            return f"An error occurred: {e}"

    def run_applescript(self, code):
        try:
            result = os.system(f'osascript -e "{code}"')
            return f"Command executed with exit code: {result}"
        except Exception as e:
            return f"An error occurred: {e}"

    def run_js(self, code):
        try:
            result = os.system(f'node -e "{code}"')
            return f"Command executed with exit code: {result}"
        except Exception as e:
            return f"An error occurred: {e}"
