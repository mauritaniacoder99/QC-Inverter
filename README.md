# QC-Inverter

QC-Inverter is a proof-of-concept quantum cryptanalysis tool designed to invert Boolean constraints (SAT problems) using Grover's Amplitude Amplification. It translates logical expressions into reversible quantum circuits and simulates the statevector collapse to identify satisfying assignments.

This tool is primarily intended for vulnerability research, allowing analysts to model how classical cryptographic constraints might withstand quantum search algorithms.

## Overview

The engine utilizes Qiskit and the Aer simulator to dynamically build phase oracles. Instead of hardcoding search targets, it accepts logical constraints, calculates the optimal theoretical Grover iterations ($\lfloor \frac{\pi}{4} \sqrt{\frac{N}{M}} \rfloor$), and applies a custom diffuser. 

It also extracts hardware-aware topology metrics (like T-counts and circuit depth) post-transpilation to estimate execution costs on fault-tolerant quantum computing (FTQC) architectures.

## Features

- **Dynamic Oracle Synthesis:** Converts standard logical expressions (e.g., `(v0 ^ v1) & v2`) into quantum phase oracles.
- **Topology Analysis:** Reports circuit depth, non-local gate counts (CX/CZ), and T-counts after Level-3 optimization.
- **Terminal UI:** Renders probability distributions and hardware metrics directly in the CLI using `rich`.
- **Noise Simulation:** Optional depolarizing error injection to observe fidelity drop in simulated NISQ environments.

## Installation

It is highly recommended to run this tool inside an isolated Python virtual environment (PEP 668 compliant).

```bash
git clone [https://github.com/mauritaniacoder99/QC-Inverter.git](https://github.com/mauritaniacoder99/QC-Inverter.git)
cd QC-Inverter

python -m venv .venv
source .venv/bin/activate

pip install qiskit qiskit-aer sympy rich numpy
chmod +x q_cryptanalysis_engine.py
```

## Usage

Pass the Boolean expression via the `-e` flag. Variables must be defined as `v0`, `v1`, `v2`, etc. Supported operators: `&` (AND), `|` (OR), `~` (NOT), `^` (XOR).

**Basic execution:**
```bash
./q_cryptanalysis_engine.py -e "(v0 ^ v1) & (v2 ^ v3) & (v4 ^ v0) & v1 & ~v2" -s 8192 -o 3
```

**Arguments:**
- `-e, --expression` : The logical payload/constraint to invert.
- `-s, --shots`      : Number of measurement shots on the AerSimulator (default: 8192).
- `-o, --opt-level`  : Transpiler optimization level (0-3). Level 3 is recommended for maximum gate fusion.
- `--noise`          : Enables a basic depolarizing error model (0.1%) to simulate hardware noise.

## Limitations & Notes

- **Simulation Overhead:** Currently, the tool relies on `AerSimulator` (`statevector` method). Executing expressions with more than 20-25 qubits will require significant RAM and may cause bottlenecks on standard classical hardware.
- **Single-Solution Bias:** The iteration calculator assumes $M=1$ (a single valid solution) to simulate a worst-case cryptographic hash collision or key extraction. Highly satisfiable formulas (where $M \gg 1$) may result in quantum overcooking (overshooting the optimal probability peak).

## License

MIT License
```
