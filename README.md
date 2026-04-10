# Quantum-Katas

A collection of quantum computing exercises and algorithm implementations using Qiskit, focusing on the Bernstein-Vazirani algorithm and phase kickback logic.

---

## Bernstein-Vazirani Algorithm

### Problem Statement

Given a black-box function (oracle) `f(x) = s · x mod 2`, where `s` is a hidden *n*-bit string and `·` denotes the bitwise inner product, find `s` using as few queries to `f` as possible.

Classically this requires **n** queries (one per bit). The Bernstein-Vazirani algorithm solves it in a **single** query using quantum superposition and interference.

### Algorithm Steps

1. **Initialise** *n* query qubits in |0⟩ and one ancilla qubit in |1⟩.
2. **Apply Hadamard** gates to all qubits, putting the query register into uniform superposition and the ancilla into `(|0⟩ − |1⟩)/√2`.
3. **Query the oracle** once. The phase-kickback mechanism encodes `s` into the phases of the query register.
4. **Apply Hadamard** gates again to the query register.
5. **Measure** the query register — the result is the hidden string `s`.

### Intuition

The second set of Hadamard gates converts the phase differences introduced by the oracle back into amplitude differences, making `s` the only outcome that has constructive interference.

---

## Project Structure

```
Quantum-Katas/
├── README.md
├── requirements.txt
└── bernstein_vazirani/
    ├── __init__.py
    └── circuit.py      # Starter script: 3-qubit BV circuit with Hadamard gates
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the starter circuit

```bash
python -m bernstein_vazirani.circuit
```

The script builds a 3-qubit Bernstein-Vazirani circuit for the hidden string `s = 101` and prints both the circuit diagram and the measurement counts from a simulator run.

---

## References

- Bernstein, E. & Vazirani, U. (1997). *Quantum Complexity Theory*. SIAM Journal on Computing, 26(5), 1411–1473.
- [Qiskit documentation](https://docs.quantum.ibm.com/)

