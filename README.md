# Quantum-Katas

A comprehensive implementation of the **Bernstein-Vazirani algorithm** using Qiskit, demonstrating:
- **Superposition**: Quantum states existing in multiple possibilities simultaneously
- **Phase Kickback**: Marking secret strings into quantum phase via CNOT gates
- **Interference**: Converting phase information back into measurable amplitudes
- **Scalability**: Automatically expanding from 3-bit to 8-bit to handle higher complexity
- **Reality Gap**: Measuring the difference between ideal (Statevector) and noisy (hardware) simulations

---

## 📚 What is Bernstein-Vazirani?

The **Bernstein-Vazirani algorithm** is a quantum algorithm that solves the following problem:

**Problem Statement:** Given a black-box function (oracle) `f(x) = s · x mod 2`, where:
- `s` is a hidden *n*-bit string (the "secret")
- `·` denotes the bitwise inner product (dot product)
- Find `s` using as few queries to `f` as possible

**Classical Complexity:** Requires **n queries** (one query per bit)  
**Quantum Complexity:** Requires **1 query** using quantum superposition and interference ⚡

---

## 🔬 How It Works: Five Key Steps

All five steps are implemented in [bernstein_vazirani/circuit.py](bernstein_vazirani/circuit.py):

### Step 1: Superposition (Hadamard Catalyst)
Initialize *n* query qubits into **Superposition** using the **Hadamard (H) Gate** as a catalyst, transforming each qubit from **Ground State** (|0⟩) into all possible states simultaneously.

```python
# Hadamard catalyst: |0⟩ → (|0⟩ + |1⟩)/√2
for i in range(n):
    circuit.h(query_qubits[i])
```

### Step 2: Helper Qubit Setup (Phase Kickback Engine)
Prepare the **Helper Qubit** (ancilla) in the |→⟩ state using X and H gates. This |−⟩ state is the **Phase Kickback engine** that enables phase-marking.

```python
# Helper Qubit preparation: |0⟩ → X → H → |−⟩ = (|0⟩ - |1⟩)/√2
circuit.x(ancilla_qubit[0])
circuit.h(ancilla_qubit[0])
```

### Step 3: Oracle (Phase Kickback)
Apply **CNOT gates** according to **Oracle Logic**: the specific arrangement that encodes the hidden secret string. The **Phase Kickback** mechanism marks the secret into quantum phase.

```python
# CNOT: Control qubit flips target if control is |1⟩
# Implements the dot product f(x) = s·x (mod 2)
for i in range(n):
    if secret_string[i] == '1':
        circuit.cx(query_qubits[i], ancilla_qubit[0])
```

### Step 4: Interference (Hadamard Extraction)
Apply **Hadamard gates** again to the query register. This **Interference** step converts the phase-encoded secret from quantum phase back into measurable amplitudes.

```python
# Hadamard catalyst again: Extract phase information
for i in range(n):
    circuit.h(query_qubits[i])
```

### Step 5: Measurement (Collapse)
**Measure** the query qubits to collapse the quantum state into the **Ground State** (|0⟩) or |1⟩ classical answer. The secret string emerges with high probability.

```python
# Measurement (M) Gate: Collapse to classical answer
circuit.measure(query_qubits, classical_bits)
```

---

## 📊 Bridging the Reality Gap

This project demonstrates the **Reality Gap** between two quantum compute models:

### 🟢 Ideal Path: Statevector Simulation
- **Statevector Simulation**: Theoretical, perfect execution of the quantum program
- Entirely noise-free; represents "ideal math"
- Achieved by `AerSimulator(method='statevector')`

### 🟡 Noisy Path: Hardware Simulation
- Real quantum hardware errors (CNOT gate errors ~5%)
- Represents what actually happens on IBM Brisbane, IonQ, etc.
- Simulated by `AerSimulator(noise_model=NoiseModel())`

### 📏 Hellinger Distance
The **Hellinger Distance** is a mathematical metric that quantifies how different two probability distributions are. It measures the **Reality Gap**.

```python
from qiskit.quantum_info import hellinger_distance

gap = hellinger_distance(ideal_counts, noisy_counts)
# gap < 0.05   → 🟢 Excellent (< 5% degradation)
# gap < 0.10   → 🟡 Good (5-10% degradation)
# gap < 0.20   → 🟠 Acceptable (10-20% degradation)
# gap ≥ 0.20   → 🔴 Critical (> 20% degradation)
```

### 🛡️ Shadow Oracle Validation
Before running on expensive quantum hardware (Blue Path), the **Shadow Oracle Validator** checks if Hellinger Distance < 0.20. If not, error mitigation is recommended instead.

```python
try:
    ShadowOracleValidator.validate_execution(gap)
    print("✅ APPROVED: Circuit ready for QPU")
except ExecutionAbortedError:
    print("❌ REJECTED: Apply error mitigation first")
```

---

## ✅ Scalability: 3-bit → 4-bit → 8-bit

The algorithm's **Scalability** automatically expands from small examples to larger problems:

```python
from bernstein_vazirani.circuit import test_scalability

results = test_scalability([3, 4, 8])
# 3-bit example: secret='101'
# 4-bit example: secret='1011'
# 8-bit example: secret='11010111'
```

All examples execute in a **single oracle query** ⚡

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Complete Analysis

