---
name: computer-first-performance-engineering
description: "Performance engineering skill for optimizing software from computer architecture, operating system behavior, memory hierarchy, IO paths, runtime behavior, and workload shape. Use when diagnosing or improving throughput, latency, tail latency, CPU usage, memory usage, allocation or GC pressure, IO wait, network saturation, database access paths, serialization hot paths, backend concurrency, batch pipelines, proxies, gateways, or Linux server performance."
metadata:
  short-description: Machine-level performance engineering
---

# Computer-First Performance Engineering Skill

## Purpose

This skill guides an AI agent to optimize software by reasoning from computer architecture, operating system behavior, memory hierarchy, IO paths, runtime behavior, and workload shape, instead of only following programming-language conventions, framework idioms, or stylistic best practices.

The objective is to produce changes that are measurably faster, more predictable, more resource-efficient, and more mechanically sympathetic to the underlying machine.

This skill is especially useful for:

- backend services under high concurrency
- latency-sensitive APIs
- batch-processing pipelines
- storage-heavy systems
- network-heavy systems
- JVM / Go / Node.js / Python / Rust / C / C++ performance tuning
- database access paths
- proxy / gateway / WAF / load-balancer code paths
- log processing
- serialization / deserialization hot paths
- memory-pressure and GC-pressure diagnosis
- Linux server performance diagnosis
- systems where throughput, latency, tail latency, CPU usage, memory usage, IO wait, or network saturation matters

---

## Core Principle

Do not optimize for language elegance first.

Optimize for the actual execution path:

1. CPU execution
2. cache behavior
3. memory allocation and layout
4. branch prediction
5. locking and synchronization
6. syscall frequency
7. IO batching
8. network packet flow
9. filesystem and page-cache behavior
10. runtime / compiler / JIT behavior
11. workload shape and backpressure
12. observability and measurement

Language-level best practices are secondary unless they preserve or improve these properties.

The golden rule:

> First make the program do less work. Then make the remaining work friendlier to the machine.

---

## Mental Model

A program is not only source code.

A running program is a flow of:

```text
request / event / input
  -> parsing
  -> allocation
  -> data movement
  -> branch decisions
  -> cache access
  -> locks / queues
  -> syscalls
  -> kernel path
  -> network / disk / database
  -> serialization
  -> response / output
```

Performance engineering means shaping this flow so that the machine does less useless work and performs necessary work in a cheaper order.

The agent must prefer explanations that connect code-level behavior to machine-level consequences.

Examples:

- This loop allocates a temporary object per item, increasing GC pressure.
- This map lookup is theoretically O(1), but random memory access may lose to a linear scan for small N.
- This code performs one syscall per record; batching will reduce kernel crossings.
- This object graph causes pointer chasing and poor cache locality.
- This lock is on the request hot path and serializes otherwise parallel work.
- This async code has hidden blocking calls, causing event-loop stalls.
- This database path performs N+1 queries and converts latency into multiplicative tail latency.

---

## When To Activate This Skill

Use this skill when the user asks about:

- performance optimization
- high concurrency
- low latency
- throughput
- CPU usage
- memory usage
- GC pressure
- IO wait
- disk throughput
- network saturation
- packet loss / retransmission / proxy performance
- slow database access
- slow build / slow deployment pipeline
- slow file processing
- slow API response
- kernel / Linux performance
- runtime tuning
- cache locality
- zero-copy
- batching
- lock contention
- thread pools
- async / event loop behavior
- profiling
- flamegraphs
- system bottlenecks

Also use this skill when reviewing code that appears simple but may be inside a hot path.

---

## Optimization Philosophy

Prefer:

- removing unnecessary work
- reducing allocations
- reducing syscalls
- reducing context switches
- reducing cache misses
- reducing pointer indirections
- reducing unpredictable branches
- reducing lock contention
- reducing copies
- batching small operations
- sequential access over random access
- flat data layout over scattered object graphs
- streaming over loading everything into memory
- bounded queues over unbounded queues
- explicit backpressure over uncontrolled concurrency
- precomputation where it removes hot-path work
- connection reuse over repeated setup
- zero-copy paths when justified
- observability over guessing

Avoid:

