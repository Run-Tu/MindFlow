from mindflow.profile import Profile
from mindflow.extensions import Browser, Email
from mindflow.utils import config
from rich import print

browser = config(Browser, engine="google", headless=True)
email = config(Email, email="run-tu@gmail.com", password="password")

profile: Profile = Profile(
    user = { 
        "name": "Amor", 
        "version": "1.0.0"
    },
    assistant = {
        "name": "Basil",
        "personality": "",
        "messages": [],
        "breakers": ["the task is done.", "the conversation is done."]
    },
    safeguards = { "timeout": 16, "auto_run": True, "auto_install": True },
    paths = { 
        "prompts": "/core/prompts",
        "memories" : f"/Amor/1.0.0" 
    },
    extensions = {
        "Browser": browser,
        "Email": email
    },
    config = {
        "telemetry": False,
        "ephemeral": False,
        "verbose": False
    },
    languages = {
        "python": ["py", "-c"]
    }
)

#macro = MindFlow(profile)
print(profile)
