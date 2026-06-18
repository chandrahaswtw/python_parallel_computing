from concurrent.futures import ThreadPoolExecutor, as_completed
import time

start = time.perf_counter()


def initiate_sleep(seconds):
    print("sleep started")
    time.sleep(seconds)
    return f"sleep ended in {seconds} seconds"


# with ThreadPoolExecutor() as executor: --> This creates a pool of worker threads.
# Instead of manually creating threads with: t1 = threading.Thread(...) t1.start() the pool manages the threads for you.
# f is called Future object.
# f.result(), just like join() waits until this task completes, then gives us return value.

with ThreadPoolExecutor() as executor:
    f = executor.submit(initiate_sleep, 1)
    print(f.result())

# In case we have a loop of Future objects, we can use as_completed.
# as_completed() lets you process Future objects in the order they finish, rather than the order you submitted them.
with ThreadPoolExecutor() as executor:
    f_objs = [executor.submit(initiate_sleep, 1) for _ in range(10)]

    for f in as_completed(f_objs):
        print(f.result())

# Say we have random seconds we can do as below:
with ThreadPoolExecutor() as executor:
    seconds = [1, 2, 3, 4, 5]

    # We can do using this:
    f_objs = [executor.submit(initiate_sleep, sec) for sec in seconds]
    for f in as_completed(f_objs):
        print(f.result())

    # We can use map as well.
    # We get the results directly. We didn't use the as_completed and f.result()
    results = executor.map(initiate_sleep, seconds)
    for result in results:
        print(result)


finish = time.perf_counter()

print(f"Total time taken is {round(finish - start, 2)} sec")
