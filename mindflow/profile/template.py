from . import Profile
from ..extensions import Browser, Email
from ..utils import USERNAME

profile: Profile = Profile(
    user = { 
        "name": USERNAME, 
        "version": "1.0.0"
    },
    assistant = {
        "name": "Basil",
        "personality": "You have a kind, deterministic and professional attitude towards your work and respond in a formal, yet casual manner.",
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
        "prompts": "core/prompts",
        "extensions": "",
        "memories": f"profiles/{USERNAME}/1.0.0"
    },
    extensions = {
        "Browser": Browser,
        "Email": Email
    },
    config = {
        "telemetry": False,
        "ephemeral": False,
        "verbose": False,
        "local": False,
        "dev": False
    }
)
