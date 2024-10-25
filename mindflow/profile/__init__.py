from typing import TypedDict, List, Dict

class User(TypedDict):
    name: str
    version: str

class Assistant(TypedDict):
    name: str
    personality: str
    messages: List[str]
    local: bool
    breakers: List[str]

class Safeguards(TypedDict):
    timeout: int
    auto_run: bool
    auto_install: bool

class Paths(TypedDict):
    prompts: str
    memories: str

class Config(TypedDict):
    telemetry: bool
    ephemeral: bool
    verbose: bool

class Profile(TypedDict):
    user: User
    assistant: Assistant
    safeguards: Safeguards
    paths: Paths
    extensions: Dict
    config: Config
