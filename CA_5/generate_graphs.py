import csv
import matplotlib.pyplot as plt

processes = []
avoidance = []
detection = []

with open("results/benchmark.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        processes.append(int(row["processes"]))
        avoidance.append(int(row["avoidance_avg_ns"]))
        detection.append(int(row["detection_avg_ns"]))

plt.figure(figsize=(10, 6))

plt.plot(processes, avoidance, marker="o", label="Deadlock Avoidance")
plt.plot(processes, detection, marker="s", label="Deadlock Detection")

plt.xlabel("Number of Processes")
plt.ylabel("Average Execution Time (ns)")
plt.title("Deadlock Avoidance vs Detection Performance")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("results/graphs/performance_comparison.png")

print("Performance graph saved successfully!")

plt.show()
