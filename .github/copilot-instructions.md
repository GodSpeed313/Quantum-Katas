# Copilot Instructions for Quantum-Katas

## Project Context
I am a student developer working on the Bernstein-Vazirani algorithm.

## Source of Truth: Quantum Computing Definitions

The following definitions are the authoritative reference for this project. When writing code or explaining concepts:
- **Prioritize the logic** found in these definitions, especially Phase Kickback and the Hadamard catalyst
- **Reference these specific terms** in code comments to reinforce learning
- **Use Statevector simulation** as the default for ideal math
- **Identify the Reality Gap** when noisy backends are used

### Quantum Gates & Operations

**Superposition:** A state where a qubit exists as both 0 and 1 at the same time [1].

**Hadamard (H) Gate:** A quantum gate that acts as a catalyst to transform qubits from a definite ground state into superposition [1, 2].

**Phase Kickback:** A process triggered by CNOT gates in a state of superposition that "marks" a secret string into the quantum phase of the system [3, 4].

**CNOT (CX) Gate:** Also known as a Controlled-NOT gate; it uses a Control qubit to determine if a Target qubit should be "flipped" [3, 5].

**Measurement (M) Gate:** A gate that causes the quantum state to collapse into a definite classical answer (0 or 1) so it can be read by the user [6, 8, 9].

### Quantum Phenomena

**Interference:** A quantum phenomenon where "wrong" answers cancel each other out and the "right" answer is strengthened, allowing for rapid isolation of the correct result [1, 2].

**Oracle Logic:** The specific arrangement of CNOT gates in a circuit that represents and encodes the hidden data or "secret string" [6].

**Helper Qubit:** A specific qubit (often q₄ or q₈ in these examples) prepared with X and H gates to serve as the "Phase Kickback" engine [4, 6, 7].

**Ground State (|0⟩):** The initial, definite state of a qubit before it is transformed by quantum gates [1].

### Performance & Simulation

**Statevector Simulation:** A theoretical, perfect execution of a quantum program that is entirely noise-free [10].

**Reality Gap:** The measurable difference between an ideal theoretical output and the results produced by real, noisy hardware [7, 11].

**Hellinger Distance:** A mathematical metric used to quantify the similarity between the probability distributions of two different quantum outputs [10].

### Circuit Design

**Scalability:** The ability of a quantum circuit architecture to automatically expand (such as from 4 bits to 8 bits) to handle higher complexity [6, 7].

---

## References

[1] **Quantum Superposition & Basic Gates**  
Core principles of quantum mechanics; fundamental to all quantum algorithms

[2] **Hadamard Gate Properties**  
The Hadamard gate as a catalyst for creating equal superposition; mathematical form and properties

[3] **CNOT & Phase Kickback Mechanics**  
Controlled-NOT gate implementation; phase kickback mechanism in quantum oracles

[4] **Phase Kickback Engine Design**  
Using Helper Qubits in |-⟩ state to enable phase marking in quantum algorithms

[5] **CNOT Gate Control Mechanics**  
Control-target qubit relationships; implementation in Qiskit with `.cx()` gates

[6] **Oracle Logic & Circuit Architecture**  
Encoding functions as quantum oracles; designing circuits for hidden data extraction

[7] **Scalability & Hardware Considerations**  
Expanding circuits from small (3-qubit) to large (8-qubit+) instances; real hardware constraints

[8] **Measurement Operations**  
Quantum measurement as state collapse; extracting classical information from quantum states

[9] **Classical State Collapse**  
The role of measurement in producing definite classical outputs from quantum superposition

[10] **Statevector Simulation & Hellinger Distance**  
Ideal (noise-free) quantum execution; mathematical metrics for comparing probability distributions

[11] **Reality Gap in Noisy Systems**  
Quantifying differences between theoretical perfect execution and real noisy hardware; 
Hellinger Distance as a metric for measuring this gap

---

## Implementation Files

This project implements all definitions above:

- **[bernstein_vazirani/circuit.py](../bernstein_vazirani/circuit.py)** — Complete BV algorithm with all 5 steps
- **[quanta/oracle.py](../quanta/oracle.py)** — Phase Kickback oracle construction
- **[main.py](../main.py)** — Reality Gap analysis with Hellinger Distance
- **[Bernstein_Vazirani_Complete.py](../Bernstein_Vazirani_Complete.py)** — Self-contained complete implementation
- **[LEXICON.md](../LEXICON.md)** — Extended reference guide

---

## Notes for Copilot

When helping with quantum code in this repository:

1. **Always reference** terms from this "Source of Truth" lexicon
2. **Prioritize Phase Kickback logic** when explaining oracle construction
3. **Use Statevector simulation** as the default (ideal math benchmark)
4. **Highlight Reality Gap** when noisy backends are discussed
5. **Track scalability** - show how circuits expand from 3-bit to 8-bit
6. **Include Hellinger Distance** in any Reality Gap measurements
7. **Comment code** with lexicon terms to reinforce learning

Example comment style:
```python
# Phase Kickback: CNOT gates mark secret into quantum phase
# Helper Qubit (ancilla) in |-⟩ state enables the phase-marking mechanism
for i, bit in enumerate(secret_string):
    if bit == '1':
        circuit.cx(query_qubits[i], ancilla[0])
```
