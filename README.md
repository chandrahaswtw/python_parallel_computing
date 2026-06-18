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



