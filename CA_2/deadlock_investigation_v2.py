"""
R14: Deadlock Avoidance vs Detection
Controlled comparison using the same allocation, availability, and outstanding
resource-demand matrix for both algorithms.

Run:
    python deadlock_investigation_v2.py

Outputs:
    deadlock_results_v2/results.csv
    execution-time and comparison-count PNG graphs

Note:
This benchmarks the algorithms' safety/detection checks on the same system
snapshot. It does not claim to measure complete OS-level policy overhead.
"""

import csv
import random
import statistics
import time
from pathlib import Path

import matplotlib.pyplot as plt

SEED = 42
REPETITIONS = 300
PROCESS_COUNTS = [5, 10, 20, 40, 80]
RESOURCE_COUNTS = [3, 5, 8]
OUTPUT_DIR = Path("deadlock_results_v2")


def banker_safety(available, allocation, need):
    """Return (safe_state, resource_comparisons)."""
    process_count = len(allocation)
    resource_count = len(available)
    work = available[:]
    finish = [False] * process_count
    comparisons = 0

    while True:
        found = False
        for p in range(process_count):
            if finish[p]:
                continue
            can_finish = True
            for r in range(resource_count):
                comparisons += 1
                if need[p][r] > work[r]:
                    can_finish = False
                    break
            if can_finish:
                for r in range(resource_count):
                    work[r] += allocation[p][r]
                finish[p] = True
                found = True
        if not found:
            break

    return all(finish), comparisons


def deadlock_detection(available, allocation, request):
    """Return (deadlocked_process_indexes, resource_comparisons)."""
    process_count = len(allocation)
    resource_count = len(available)
    work = available[:]
    finish = [
        all(allocation[p][r] == 0 for r in range(resource_count))
        for p in range(process_count)
    ]
    comparisons = 0

    while True:
        found = False
        for p in range(process_count):
            if finish[p]:
                continue
            can_finish = True
            for r in range(resource_count):
                comparisons += 1
                if request[p][r] > work[r]:
                    can_finish = False
                    break
            if can_finish:
                for r in range(resource_count):
                    work[r] += allocation[p][r]
                finish[p] = True
                found = True
        if not found:
            break

    return [p for p in range(process_count) if not finish[p]], comparisons


def make_workload(process_count, resource_count, rng):
    allocation = [
        [rng.randint(0, 3) for _ in range(resource_count)]
        for _ in range(process_count)
    ]
    # This single matrix is used as Banker's NEED and detection REQUEST.
    outstanding = [
        [rng.randint(0, 4) for _ in range(resource_count)]
        for _ in range(process_count)
    ]
    available = [rng.randint(0, 5) for _ in range(resource_count)]
    return available, allocation, outstanding


def benchmark(function, args):
    function(*args)  # warm-up
    times = []
    result = None
    operations = 0
    for _ in range(REPETITIONS):
        start = time.perf_counter_ns()
        result, operations = function(*args)
        times.append((time.perf_counter_ns() - start) / 1000)
    return statistics.median(times), operations, result


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    rows = []

    for p_count in PROCESS_COUNTS:
        for r_count in RESOURCE_COUNTS:
            available, allocation, shared_demand = make_workload(
                p_count, r_count, rng
            )

            banker_us, banker_ops, safe = benchmark(
                banker_safety, (available, allocation, shared_demand)
            )
            detect_us, detect_ops, deadlocked = benchmark(
                deadlock_detection, (available, allocation, shared_demand)
            )

            rows.append({
                "processes": p_count,
                "resources": r_count,
                "banker_median_time_us": round(banker_us, 3),
                "detection_median_time_us": round(detect_us, 3),
                "banker_comparisons": banker_ops,
                "detection_comparisons": detect_ops,
                "banker_safe": safe,
                "detection_deadlocked_process_count": len(deadlocked),
                "same_allocation_available_and_demand": True,
            })

            print(
                f"P={p_count:>2}, R={r_count}: "
                f"Banker={banker_us:.3f} us ({banker_ops} comparisons), "
                f"Detection={detect_us:.3f} us ({detect_ops} comparisons), "
                f"safe={safe}, deadlocked={len(deadlocked)}"
            )

    with (OUTPUT_DIR / "results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for r_count in RESOURCE_COUNTS:
        subset = [row for row in rows if row["resources"] == r_count]
        x = [row["processes"] for row in subset]

        plt.figure()
        plt.plot(x, [row["banker_median_time_us"] for row in subset],
                 marker="o", label="Banker's safety check")
        plt.plot(x, [row["detection_median_time_us"] for row in subset],
                 marker="s", label="Deadlock detection")
        plt.xlabel("Number of processes")
        plt.ylabel("Median execution time (microseconds)")
        plt.title(f"Execution Time Comparison ({r_count} resource types)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"execution_time_{r_count}_resources.png", dpi=160)
        plt.close()

        plt.figure()
        plt.plot(x, [row["banker_comparisons"] for row in subset],
                 marker="o", label="Banker's safety check")
        plt.plot(x, [row["detection_comparisons"] for row in subset],
                 marker="s", label="Deadlock detection")
        plt.xlabel("Number of processes")
        plt.ylabel("Resource comparisons")
        plt.title(f"Comparison Count ({r_count} resource types)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"operation_count_{r_count}_resources.png", dpi=160)
        plt.close()

    print(f"\nSaved CSV and six graphs in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
