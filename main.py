"""
Main Entry Point for Quantum-Katas

This module serves as the main entry point for running quantum algorithm implementations.
It orchestrates the various quantum circuits and telemetry monitoring.
"""

from bernstein_vazirani.circuit import create_bernstein_vazirani_circuit, run_simulation, verify_result
from bernstein_vazirani.telemetry import telemetry
from quanta.oracle import (
    PhaseOracleMarkingBits,
    BalancedOracleConstantZero,
    BalancedOracleConstantOne,
    GroverOracleMarkedStates
)


def run_bernstein_vazirani_demo(secret_string: str):
    """
    Run a demonstration of the Bernstein-Vazirani algorithm.
    
    Args:
        secret_string: The secret binary string to discover
    """
    print(f"\n{'='*60}")
    print(f"Bernstein-Vazirani Algorithm Demo")
    print(f"{'='*60}")
    print(f"Secret string: {secret_string}\n")
    
    # Start telemetry monitoring
    monitor = telemetry.create_monitor(f"bv_{secret_string}", check_interval=0.1)
    
    try:
        # Update status to running
        telemetry.update_status(f"bv_{secret_string}", "running")
        
        # Create and display circuit
        circuit = create_bernstein_vazirani_circuit(secret_string)
        print("Circuit:")
        print(circuit)
        print()
        
        # Run simulation
        print("Running simulation...")
        counts = run_simulation(secret_string, shots=1024)
        
        # Verify results
        is_correct = verify_result(secret_string, counts)
        most_common = max(counts, key=counts.get)
        
        print(f"\nMeasurement results:")
        print(f"  Most common: {most_common}")
        print(f"  Expected:    {secret_string}")
        print(f"  Success:     {is_correct}")
        
        # Update status to completed
        telemetry.update_status(f"bv_{secret_string}", "completed")
        
        return is_correct
        
    finally:
        telemetry.stop_monitor(f"bv_{secret_string}")


def display_oracles():
    """Display various oracle implementations."""
    print(f"\n{'='*60}")
    print("Oracle Implementations")
    print(f"{'='*60}\n")
    
    # Phase Oracle
    print("1. Phase Oracle (Bernstein-Vazirani, secret='101'):")
    oracle_bv = PhaseOracleMarkingBits("101")
    print(oracle_bv.build())
    print()
    
    # Balanced Oracle
    print("2. Balanced Oracle (Constant Zero):")
    oracle_balanced = BalancedOracleConstantZero(3)
    print(oracle_balanced.build())
    print()
    
    # Constant Oracle
    print("3. Constant Oracle (Always 1):")
    oracle_constant = BalancedOracleConstantOne(3)
    print(oracle_constant.build())
    print()
    
    # Grover Oracle
    print("4. Grover Oracle (marks '101' and '110'):")
    oracle_grover = GroverOracleMarkedStates(3, ['101', '110'])
    print(oracle_grover.build())
    print()


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("Quantum-Katas: Quantum Algorithm Implementations")
    print("="*60)
    
    # Test Bernstein-Vazirani with different secret strings
    test_secrets = ['101', '110', '001', '111']
    
    results = {}
    for secret in test_secrets:
        results[secret] = run_bernstein_vazirani_demo(secret)
    
    # Display oracle implementations
    display_oracles()
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Bernstein-Vazirani Results:")
    for secret, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {secret}: {status}")
    print()


if __name__ == "__main__":
    main()
import quanta.oracle as quanta
from qiskit.circuit.library import RealAmplitudes

@quanta.optimize
def build_vqe_ansatz(num_qubits=4):
    """
    Creates a VQE ansatz. Quanta will analyze this to decide 
    if it stays local (Green) or needs a noisy simulation (Yellow).
    """
    # Decomposing ensures Quanta can see the actual CNOT gates
    return RealAmplitudes(num_qubits, reps=2).decompose()

if __name__ == "__main__":
    print("--- Test 1: Simple 4-Qubit Ansatz ---")
    small_circuit = build_vqe_ansatz(num_qubits=4)
    
    print("\n--- Test 2: High-Complexity 22-Qubit Ansatz ---")
    # This should trigger the 'Yellow' routing logic
    complex_circuit = build_vqe_ansatz(num_qubits=22)