# MindFlow

<div align="center">
<a href="https://github.com/Run-Tu/MindFlow/blob/main/LICENSE"><img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/></a>
<a href="https://github.com/Run-Tu/MindFlow/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/m/Run-Tu/MindFlow" alt="Commit Activity"/></a>
<a href="https://github.com/Run-Tu/MindFlow/commits/"><img src="https://img.shields.io/github/last-commit/Run-Tu/MindFlow" alt="Last Commit"/></a>
<a href="https://github.com/Run-Tu/MindFlow/stargazers"><img src="https://img.shields.io/github/stars/Run-Tu/MindFlow" alt="Stars"/></a>
</div>

MindFlow is an advanced multimodal personal agent designed to harness the power of Large Language Models (LLMs) for local code execution. As your autonomous digital assistant, MindFlow can complete and automate a wide range of tasks, from simple to complex, through self-prompting and natural language commands.

## Features

MindFlow provides a command-line interface for natural language interaction, allowing you to:

- Automate and complete various tasks.
- Analyze and visualize data.
- Access and browse the web for up-to-date information.
- Manipulate a variety of file types, including photos, videos, PDFs, and more.

Currently, MindFlow supports API keys for models powered by SambaNova. This choice is due to SambaNova's free, fast, and reliable service, which is ideal for the project's testing phase. Future versions will include support for other providers such as OpenAI and Anthropic.