- blind abstraction in hot paths
- excessive object wrapping
- deep call chains on critical paths
- per-item IO
- per-request expensive initialization
- repeated parsing / serialization
- hidden allocations
- accidental synchronization
- unbounded concurrency
- unbounded buffering
- framework magic in performance-critical paths
- tuning before profiling
- micro-optimization before removing large waste
- optimizing cold paths

---

## Required Analysis Flow

When analyzing a performance problem, follow this order.

### 1. Define the Workload

Identify what the program is actually doing.

Ask:

- Is this request-heavy, batch-heavy, IO-heavy, CPU-heavy, memory-heavy, or mixed?
- What is the unit of work: request, file, row, message, packet, event, frame, transaction, or job?
- How many units per second are expected?
- What is the average size and worst-case size?
- What is the concurrency level?
- Is the bottleneck average latency, tail latency, throughput, CPU, memory, disk, network, or external dependency latency?

Do not optimize without knowing the workload shape.

### 2. Identify the Hot Path

Find the code executed most frequently or with the highest cost.

Ask:

- Is this inside a loop?
- Is this per request?
- Is this per row?
- Is this per packet?
- Is this per byte?
- Is this per log line?
- Is this run once at startup or repeatedly at runtime?
- Can expensive work be moved out of the hot path?

Hot-path code deserves mechanical sympathy. Cold-path code deserves readability.

### 3. Measure Before Changing

Prefer evidence over intuition.

At minimum, establish:

- baseline latency
- baseline throughput
- baseline CPU usage
- baseline memory usage
- baseline allocation rate if applicable
- baseline IO wait if applicable
- baseline network throughput / retransmits if applicable
- baseline database query count / latency if applicable

Never claim a performance improvement without a measurement plan.

### 4. Classify the Bottleneck

Classify the likely dominant bottleneck:

| Bottleneck | Common Symptoms | Typical Causes |
|---|---|---|
| CPU-bound | high CPU, low IO wait | heavy compute, parsing, compression, encryption, bad algorithm |
| Memory-bound | high CPU but poor scaling | cache misses, pointer chasing, large working set |
| Allocation-bound | high GC, high allocation rate | temporary objects, string churn, boxing, closures |
| IO-bound | high wait, low CPU | disk, network, DB, small IO, fsync |
| Lock-bound | CPU underused, high latency | mutex contention, global locks, synchronized queues |
| Scheduler-bound | many runnable tasks, context switching | too many threads/goroutines/tasks |
| Network-bound | saturated NIC, retransmits | large responses, poor backpressure, proxy buffering |
| Database-bound | slow endpoints, many queries | N+1, missing indexes, chatty transactions |
| Runtime-bound | GC pauses, JIT warmup | runtime configuration, heap sizing, object churn |

### 5. Reduce Work First

Before tuning, remove waste.

Ask:

- Can this calculation be skipped?
- Can this data be fetched once instead of repeatedly?
- Can this parse be avoided?
- Can this conversion be eliminated?
- Can this serialization happen once?
- Can this query be merged?
- Can this logging be sampled?
- Can this validation be moved to the boundary?
- Can this object be reused safely?

The fastest work is work not done.

---

## Detailed Analysis Dimensions

## 1. CPU Execution

Look for:

- expensive loops
- high-complexity algorithms
- unnecessary conversions
- repeated parsing
- compression / encryption hotspots
- regex on hot paths
- reflection / dynamic dispatch
- polymorphic call sites
- excessive virtual calls
- repeated date/time formatting
- repeated JSON/XML/YAML operations

Prefer:

- simpler algorithms
- precomputed tables
- fast-path / slow-path separation
- avoiding regex in tight loops
- avoiding reflection in hot paths
- moving invariant work outside loops
- using primitive operations where appropriate
- using specialized parsers for hot formats

Key questions:

- Is the CPU doing useful work or framework overhead?
- Is the same work repeated unnecessarily?
- Is the algorithmic cost appropriate for the input size?
- Is a general-purpose abstraction being used where a specialized path is justified?

---

## 2. Memory Allocation

Look for:

- temporary objects
- repeated string concatenation
- boxing / unboxing
- collection resizing
- JSON/XML object trees
- per-request buffers
- closure / lambda allocation
- reflection-created objects
- exception creation in non-exceptional paths
- copying byte arrays / strings repeatedly
- converting between string, bytes, buffer, stream, and object too often

Prefer:

