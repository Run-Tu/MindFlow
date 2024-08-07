import chromadb
from pathlib import Path

class VectorDB:
    def __init__(self, 
                 name: str,
                 location: str = '',
                 in_memory: bool = False,):

        self.name = name
        self.location = Path(location)
        if in_memory:
            self.client = chromadb.client()
        else:
            self.setup_persistence()  
            self.client = chromadb.PersistentClient(self.location)
        
    def setup_persistence(self):
        if self.location.is_dir():
            location /= f"{self.name}.db"
        if not self.location.is_file():
            location.touch()
