from ..utils import lazy_import

class Speech:
    def __init__(self, 
                 tts: dict = None, 
                 stt: dict = None) -> None:
        config = stt or {}
        if config.get("enabled"):
            try: 
                from .stt import STT
                self.stt = STT(config, config.get("engine", "SystemEngine"))
            except: 
                print("An error occured: Disabling STT.")
            
        config = tts or {}
        if config.get("enabled"):
            try: 
                from .tts import TTS
                self.tts = TTS(config, config.get("engine", "SystemEngine"))
            except: 
                print("An error occured: Disabling TTS.")
