from ...core.utils.general import load_settings
from gradio_client import Client, exceptions
from datetime import datetime
from functools import partial
import asyncio
import os
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
        return f'\033[90m({time})\033[0m [type: {_type if _format is None else f"{_type}, format: {_format}"}] \033[1m{_role}\033[0m: {_content}'
    
    if _role == "system":
        return ("----- SYSTEM PROMPT -----\n" +
                _content + "\n----- END SYSTEM PROMPT -----")
    
    return f'({time}) [type: {_type if _format is None else f"{_type}, format: {_format}"}] *{_role}*: {_content}'

class LLM:
    def __init__(self, profile, verbose=False, messages: list = []):
        self.settings = profile.settings
        self.keys = profile.keys

        self.verbose = verbose
        self.messages = messages
        
        self.is_llm_default = self.keys["llm"] == self.settings["defaults"]["llm"]
        self.is_code_default = self.keys["code"] == self.settings["defaults"]["code"]
        self.is_vision_default = self.keys["vision"] == self.settings["defaults"]["vision"]

        # Set up Gradio Client Endpoints
        asyncio.run(self.setup_client())

        if self.is_llm_default:
            self.chat = self.gradio_chat

    async def create_client(self, key):
        return Client(self.settings["defaults"]["src"][key])

    async def setup_client(self):
        tasks = {key: self.create_client(key) for key in tuple(self.keys)[:-1] if getattr(self, f"is_{key}_default")}
        clients = await asyncio.gather(*tasks.values())
        
        for key, client in zip(tasks.keys(), clients):
            setattr(self, key, client)

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
        
        to_send = (self.messages if context is True else context) + [message]
        
        if remember:
            self.messages.append(message)
            
        if self.verbose:
            print("\n----- MESSAGE HISTORY -----")
            print('\n'.join(map(partial(to_chat, logs=True), to_send)))
        
        try:
            response = self.llm.predict(history=[['\n'.join(map(to_chat, to_send)), None]], 
                                                         system_prompt=system,
                                                         max_tokens=8192,
                                                         api_name="/bot")
            responses = interpret_input(response[-1][-1])
        except exceptions.AppError as e:
            print(f"gradio_client.exceptions.AppError({e})")
            exit()
        
        for response in responses:
            if remember:
                self.messages.append(response | {"role": "assistant"})
                
            if self.verbose:
                print(to_chat(response | {"role": "assistant"}, logs=True))
        
        if self.verbose:    
            print("--- END MESSAGE HISTORY ---\n")

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


