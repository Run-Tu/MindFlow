import subprocess
from pathlib import Path
import chromadb
from chromadb.config import Settings

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
    
    def serve(self):
        self.process = subprocess.Popen(
            ["chroma", "run", "--path", str(self.path), "--port", str(self.port)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )

    def serve_and_wait(self):
        self.serve() 
        for line in iter(self.process.stdout.readline, ''):
            # print(line, end='')
            if f"running on http://localhost:{self.port}" in line:
                break
