#!/usr/bin/env python3
"""
Quantum Boolean Satisfiability (SAT) Cryptanalysis Engine
---------------------------------------------------------
An advanced, fault-tolerant-aware quantum cryptanalysis framework designed 
to invert complex cryptographic Boolean constraints using optimized Grover's 
Amplitude Amplification.

Author: Mohamed Lemine Ahmed Jidou
Architecture: Qiskit 1.x / AerSimulator
"""

import argparse
import math
import sys
import logging
from typing import Dict, Tuple, Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle
from qiskit.quantum_info import Statevector, entropy
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

# Configure Elite Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")
console = Console()

class QuantumCryptanalysisEngine:
    def __init__(self, expression: str, shots: int = 8192, opt_level: int = 3, simulate_noise: bool = False):
        """
        Initializes the Quantum Engine with cryptographic constraints.
        """
        self.expression = expression
        self.shots = shots
        self.opt_level = opt_level
        self.simulate_noise = simulate_noise
        self.oracle = None
        self.num_qubits = 0
        self.circuit = None
        
        log.info(f"Initializing Quantum Cryptanalysis Engine.")
        log.info(f"Target Constraint (CNF/Logic): {self.expression}")

    def _synthesize_oracle(self) -> None:
        """Parses the boolean expression into a reversible quantum phase oracle."""
        try:
            # Note: In a pure custom FTQC engine, this would use Tweedledum or PyEDA directly.
            # We use PhaseOracle for stable AST parsing to quantum DAGs.
            self.oracle = PhaseOracle(self.expression)
            self.num_qubits = self.oracle.num_qubits
            log.info(f"Oracle synthesized successfully. Qubits required: {self.num_qubits}")
        except Exception as e:
            log.fatal(f"Failed to synthesize logical expression: {e}")
            sys.exit(1)

    def _build_diffuser(self) -> QuantumCircuit:
        """
        Constructs a highly optimized Grover Diffuser (Inversion about the mean)
        manually to ensure control over gate transpilation.
        """
        qc = QuantumCircuit(self.num_qubits)
        qc.h(range(self.num_qubits))
        qc.x(range(self.num_qubits))
        
        # Multi-Controlled Z gate (MCZ) implementation
        qc.h(self.num_qubits - 1)
        qc.mcx(list(range(self.num_qubits - 1)), self.num_qubits - 1)
        qc.h(self.num_qubits - 1)
        
        qc.x(range(self.num_qubits))
        qc.h(range(self.num_qubits))
        return qc

    def construct_circuit(self) -> None:
        """Assembles the full quantum circuit with calculated optimal iterations."""
        self._synthesize_oracle()
        
        # Mathematical derivation of optimal Grover iterations assuming M=1 (Worst Case)
        N = 2 ** self.num_qubits
        optimal_iterations = math.floor((math.pi / 4) * math.sqrt(N))
        log.info(f"Search Space (N): {N}. Optimal Iterations calculated: {optimal_iterations}")

        self.circuit = QuantumCircuit(self.num_qubits)
        self.circuit.h(range(self.num_qubits)) # Initial uniform superposition

        diffuser = self._build_diffuser()

        for step in range(optimal_iterations):
            self.circuit.compose(self.oracle, inplace=True)
            self.circuit.compose(diffuser, inplace=True)
            
        self.circuit.measure_all()
        log.info("Quantum circuit assembly complete.")

    def analyze_topology(self, compiled_circuit: QuantumCircuit) -> Dict[str, Any]:
        """Extracts Fault-Tolerant Quantum Computing (FTQC) metrics from the DAG."""
        ops = compiled_circuit.count_ops()
        # T-gates and CCX (Toffoli) are the most expensive in error-corrected hardware
        t_count = ops.get('t', 0) + ops.get('tdg', 0)
        cx_count = ops.get('cx', 0) + ops.get('cz', 0)
        
        return {
            "depth": compiled_circuit.depth(),
            "gate_count": sum(ops.values()),
            "t_count": t_count,
            "cx_count": cx_count,
            "width": compiled_circuit.num_qubits
        }

    def execute(self) -> Tuple[Dict[str, int], Dict[str, Any]]:
        """Transpiles and executes the payload on the Aer simulator."""
        simulator = AerSimulator(method='statevector')
        
        # Optional: Inject realistic hardware noise
        if self.simulate_noise:
            noise_model = NoiseModel()
            error = depolarizing_error(0.001, 1) # 0.1% single-qubit error
            noise_model.add_all_qubit_quantum_error(error, ['u1', 'u2', 'u3'])
            log.warning("Hardware noise simulation ENABLED (Depolarizing Error injected).")
            simulator = AerSimulator(noise_model=noise_model)

        log.info(f"Transpiling circuit (Optimization Level {self.opt_level})...")
        compiled_circuit = transpile(self.circuit, simulator, optimization_level=self.opt_level)
        
        topology_metrics = self.analyze_topology(compiled_circuit)
        
        log.info(f"Executing payload with {self.shots} shots...")
        job = simulator.run(compiled_circuit, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        
        return counts, topology_metrics

def render_results(counts: Dict[str, int], metrics: Dict[str, Any], shots: int) -> None:
    """Renders elite TUI tables for Cryptanalysis results."""
    # 1. Hardware Metrics Table
    hw_table = Table(title="FTQC Hardware Topology Analysis", style="cyan")
    hw_table.add_column("Metric", style="bold blue")
    hw_table.add_column("Value", style="bold green", justify="right")
    hw_table.add_row("Logical Qubits", str(metrics["width"]))
    hw_table.add_row("Circuit Depth", str(metrics["depth"]))
    hw_table.add_row("Total Gate Count", str(metrics["gate_count"]))
    hw_table.add_row("Non-Local Gates (CX/CZ)", str(metrics["cx_count"]))
    hw_table.add_row("T-Count (Magic States)", str(metrics["t_count"]))
    
    console.print("\n")
    console.print(hw_table)

    # 2. State Probability Distribution
    state_table = Table(title="Quantum State Probability Vector", style="magenta")
    state_table.add_column("Measured State (Key)", style="bold yellow")
    state_table.add_column("Probability", justify="right")
    state_table.add_column("Hits (Shots)", justify="right")
    state_table.add_column("Confidence Bar", style="dim")

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    max_count = sorted_counts[0][1] if sorted_counts else 1

    for state, count in sorted_counts[:10]:  # Show top 10 states
        prob = (count / shots) * 100
        bar_len = int((count / max_count) * 20)
        bar = "█" * bar_len
        
        if prob > 50.0:
            state_table.add_row(f"[bold red]{state}[/bold red]", f"[bold red]{prob:.2f}%[/bold red]", str(count), f"[red]{bar}[/red]")
        else:
            state_table.add_row(state, f"{prob:.2f}%", str(count), bar)

    console.print("\n")
    console.print(state_table)

def main():
    parser = argparse.ArgumentParser(
        prog="QC-Inverter",
        description="Advanced Quantum SAT Cryptanalysis Engine (Grover's Algorithm)",
        epilog="Designed for Vulnerability Research & Post-Quantum Analysis."
    )
    parser.add_argument("-e", "--expression", required=True, type=str, help="Logical payload to invert (e.g., '(v0 ^ v1) & v2')")
    parser.add_argument("-s", "--shots", type=int, default=8192, help="Number of measurement shots (default: 8192)")
    parser.add_argument("-o", "--opt-level", type=int, default=3, choices=[0, 1, 2, 3], help="Transpiler optimization depth")
    parser.add_argument("--noise", action="store_true", help="Enable hardware depolarizing noise simulation")
    
    args = parser.parse_args()

    engine = QuantumCryptanalysisEngine(
        expression=args.expression,
        shots=args.shots,
        opt_level=args.opt_level,
        simulate_noise=args.noise
    )
    
    engine.construct_circuit()
    counts, metrics = engine.execute()
    render_results(counts, metrics, args.shots)

if __name__ == "__main__":
    main()
