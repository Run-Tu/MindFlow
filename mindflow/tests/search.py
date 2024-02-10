from core.utils.engines import Search
import time

if __name__ == '__main__':
    SEARCH = Search()
    query = input("\nGoogle> ")

    start = time.time()
    results = SEARCH.search(query.split(","))
    print(f"completed in {time.time() - start} s")
    print(results)
