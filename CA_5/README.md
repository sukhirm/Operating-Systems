# DEADLOCK ENGINEERING PROJECT

## 1. Introduction

The Deadlock Engineering Project is a Rust-based implementation of operating system deadlock management techniques. It demonstrates how deadlocks can be avoided, detected, and recovered from using different algorithms.

A deadlock occurs when two or more processes are permanently blocked because each process is waiting for a resource held by another process.

This project implements three major deadlock management techniques: Deadlock Avoidance, Deadlock Detection, and Deadlock Recovery.

## 2. Objectives

The main objectives of this project are:

- To understand the concept of deadlocks in operating systems.
- To implement the Banker's Algorithm for deadlock avoidance.
- To identify deadlocked processes using a detection algorithm.
- To recover from deadlocks by terminating affected processes and releasing resources.
- To measure the performance of deadlock management algorithms.
- To generate graphical representations of performance results.
- To examine system hardware and resource information.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Rust | Core algorithm implementation |
| Python | Performance graph generation |
| Cargo | Rust project management and compilation |
| Matplotlib | Graph visualization |
| Linux (WSL) | Development and execution environment |
| CSV | Benchmark data storage |

## 4. Project Structure

```text
deadlock_engineering/
│
├── Cargo.toml
├── Cargo.lock
├── generate_graphs.py
│
├── src/
│   ├── main.rs
│   ├── avoidance.rs
│   ├── detection.rs
│   ├── recovery.rs
│   └── experiment.rs
│
├── results/
│   ├── benchmark.csv
│   ├── cpu_info.txt
│   ├── disk_info.txt
│   ├── memory_info.txt
│   ├── process_info.txt
│   ├── run_output.txt
│   ├── system_metrics.txt
│   │
│   └── graphs/
│       └── performance_comparison.png
│
└── screenshots/
```

## 5. Deadlock Avoidance

Deadlock avoidance is implemented using the Banker's Algorithm.

The algorithm checks whether allocating resources to a process will leave the system in a safe state.

It considers:
- Available resources.
- Current resource allocation.
- Maximum resource requirements.
- Remaining resource needs.

The system grants resources only when a safe execution sequence exists.

The implementation is available in `src/avoidance.rs`.

## 6. Deadlock Detection

The detection module identifies processes that cannot complete because their required resources are unavailable.

It uses the available resources, current allocations, and outstanding requests to determine which processes can finish.

Processes that cannot be completed are reported as deadlocked.

The implementation is available in `src/detection.rs`.

## 7. Deadlock Recovery

The recovery module resolves detected deadlocks.

The implemented recovery approach terminates an affected process and releases the resources allocated to it.

The released resources become available to other processes.

After recovery, the system verifies whether the deadlock has been resolved.

The implementation is available in `src/recovery.rs`.

## 8. Performance Benchmarking

The project includes a performance benchmarking module to compare the execution time of deadlock avoidance and detection.

The algorithms are tested with different numbers of processes:

- 10 processes
- 50 processes
- 100 processes
- 250 processes
- 500 processes

The execution times are measured in nanoseconds.

The benchmark results are stored in:

`results/benchmark.csv`

## 9. Graphical Analysis

Python is used to generate a graphical comparison of deadlock avoidance and detection performance.

The graph displays:

- Number of processes on the X-axis.
- Average execution time in nanoseconds on the Y-axis.
- Deadlock avoidance performance.
- Deadlock detection performance.

The generated graph is saved as:

`results/graphs/performance_comparison.png`

## 10. System Information

The project also collects information about the development environment.

The collected information includes:

- CPU architecture and processor details.
- Memory usage.
- Disk storage information.
- Running processes.
- System performance metrics.

These details are stored in individual text files inside the `results` directory.

## 11. Testing and Results

The project includes unit tests to verify the functionality of its major components.

The tests cover:

1. Safe-state verification.
2. Unsafe-state identification.
3. Deadlock detection.
4. No-deadlock identification.
5. Resource recovery.

All five implemented unit tests passed successfully.

The program also successfully demonstrated deadlock detection, process termination, resource release, and recovery verification.

## 12. Conclusion

The Deadlock Engineering Project demonstrates the practical implementation of important operating system deadlock management techniques using Rust.

Through deadlock avoidance, detection, and recovery, the project illustrates how operating systems can manage competing resource requirements and resolve situations where processes become blocked.

Performance benchmarking provides an additional understanding of how execution time changes with increasing process counts.

The project combines systems programming, algorithm implementation, testing, and graphical analysis to provide a practical demonstration of deadlock management.

## 13. How to Run the Project

### Prerequisites
- Rust and Cargo
- Python 3
- Matplotlib

### Run the Tests
```bash
cargo test
