import json
from pathlib import Path
from utils.engines import SearchEngine

ENGINE = SearchEngine()

if __name__ == '__main__':
    query = input("\ngoogle> ") or "history of cheese"
    results = ENGINE.search(query)
    print(results)
