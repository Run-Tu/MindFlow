from ..computer import Computer
from ..profile import Profile
from ..profile.template import profile as default_profile

from ..llm import LLM, to_lmc, to_chat, interpret_input
from ..utils import ROOT_DIR, OS, generate_id, get_relevant, load_profile, load_prompts

from ..memory.server import Manager
from ..memory.client import Memory
from chromadb.config import Settings

from datetime import datetime
from pathlib import Path
import threading
import asyncio
import json
import os
import re


class MindFlow:
    """
    The core of all operations occurs here.
    Where the system breaks down requests from the user and executes them.
    """
    def __init__(
            self,
            profile: Profile = None,
            profile_path: Path | str = None,
            messages: list | None = None,
            prompts_dir: Path | None = None,
            memories_dir: Path | None = None,
            tts: bool = False,
            stt: bool = False,
            verbose: bool = False,
            conversational: bool = False,
            telemetry: bool = False,
            local: bool = False,
            computer = None,
            dev = False,
            llm = None,
            extensions: dict = {},
            breakers = ("the task is done.", "the conversation is done.")) -> None:
        
        profile = profile or load_profile(profile_path) or default_profile
        self.profile = profile
        
        # setup other instances
        self.computer = computer or Computer(profile_path=profile.get("path", None),
                                             paths=profile.get("languages", {}),
                                             extensions=extensions or profile.get("extensions", {}))
    
        # logging + debugging
        self.verbose = verbose or profile["config"]["verbose"]
        self.conversational = conversational or profile["config"]["conversational"]
        self.tts = tts or profile["config"].get("tts", {})
        self.stt = tts or profile["config"].get("stt", {})
        
        # loop breakers
        self.breakers = breakers or profile["assistant"]["breakers"]
        
        # settings
        self.safeguards = profile["safeguards"]
        self.dev = dev or profile["config"]["dev"]
        
        # setup setup variables
        self.info = {
            "assistant": profile['assistant']['name'],
            "personality": profile['assistant']['personality'],
            "username": profile["user"]["name"],
            "version": profile["user"]["version"],
            "os": OS,
            "supported": list(self.computer.supported),
            "extensions": extensions or self.computer.load_instructions()
        }
        
        # setup paths
        paths = self.profile["paths"]
        self.prompts_dir = prompts_dir or paths.get("prompts")
        self.memories_dir = memories_dir or paths.get("memories") or Path(ROOT_DIR, "profiles", self.info["username"], self.info["version"])
        
        # setup memory
        self.memory_manager = Manager(path=self.memories_dir, telemetry=telemetry)
        self.memory_manager.serve()
        
        self.memory = Memory(host='localhost', 
                             port=8000,
                             settings=Settings(anonymized_telemetry=telemetry))
        self.ltm = self.memory.get_or_create_collection("ltm")
        self.cache = self.memory.get_or_create_collection("cache")
        
        # experimental (not yet implemented)
        self.local = local or profile["config"]["local"]

        # setup prompts
        self.prompts = load_prompts(self.prompts_dir, 
                                    self.info, 
                                    self.conversational)
            
        # setup llm
        self.name = profile['assistant']["name"]
        self.llm = llm or LLM(messages=messages, 
                              verbose=verbose, 
                              system=self.prompts['initial']) 
        
        self.loop = asyncio.get_event_loop()
        
    async def remember(self, message):
        document = self.ltm.query(query_texts=[message],
                                  n_results=3,
                                  include=["documents", "metadatas", "distances"])
        
        # filter by distance
        snapshot = get_relevant(document, threshold=1.45)
        #print(snapshot)
        if not snapshot.get("documents"):
            return []
        
        memories = []
        for document, metadata in zip(snapshot.get("documents", []),
                                      snapshot.get("metadatas", [])):
            text = f"{document}\n[metadata: {metadata}]"
            memories.append(to_lmc(text, role="Memory", type="memory snapshot"))
        
        #print(memories)
        return memories
    
    def add_memory(self, memory):
        # check if ai fails to format json
        try: memory = json.loads(memory)
        except: return
        
        # check memory defined correctly
        if not memory.get("memory"): 
            return
            
        kwargs = {"documents": [memory["memory"]],
                  "ids": [generate_id()],
                  "metadatas": [memory.get("metadata", {}) | 
                                {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]}
        self.ltm.add(**kwargs)

        
    def memorise(self, messages):
        memory = self.llm.chat("\n\n".join(map(to_chat, messages)), 
                               system=self.prompts["memorise"],
                               remember=False,
                               stream=False)
        if not memory: return
        self.add_memory(memory)
        
    def thread_memorise(self, messages: list[str]):
        thread = threading.Thread(target=self.memorise, args=[messages])
        thread.start()
        thread.join()
        
    async def streaming_chat(self, 
                             message: str = None, 
                             remember=True,
                             timeout=None,
                             lmc=False):
        
        timeout = timeout or self.safeguards["timeout"]
    
        response, notebooks, hidden = "", {}, False
        for _ in range(timeout):
            # TODO: clean up. this is really messy.
            
            # remember anything relevant
            
            if not lmc and (memory := await self.remember(message)):
                #print(memory)
                # if self.dev or self.verbose:
                #     for chunk in memory:
                #         yield chunk
                self.llm.messages += memory
            
            async for chunk in self.llm.chat(message=message, 
                                             stream=True,
                                             remember=remember, 
                                             lmc=lmc):
                response += chunk
                if self.conversational:
                    if self.verbose or self.dev:
                        pass
                    elif "<hidden>" in chunk:
                        hidden = True
                        continue
                    elif "</hidden>" in chunk:
                        hidden = False
                        continue
                
                if not hidden:
                    yield chunk
                
            if self.conversational:
                yield "<end>"
                
            # memorise if relevant
            memorise = [] if lmc else [to_lmc(message, role="User")]
            self.thread_memorise(self.llm.messages[:-3] + memorise + [to_lmc(response)])
                
            # because of this, it's only partially async
            # will fix in future versions
            lmc = False
            
            for chunk in interpret_input(response): 
                if chunk.get("type", None) == "code":
                    language, code = chunk.get("format"), chunk.get("content")
                    if language in notebooks: notebooks[language] += "\n\n" + code
                    else: notebooks[language] = code
                
                elif "let's run the code" in chunk.get("content").lower():
                    for language, code in notebooks.items():
                        output = self.computer.run(code, language)
                        message, lmc = to_lmc(output, role="computer", format="output"), True
                        if self.dev or self.verbose: 
                            yield message
                    notebooks = {}
                    
            response = ""
            if not lmc or chunk.get("content", "").lower().endswith(self.breakers):
                return
    
        raise Warning("MindFlow has exceeded it's timeout stream of thoughts!")
    
    async def _gather(self, gen):
        return "".join([str(chunk) async for chunk in gen])

    def chat(self, 
             message: str | None = None, 
             stream: bool = False,
             remember: bool = True,
             lmc: bool = False,
             timeout=16):
        timeout = timeout or self.safeguards["timeout"]
    
        gen = self.streaming_chat(message, remember, timeout, lmc)
        if stream: return gen
        return self.loop.run_until_complete(self._gather(gen))