- preallocation
- object reuse where safe
- buffer pooling
- arena allocation where appropriate
- stack allocation where supported
- primitive arrays
- compact structs
- immutable shared constants
- streaming parsers
- avoiding intermediate representations

Questions:

- How many objects are allocated per request?
- How many bytes are allocated per request?
- Is allocation rate causing GC pressure?
- Does this object escape to the heap?
- Can this data stay as bytes instead of becoming strings or objects?
- Are buffers copied when they could be sliced, referenced, streamed, or transferred?

---

## 3. Cache Locality and Data Layout

CPU cache behavior often dominates real-world performance.

Look for:

- linked lists
- deep object graphs
- hash maps on tiny hot datasets
- pointer chasing
- random memory access
- sparse arrays
- large object headers
- poor spatial locality
- poor temporal locality
- array-of-objects layout where flat arrays would work better

Prefer:

- contiguous arrays
- compact structs
- flat records
- sequential access
- sorted arrays for read-heavy access
- struct-of-arrays for columnar processing
- small fixed arrays for small N
- cache-line-aware layout in very hot code

Questions:

- Does iteration follow memory order?
- Is the working set larger than CPU cache?
- Are we paying cache misses for every pointer hop?
- Is Big-O hiding bad constants and bad locality?
- Would a linear scan beat a map for this small data size?

Rule:

> Big-O explains growth. Cache locality often explains actual speed.

---

## 4. Branch Prediction

Look for:

- unpredictable branches inside tight loops
- mixed normal and error paths
- repeated type checks
- polymorphic dispatch in hot loops
- complex nested conditionals
- random-condition branches

Prefer:

- common path first
- rare path separated
- fast-path / slow-path split
- table-driven dispatch where appropriate
- branchless code only when it is clearly beneficial and readable enough

Questions:

- Is this condition predictable?
- Is the common case optimized?
- Can error handling move away from the normal path?
- Is the branch cost larger than the computation saved?

---

## 5. Syscalls and Kernel Crossings

Syscalls are not free. Kernel crossings, context switches, and wakeups can dominate high-throughput systems.

Look for:

- tiny reads / writes
- repeated open / close
- repeated stat calls
- per-line fsync
- excessive logging
- per-request file access
- per-message socket writes
- short-lived connections
- excessive timers
- excessive wakeups

Prefer:

- buffered IO
- batching
- connection pooling
- persistent connections
- larger reads / writes
- async IO where appropriate
- sendfile / splice / zero-copy where appropriate
- log buffering and sampling
- fewer fsync calls

Questions:

- How many syscalls happen per request?
- Can multiple operations be combined?
- Can kernel crossings be reduced?
- Is logging causing IO amplification?
- Is the program waking too frequently?

Useful tools:

```bash
strace -c -p <pid>
strace -f -tt -T -p <pid>
perf trace -p <pid>
pidstat -w -p <pid> 1
```

---

## 6. IO Batching and Zero-Copy

Look for:

- per-record database writes
- per-message network writes
- per-file tiny reads
- repeated serialization
- memory copies between layers
- proxy buffering of large files
- loading full files into memory unnecessarily

Prefer:

- batch inserts / updates
- bulk reads
- stream processing
- chunked transfer
- backpressure-aware streams
- sendfile-like paths
- avoiding byte[] duplication
- avoiding string conversion for binary data
- using direct buffers where justified

Questions:

- Is data copied between user space and kernel space unnecessarily?
- Can large files bypass application-layer buffering?
- Can multiple small writes become one larger write?
- Is the program buffering more than needed?
- Is backpressure propagated upstream?

---

## 7. Concurrency, Locking, and Scheduling

Concurrency is not free. More workers can increase contention, memory pressure, and context switching.

Look for:

- global locks
- synchronized hot methods
- atomic counters updated per request
- shared queues
- lock contention
- too many threads
- goroutine / task explosion
- blocking inside async paths
- thread pool starvation
- false sharing
- unbounded queues
- unbounded parallelism

Prefer:

- sharded locks
- single-writer pattern
- read/write separation
- bounded queues
- backpressure
- batch handoff
- per-core or per-worker local state
- reducing shared mutable state
- lock-free only when actually justified
- explicit thread-pool sizing

Questions:

- Are workers actually parallel or serialized by a shared lock?
- Is the queue hiding overload instead of applying backpressure?
- Is context switching eating CPU?
- Are async tasks blocking event-loop threads?
- Is an atomic variable becoming a cache-line ping-pong point?
- Would fewer workers improve throughput?

