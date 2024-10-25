from ..computer import Computer
from ..profile.template import profile as default_profile

from ..llm import LLM, to_lmc, interpret_input
from ..utils import ROOT_DIR, OS

import chromadb
from chromadb.config import Settings

from pathlib import Path
import asyncio
import os
import re

class MindFlow:
    """
    The core of all operations occurs here.
    Where the system breaks down requests from the user and executes them.
    """
    def __init__(
            self,
            profile = None,
            messages: list | None = None,
            prompts_dir: Path | None = None,
            memories_dir: Path | None = None,
            extensions_dir: Path | None= None,
            verbose: bool = False,
            telemetry: bool = False,
            local: bool = False,
            computer = None,
            dev = True,
            llm = None,
            extensions: dict = {},
            breakers = ("the task is done.", "the conversation is done.")) -> None:
        
    
        # logging + debugging
        self.verbose = verbose or profile["config"]["verbose"]
        
        # loop breakers
        self.breakers = breakers or profile["assistant"]["breakers"]
        
        # settings
        self.profile = profile or default_profile
        self.safeguards = profile["safeguards"]
        self.dev = dev or profile["config"]["dev"]
        
        # setup other instances
        self.computer = computer or Computer(extensions or profile["extensions"])
        
        # setup setup variables
        self.info = {
            "assistant": profile['assistant']['name'],
            "personality": profile['assistant']['personality'],
            "username": profile["user"]["name"],
            "version": profile["user"]["version"],
            "os": OS,
            "supported": self.computer.supported,
            "extensions": "" # extensions or profile["extensions"]
        }
        
        # setup paths
        paths = self.profile["paths"]
        self.prompts_dir = prompts_dir or ROOT_DIR / Path(paths["prompts"])
        self.memories_dir = memories_dir or ROOT_DIR / Path(paths["memories"])
        self.extensions_dir = extensions_dir or ROOT_DIR / Path(paths["extensions"])
        
        # setup memory
        self.ltm = chromadb.PersistentClient(str(self.memories_dir), Settings(anonymized_telemetry=telemetry))    
        self.stm = chromadb.Client(Settings(anonymized_telemetry=telemetry))
        self.collection = self.stm.create_collection("global")
        
        # experimental (not yet implemented)
        self.local = local or profile["config"]["local"]

        # setup prompts
        self.prompts = {}
        prompts = os.listdir(self.prompts_dir)
        for filename in prompts:
            with open(Path(self.prompts_dir, filename), "r") as f:
                name = filename.split('.')[0]
                self.prompts[name] = f.read().strip()
            self.prompts[name] = self.prompts[name].format(**{replace:self.info.get(replace) 
                                                              for replace in re.findall(r'\{(.*?)\}', self.prompts[name])})

        self.prompts['initial'] += "\n\n" + self.prompts['instructions']
            
        # setup llm
        self.name = profile['assistant']["name"]
        self.llm = LLM(messages=messages, 
                       verbose=verbose, 
                       system=self.prompts['initial']) if llm is None else llm
        self.loop = asyncio.get_event_loop()
        
    async def streaming_chat(self, 
                             message: str = None, 
                             remember=True,
                             timeout=None,
                             lmc=False):
        
        timeout = timeout or self.safeguards["timeout"]
    
        response, notebooks = "", {}
        for _ in range(timeout):
            async for chunk in self.llm.chat(message=message, 
                                             stream=True,
                                             remember=remember, 
                                             lmc=lmc):
                response += chunk
                yield chunk
                
            # because of this, it's only partially async
            # will fix in future versions
            lmc = False
            
            for chunk in interpret_input(response): 
                if chunk.get("type", None) == "code":
                    language, code = chunk.get("format"), chunk.get("content")
                    if language in notebooks:
                        notebooks[language] += "\n\n" + code
                    else:
                        notebooks[language] = code
                
                elif "let's run the code" in chunk.get("content").lower():
                    for language, code in notebooks.items():
                        output = self.computer.run(code, language)
                        message, lmc = to_lmc(output, role="computer", format="output"), True
                        if self.dev:
                            yield message
                    notebooks = {}
                    
            response = ""
            if not lmc or chunk.get("content", "").lower().endswith(self.breakers):
                return
    
        raise Warning("MindFlow has exceeded it's timeout stream of thoughts!")
    
    async def _gather(self, gen):
        return await "".join([chunk async for chunk in gen])

    def chat(self, 
             message: str | None = None, 
             stream: bool = False,
             remember: bool = True,
             lmc: bool = False,
             timeout=16):
        timeout = timeout or self.safeguards["timeout"]
    
        gen = self.streaming_chat(message, remember, timeout, lmc)
        if stream: return gen
        return self.loop.run_until_complete(self._gather(self, gen))
