import sys
import io
from contextlib import redirect_stdout

class Computer:
    def __init__(self) -> None:
        pass
    
    def run_python(self, code):
        return eval(code)
