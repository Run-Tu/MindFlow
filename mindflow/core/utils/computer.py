import sys
import io
from contextlib import redirect_stdout

class Computer:
    def __init__(self) -> None:
        pass
    
    def run_python(self, code):
        output = io.StringIO()
        stdout = sys.stdout
        sys.stdout = output
        
        try:
            exec(code)
        finally:
            sys.stdout = stdout
            
        output = output.getvalue()
        
        return output if output else "The following code did not generate any output"
