import time
import threading

start = time.perf_counter()


def initiate_sleep():
    print("sleep started")
    time.sleep(1)
    print("sleep ended")


t1 = threading.Thread(target=initiate_sleep)
t2 = threading.Thread(target=initiate_sleep)

# t1.start() → starts Thread 1
# t2.start() → starts Thread 2
t1.start()
t2.start()

# t1.join() → main thread waits until t1 completes
# t2.join() → then waits until t2 completes
# Only after both threads are done does the program continue to:
t1.join()
t2.join()

finish = time.perf_counter()

print(f"Total time taken is {round(finish - start, 2)} sec")
