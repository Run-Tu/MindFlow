from gradio_client import Client
from datetime import datetime
from functools import partial

from mindflow.core.defaults import (LLM_DEFAULT, LLM_SRC,
                        CODE_DEFAULT, CODE_SRC,
                        VISION_DEFAULT, VISION_SRC)
# omg lmao this is so bad

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
    
    # _args = lmc.keys()
    # _args.remove("role")
    # _args.remove("content")
    
    # _args = [arg + ": " + lmc.get(arg, "None") for arg in _args]
    
    time = datetime.now().strftime("%I:%M %p %m/%d/%Y")
    
    if logs:
        return f'\033[90m({time})\033[0m [type: {_type if _format is None else f"{_type}, format: {_format}"}] \033[1m{_role}\033[0m: {_content}'
    return f'({time}) [type: {_type if _format is None else f"{_type}, format: {_format}"}] *{_role}*: {_content}'

class LLM:
    def __init__(self, api_key, verbose=False, messages: list = []):
        self.keys = api_key.keys

        self.verbose = verbose
        self.messages = messages

        is_llm_default = self.keys.get("llm", LLM_DEFAULT) == LLM_DEFAULT
        is_code_default = self.keys.get("code", CODE_DEFAULT) == CODE_DEFAULT
        is_vision_default = self.keys.get("vision", VISION_DEFAULT) == VISION_DEFAULT

        # self.chat = self.litellm_chat
        if is_llm_default: 
            self.llm = Client(LLM_SRC)
            self.chat = self.gradio_chat

        if is_code_default: pass
        if is_vision_default: pass

    # def perform_search(self, queries, complexity, widget=None):
    #     # placeholder function
    #     if self.verbose:
    #         print(f"\nSearching results for `{queries}`")
    #     return self.browser.search(queries, complexity, widget)
        

    def gradio_chat(self, 
                    message: str, 
                    role = "user", 
                    remember=True, 
                    context=True,
                    lmc=False,
                    system: str = 'You are a helpful assistant.'):
        
        system = to_lmc(system, role="system")
        message = message if lmc else to_lmc(message, role=role)
        
        to_send = [system] + (self.messages if context is True else context) + [message]
        
        if remember:
            self.messages.append(message)
            
        if self.verbose:
            print('\n' + '\n'.join(map(partial(to_chat, logs=True), to_send)))
            
        responses = interpret_input(self.llm.predict(user_message='\n'.join(map(to_chat, to_send)), api_name="/predict"))
        
        for response in responses:
            if remember:
                self.messages.append(response | {"role": "assistant"})
                
            if self.verbose:
                print(to_chat(response | {"role": "assistant"}, logs=True))

        return responses

    # def chat(self, message: str):
    #     # Classify the prompt
    #     needs_search = self.classify_prompt(message)

    #     # Check if a web search is needed
    #     if not needs_search['search']:
    #         # Generate a response using LLM
    #         response = self.chat(message, role="user")
    #         return response

    #     # Check if widget is available
    #     if needs_search['widget']:

    #         # Perform the search
    #         to_search, n, widget = needs_search["search"], needs_search["complexity"], needs_search["widget"]
    #         search = self.perform_search(to_search, n, widget)

    #         response = self.chat(message, role="user", context=[to_lmc(search, role="browser", type="info")]) 
    #         return response
        
    #     searches = self.perform_search(needs_search['search'], needs_search.get('complexity', 1))
    #     results = self.browser.load_searches(searches, complexity=needs_search.get('complexity', 1))
        
    #     response = self.chat(message, 
    #                              role="user", 
    #                              context=self.messages + [to_lmc(str(results))])

    #     return response