Useful tools:

```bash
pidstat -w -p <pid> 1
pidstat -t -p <pid> 1
perf sched record
perf sched latency
perf lock record
perf lock report
```

---

## 8. Network Path Performance

For network services, always reason about the full path:

```text
client
  -> DNS
  -> TCP/TLS handshake
  -> load balancer
  -> WAF / proxy
  -> application
  -> database / storage
  -> response body
  -> kernel socket buffer
  -> NIC
```

Look for:

- short-lived connections
- missing keepalive
- TLS overhead
- proxy buffering
- slow clients
- large responses
- head-of-line blocking
- retransmissions
- small packet writes
- Nagle / delayed ACK interaction
- insufficient socket buffers
- saturated upstream bandwidth
- lack of backpressure
- application proxying large static files unnecessarily

Prefer:

- keepalive
- connection reuse
- HTTP/2 or HTTP/3 when appropriate
- static-file offload
- sendfile for large files
- rate limiting at the correct layer
- streaming responses
- bounded buffering
- kernel / proxy-level handling for large downloads
- separating dynamic paths from large static paths

Questions:

- Is the bottleneck CPU, NIC bandwidth, upstream bandwidth, proxy buffering, or slow clients?
- Are large files passing through expensive application logic?
- Can the edge proxy handle this path more cheaply?
- Are slow clients occupying expensive resources?
- Is there a bandwidth fairness policy?
- Are retransmits or packet drops present?

Useful tools:

```bash
ss -s
ss -tinp
sar -n DEV 1
sar -n TCP,ETCP 1
iftop
nload
tcpdump -i <iface> -nn host <ip>
ethtool -S <iface>
```

---

## 9. Filesystem and Page Cache

Look for:

- tiny random IO
- sync writes
- fsync storms
- metadata-heavy workloads
- repeated open/stat/close
- working set larger than RAM
- page-cache thrashing
- direct IO misuse
- network filesystem latency
- slow small-file operations
- compression/checksum overhead on storage paths

Prefer:

- sequential IO
- batching
- fewer files
- larger chunks
- avoiding unnecessary fsync
- keeping hot data in page cache
- separating metadata-heavy from throughput-heavy workloads
- using storage layout appropriate for random vs sequential IO

Questions:

- Is this workload random or sequential?
- Is it metadata-heavy or data-heavy?
- Is the page cache helping or thrashing?
- Is the storage backend suitable for this IO pattern?
- Is the filesystem doing extra work that the workload does not need?

Useful tools:

```bash
iostat -xz 1
pidstat -d -p <pid> 1
iotop
vmtouch <path>
free -h
vmstat 1
```

---

## 10. Database Access Path

Look for:

- N+1 queries
- missing indexes
- excessive joins
- fetching too many columns
- fetching too many rows
- per-row updates
- long transactions
- lock waits
- connection pool starvation
- repeated prepare / parse
- ORM object hydration overhead
- chatty application-database interaction

Prefer:

- query count reduction
- projection of only needed columns
- pagination / cursor streaming
- batch writes
- prepared statements
- proper indexes
- avoiding ORM hydration on hot paths
- read/write separation where appropriate
- connection pool sizing based on DB capacity, not application thread count

Questions:

- How many queries per request?
- How much data is returned but unused?
- Is the database doing CPU work, IO work, or lock waiting?
- Is the application multiplying latency through sequential queries?
- Is the connection pool hiding saturation?

---

## 11. Runtime-Specific Guidance

### JVM

Check:

- allocation rate
- GC pressure
- heap sizing
- JIT warmup
- boxing / unboxing
- reflection
- string churn
- synchronized hot paths
- thread pool saturation
- class loading on runtime paths
- excessive object graphs from frameworks / ORM

Prefer:

- primitive collections where justified
- avoiding boxing in hot paths
- buffer reuse
- reducing temporary strings
- JFR / async-profiler evidence
- GC log analysis
- right-sized thread pools

Useful tools:

```bash
jcmd <pid> VM.flags
jcmd <pid> GC.heap_info
jcmd <pid> Thread.print
jcmd <pid> JFR.start duration=60s filename=profile.jfr
jstat -gcutil <pid> 1s
```

### Go

Check:

