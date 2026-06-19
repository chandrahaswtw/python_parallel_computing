import time

start = time.perf_counter()


def initiate_sleep():
    print("sleep started")
    time.sleep(1)
    print("sleep ended")


initiate_sleep()

finish = time.perf_counter()

print(f"Total time taken is {round(finish - start, 2)} sec")
