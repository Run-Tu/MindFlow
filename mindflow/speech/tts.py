from ..utils import lazy_import
import os

RealtimeTTS = lazy_import("realtimetts", 
                          "RealtimeTTS",
                          "realtimetts[system,gtts,elevenlabs]", 
                          optional=False, 
                          verbose=False,
                          install=True)

import logging
logging.disable(logging.CRITICAL + 1)

def setup(engine: str, api_key: str = None, voice: str = None):
    free = {"SystemEngine", "GTTSEngine"}
    paid = {"ElevenlabsEngine": "ELEVENLABS_API_KEY",
            "OpenAIEngine": "OPENAI_API_KEY"}
    supported = free | set(paid)
    
    if not engine in supported:
        raise ValueError(f"Engine not supported in following: {supported}")
    
    if engine in free:
        return {}
    
    if api_key is None:
        raise ValueError(f"API_KEY not specified")
    
    os.environ[paid[engine]] = api_key
    return {"voice": voice} if voice else {}
    

class TTS(RealtimeTTS.TextToAudioStream):
    def __init__(self,
                 tts: dict = None,
                 engine: str = None,
                 api_key: str = None,
                 voice: str = None,
                 *args, **kwargs):
        self.config = tts or {}
    
        engine_kwargs = setup(engine, 
                              api_key or self.config.get("api_key"),
                              voice or self.config.get("voice"))

        self.engine = getattr(RealtimeTTS, engine)(**engine_kwargs)
        super().__init__(self.engine, *args, **kwargs)
        self.chunks = ""
        
    def stream(self, chunk):
        if chunk == "<end>":
            self.feed(self.chunks)
            self.chunks = ""
            self.play_async()
        else:
            self.chunks += chunk