- goroutine explosion
- channel overhead
- heap escapes
- allocation in loops
- interface dispatch
- reflection
- string / []byte conversions
- GC pressure
- mutex contention
- blocking syscalls

Prefer:

- pprof CPU / heap / mutex profiles
- reducing heap escapes
- explicit buffer reuse
- bounded goroutine pools
- sync.Pool only when it actually reduces allocation pressure

Useful tools:

```bash
go test -bench=. -benchmem
 go tool pprof cpu.pprof
 go tool pprof heap.pprof
 GODEBUG=gctrace=1 ./app
```

### Node.js

Check:

- event-loop blocking
- excessive JSON parsing
- promise churn
- buffer copies
- stream backpressure
- synchronous filesystem calls
- native boundary overhead
- large object retention

Prefer:

- streams
- backpressure-aware pipelines
- worker threads for CPU-bound tasks
- avoiding sync calls in request path
- reducing JSON transformations

Useful tools:

```bash
node --prof app.js
node --inspect app.js
clinic flame -- node app.js
clinic doctor -- node app.js
```

### Python

Check:

- interpreter overhead
- GIL contention
- object allocation
- per-item Python loops
- CPU-bound work in Python layer
- inefficient pandas usage
- repeated serialization
- multiprocessing overhead

Prefer:

- vectorization
- C extensions / native libraries
- batching
- generators / streaming
- multiprocessing for CPU-bound work when data transfer cost is acceptable
- async for IO-bound work

Useful tools:

```bash
python -m cProfile -o out.prof app.py
py-spy top --pid <pid>
py-spy record -o profile.svg --pid <pid>
```

### Rust / C / C++

Check:

- unnecessary copies
- allocator behavior
- bounds checks in hot loops
- cache layout
- branch prediction
- SIMD opportunity
- false sharing
- ownership-driven copies
- undefined behavior risks
- lock contention

Prefer:

- zero-copy references where safe
- compact structs
- explicit allocation strategy
- reserving capacity
- avoiding virtual dispatch in hot paths
- SIMD only with benchmark evidence
- sanitizers during safety validation

Useful tools:

```bash
perf record -g ./app
perf report
valgrind --tool=cachegrind ./app
heaptrack ./app
```

---

## Data Structure Selection Rules

Do not choose data structures based only on theoretical Big-O.

Also consider:

- constant factors
- memory layout
- cache locality
- number of elements
- mutation frequency
- lookup frequency
- iteration frequency
- sortability
- append pattern
- concurrency behavior
- allocation behavior

Examples:

| Situation | Often Better Choice | Reason |
|---|---|---|
| Small N lookup | linear scan over array | better locality, lower overhead |
| Read-heavy sorted data | sorted array + binary search | compact and cache-friendly |
| Hot iteration | array / vector | contiguous memory |
| Frequent insert/delete middle | linked structure may help | but cache locality may suffer |
| High-cardinality lookup | hash map | good average lookup |
| Prefix matching | trie / radix tree | avoids repeated string scans |
| Time-window metrics | ring buffer | bounded memory and predictable access |
| Producer-consumer | bounded queue | backpressure and memory control |
| Per-core counters | sharded counters | avoids atomic contention |

Rule:

> A theoretically worse structure with better locality may outperform a theoretically better structure on real hardware.

---

## Preferred Optimization Order

Apply optimizations in this order unless evidence suggests otherwise:

1. remove unnecessary work
2. reduce algorithmic complexity
3. reduce allocations
4. batch IO
5. reduce serialization / parsing
6. improve data locality
7. reduce lock contention
8. reduce syscalls
9. reduce copies
10. tune runtime / GC / thread pools
11. tune OS / kernel parameters
12. use native extensions / SIMD / zero-copy paths
13. change architecture or split workload paths

Do not start with kernel tuning when the application is doing obviously wasteful work.

---

## Measurement Requirements

Every optimization proposal must include:

1. expected bottleneck reduced
2. expected metric improvement
3. how to measure before and after
4. risk or tradeoff
5. rollback strategy when appropriate

Example:

```text
Change:
Batch 100 database inserts per transaction instead of inserting one row per transaction.

Expected bottleneck reduced:
Reduces network round trips, database transaction overhead, and fsync pressure.

Measure:
Compare rows/sec, p95 latency, DB commit rate, disk fsync rate, and application CPU before/after.

Tradeoff:
Higher per-batch memory usage and slightly higher latency for the first item in each batch.
```

