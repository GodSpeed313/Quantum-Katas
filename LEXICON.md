# Quantum Computing Lexicon

Reference guide for terminology and concepts used in the Bernstein-Vazirani algorithm implementation.

## Quantum Gates & Operations

### Superposition
A state where a qubit exists as both 0 and 1 at the same time [1].

### Hadamard (H) Gate
A quantum gate that acts as a catalyst to transform qubits from a definite ground state into superposition [1, 2].

### Phase Kickback
A process triggered by CNOT gates in a state of superposition that "marks" a secret string into the quantum phase of the system [3, 4].

### CNOT (CX) Gate
Also known as a Controlled-NOT gate; it uses a Control qubit to determine if a Target qubit should be "flipped" [3, 5].

### Measurement (M) Gate
A gate that causes the quantum state to collapse into a definite classical answer (0 or 1) so it can be read by the user [6, 8, 9].

### Ground State (|0⟩)
The initial, definite state of a qubit before it is transformed by quantum gates [1].

## Quantum Phenomena

### Interference
A quantum phenomenon where "wrong" answers cancel each other out and the "right" answer is strengthened, allowing for rapid isolation of the correct result [1, 2].

### Oracle Logic
The specific arrangement of CNOT gates in a circuit that represents and encodes the hidden data or "secret string" [6].

### Helper Qubit
A specific qubit (often q₄ or q₈ in these examples) prepared with X and H gates to serve as the "Phase Kickback" engine [4, 6, 7].

## Performance & Simulation

### Statevector Simulation
A theoretical, perfect execution of a quantum program that is entirely noise-free [10].

### Reality Gap
The measurable difference between an ideal theoretical output and the results produced by real, noisy hardware [7, 11].

### Hellinger Distance
A mathematical metric used to quantify the similarity between the probability distributions of two different quantum outputs [10].

## Circuit Design

### Scalability
The ability of a quantum circuit architecture to automatically expand (such as from 4 bits to 8 bits) to handle higher complexity [6, 7].

---

**References:**
[1] Quantum superposition and basic gates
[2] Hadamard gate catalytic properties
[3] CNOT and phase kickback mechanics
[4] Phase kickback engine design
[5] CNOT gate control mechanics
[6] Oracle logic and circuit architecture
[7] Scalability and hardware considerations
[8] Measurement operations
[9] Classical state collapse
[10] Statevector simulation and Hellinger distance
[11] Reality gap in noisy systems
