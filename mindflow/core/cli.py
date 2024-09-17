from rich import print
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
    split = False
    while True:
        user = to_chat({"role": macro.computer.user}, content=False)
        print(user)
        try:
            query = input('~ ') or "plot an exponential graph"
        except Exception as e:
            print("Exiting `mindflow`...")
            exit()
            
        
        assistant = to_chat({"role": macro.name}, content=False)
        print("\n" + assistant)
        async for chunk in macro.chat(query, stream=True):
            if split:
                assistant = to_chat({"role": macro.name}, content=False)
                print("\n" + assistant)
                split = False
        
            if isinstance(chunk, dict):
                split = True
                print("\n")
                computer, content = to_chat(chunk)
                print(computer)
                print(content, end="")
            else:
                print(chunk, end="")

        print("\n")
