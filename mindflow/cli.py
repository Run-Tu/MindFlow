from rich import print
from rich.markdown import Markdown
from datetime import datetime
from .speech import Speech

import threading


def to_chat(lmc: dict, content = True) -> str:
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    time = datetime.now().strftime("%I:%M %p %d/%m/%Y")
    display = f"[bold #4a4e54]\u25CB ({time})[/bold #4a4e54] [italic bold]{_role}[/italic bold]"
    if content:
        return (display, _content)
    return display

async def main(macro):
    split = False
    hidden = False
    
    if macro.profile["tts"]["enabled"]:
        speech = Speech(tts=macro.profile["tts"])
        
    while True:
        user = to_chat({"role": macro.profile["user"]["name"]}, content=False)
        print(user)
        try:
            query = input('~ ') or "plot an exponential graph"
        except Exception as e:
            print("Exiting `mindflow`...")
            exit()
        
        assistant = to_chat({"role": macro.name}, content=False)
        print("\n" + assistant)
        async for chunk in macro.chat(query, stream=True):
            if isinstance(chunk, dict):        
                print("\n")
                computer, content = to_chat(chunk)
                print(computer)
                print(content)
                
                if chunk.get("role", "").lower() == "computer":
                    assistant = to_chat({"role": macro.name}, content=False)
                    print("\n" + assistant)
        

            elif macro.profile["tts"]["enabled"]:
                if "<hidden>" in chunk:
                    hidden = True
                elif "</hidden>" in chunk:
                    hidden = False
                    
                if not hidden and not "</hidden>" in chunk:
                    speech.tts.stream(chunk)
                    
            if isinstance(chunk, str) and not (chunk == "<end>"):
                print(chunk, end="")
            
        print("\n")
