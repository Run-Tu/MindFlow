from ..utils import lazy_import

RealtimeTTS = lazy_import("realtimetts", 
                          "RealtimeTTS",
                          "realtimetts[system,gtts]", 
                          optional=False, 
                          verbose=False,
                          install=True)

import logging
logging.disable(logging.CRITICAL + 1)

class TTS(RealtimeTTS.TextToAudioStream):
    def __init__(self,
                 tts: dict = None,
                 engine: str = None,
                 *args, **kwargs):
        super().__init__(getattr(RealtimeTTS, engine)(), *args, **kwargs)
        self.config = tts or {}
        self.chunks = ""
        
    def stream(self, chunk):
        if chunk == "<end>":
            self.feed(self.chunks)
            self.chunks = ""
            self.play_async()
        else:
            self.chunks += chunk