---

## Recommended Tooling

### Linux System-Level Tools

```bash
# CPU and scheduler
 top
 htop
 pidstat -u -p <pid> 1
 pidstat -t -p <pid> 1
 pidstat -w -p <pid> 1
 perf top
 perf record -g -p <pid> -- sleep 60
 perf report

# Memory
 free -h
 vmstat 1
 pmap -x <pid>
 smem -p

# Syscalls
 strace -c -p <pid>
 strace -f -tt -T -p <pid>
 perf trace -p <pid>

# Disk IO
 iostat -xz 1
 pidstat -d -p <pid> 1
 iotop

# Network
 ss -s
 ss -tinp
 sar -n DEV 1
 sar -n TCP,ETCP 1
 iftop
 nload
 tcpdump -i <iface> -nn host <ip>
 ethtool -S <iface>

# Flamegraph / eBPF / BCC tools when available
 profile-bpfcc
 offcputime-bpfcc
 runqlat-bpfcc
 biolatency-bpfcc
 tcplife-bpfcc
```

### Application-Level Tools

Use language-specific profilers:

- JVM: JFR, async-profiler, jcmd, jstat, GC logs
- Go: pprof, trace, benchmem, gctrace
- Node.js: clinic.js, --prof, inspector, flamegraphs
- Python: cProfile, py-spy, scalene
- Rust/C/C++: perf, heaptrack, valgrind, cachegrind, sanitizers

---

## Output Format For Code Review

When reviewing code for performance, respond using this structure:

```markdown
## Performance Diagnosis

### Likely Bottleneck
...

### Computer-Level Cause
...

### Code-Level Cause
...

### Optimization Direction
...

### Concrete Changes
...

### Measurement Plan
...

### Tradeoffs
...
```

---

## Output Format For Incident Diagnosis

When diagnosing a live performance incident, respond using this structure:

```markdown
## Incident Performance Diagnosis

### Symptom
...

### Most Likely Bottleneck Class
CPU-bound / memory-bound / IO-bound / network-bound / lock-bound / database-bound / runtime-bound / unknown

### Fast Verification Commands
```bash
...
```

### Interpretation Guide
- If you see X, it means Y.
- If you see A, it means B.

### Immediate Mitigation
...

### Permanent Fix
...

### Risk
...
```

---

## Output Format For Optimization Proposal

When proposing a performance optimization plan, respond using this structure:

```markdown
## Optimization Plan

### Target Metric
...

### Baseline To Capture
...

### Priority 1: Remove Waste
...

### Priority 2: Reduce Allocation / IO / Locking
...

### Priority 3: Runtime / OS Tuning
...

### Validation Plan
...

### Rollback Plan
...
```

---

## Anti-Patterns

### Language-Level Anti-Patterns

- optimizing for elegance in a hot path while ignoring allocation cost
- using framework abstractions for per-item operations at huge scale
- using reflection where static dispatch is possible
- converting data formats repeatedly
- treating all allocations as harmless
- assuming async automatically means fast
- assuming more threads always improves throughput
- assuming Big-O is enough to predict performance

### Systems-Level Anti-Patterns

- one syscall per item
- one database query per row
- one network write per tiny chunk
- unbounded queues
- unbounded goroutines / tasks / threads
- global locks in hot paths
- large file transfers through expensive application logic
- buffering entire files unnecessarily
- logging too much on hot paths
- tuning kernel parameters without measuring application waste

### Observability Anti-Patterns

- optimizing without baseline
- using average latency only and ignoring p95 / p99
- ignoring allocation rate
- ignoring IO wait
- ignoring network retransmits
- ignoring queue length
- ignoring database query count
- trusting intuition over profiler data

---

## Mechanical Sympathy Checklist

Before finalizing an optimization answer, check:

- [ ] Did I identify the workload shape?
- [ ] Did I identify the hot path?
- [ ] Did I classify the bottleneck?
- [ ] Did I connect code behavior to machine behavior?
- [ ] Did I reduce work before tuning?
- [ ] Did I consider allocation pressure?
- [ ] Did I consider cache locality?
- [ ] Did I consider syscalls and IO batching?
- [ ] Did I consider locks and scheduling?
- [ ] Did I consider runtime-specific behavior?
- [ ] Did I provide measurement commands or metrics?
- [ ] Did I disclose tradeoffs?
- [ ] Did I avoid claiming unmeasured performance gains as fact?

