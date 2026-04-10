"""
Bernstein-Vazirani Algorithm Implementation using Qiskit

This module implements the Bernstein-Vazirani algorithm, which determines
a secret binary string by querying a function in a single query (using quantum parallelism).

The algorithm demonstrates phase kickback and amplitude amplification principles.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def build_bv_circuit(secret_string: str) -> QuantumCircuit:
    """
    Create a Bernstein-Vazirani circuit for a given secret string.
    
    Args:
        secret_string: A binary string (e.g., '101') representing the secret
        
    Returns:
        A QuantumCircuit implementing the Bernstein-Vazirani algorithm
    """
    n = len(secret_string)  # Number of query qubits
    
    # Create quantum registers: n query qubits + 1 ancilla qubit
    query_qubits = QuantumRegister(n, 'q')
    ancilla_qubit = QuantumRegister(1, 'a')
    
    # Create classical register for measurement results
    classical_bits = ClassicalRegister(n, 'c')
    
    # Create the circuit
    circuit = QuantumCircuit(query_qubits, ancilla_qubit, classical_bits, name='Bernstein-Vazirani')
    
    # Step 1: Initialize ancilla qubit to |-⟩ state
    # Apply X gate to flip |0⟩ to |1⟩
    circuit.x(ancilla_qubit[0])
    # Apply Hadamard to create |-⟩ = (|0⟩ - |1⟩)/√2
    circuit.h(ancilla_qubit[0])
    
    # Step 2: Apply Hadamard gates to all query qubits
    for i in range(n):
        circuit.h(query_qubits[i])
    
    circuit.barrier()
    
    # Step 3: Apply the oracle using CNOT gates
    # The oracle implements the function f(x) = s·x (mod 2)
    # where s is the secret string and · is the dot product
    for i in range(n):
        if secret_string[i] == '1':
            # If the i-th bit of secret string is 1, apply CNOT controlled by query qubit i
            circuit.cx(query_qubits[i], ancilla_qubit[0])
    
    circuit.barrier()
    
    # Step 4: Apply Hadamard gates again to query qubits
    for i in range(n):
        circuit.h(query_qubits[i])
    
    circuit.barrier()
    
    # Step 5: Measure the query qubits
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


if __name__ == "__main__":
    # Example: Run the algorithm for secret string '101'
    secret = '101'
    print(f"Secret string: {secret}")
    print(f"Running Bernstein-Vazirani algorithm...\n")
    
    # Get the circuit
    circuit = build_bv_circuit(secret)
    print("Circuit:")
    print(circuit)
    print()
    
    # Run simulation
    counts = run_simulation(secret)
    print("Measurement results:")
    print(counts)
    print()
    
    # Verify the result
    is_correct = verify_result(secret, counts)
    most_common = max(counts, key=counts.get)
    print(f"Most common result: {most_common}")
    print(f"Algorithm successful: {is_correct}")
