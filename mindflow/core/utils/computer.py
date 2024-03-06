import io
import sys
import subprocess
import platform

class Computer:
    def __init__(self) -> None:
        pass
        
    def run(self, code, format='python'):
        lines = code.splitlines()
        print(f'Running `{format}`...')
        print('\n' + '\n'.join([f'{str(i+1).rjust(len(str(len(lines))))} | {line}' for i, line in enumerate(lines)]) + '\n')
        
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
        
        return output if output else "The following code did not generate any output"
 

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
            result = subprocess.run(code, shell=True, capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"An error occurred: {e}"

    def run_applescript(self, code):
        try:
            result = subprocess.run(['osascript', '-e', code], capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"An error occurred: {e}"

    def run_js(self, code):
        # try:
        #     subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        # except subprocess.CalledProcessError:
        #     return "Node.js is not installed. Please install Node.js to run JavaScript code."
        
        try:
            result = subprocess.run(['node', '-e', code], capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"An error occurred: {e}"
