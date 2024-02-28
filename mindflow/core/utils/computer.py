import sys
import io
from contextlib import redirect_stdout

class Computer:
    def __init__(self) -> None:
        pass
    
    def run_python(self, code):
        output = io.StringIO()
        stdout = sys.stdout
        lines = code.splitlines()
        print('\n' + '\n'.join([f'{" "*(len(str(len(lines))) - len(str(i+1)))}{i+1} | {line}' for i, line in enumerate(lines)]) + '\n')
        
        sys.stdout = output
        exec(code)
        sys.stdout = stdout

        # try:
        #     print('\n' * 10 + '\n'.join([f'{i} | {line}' for i, line in enumerate(code.splitlines())]) + '\n' * 10)
        #     exec(code)
        # finally:
        #     sys.stdout = stdout
            
        output = output.getvalue()
        
        return output if output else "The following code did not generate any output"
