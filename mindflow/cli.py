from mindflow import macro
from rich.console import Console
from rich.markdown import Markdown
from datetime import datetime

def to_chat(lmc: dict) -> str:
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    time = datetime.now().strftime("%I:%M %p %d/%m/%Y")
    return (f"[bold #4a4e54]{chr(0x1F785)} ({time})[/bold #4a4e54] [italic bold]{_role}[/italic bold]", Markdown(_content))

def main():
    console = Console()
    while True:
        query = input('~ ') or "plot an exponential graph"
        for response in macro.chat(query):
            author, content = to_chat(response)
            console.print(author)
            console.print(content)
            print()
            
if __name__ == "__main__":
    main()
