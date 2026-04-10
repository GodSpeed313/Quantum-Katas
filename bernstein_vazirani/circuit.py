"""
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
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


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
