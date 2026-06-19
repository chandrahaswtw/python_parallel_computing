# Parallel Computing in Python

## Processes and Threads

A **process** is an independent program in execution with its own isolated memory space.

A **thread** is a lightweight unit of execution that runs within a process and shares the process's memory and resources.

Every running application creates at least one process, and every process starts with at least one thread (often called the main thread).

Threads exist inside a process and allow concurrent work.

Example:

- One thread handles keyboard input.
- Another thread performs spell checking in the background.

---

## CPython and the Global Interpreter Lock (GIL)

Most people use **CPython**, when you type `python app.py`, you are running CPython.

The **Global Interpreter Lock (GIL)** is a lock used by CPython to protect its internal memory management and object model.

### What does the GIL do?

The GIL ensures that:

> Only one thread at a time can execute Python bytecode within a CPython process.

Even if a process contains multiple threads, only one of them can execute Python bytecode at any given moment.

### What the GIL does NOT do

The GIL is not a replacement for synchronization primitives such as:

- `threading.Lock`
- `threading.RLock`
- `threading.Semaphore`

If multiple threads modify shared application data, you may still need locks to avoid race conditions.

---

## How the GIL Works

Assume we have two threads:

- T1
- T2

The execution may look like this:

```text
T1 acquires the GIL
↓
Executes some Python bytecode
↓
Interpreter periodically allows another thread to acquire the GIL
↓
T2 acquires the GIL
↓
Executes some Python bytecode
↓
Interpreter switches again
↓
T1 resumes
```

This switching can happen even when the threads are performing CPU-bound work.

Therefore, threads do not need to wait until another thread finishes completely before they can run.

---

## GIL and I/O Operations

Suppose T1 performs a blocking operation:

```python
file.read()
```

or

```python
requests.get(...)
```

While T1 waits for the operation to complete:

- T1 enters a waiting (blocked) state.
- CPython typically releases the GIL.
- Another runnable thread can acquire the GIL and continue executing.

Example:

```text
T1 waiting for file I/O
↓
T2 acquires GIL
↓
T2 executes Python bytecode
```

---

## Threads vs Processes

### Threads

Threads:

- Share the same memory space
- Share the same CPython interpreter
- Share one GIL

Only one thread can execute Python bytecode at a time.

```text
Process P1
├── T1
├── T2
└── T3
```

All threads compete for the same GIL.

### Processes

Processes:

- Have separate memory spaces
- Have separate CPython interpreters
- Have separate GILs

```text
Process P1
└── T1

Process P2
└── T1
```

Because each process has its own GIL, processes can execute on different CPU cores simultaneously.

This enables true CPU parallelism.

---

## Ready Queue and Waiting Queue

Assume we have four threads:

```text
T1, T2, T3, T4
```

Initial state:

```text
Ready Queue:
T1, T2, T3, T4

Waiting Queue:
Empty
```

The scheduler selects T1.

### Step 1: T1 Starts Running

```text
Running:
T1

Ready Queue:
T2, T3, T4

Waiting Queue:
Empty
```

### Step 2: T1 Performs Blocking I/O

Suppose T1 executes:

```python
file.read()
```

T1 cannot continue until the I/O operation completes.

The operating system moves T1 to the waiting (blocked) state.

```text
Running:
None

Ready Queue:
T2, T3, T4

Waiting Queue:
T1
```

### Step 3: Another Thread Runs

The scheduler selects T2.

```text
Running:
T2

Ready Queue:
T3, T4

Waiting Queue:
T1
```

### Step 4: I/O Completes

When the file read finishes, T1 becomes runnable again.

```text
Running:
T2

Ready Queue:
T1, T3, T4

Waiting Queue:
Empty
```

### Key Point

Only the blocked thread moves to the waiting queue.

Other threads:

- Remain in the ready queue
- Remain eligible for execution
- Continue competing for CPU time and the GIL

---

## Simple Analogy

Imagine the CPython interpreter is a room and the GIL is the only key to that room.

- Ten threads may be waiting outside.
- Only the thread holding the key can enter and execute Python bytecode.
- When it releases the key, another thread may enter.

Therefore:

> The GIL is a lock in CPython that allows only one thread at a time to execute Python bytecode within a process, even when multiple threads exist.





---

## ThreadPoolExecutor - Best Practice for Thread Management

### Context Manager Pattern

The `with ThreadPoolExecutor(max_workers=3) as executor:` pattern is a best-practice Pythonic context manager for asynchronous task execution.

