from core.utils.engines import Search
import time
import os

if __name__ == '__main__':
    browser = Search()
    modes = [("showtimes", "Inside Out 2 Hoyts showtimes"), 
             ("weather", "What's the weather like?"),
             ("events", "Are there any concerts going around?"),
             ("reviews", "Reviews for the movie Inside Out 2.")][2:]
    
    for mode, default in modes:
        query = input(f"{mode}> ") or default

        start = time.time()
        results = browser.search(query.split(","), 0, [mode])
        print(f"completed in {time.time() - start} s")
        print(results)

        os.system('pause')
        os.system('cls')
