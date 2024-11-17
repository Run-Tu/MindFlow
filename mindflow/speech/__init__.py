from ..utils import lazy_import

class Speech:
    def __init__(self, 
                 tts: dict = None, 
                 stt: dict = None) -> None:
        self.stt_config = stt or {}
            
        config = tts or {}
        if config.get("enabled"):
            from .tts import TTS
            self.tts = TTS(config, config.get("engine", "SystemEngine"))