**Benefits:**
- Safely initializes a thread pool with a maximum of 3 concurrent worker threads
- Automatically shuts down the executor upon exiting the block
- Prevents resource leaks
- Blocks execution until all submitted tasks are complete

**Ideal Use Cases:**
- I/O-bound tasks (API requests, database queries, web scraping)
- Prevents overwhelming your system or server

### Three Common Usage Patterns

#### 1. Using executor.submit() (For individual/different tasks)

Schedules a callable to be executed as `fn(*args, **kwargs)` and returns a Future object representing the eventual result.

```python
import concurrent.futures
import time

def fetch_data(url):
    print(f"Started fetching: {url}")
    time.sleep(2)  # Simulate I/O delay
    return f"Data from {url}"

urls = ["https://example.com", "https://example.com", "https://example.com"]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    # Submit tasks for each URL
    futures = [executor.submit(fetch_data, url) for url in urls]
    
    # Process results as they complete
    for future in concurrent.futures.as_completed(futures):
        print(future.result())
```

#### 2. Using executor.map() (For identical functions applied to a list)

Acts like the built-in `map()` function but runs tasks asynchronously. Cleaner to write and yields results in the exact order inputs were submitted.

```python
import concurrent.futures
import time

def square(n):
    time.sleep(1)
    return n * n

numbers = [1, 2, 3, 4, 5]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    # executor.map automatically assigns threads and returns results
    results = executor.map(square, numbers)
    
    for result in results:
        print(result)
```

#### 3. Handling Exceptions

If your function raises an error during execution, `future.result()` will propagate that exception. Catch it using `future.exception()` to prevent crashes.

```python
import concurrent.futures

def faulty_task(x):
    if x == 2:
        raise ValueError("Simulated failure")
    return x * 2

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(faulty_task, i) for i in range(4)]
    
    for future in futures:
        if future.exception():
            print(f"Task failed: {future.exception()}")
        else:
            print(f"Result: {future.result()}")
```

---

## ThreadPoolExecutor in API Endpoints - Critical Placement

### Scenario A: Inside the Endpoint (❌ Dangerous under load)

If you instantiate ThreadPoolExecutor inside the route handler function, every incoming API request creates its own independent thread pool.

```python
@app.get("/endpoint")
def my_api_endpoint():
    # ❌ EVERY user request triggers this block and spawns 3 brand-new threads!
    with ThreadPoolExecutor(max_workers=3) as executor:
        ...
```

**If 100 users hit this at once:**
- Your API server will spin up 100 separate executors
- Each executor creates up to 3 threads
- You will have **300 threads** running simultaneously

**Why this is bad:**
- Completely defeats the purpose of limiting workers

### Manual Thread Creation (❌ Also Inefficient)

Similarly, manually creating threads per request is inefficient because thread creation has overhead.

```python
from threading import Thread

@app.get("/endpoint")
def handle_request():
    t1 = Thread(target=task1)
    t2 = Thread(target=task2)
    t3 = Thread(target=task3)
    
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()
```

**If 100 requests arrive simultaneously:**
- Request 1 → creates 3 threads
- Request 2 → creates 3 threads
- Request 3 → creates 3 threads
- ...
- **Total: 100 × 3 = 300 threads**

**Why this is inefficient:**
- Thread creation is not free (memory allocation, OS overhead)
- Context switching between hundreds of threads degrades performance
- No thread reuse - threads are created and destroyed for each request
- Can lead to resource exhaustion under high load

**Better approach:** Use a global ThreadPoolExecutor that reuses a fixed pool of threads across all requests.
- If thousands of users arrive, your server will run out of memory or crash due to thread exhaustion

### Scenario B: As a Global Instance (✅ Correct approach)

To enforce a strict ceiling of 3 threads total across your entire API, define the executor globally (outside the endpoint function).

```python
# Defined globally at the app level (Only 3 threads will EVER exist)
global_executor = ThreadPoolExecutor(max_workers=3)

@app.get("/endpoint")
def my_api_endpoint():
    # Each user request submits work to the SAME pool of 3 threads
    future = global_executor.submit(some_task)
    return future.result()
```

**If 100 users hit this at once:**
- The API will use exactly **3 threads total**
- The first 3 requests will be processed concurrently by those 3 threads
- The remaining 97 requests will be safely placed in an internal queue, waiting for a thread to become free
- No new threads are created, and your server remains stable
