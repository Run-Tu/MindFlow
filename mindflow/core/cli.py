from .core import MindFlow
from rich.console import Console
from rich.markdown import Markdown
from datetime import datetime

def to_chat(lmc: dict) -> str:
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    time = datetime.now().strftime("%I:%M %p %d/%m/%Y")
    return (f"[bold #4a4e54]\u25CB ({time})[/bold #4a4e54] [italic bold]{_role}[/italic bold]", Markdown(_content))

def main(macro):
    console = Console()
    while True:
        query = input('~ ') or "plot an exponential graph"
        for response in macro.chat(query):
            author, content = to_chat(response)
            console.print(author)
            console.print(content)
            print()
