import time
import threading

start = time.perf_counter()


def initiate_sleep(seconds):
    print("sleep started")
    time.sleep(seconds)
    print("sleep ended")


# We are pasing arguments using args as seen below:

t1 = threading.Thread(target=initiate_sleep, args=[1.5])
t2 = threading.Thread(target=initiate_sleep, args=[1.5])

t1.start()
t2.start()

t1.join()
t2.join()

finish = time.perf_counter()

print(f"Total time taken is {round(finish - start, 2)} sec")
