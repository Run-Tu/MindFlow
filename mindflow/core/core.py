from ..core.utils.computer import Computer
from ..core.utils.llm import LLM, to_lmc
from ..core.utils.general import load_settings, ROOT_DIR
from ..extensions import Extensions
from pathlib import Path
import os

class Profile:
    """
    store apikeys here. this is temp since its a bad setup omg.
    """
    def __init__(self, config_file= None, keys: dict ={}):
        
        self.settings = load_settings(file=config_file)
        self.keys = keys
        if not keys:
            self.keys = self.settings["defaults"]
            
            
    def __str__(self):
        return f'Profile({self.keys})'

class MindFlow:
    """
    The core of all operations occurs here.
    Where the system breaks down requests from the user and executes them.
    """
    def __init__(
            self,
            messages: list | None = None,
            history_dir: Path | None = None,
            skills_dir: Path | None = None,
            prompts_dir: Path | None = None,
            extensions_dir: Path | None= None,
            verbose: bool = False,
            local: bool = False,
            computer = None,
            profile = None,
            llm = None,
            tasks = False,
            breakers = ("the task is done.", "the conversation is done.")) -> None:
        
        # settings
        self.profile = Profile() if profile is None else profile
        self.settings = self.profile.settings
        
        # utils
        self.extensions = Extensions()
        self.computer = Computer(self.extensions) if computer is None else computer
        self.llm = LLM(self.profile, messages=messages, verbose=verbose) if llm is None else llm
        self.tasks = tasks

        # logging + debugging
        self.verbose = verbose
        
        # loop breakers
        self.breakers = breakers
        
        # memory + history
        self.history_dir = Path(Path(__file__).parent, "memory", "history") if history_dir is None else history_dir
        self.skills_dir = Path(Path(__file__).parent, "memory", "skills") if skills_dir is None else skills_dir
        self.prompts_dir = Path(Path(__file__).parent, "prompts") if prompts_dir is None else prompts_dir
        self.extensions_dir = Path(Path(__file__).parent.parent, "extensions") if extensions_dir is None else extensions_dir
        
        self.llm.messages = [] if messages is None else messages

        # experimental
        self.local = local

        # prompts
        self.prompts = {}
        prompts = os.listdir(self.prompts_dir)
        for filename in prompts:
            with open(Path(self.prompts_dir, filename), "r") as f:
                self.prompts[filename.split('.')[0]] = f.read().strip()
        
        self.prompts['initial'] = self.prompts['initial'].format(assistant=self.settings['assistant']['name'],
                                                                 personality=self.settings['assistant']['personality'],
                                                                 username=self.computer.user,
                                                                 os=self.computer.os)
        
        self.prompts['initial'] += "\n\n" + self.prompts['instructions'].format(supported=self.computer.supported,
                                                                                extensions=self.extensions.load_instructions())

    def chat(self, 
            message: str = None, 
            stream: bool = False,
            timeout=16):
        
        lmc, conversation = False, set()
        notebooks = {}
        for _ in range(timeout):
            responses = self.llm.chat(message=message, 
                                      system=self.prompts["initial"],
                                      lmc=lmc)
            lmc = False
            
            for response in responses: 
                if response.get("type", None) == "message":
                    conversation.add("message")
                    yield response
                
                if response.get("type", None) == "code":
                    language, code = response.get("format", "python"), response.get("content", None)
                    if language in notebooks:
                        notebooks[language] += "\n\n" + code
                    else:
                        notebooks[language] = code
                    self.computer.md(code, language)
                    
                if "let's run the code" in response.get("content").lower():
                    for language, code in notebooks.items():
                        output = to_lmc(self.computer.run(code, format=language),
                                            role="computer", format="output")
                        if output.get("content", None):
                            yield output
                            message, lmc = output, True
                        conversation.add("code")
            
            if not ("code" in conversation) or response.get("content").lower().endswith(self.breakers):
                notebooks = {}
                return 
            
        raise Warning("MindFlow has exceeded it's timeout stream of thoughts!")

