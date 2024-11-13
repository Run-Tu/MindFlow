from pathlib import Path
from random import choice
from rich import print
import aiohttp
import asyncio
import json

def to_lmc(content: str, role: str = "assistant") -> dict: 
    return {"role": role, "content": content}

def available() -> set:
    return {"Meta-Llama-3.1-8B-Instruct", "Meta-Llama-3.1-70B-Instruct", "Meta-Llama-3.1-405B-Instruct", "Samba CoE", "Mistral-T5-7B-v1", "v1olet_merged_dpo_7B", "WestLake-7B-v2-laser-truthy-dpo", "DonutLM-v1", "SambaLingo Arabic", "SambaLingo Bulgarian", "SambaLingo Hungarian", "SambaLingo Russian", "SambaLingo Serbian (Cyrillic)", "SambaLingo Slovenian", "SambaLingo Thai", "SambaLingo Turkish", "SambaLingo Japanese"}

class SambaNova:
    def __init__(self, 
                 api_key: str,
                 model="Meta-Llama-3.1-8B-Instruct", 
                 messages=None,
                 system="You are a helpful assistant.",
                 remember=False,
                 limit=30,
                 endpoint= "https://api.sambanova.ai/v1/chat/completions"):
    
        if model in available(): 
            self.model = model
        else: 
            self.model = "Meta-Llama-3.1-8B-Instruct"
        
        self.api_key = api_key
        self.messages = [] if messages is None else messages
        self.remember = remember
        self.limit = limit
        self.system = to_lmc(system, role="system")
        self.endpoint = endpoint
        self.loop = asyncio.get_event_loop()
            
    async def async_stream_chat(self, data, remember=False):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint, 
                                    headers={"Authorization": f"Bearer {self.api_key}"}, 
                                    json=data) as response:
                message = ""
                async for line in response.content:
                    if line:
                        decoded_line = line.decode('utf-8')[6:]
                        if not decoded_line or decoded_line.strip() == "[DONE]":
                            continue
        
                        try:
                            json_line = json.loads(decoded_line)
                        except json.JSONDecodeError as e:
                            print(line)
                            raise json.JSONDecodeError(e) # better implementation for later
                        
                        if json_line.get("error"):
                            yield json_line.get("error", {}).get("message", "An unexpected error occured!")
                    
                        options = json_line.get("choices")[0]
                        if options.get("finish_reason") == "end_of_text":
                            continue

                        chunk = options.get('delta', {}).get('content', '')
                        if self.remember or remember:
                            message += chunk

                        yield chunk
                
                if self.remember or remember:
                    self.messages.append(to_lmc(message))
                    if (length := len(self.messages)) > self.limit:
                        del self.messages[0]

    def chat(self, 
             message: str, 
             role="user", 
             stream=False,
             max_tokens=1400,
             remember=False, 
             lmc=False,
             asynchronous=True,
             system: str = None):
        
        system = to_lmc(system, role="system") if system else self.system
        if not lmc:
            message = to_lmc(message, role=role)
        elif message is None:
            message = self.messages[-1]
            self.messages = self.messages[:-1]
                    
        template = {"model": self.model,
                    "messages": [system] + self.messages + [message],
                    "max_tokens": max_tokens,
                    "stream": True} # lmao, we'll fix this later :p
            
        if self.remember or remember:
            self.messages.append(message)
            
        if stream: 
            return self.async_stream_chat(template, remember)
        return self.loop.run_until_complete(self.static_chat(template, remember))
        
    async def static_chat(self, template, remember):
        return "".join([chunk 
                        async for chunk in 
                        self.async_stream_chat(template, remember)])

async def main():
    llm = SambaNova("APIKEY",
                    remember=True)
    while True:
        async for chunk in llm.chat(input("message: "), stream=True):
            print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(main())
