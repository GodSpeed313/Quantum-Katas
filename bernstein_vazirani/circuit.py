"""
<<<<<<< HEAD
Bernstein-Vazirani Algorithm Implementation using Qiskit

This module implements the Bernstein-Vazirani algorithm, which determines
a secret binary string by querying a function in a single query (using quantum parallelism).

The algorithm demonstrates phase kickback and amplitude amplification principles.
=======
Starter script: Bernstein-Vazirani algorithm on a 3-qubit circuit.

Hidden string: s = '101'

Circuit layout (4 qubits total):
  q0, q1, q2  – query register  (3 qubits)
  q3          – ancilla qubit   (1 qubit, initialised to |1⟩)
  c0, c1, c2  – classical bits for measurement results

Steps
-----
1. Initialise ancilla to |1⟩ with an X gate.
2. Apply Hadamard (H) to all qubits.
3. Apply the phase-kickback oracle for s = '101':
   - CNOT with control q0 → target ancilla  (bit 0 of s is 1)
   - CNOT with control q2 → target ancilla  (bit 2 of s is 1)
   (q1 is skipped because bit 1 of s is 0)
4. Apply Hadamard (H) to the query register again.
5. Measure the query register.

Expected result: measuring '101' with probability ~1.
>>>>>>> e6ac256f335ac1875a25b697797ac819dd233650
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


<<<<<<< HEAD
def create_bernstein_vazirani_circuit(secret_string: str) -> QuantumCircuit:
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
    circuit = create_bernstein_vazirani_circuit(secret_string)
    
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
    circuit = create_bernstein_vazirani_circuit(secret)
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
=======
def build_bv_circuit(hidden_string: str) -> QuantumCircuit:
    """Build the Bernstein-Vazirani circuit for a given hidden bit-string.

    Parameters
    ----------
    hidden_string:
        A string of '0'/'1' characters representing the hidden string *s*.
        The least-significant bit is hidden_string[0].

    Returns
    -------
    QuantumCircuit
        The fully constructed BV circuit, ready to be transpiled / simulated.
    """
    n = len(hidden_string)

    qr = QuantumRegister(n, name="q")
    ancilla = QuantumRegister(1, name="anc")
    cr = ClassicalRegister(n, name="c")

    qc = QuantumCircuit(qr, ancilla, cr)

    # Step 1 – put ancilla into |1⟩
    qc.x(ancilla[0])

    # Step 2 – Hadamard on all qubits
    qc.h(qr)
    qc.h(ancilla[0])

    qc.barrier()

    # Step 3 – oracle: CNOT for each '1' bit in hidden_string
    for i, bit in enumerate(hidden_string):
        if bit == "1":
            qc.cx(qr[i], ancilla[0])

    qc.barrier()

    # Step 4 – Hadamard on query register
    qc.h(qr)

    # Step 5 – measure query register
    qc.measure(qr, cr)

    return qc


def run_simulation(qc: QuantumCircuit, shots: int = 1024) -> dict:
    """Simulate the circuit and return measurement counts.

    Parameters
    ----------
    qc:
        The quantum circuit to simulate.
    shots:
        Number of simulation shots.

    Returns
    -------
    dict
        Measurement outcome counts, e.g. ``{'101': 1024}``.
    """
    simulator = AerSimulator()
    job = simulator.run(qc, shots=shots)
    return job.result().get_counts(qc)


if __name__ == "__main__":
    hidden_string = "101"
    print(f"Building Bernstein-Vazirani circuit for hidden string s = '{hidden_string}'")
    print()

    circuit = build_bv_circuit(hidden_string)
    print(circuit.draw(output="text"))
    print()

    counts = run_simulation(circuit)
    print("Simulation results (counts):", counts)

    if not counts:
        raise RuntimeError("Simulation returned no measurement counts.")

    recovered = max(counts, key=counts.get)
    print(f"Recovered hidden string: '{recovered}'")
    assert recovered == hidden_string, f"Expected '{hidden_string}', got '{recovered}'"
    print("✓ Correct!")
>>>>>>> e6ac256f335ac1875a25b697797ac819dd233650
