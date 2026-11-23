"""
CA-2 Performance Investigation
R14: Deadlock Avoidance vs Deadlock Detection

Compares:
  1. Banker's safety check (avoidance)
  2. Deadlock detection algorithm (detection)

Both algorithms receive the same generated allocation, availability and
per-process demand matrix for each configuration. The matrix is interpreted
as remaining need by Banker's algorithm and as outstanding request by the
detection algorithm. This creates a controlled paired input comparison,
although the algorithms still perform different OS functions.

Run:
    python deadlock_investigation.py

Outputs:
    results.csv
    execution_time.png
    operation_count.png

The script uses deterministic generated workloads and reports measured values
from the machine on which it is executed.
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
OUTPUT_DIR = Path("deadlock_results")


def banker_safety(available, allocation, maximum):
    """Return (is_safe, number_of_comparisons) using Banker's safety algorithm."""
    process_count = len(allocation)
    resource_count = len(available)
    need = [
        [maximum[p][r] - allocation[p][r] for r in range(resource_count)]
        for p in range(process_count)
    ]

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
    """Return (deadlocked_process_indexes, number_of_comparisons)."""
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

    deadlocked = [p for p in range(process_count) if not finish[p]]
    return deadlocked, comparisons


def make_workload(process_count, resource_count, rng):
    """Create one reproducible allocation/claim/request snapshot."""
    allocation = [
        [rng.randint(0, 3) for _ in range(resource_count)]
        for _ in range(process_count)
    ]
    remaining_claim = [
        [rng.randint(0, 4) for _ in range(resource_count)]
        for _ in range(process_count)
    ]
    maximum = [
        [allocation[p][r] + remaining_claim[p][r]
         for r in range(resource_count)]
        for p in range(process_count)
    ]
    available = [rng.randint(0, 5) for _ in range(resource_count)]
    request = [
        [rng.randint(0, remaining_claim[p][r])
         for r in range(resource_count)]
        for p in range(process_count)
    ]
    return available, allocation, maximum, request


def benchmark(function, args, repetitions):
    """Return median runtime in microseconds and operation count."""
    durations_us = []
    operation_count = None
    result = None

    # A short warm-up reduces one-time interpreter effects.
    function(*args)

    for _ in range(repetitions):
        start = time.perf_counter_ns()
        result, operation_count = function(*args)
        elapsed = time.perf_counter_ns() - start
        durations_us.append(elapsed / 1000.0)

    return statistics.median(durations_us), operation_count, result


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    rows = []

    for process_count in PROCESS_COUNTS:
        for resource_count in RESOURCE_COUNTS:
            available, allocation, maximum, request = make_workload(
                process_count, resource_count, rng
            )

            banker_time, banker_ops, banker_result = benchmark(
                banker_safety,
                (available, allocation, maximum),
                REPETITIONS,
            )
            detection_time, detection_ops, detection_result = benchmark(
                deadlock_detection,
                (available, allocation, request),
                REPETITIONS,
            )

            rows.append({
                "processes": process_count,
                "resources": resource_count,
                "banker_median_time_us": round(banker_time, 3),
                "detection_median_time_us": round(detection_time, 3),
                "banker_comparisons": banker_ops,
                "detection_comparisons": detection_ops,
                "banker_safe": banker_result,
                "detection_deadlocked_process_count": len(detection_result),
            })

            print(
                f"P={process_count:>2}, R={resource_count}: "
                f"Banker={banker_time:.3f} us ({banker_ops} comparisons), "
                f"Detection={detection_time:.3f} us "
                f"({detection_ops} comparisons)"
            )

    csv_path = OUTPUT_DIR / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Plot execution time for each resource-count setting.
    for resource_count in RESOURCE_COUNTS:
        subset = [row for row in rows if row["resources"] == resource_count]
        x = [row["processes"] for row in subset]
        plt.figure()
        plt.plot(x, [row["banker_median_time_us"] for row in subset],
                 marker="o", label="Banker's safety check (avoidance)")
        plt.plot(x, [row["detection_median_time_us"] for row in subset],
                 marker="s", label="Deadlock detection")
        plt.xlabel("Number of processes")
        plt.ylabel("Median execution time (microseconds)")
        plt.title(f"Execution Time Comparison ({resource_count} resource types)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"execution_time_{resource_count}_resources.png",
                    dpi=160)
        plt.close()

    # Plot algorithmic comparison counts for each resource-count setting.
    for resource_count in RESOURCE_COUNTS:
        subset = [row for row in rows if row["resources"] == resource_count]
        x = [row["processes"] for row in subset]
        plt.figure()
        plt.plot(x, [row["banker_comparisons"] for row in subset],
                 marker="o", label="Banker's safety check (avoidance)")
        plt.plot(x, [row["detection_comparisons"] for row in subset],
                 marker="s", label="Deadlock detection")
        plt.xlabel("Number of processes")
        plt.ylabel("Resource comparisons")
        plt.title(f"Operation Count Comparison ({resource_count} resource types)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"operation_count_{resource_count}_resources.png",
                    dpi=160)
        plt.close()

    print(f"\nSaved raw measurements and graphs in: {OUTPUT_DIR.resolve()}")
    print("Keep results.csv as the raw experimental data for your report.")


if __name__ == "__main__":
    main()