---

## Decision Rules

### Rule 1: Hot Path Overrides Style

If a code path is demonstrably hot, machine-level efficiency may override language or framework elegance.

But the answer must explain:

- why it is hot
- what machine-level cost is reduced
- how to measure the improvement
- what readability or maintainability cost is introduced

### Rule 2: Cold Path Favors Clarity

If a code path is cold, prefer readability, correctness, and maintainability.

Do not make cold code complex for theoretical performance.

### Rule 3: Batch Before Parallelizing

Before adding more workers, check whether the work can be batched.

Batching often reduces:

- syscalls
- network round trips
- database commits
- lock acquisitions
- context switches
- serialization overhead

### Rule 4: Backpressure Before Buffering

Unbounded buffering hides overload and turns latency into memory pressure.

Prefer bounded queues and explicit backpressure.

### Rule 5: Measure Tail Latency

Average latency is not enough for high-concurrency systems.

Always consider:

- p50
- p90
- p95
- p99
- max latency
- queue depth
- timeout rate
- retry rate

### Rule 6: Do Not Confuse Concurrency With Throughput

Concurrency increases in-flight work. It does not automatically increase completed work.

More concurrency may reduce throughput when the bottleneck is:

- lock contention
- memory bandwidth
- database saturation
- disk IO
- network bandwidth
- GC pressure
- scheduler overhead

---

## Common Diagnosis Patterns

### Pattern: High CPU But Low Throughput

Check:

- algorithmic complexity
- parsing / serialization cost
- compression / encryption
- regex
- GC pressure
- lock contention causing spin
- excessive context switches

Commands:

```bash
pidstat -u -p <pid> 1
perf top -p <pid>
perf record -g -p <pid> -- sleep 60
```

### Pattern: Low CPU But High Latency

Check:

- IO wait
- database latency
- network latency
- queueing
- locks
- thread pool starvation
- external service dependency

Commands:

```bash
pidstat -d -p <pid> 1
iostat -xz 1
ss -tinp
pidstat -w -p <pid> 1
```

### Pattern: Increasing Latency Over Time

Check:

- memory leak
- unbounded queue
- GC pressure
- connection leak
- file descriptor leak
- cache growth
- log accumulation
- retry storm

Commands:

```bash
free -h
vmstat 1
lsof -p <pid> | wc -l
ss -s
jstat -gcutil <pid> 1s   # JVM only
```

### Pattern: High Network Throughput Hurts Application

Check:

- large static files through application layer
- proxy buffering
- slow clients
- missing rate limiting
- missing sendfile
- response compression cost
- excessive TLS overhead

Commands:

```bash
sar -n DEV 1
sar -n TCP,ETCP 1
ss -tinp
iftop
```

### Pattern: GC Pauses Or Memory Pressure

Check:

- allocation rate
- object lifetime
- temporary objects
- large object allocation
- string churn
- object retention
- cache without bounds

Language-specific profiling is required.

---

## Example Reasoning Style

Poor answer:

```text
Use a map because map lookup is O(1).
```

Better answer:

```text
For this path, the dataset has only 8 entries and is scanned per request. A flat array with linear scan may outperform a hash map because it avoids hashing, bucket indirection, and random memory access. Benchmark both with representative request volume. If N remains below ~16 and the scan is hot, the array is likely more cache-friendly.
```

Poor answer:

```text
Use async to improve performance.
```

Better answer:

```text
Async helps only if the bottleneck is waiting on IO. If the bottleneck is CPU-bound JSON parsing, async will not reduce CPU cost and may add scheduling overhead. First profile CPU and event-loop delay. If IO wait dominates, use async with bounded concurrency and backpressure.
```

Poor answer:

```text
Increase thread pool size.
```

Better answer:

```text
Increasing thread count may worsen context switching if the bottleneck is CPU or lock contention. First inspect runnable threads, context switches, queue depth, and lock contention. If workers are blocked on external IO and the downstream dependency has capacity, increasing the pool may help. Otherwise, use batching or reduce contention first.
```

---

## Final Principle

Programming language rules describe how code should look.

Computer principles describe how code actually runs.

High-performance engineering requires both, but when the code is on a verified hot path, the machine has the final vote.

