import chromadb
from pathlib import Path

class VectorDB:
    def __init__(self, 
                 name: str,
                 location: str = '',
                 persistent: bool = False,):

        self.name = name
        self.location = Path(location)
        if persistent:
            self.setup_persistent()  
            self.client = chromadb.PersistentClient(self.location)
        else:
            self.client = chromadb.Client()
        
    def setup_persistent(self):
        if self.location.is_dir():
            location /= f"{self.name}.db"
        if not self.location.is_file():
            location.touch()
