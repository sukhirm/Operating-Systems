"""
CA-3 | R14: Deadlock Avoidance vs Detection
Debugging simulator with a deliberate defect, corrected algorithms,
validation tests, and a small performance benchmark.

Run:
    python r14_deadlock_debugger.py

No third-party packages are required.
"""

from time import perf_counter
import csv
from pathlib import Path


# ---------------------------------------------------------------------
# 1. DELIBERATELY DEFECTIVE IMPLEMENTATION (for failure reproduction)
# ---------------------------------------------------------------------

def banker_safety_buggy(available, allocation, need):
    """BUG: uses >= instead of >, incorrectly rejecting exact resource fits."""
    n = len(allocation)
    work = available[:]
    finish = [False] * n

    while True:
        progress = False
        for p in range(n):
            if finish[p]:
                continue

            possible = True
            for r in range(len(available)):
                # DEFECT: exact fit (need == work) must be allowed.
                if need[p][r] >= work[r]:
                    possible = False
                    break

            if possible:
                for r in range(len(available)):
                    work[r] += allocation[p][r]
                finish[p] = True
                progress = True

        if not progress:
            break

    return all(finish)


# ---------------------------------------------------------------------
# 2. CORRECTED BANKER'S SAFETY ALGORITHM (DEADLOCK AVOIDANCE)
# ---------------------------------------------------------------------

def banker_safety(available, allocation, need):
    """Return (safe_state, safe_sequence)."""
    n = len(allocation)
    work = available[:]
    finish = [False] * n
    sequence = []

    while True:
        progress = False
        for p in range(n):
            if finish[p]:
                continue

            # Correct condition: a process can proceed when NEED <= WORK.
            if all(need[p][r] <= work[r] for r in range(len(available))):
                for r in range(len(available)):
                    work[r] += allocation[p][r]
                finish[p] = True
                sequence.append(p)
                progress = True

        if not progress:
            break

    return all(finish), sequence


# ---------------------------------------------------------------------
# 3. DEADLOCK DETECTION ALGORITHM
# ---------------------------------------------------------------------

def deadlock_detection(available, allocation, request):
    """Return indexes of processes that remain unfinished (deadlocked)."""
    n = len(allocation)
    work = available[:]

    # Processes holding no resources can be marked finished immediately.
    finish = [
        all(allocation[p][r] == 0 for r in range(len(available)))
        for p in range(n)
    ]

    while True:
        progress = False
        for p in range(n):
            if finish[p]:
                continue

            if all(request[p][r] <= work[r] for r in range(len(available))):
                for r in range(len(available)):
                    work[r] += allocation[p][r]
                finish[p] = True
                progress = True

        if not progress:
            break

    return [p for p in range(n) if not finish[p]]


# ---------------------------------------------------------------------
# 4. VALIDATION: REPRODUCE BUG, THEN PROVE THE FIX
# ---------------------------------------------------------------------

def run_tests():
    print("=" * 68)
    print("CA-3 R14 | DEBUGGING AND VALIDATION")
    print("=" * 68)

    # Boundary case: process needs exactly the amount currently available.
    available = [2]
    allocation = [[0]]
    need = [[2]]

    buggy_result = banker_safety_buggy(available, allocation, need)
    fixed_result, sequence = banker_safety(available, allocation, need)

    print("\nTEST 1 — Exact resource-fit boundary case")
    print(f"Available: {available}, Need: {need}")
    print(f"Defective algorithm says safe: {buggy_result}")
    print(f"Corrected algorithm says safe: {fixed_result}")
    print(f"Safe sequence: {sequence}")
    assert buggy_result is False, "The deliberate defect was not reproduced."
    assert fixed_result is True, "Corrected algorithm failed exact-fit test."

    # Safe multi-process case.
    available = [3, 3]
    allocation = [[1, 0], [0, 1], [1, 1]]
    need = [[2, 1], [1, 2], [1, 1]]
    safe, sequence = banker_safety(available, allocation, need)
    print("\nTEST 2 — Safe multi-process state")
    print(f"Safe: {safe}; sequence: {sequence}")
    assert safe

    # Unsafe state: no process can finish with currently available resources.
    available = [0, 0]
    allocation = [[1, 0], [0, 1]]
    need = [[0, 1], [1, 0]]
    safe, sequence = banker_safety(available, allocation, need)
    print("\nTEST 3 — Unsafe state")
    print(f"Safe: {safe}; partial sequence: {sequence}")
    assert not safe

    # Detection case: P0 waits for one unit held by P1; P1 waits for one held by P0.
    available = [0]
    allocation = [[1], [1]]
    request = [[1], [1]]
    deadlocked = deadlock_detection(available, allocation, request)
    print("\nTEST 4 — Deadlock detection")
    print(f"Deadlocked process indexes: {deadlocked}")
    assert deadlocked == [0, 1]

    # No-deadlock detection case: P0 has no outstanding request and can release.
    available = [0]
    allocation = [[1], [1]]
    request = [[0], [1]]
    deadlocked = deadlock_detection(available, allocation, request)
    print("\nTEST 5 — Detection recovery path / no deadlock")
    print(f"Deadlocked process indexes: {deadlocked}")
    assert deadlocked == []

    print("\nAll validation tests passed.")


# ---------------------------------------------------------------------
# 5. PERFORMANCE EXPERIMENT
# ---------------------------------------------------------------------

def benchmark():
    rows = []
    resource_count = 3
    print("\nPERFORMANCE BENCHMARK (synthetic deterministic workloads)")
    print("Processes | Banker median (us) | Detection median (us)")

    for n in [5, 10, 20, 40, 80, 120]:
        available = [n // 2 + 2] * resource_count
        allocation = [
            [((p + r) % 3) for r in range(resource_count)]
            for p in range(n)
        ]
        need = [
            [((p * 2 + r) % 4) for r in range(resource_count)]
            for p in range(n)
        ]
        request = [row[:] for row in need]

        def measure(fn, *args):
            samples = []
            for _ in range(100):
                start = perf_counter()
                fn(*args)
                samples.append((perf_counter() - start) * 1_000_000)
            samples.sort()
            return samples[len(samples) // 2]

        banker_us = measure(banker_safety, available, allocation, need)
        detection_us = measure(deadlock_detection, available, allocation, request)

        rows.append({
            "processes": n,
            "resources": resource_count,
            "banker_median_us": round(banker_us, 3),
            "detection_median_us": round(detection_us, 3),
        })
        print(f"{n:9} | {banker_us:18.3f} | {detection_us:19.3f}")

    output = Path("r14_results.csv")
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nRaw benchmark data saved to: {output.resolve()}")
    print("Timing values depend on your computer and current system load.")


if __name__ == "__main__":
    run_tests()
    benchmark()
