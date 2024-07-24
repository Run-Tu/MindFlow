from .core import MindFlow
from rich.console import Console
from rich.markdown import Markdown
from datetime import datetime

def to_chat(lmc: dict, content = True) -> str:
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    time = datetime.now().strftime("%I:%M %p %d/%m/%Y")
    display = f"[bold #4a4e54]\u25CB ({time})[/bold #4a4e54] [italic bold]{_role}[/italic bold]"
    if content:
        return (display, Markdown(_content))
    return display

async def main(macro):
    console = Console()
    split = False
    while True:
        user = to_chat({"role": macro.computer.user}, content=False)
        console.print(user)
        query = input('~ ') or "plot an exponential graph"
        
        assistant = to_chat({"role": macro.name}, content=False)
        console.print("\n" + assistant)
        async for chunk in macro.chat(query, stream=True):
            if split:
                assistant = to_chat({"role": macro.name}, content=False)
                console.print("\n" + assistant)
                split = False
        
            if isinstance(chunk, dict):
                split = True
                print("\n")
                computer, content = to_chat(chunk)
                console.print(computer)
                console.print(content)
                print()
            else:
                console.print(chunk, end="")

        print("\n")