This project draws significant inspiration from [`Open Interpreter`](https://github.com/OpenInterpreter/open-interpreter) ❤️

## Getting Started

To begin using MindFlow, obtain a free API key by creating an account at [https://cloud.sambanova.ai/](https://cloud.sambanova.ai/).

Next, install and start MindFlow with the following commands:

```shell
pip install mindflow
mindflow --api_key "YOUR_API_KEY"
```

> [!TIP]
> Encountering issues? Report them [here](https://github.com/amooo-ooo/MindFlow/issues/new) or try:

```shell
py -m pip install mindflow
py -m mindflow --api_key "YOUR_API_KEY"
```

> [!NOTE]
> The `--api_key` parameter is only needed once. For subsequent uses, simply run `mindflow` or `py -m mindflow`.

> [!TIP]
> Different API keys can be assigned to different profiles:

```shell
py -m mindflow --api_key "YOUR_API_KEY" --profile "path\to\profile"
```

## Profiles

MindFlow supports command-line arguments and customizable settings. View argument options with:

```shell
mindflow --help
```

To create and save personalized settings for future use:

```shell
mindflow --profile "path\to\profile"
```

MindFlow supports profiles in `JSON`, `TOML`, `YAML`, and `Python` formats. Below are examples of each format.

<details open>
<summary>Python</summary>

Example `profile.py`:

```python
from mindflow.profile import Profile
from mindflow.extensions import BrowserKwargs, EmailKwargs

profile: Profile = Profile(
    user = { 
        "name": "Run-Tu", 
        "version": "1.0.0"
    },
    assistant = {
        "name": "MindFlow",
        "personality": "You respond in a professional attitude and respond in a formal, yet casual manner.",
        "messages": [],
        "breakers": ["the task is done.", "the conversation is done."]
    },
    safeguards = { 
        "timeout": 16, 
        "auto_run": True, 
        "auto_install": True 
    },
    extensions = {
        "Browser": BrowserKwargs(headless=False, engine="google"),
        "Email": EmailKwargs(email="run-tu@example.com", password="password")
    },
    config = {
        "verbose": True,
        "conversational": True,
        "dev": False
    },
    languages = {
        "python": ["C:\Windows\py.EXE", "-c"],
        "rust": ["cargo", "script", "-e"]
    },
    tts = {
        "enabled": True,
        "engine": "OpenAIEngine",
        "api_key": "sk-example"
    }
)
```

To extend MindFlow and build your own app:

```python
async def main():
    from mindflow.core import MindFlowCore

    mindflow = MindFlowCore(profile)
    mindflow.llm.messages = []

    async for chunk in mindflow.chat("Plot an exponential graph for me!", stream=True):
        print(chunk, end="")

import asyncio
asyncio.run(main)
```

</details>

<details>
<summary>JSON</summary>

Example `profile.json`:

```json
{
    "user": {
        "name": "Run-Tu",
        "version": "1.0.0"
    },
    "assistant": {
        "name": "MindFlow",
        "personality": "You respond in a professional attitude and respond in a formal, yet casual manner.",
        "messages": [],
        "breakers": ["the task is done.", "the conversation is done."]
    },
    "safeguards": {
        "timeout": 16,
        "auto_run": true,
        "auto_install": true
    },
    "extensions": {
        "Browser": {
            "headless": false,
            "engine": "google"
        },
        "Email": {
            "email": "run-tu@example.com",
            "password": "password"
        }
    },
    "config": {
        "verbose": true,
        "conversational": true,
        "dev": false
    },
    "languages": {
        "python": ["C:\\Windows\\py.EXE", "-c"],
        "rust": ["cargo", "script", "-e"]
    },
    "tts": {
        "enabled": true,
        "engine": "OpenAIEngine",
        "api_key": "sk-example"
    }
}
```

</details>

<details>
<summary>TOML</summary>

Example `profile.toml`:

```toml
[user]
name = "Run-Tu"
version = "1.0.0"

[assistant]
name = "MindFlow"
personality = "You respond in a professional attitude and respond in a formal, yet casual manner."
messages = []
breakers = ["the task is done.", "the conversation is done."]

[safeguards]
timeout = 16
auto_run = true
auto_install = true

[extensions.Browser]
headless = false
engine = "google"

[extensions.Email]
email = "run-tu@example.com"
password = "password"

[config]
verbose = true
conversational = true
dev = false

[languages]
python = ["C:\\Windows\\py.EXE", "-c"]
rust = ["cargo", "script", "-e"]

[tts]
enabled = true
engine = "OpenAIEngine"
api_key = "sk-example"
```

</details>

<details>
<summary>YAML</summary>

Example `profile.yaml`:

```yaml
user:
  name: "Run-Tu"
  version: "1.0.0"

assistant:
  name: "MindFlow"
  personality: "You respond in a professional attitude and respond in a formal, yet casual manner."
  messages: []
  breakers:
    - "the task is done."
    - "the conversation is done."

safeguards:
  timeout: 16
  auto_run: true
  auto_install: true

extensions:
  Browser:
    headless: false
    engine: "google"
  Email:
    email: "run-tu@example.com"
    password: "password"

config:
  verbose: true
  conversational: true
  dev: false

languages:
  python: ["C:\\Windows\\py.EXE", "-c"]
  rust: ["cargo", "script", "-e"]

tts:
  enabled: true
  engine: "OpenAIEngine"
  api_key: "sk-example"
```

</details>

To switch between profiles, use:

```shell
mindflow --switch "run-tu"
```

Profiles also support versioning:

```shell
mindflow --switch "run-tu:1.0.0"
```

> [!NOTE]
> All profiles are isolated. LTM from different profiles and versions are not shared.

For quick profile updates `[BETA]`:

```shell
mindflow --update "run-tu"
```

To view all available profiles:

```shell
mindflow --profiles
```

To view all profile versions:

```shell
mindflow --versions <profile_name>
```

## Extensions

MindFlow supports custom RAG extensions for enhanced capabilities. The default extensions include `browser` and `email`.

### Writing Extensions

Create extensions using the following template:

```python
from typing import TypedDict

class ExtensionKwargs(TypedDict):
    ...

class ExtensionName:
    def __init__(self):
        ...
    
    @staticmethod
    def load_instructions() -> str:
        return "<instructions>"
```

If your extension does not include a kwarg class, use:

```python
from mindflow.utils import Kwargs
```

Upload your code to `pypi` using `twine` and `poetry`. To add it to `mindflow.extensions` for profiles:

```shell
omi install <module_name>
```

or

```shell
pip install <module_name>
omi add <module_name>
```

To test your extensions locally:

```shell
omi install .
```

## Todo List

- [x] AI Interpreter
- [X] Web Search Capability
- [X] Async Chunk Streaming
- [X] API Keys Support
- [X] Profiles Support
- [X] Extensions API
- [ ] Semantic File Search
- [ ] Optional Telemetry
- [ ] Desktop, Android & iOS App Interface

## Current Focus

- Optimizations
- Cost-efficient long-term memory and conversational context managers using vector databases, likely powered by [`ChromaDB`](https://github.com/chroma-core/chroma).
- Hooks API and Live Code Output Streaming

## Contributions

As my first major open-source project, there may be challenges and plenty of room for improvement. Contributions are welcome, whether through raising issues, improving documentation, adding comments, or suggesting features. Your support is greatly appreciated!

## Support

You can support this project by writing custom extensions for MindFlow. The aim is to be community-powered, with its capabilities expanding through collective effort. More extensions mean better handling of complex tasks. An official list of verified MindFlow extensions will be created in the future.
