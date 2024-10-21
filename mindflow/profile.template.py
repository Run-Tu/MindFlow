from mindflow import Profile, macro
from mindflow.extensions import browser, email

profile: Profile = Profile(
    user = { 
        "name": "Amor", 
        "version": "1.0.0"
        },
    safeguards = { "timeout": 16 },
    path = { 
        "prompts": "/core/prompts",
        "memories" : f"/{macro.name}/{macro.version}" 
        },
    extensions = {
        "browser": browser,
        "email": email
        }
)

macro.profile = profile
macro.llm.messages = []
