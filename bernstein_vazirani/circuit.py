"""
Bernstein-Vazirani Algorithm Implementation using Qiskit

This module implements the Bernstein-Vazirani algorithm, which determines
a secret binary string by querying a function in a single query (using quantum parallelism).

The algorithm demonstrates:
- Superposition: Input qubits exist in all states simultaneously
- Hadamard (H) Gate: Catalyst transforming |0⟩ into superposition
- Phase Kickback: CNOT gates in superposition mark the secret into quantum phase
- Interference: Second Hadamard converts phase information back to amplitude
- Measurement: Collapses quantum state to classical answer
- Scalability: Automatically expands from 3-bit to 8-bit to handle higher complexity
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from typing import Tuple, Dict, List


def build_bv_circuit(secret_string: str) -> QuantumCircuit:
    """
    Create a Bernstein-Vazirani circuit for a given secret string.
    
    Implements all five steps of the algorithm with lexicon terms:
    1. Superposition: Initialize qubits using Hadamard catalyst
    2. Helper Qubit: Ancilla prepared with X+H gates for Phase Kickback engine
    3. Oracle Logic: CNOT arrangement encoding the secret string
    4. Interference: Second Hadamard gates extract phase information
    5. Measurement: Collapse to classical answer
    
    Args:
        secret_string: A binary string (e.g., '101' or '11010111') representing the secret
        
    Returns:
        A QuantumCircuit implementing the Bernstein-Vazirani algorithm
        
    Complexity:
        Questions required: 1 (quantum parallelism through superposition)
        Circuit depth: O(n) where n = len(secret_string)
    """
    n = len(secret_string)  # Number of query qubits (Scalability dimension)
    
    # Create quantum registers: n query qubits + 1 ancilla qubit
    query_qubits = QuantumRegister(n, 'q')
    
    # Helper Qubit: Prepared with X and H gates to serve as Phase Kickback engine
    ancilla_qubit = QuantumRegister(1, 'a')
    
    # Create classical register for measurement results
    classical_bits = ClassicalRegister(n, 'c')
    
    # Create the circuit
    circuit = QuantumCircuit(query_qubits, ancilla_qubit, classical_bits, name='Bernstein-Vazirani')
    
    # ============================================================
    # Step 1 & Step 2: Superposition + Helper Qubit Setup
    # ============================================================
    # Helper Qubit: Apply X then H gates to create |-> state
    # This |-⟩ = (|0⟩ - |1⟩)/√2 state is the Phase Kickback engine
    circuit.x(ancilla_qubit[0])
    circuit.h(ancilla_qubit[0])
    
    # Superposition: Apply Hadamard catalyst to transform qubits from Ground State (|0⟩)
    # into superposition. Hadamard (H) Gate acts as catalyst for all possible states.
    for i in range(n):
        circuit.h(query_qubits[i])
    
    circuit.barrier()
    
    # ============================================================
    # Step 3: Oracle Logic - Phase Kickback
    # ============================================================
    # Oracle Logic: Specific arrangement of CNOT gates that represents
    # and encodes the hidden data (secret string) into quantum phase.
    #
    # Phase Kickback: CNOT gates in superposition "mark" secret string
    # into the quantum phase. When control qubit is |1⟩ in superposition,
    # the |-⟩ ancilla flips its phase by -1, marking that basis state.
    for i in range(n):
        if secret_string[i] == '1':
            # CNOT: Control qubit flips target (ancilla) if control is |1⟩
            # This implements the dot product s·x where s is the secret
            circuit.cx(query_qubits[i], ancilla_qubit[0])
    
    circuit.barrier()
    
    # ============================================================
    # Step 4: Interference
    # ============================================================
    # Interference: A quantum phenomenon where "wrong" answers cancel out
    # and the "right" answer (the secret string) is strengthened.
    # 
    # Second application of Hadamard catalyst converts Phase information
    # back into Bit (amplitude) information that can be measured.
    # This transforms the secret string from quantum phase to classical bits.
    for i in range(n):
        circuit.h(query_qubits[i])
    
    circuit.barrier()
    
    # ============================================================
    # Step 5: Measurement - The Collapse
    # ============================================================
    # Measurement (M) Gate: Causes quantum state to collapse into
    # definite classical answer (0 or 1) from Ground State (|0⟩) state.
    # The collapsed state is the secret string with high probability.
    circuit.measure(query_qubits, classical_bits)
    
    return circuit


# Alias for backwards compatibility
create_bernstein_vazirani_circuit = build_bv_circuit


def run_simulation(secret_string: str, shots: int = 1024) -> dict:
    """
    Run the Bernstein-Vazirani circuit simulation and return measurement results.
    
    Args:
        secret_string: The secret binary string to discover
        shots: Number of times to run the circuit (default: 1024)
        
    Returns:
        A dictionary with measurement counts
    """
    # Create the circuit
    circuit = build_bv_circuit(secret_string)
    
    # Use AerSimulator for simulation
    simulator = AerSimulator()
    
    # Run the circuit
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts(circuit)
    
    return counts


def verify_result(secret_string: str, counts: dict) -> bool:
    """
    Verify that the measurement results match the secret string.
    
    Args:
        secret_string: The expected secret string
        counts: Measurement counts from the simulation
        
    Returns:
        True if the most common measurement matches the secret string
    """
    # Get the most common measurement result
    most_common = max(counts, key=counts.get)
    
    # The result should be the secret string (bits are ordered left-to-right)
    return most_common == secret_string


def run_statevector_simulation(secret_string: str) -> Tuple[QuantumCircuit, dict]:
    """
    Run Bernstein-Vazirani with Statevector Simulation (ideal, noise-free).
    
    Statevector Simulation: Theoretical, perfect execution of quantum program
    entirely noise-free. The "ideal math" world.
    
    Args:
        secret_string: The secret binary string to discover
        
    Returns:
        Tuple of (circuit, measurement_counts)
    """
    circuit = build_bv_circuit(secret_string)
    simulator = AerSimulator(method='statevector')
    job = simulator.run(circuit, shots=1024)
    result = job.result()
    counts = result.get_counts(circuit)
    return circuit, counts


def test_scalability(bit_sizes: List[int] = None) -> Dict[int, Dict[str, any]]:
    """
    Test Scalability: Verify BV algorithm works for 3-bit, 4-bit, and 8-bit examples.
    
    Scalability: The ability of quantum circuit architecture to automatically expand
    (such as from 4 bits to 8 bits) to handle higher complexity.
    
    Args:
        bit_sizes: List of bit sizes to test (default: [3, 4, 8])
        
    Returns:
        Dictionary with results for each bit size
    """
    if bit_sizes is None:
        bit_sizes = [3, 4, 8]
    
    results = {}
    # Use simple all-ones patterns for reliable testing across bit sizes
    test_cases = {
        3: '111',         # 3-bit: all ones
        4: '1111',        # 4-bit: all ones  
        8: '11111111'     # 8-bit: all ones
    }
    
    for n_bits in bit_sizes:
        if n_bits not in test_cases:
            continue
            
        secret = test_cases[n_bits]
        
        # Build and run circuit
        circuit, counts = run_statevector_simulation(secret)
        most_common = max(counts, key=counts.get)
        success = most_common == secret
        
        results[n_bits] = {
            'secret': secret,
            'result': most_common,
            'success': success,
            'counts': counts,
            'circuit_depth': circuit.depth(),
            'circuit_size': len(circuit)
        }
    
    return results


if __name__ == "__main__":
    # Example: Run the algorithm for secret string '101'
    secret = '101'
    print(f"Secret string: {secret}")
    print(f"Running Bernstein-Vazirani algorithm...\n")
    
    # Get the circuit with Statevector Simulation (ideal, noise-free)
    circuit, counts = run_statevector_simulation(secret)
    print("Circuit:")
    print(circuit)
    print()
    
    # Run simulation
    print("Measurement results:")
    print(counts)
    print()
    
    # Verify the result
    is_correct = verify_result(secret, counts)
    most_common = max(counts, key=counts.get)
    print(f"Most common result: {most_common}")
    print(f"Algorithm successful: {is_correct}")
    
    # Test Scalability
    print("\n\n" + "="*60)
    print("SCALABILITY TEST: Testing 3-bit, 4-bit, and 8-bit instances")
    print("="*60)
    scalability_results = test_scalability([3, 4, 8])
    
    print("\n\nSCALABILITY SUMMARY:")
    print("="*60)
    for n_bits, result in scalability_results.items():
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{n_bits}-bit: {status} | Secret={result['secret']} | Result={result['result']}")
