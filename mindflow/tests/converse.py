from utils.model import Model
import time

if __name__ == '__main__':
    COMPUTER = Model()
    query = input("\Ask> ")

    start = time.time()
    results = COMPUTER.chat(query, log=True)

    print(f"completed in {time.time() - start} s")
    print(results)