```bash
python main.py
```

Output includes:
- ✅ Ideal simulation results (Statevector)
- ❌ Noisy simulation results (5% CNOT error)
- 📊 Hellinger Distance (Reality Gap)
- 🛡️ Shadow Oracle validation status
- 📈 Scalability test results for 3-bit, 4-bit, 8-bit

### Run Just the Circuit

```bash
python -m bernstein_vazirani.circuit
```

### Interactive Usage

```python
from bernstein_vazirani.circuit import build_bv_circuit, run_statevector_simulation

# Create circuit for secret '101'
circuit, counts = run_statevector_simulation('101')
print(counts)  # {'101': 1024}  (100% probability)

# Test scalability
from bernstein_vazirani.circuit import test_scalability
results = test_scalability([3, 4, 8])
```

---

## 📁 Project Structure

```
Quantum-Katas/
├── README.md                          # This file
├── LEXICON.md                         # Quantum computing definitions
├── requirements.txt                   # Python dependencies
├── main.py                            # Main execution (Reality Gap analysis)
├── Bernstein_Vazirani_Complete.py     # Full integrated implementation
├── .github/
│   └── copilot-instructions.md        # Copilot configuration & definitions
├── bernstein_vazirani/
│   ├── __init__.py
│   ├── circuit.py                     # BV circuit implementation
│   ├── telemetry.py                   # Reality Gap telemetry & monitoring
│   └── test_scalability.py            # Scale tests (3-bit to 8-bit)
└── quanta/
    ├── __init__.py
    └── oracle.py                      # Oracle implementations (Phase Kickback)
```

---

## 🔍 Key Files

| File | Purpose |
|------|---------|
| [bernstein_vazirani/circuit.py](bernstein_vazirani/circuit.py) | Full BV algorithm with all 5 steps, Statevector simulation, Scalability testing |
| [quanta/oracle.py](quanta/oracle.py) | Phase Kickback oracle construction using CNOT gates |
| [main.py](main.py) | Reality Gap analysis (ideal vs noisy), Hellinger Distance, Shadow Oracle |
| [bernstein_vazirani/telemetry.py](bernstein_vazirani/telemetry.py) | Hellinger Distance tracking, statistics, health status |
| [LEXICON.md](LEXICON.md) | Complete reference for quantum computing definitions |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Copilot configuration & source of truth |

---

## 📖 Full Lexicon

See [LEXICON.md](LEXICON.md) for complete quantum computing reference including:
- ✓ Superposition
- ✓ Hadamard (H) Gate
- ✓ Phase Kickback
- ✓ CNOT (CX) Gate
- ✓ Interference
- ✓ Oracle Logic
- ✓ Helper Qubit
- ✓ Measurement (M) Gate
- ✓ Statevector Simulation
- ✓ Reality Gap
- ✓ Hellinger Distance
- ✓ Ground State (|0⟩)
- ✓ Scalability

---

## 🎯 Example Output

```
🔍 REALITY GAP ANALYSIS FOR SECRET '101'
======================================================================

🟢 IDEAL (Statevector Simulation - Noise-Free):
   Result: 101
   Top Probabilities: [('101', 1024)]

🟡 ACTUAL (Noisy Simulation - 5% CNOT Error Rate):
   Result: 101
   Top Probabilities: [('101', 987), ('100', 22), ('001', 15)]

📊 HELLINGER DISTANCE (Reality Gap):
   Distance: 0.0341
   Interpretation: 3.41% degradation from ideal
   Health: 🟢 EXCELLENT (< 5% degradation)

🛡️  SHADOW ORACLE VALIDATION:
   ✅ APPROVED: Circuit ready for Blue (QPU) Execution
======================================================================

======================================================================
SCALABILITY TEST: 3-BIT, 4-BIT, 8-BIT BERNSTEIN-VAZIRANI
======================================================================

SCALABILITY RESULTS:
----------------------------------------------------------------------
3-BIT  | ✓ SUCCESS | Secret=101     | Result=101
4-BIT  | ✓ SUCCESS | Secret=1011    | Result=1011
8-BIT  | ✓ SUCCESS | Secret=11010111 | Result=11010111
```

---

## 🧪 Learning Path

1. **Start here:** Run `python main.py` to see the full algorithm
2. **Understand circuits:** Read [bernstein_vazirani/circuit.py](bernstein_vazirani/circuit.py) comments
3. **Explore oracles:** Review [quanta/oracle.py](quanta/oracle.py) for Phase Kickback details
4. **Study definitions:** Reference [LEXICON.md](LEXICON.md) for quantum concepts
5. **Test scalability:** Modify `test_scalability()` with your own bit sizes
6. **Measure Reality Gap:** See how algorithms degrade with noise in [bernstein_vazirani/telemetry.py](bernstein_vazirani/telemetry.py)

---

## 📚 References

1. Bernstein & Vazirani (1997) - Original paper
2. IBM Qiskit Documentation
3. Quantum Computing Basics - Michael Nielsen & Isaac Chuang
4. Architecture patterns for quantum algorithms

---

## 📝 Notes

- All code uses **Qiskit 1.0+** with Aer simulator
- Noise model represents 5% CNOT error (typical for NISQ devices)
- Circuit depths scale linearly with secret string length (O(n))
- Measurement takes all queries to classical bits simultaneously
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

