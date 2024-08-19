from snova import SnSdk
from datetime import datetime
import re

def interpret_input(input_str):
    pattern = r'```(?P<format>\w+)\n(?P<content>[\s\S]+?)```|(?P<text>[^\n]+)'
    
    matches = re.finditer(pattern, input_str)
    
    blocks = []
    current_message = None
    
    for match in matches:
        if match.group("format"):
            if current_message:
                blocks.append(current_message)
                current_message = None
            block = {
                "type": "code",
                "format": match.group("format"),
                "content": match.group("content").strip()
            }
            blocks.append(block)
        else:
            text = match.group("text").strip()
            if current_message:
                current_message["content"] += "\n" + text
            else:
                current_message = {
                    "type": "message",
                    "content": text
                }
    
    if current_message:
        blocks.append(current_message)
    
    return blocks

def to_lmc(content: str, role: str = "assistant", type="message", format: str | None = None) -> dict:            
    lmc = {"role": role, "type": type, "content": content} 
    return lmc | ({} if format is None else {"format": format})
    
def to_chat(lmc: dict, logs=False) -> str:
    #_defaults = {}
    
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    time = datetime.now().strftime("%I:%M %p %m/%d/%Y")
    
    if logs:
        return f'\033[90m({time})\033[0m <type: {_type if _format is None else f"{_type}, format: {_format}"}> \033[1m{_role}\033[0m: {_content}'
    
    if _role == "system":
        return ("----- SYSTEM PROMPT -----\n" +
                _content + "\n----- END SYSTEM PROMPT -----")
    
    return f'({time}) [type: {_type if _format is None else f"{_type}, format: {_format}"}] *{_role}*: {_content}'

class LLM:
    def __init__(self, profile, verbose=False, messages: list = None, system=""):
        self.settings = profile.settings
        self.keys = profile.keys
        self.system = system

        self.verbose = verbose
        
        self.is_llm_default = self.keys["llm"] == self.settings["defaults"]["llm"]
        self.is_code_default = self.keys["code"] == self.settings["defaults"]["code"]
        self.is_vision_default = self.keys["vision"] == self.settings["defaults"]["vision"]

        # use SnSdk
        self.llm = SnSdk("Meta-Llama-3.1-405B-Instruct",
                         remember=True,
                         priority=0,
                         system=self.system,
                         messages=[] if messages is None else messages)
        self.messages = self.llm.messages

        if self.is_llm_default:
            self.chat = self.sn_chat
            
    def sn_chat(self, **kwargs):
        if self.system:
            return self.llm.chat(**kwargs, system=self.system, max_tokens=3000)
        return self.llm.chat(**kwargs, max_tokens=3000)
