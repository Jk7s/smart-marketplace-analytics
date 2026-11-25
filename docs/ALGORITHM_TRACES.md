# Guided algorithm traces

These traces use the same marketplace domain as the application.

## L1 — Linear scan and cost model
Input prices: `[45000, 72000, 52000, 61000]`; stock: `[3, 4, 0, 2]`; limit: `60000`.
Scan left to right and accept records where `price <= 60000` and `stock > 0`.
Expected IDs: records 1 only. Records examined: 4. RAM work is O(n); a block model transfers approximately ceil(n/B) blocks for sequential records, where B is records per block.

## L2 — Memory layout
A contiguous array can make sequential access cache-friendly. An indirect layout may require pointer chasing and extra cache misses. This prototype stores rows in SQLite and loads them into Python dictionaries; compare repeated scans only as a local demonstration. Hardware-counter and NUMA/GPU traces require suitable hardware or instructor-supplied traces.

## L3 — Amortized append
A doubling buffer with capacities 1, 2, 4, 8 copies old elements only when full. For 8 appends, resize copies are 1 + 2 + 4 = 7; total append work including writes is 15, which is linear in the number of appends. A single resize is expensive, but the amortized cost per append is constant.

## L4 — Fingerprint collisions
A fingerprint match only creates a candidate. A deliberately tiny fingerprint domain can map two different descriptions to the same fingerprint. Always compare the original normalized text before declaring an exact duplicate. The dashboard follows this principle by reporting similarity candidates and an `exact_match` field instead of auto-merging records.

## L5 — Profiling workflow
Record machine, Python version, catalogue size, query, number of repetitions, median elapsed time, and correctness result. Change one factor at a time. A speedup is valid only if the output remains identical.

## L6 — Model selection
A scan is simple and often suitable for small catalogues. An index or hash-based prefilter can help repeated queries, while a vector candidate stage can improve semantic recall. Select based on measured latency, memory, workload, and correctness—not Big-O notation alone.
