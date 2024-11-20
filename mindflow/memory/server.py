import subprocess
from pathlib import Path
import threading
import chromadb
from chromadb.config import Settings
import time

class Manager:
    def __init__(self, 
                 path: Path | str = None,
                 port: int = None,
                 collections: list[str] = None,
                 telemetry: bool = False):
        self.port = port or 8000
        self.path = path
        self.collections = collections or ["ltm", "cache"]
        self.process = None
        
        if not Path(path).is_dir():
            client = chromadb.PersistentClient(str(path), Settings(anonymized_telemetry=telemetry))
            for collection in self.collections:
                client.create_collection(name=collection)
    
    def run(self):
        self.process = subprocess.Popen(
            ["chroma", "run", "--path", str(self.path), "--port", str(self.port)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
    def serve(self):
        threading.Thread(target=self.run).start()
        while not self.process:
            pass
            
            
        for line in iter(self.process.stdout.readline, ''):
            if f"running on http://localhost:{self.port}" in line:
                return
            # print(line, end='')
