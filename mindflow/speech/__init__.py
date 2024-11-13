import RealtimeTTS

import logging
logging.disable(logging.CRITICAL + 1)

class TTS(RealtimeTTS.TextToAudioStream):
    def __init__(self,
                 tts: dict = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = tts or {}
        self.chunks = ""
        
    def stream(self, chunk):
        if chunk == "<end>":
            self.feed(self.chunks)
            self.chunks = ""
            self.play_async()
        else:
            self.chunks += chunk


class Speech:
    def __init__(self, 
                 tts: dict = None, 
                 stt: dict = None) -> None:
        self.stt_config = stt or {}
            
        config = tts or {}
        self.tts = TTS(config, getattr(RealtimeTTS, config.get("engine", "SystemEngine"))())
