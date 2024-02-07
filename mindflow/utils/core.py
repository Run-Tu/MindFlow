from .engines import Search
from .computer import Computer
from .model import Model
from pathlib import Path

class MindFlow:
    """
    The core of all operations occurs here.
    Where the system breaks down requests from the user and executes them.
    """
    def __init__(self,
                 messages: list | None = None,
                 history_dir: Path | None = None,
                 skills_dir: Path | None = None,
                 prompts_dir: Path | None = None,
                 verbose: bool = False,
                 local: bool = False,
                 computer = None,
                 browser = None,
                 model = None) -> None:
        
        # utils
        self.browser = Search() if browser is None else browser
        self.computer = Computer() if computer is None else computer
        self.model = Model() if model is None else model

        # logging + debugging
        self.verbose = verbose
        
        # memory + history
        self.history_dir = Path(Path(__file__).parent, "memory", "history") if history_dir is None else history_dir
        self.skills_dir = Path(Path(__file__).parent, "memory", "skills") if skills_dir is None else skills_dir
        self.prompts_dir = Path(Path(__file__).parent, "prompts") if prompts_dir is None else prompts_dir
        self.messages = [] if messages is None else messages

        # experimental
        self.local = local

    def classify(self, message):
        """
        Classify whether the message is either a question, task or routine.
        """
        with open(Path(self.prompts_dir, "classify.txt"), "r") as f:
            prompt = f.read()
        return self.model.chat(prompt + message, model="gpt-4o")

    def chat(self, 
             message: str = None, 
             display: bool = True, 
             stream: bool = False):
        
        self.messages.append(self.to_lmc(message, role="user"))        
        mode = self.classify(message).lower()

        if mode == "chat":
            self.set_chat(message, display)
        elif mode == "task":
            self.set_task(message, display)
        elif mode == "routine":
            self.set_routine(message, display)
        else:
            raise ValueError("Invalid classification of message.")

    def set_chat(self, message, display):
        response = self.model.chat(message, model="gpt-4o")
        self.messages.append(self.to_lmc(response))

        if display:
            print(response)

    def set_task(self):
        pass

    def set_routine(self):
        pass

    def to_lmc(self, 
               content: str, 
               role: str = "assistant",
               type="message") -> dict:
        return {"role": role, "type": type, "content": content}



