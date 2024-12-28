from mindflow.profile import Profile
from mindflow.utils import USERNAME, ROOT_DIR
from mindflow.extensions import BrowserKwargs
from pathlib import Path

profile: Profile = Profile(
    user = { 
        "name": USERNAME, 
        "version": "1.0.0"
    },
    assistant = {
        "name": "Macro",
        "personality": "You respond in a professional attitude and respond in a formal, yet casual manner.",
        "messages": [],
        "breakers": ["the task is done.", 
                     "the conversation is done."]
    },
    safeguards = { 
        "timeout": 16, 
        "auto_run": True, 
        "auto_install": True 
    },
    paths = { 
        "prompts": Path(ROOT_DIR, "core", "prompts"),
    },
    config = {
        "telemetry": False,
        "ephemeral": False,
        "verbose": True,
        "local": False,
        "dev": False,
        "conversational": True,
    },
    extensions = {
        "Browser": BrowserKwargs(engine="google")
    },
    tts = {
        "enabled": True,
        "engine": "SystemEngine"
    },
    env = {
        
    }
)
