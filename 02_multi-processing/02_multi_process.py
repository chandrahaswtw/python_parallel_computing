# All the concepts we worked with multi-threading works here.
# Instead of ThreadPoolExecutor we import ProcessPoolExecutor as "from concurrent.futures import as_completed, ProcessPoolExecutor".
# We can use executor.map() just as we did in multi-threading.


import time
import multiprocessing


def initiate_sleep():
    print("sleep started")
    time.sleep(1)
    print("sleep ended")


# To run a multi-process we need to add the condition __name__ == "__main__" on
#   - mac
#   - windows
#   - On Linux it's not required.

if __name__ == "__main__":
    start = time.perf_counter()

    p1 = multiprocessing.Process(target=initiate_sleep)
    p2 = multiprocessing.Process(target=initiate_sleep)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    finish = time.perf_counter()

    print(f"Total time taken is {round(finish - start, 2)} sec")
