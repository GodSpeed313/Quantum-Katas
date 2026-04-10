"""
Oracle Implementations for Quantum Algorithms

This module provides various oracle constructions used in quantum algorithms
such as Deutsch-Jozsa, Bernstein-Vazirani, and Grover's algorithm.

An oracle is a black-box quantum gate that encodes a classical function
into a quantum circuit, allowing quantum algorithms to query it in superposition.
"""

from typing import List, Callable, Optional
from qiskit import QuantumCircuit, QuantumRegister


class Oracle:
    """Base class for quantum oracle implementations."""
    
    def __init__(self, num_qubits: int, name: str = "oracle"):
        """
        Initialize an oracle.
        
        Args:
            num_qubits: Number of qubits the oracle operates on
            name: Name for the oracle circuit
        """
        self.num_qubits = num_qubits
        self.name = name
    
    def build(self) -> QuantumCircuit:
        """
        Build and return the oracle circuit.
        
        Returns:
            QuantumCircuit representing the oracle
        """
        raise NotImplementedError("Subclasses must implement build()")


class PhaseOracleMarkingBits(Oracle):
    """
    Oracle that marks qubits based on a secret bit string using phase kickback.
    
    Used in algorithms like Bernstein-Vazirani where we want to encode
    a binary string s into an oracle that applies a phase based on s·x.
    """
    
    def __init__(self, secret_string: str, ancilla_index: Optional[int] = None):
        """
        Initialize a phase oracle for a secret bit string.
        
        Args:
            secret_string: Binary string (e.g., '101') representing which qubits to mark
            ancilla_index: Index of the ancilla qubit (usually n where qubits are 0..n)
        """
        self.secret_string = secret_string
        self.n = len(secret_string)
        self.ancilla_index = ancilla_index if ancilla_index is not None else self.n
        super().__init__(self.n + 1, f"phase_oracle_{secret_string}")
    
    def build(self) -> QuantumCircuit:
        """
        Build the oracle using CNOT gates with phase kickback.
        
        The oracle implements f(x) = s·x (mod 2) where s is the secret string.
        
        Returns:
            QuantumCircuit implementing the phase oracle
        """
        qubits = QuantumRegister(self.n, 'q')
        ancilla = QuantumRegister(1, 'a')
        circuit = QuantumCircuit(qubits, ancilla, name=self.name)
        
        # Apply CNOT from each query qubit where secret bit is 1 to ancilla
        for i, bit in enumerate(self.secret_string):
            if bit == '1':
                circuit.cx(qubits[i], ancilla[0])
        
        return circuit


class BalancedOracleConstantZero(Oracle):
    """
    A balanced oracle that always returns 0 (all CNOTs cancel out).
    
    Used for testing Deutsch-Jozsa and other algorithms that distinguish
    between balanced and constant functions.
    """
    
    def __init__(self, num_qubits: int):
        """
        Initialize a balanced oracle that computes 0.
        
        Args:
            num_qubits: Number of query qubits
        """
        super().__init__(num_qubits + 1, f"balanced_zero_oracle")
        self.num_query_qubits = num_qubits
    
    def build(self) -> QuantumCircuit:
        """
        Build the oracle (identity for this case).
        
        Returns:
            QuantumCircuit with no operations (identity)
        """
        qubits = QuantumRegister(self.num_query_qubits, 'q')
        ancilla = QuantumRegister(1, 'a')
        circuit = QuantumCircuit(qubits, ancilla, name=self.name)
        circuit.id(ancilla[0])  # Identity gate (no-op)
        return circuit


class BalancedOracleConstantOne(Oracle):
    """
    A constant oracle that always returns 1 (all qubits flip ancilla).
    
    Used for testing in Deutsch-Jozsa and related algorithms.
    """
    
    def __init__(self, num_qubits: int):
        """
        Initialize a balanced oracle that computes 1.
        
        Args:
            num_qubits: Number of query qubits
        """
        super().__init__(num_qubits + 1, f"constant_one_oracle")
        self.num_query_qubits = num_qubits
    
    def build(self) -> QuantumCircuit:
        """
        Build the oracle (X gate on ancilla).
        
        Returns:
            QuantumCircuit that always flips the ancilla
        """
        qubits = QuantumRegister(self.num_query_qubits, 'q')
        ancilla = QuantumRegister(1, 'a')
        circuit = QuantumCircuit(qubits, ancilla, name=self.name)
        circuit.x(ancilla[0])  # X gate flips ancilla
        return circuit


class GroverOracleMarkedStates(Oracle):
    """
    Oracle for Grover's algorithm that marks specific marked states.
    
    Applies a phase flip (-1) to marked computational basis states
    and identity to other states.
    """
    
    def __init__(self, num_qubits: int, marked_states: List[str]):
        """
        Initialize a Grover oracle with marked states.
        
        Args:
            num_qubits: Number of qubits
            marked_states: List of binary strings to mark (e.g., ['101', '110'])
        """
        self.marked_states = marked_states
        super().__init__(num_qubits, f"grover_oracle")
    
    def build(self) -> QuantumCircuit:
        """
        Build the oracle that marks specified states with a phase flip.
        
        Returns:
            QuantumCircuit implementing the Grover oracle
        """
        qubits = QuantumRegister(self.num_qubits, 'q')
        circuit = QuantumCircuit(qubits, name=self.name)
        
        for marked_state in self.marked_states:
            # For each marked state, apply phase flip
            self._apply_phase_flip(circuit, qubits, marked_state)
        
        return circuit
    
    def _apply_phase_flip(self, circuit: QuantumCircuit, qubits: QuantumRegister, 
                         state: str) -> None:
        """
        Apply controlled-Z phase flip for a specific state.
        
        Args:
            circuit: The circuit to add gates to
            qubits: The quantum register
            state: Binary string representing the marked state
        """
        # X gates on qubits where the state has 0
        for i, bit in enumerate(state):
            if bit == '0':
                circuit.x(qubits[i])
        
        # Multi-controlled Z gate (implemented with Toffoli gates)
        if self.num_qubits == 1:
            circuit.z(qubits[0])
        else:
            # Simple case: use multi-controlled Z
            # For efficiency, we can use a multi-controlled NOT with Z basis
            control_qubits = list(range(self.num_qubits - 1))
            target = self.num_qubits - 1
            
            # Apply multi-controlled phase flip
            if len(control_qubits) > 0:
                circuit.h(qubits[target])
                circuit.mcx(control_qubits=[qubits[i] for i in control_qubits], 
                           target_qubit=qubits[target])
                circuit.h(qubits[target])
        
        # Undo X gates
        for i, bit in enumerate(state):
            if bit == '0':
                circuit.x(qubits[i])


class CustomOracle(Oracle):
    """
    Custom oracle that applies a user-defined unitary function.
    
    Allows constructing oracles from arbitrary gate sequences.
    """
    
    def __init__(self, num_qubits: int, gate_function: Callable[[QuantumCircuit, QuantumRegister], None]):
        """
        Initialize a custom oracle.
        
        Args:
            num_qubits: Number of qubits
            gate_function: A callable that takes (circuit, qubits) and adds gates to the circuit
        """
        self.gate_function = gate_function
        super().__init__(num_qubits, "custom_oracle")
    
    def build(self) -> QuantumCircuit:
        """
        Build the oracle by applying the custom gate function.
        
        Returns:
            QuantumCircuit with custom gates applied
        """
        qubits = QuantumRegister(self.num_qubits, 'q')
        circuit = QuantumCircuit(qubits, name=self.name)
        self.gate_function(circuit, qubits)
        return circuit


def create_oracle_circuit(oracle: Oracle) -> QuantumCircuit:
    """
    Convenience function to create and return an oracle circuit.
    
    Args:
        oracle: An Oracle instance
        
    Returns:
        The built QuantumCircuit from the oracle
    """
    return oracle.build()


if __name__ == "__main__":
    # Example usage
    print("Oracle Implementations Examples\n")
    
    # Example 1: Phase Oracle for Bernstein-Vazirani
    print("1. Phase Oracle (secret='101'):")
    oracle_bv = PhaseOracleMarkingBits("101")
    circuit_bv = oracle_bv.build()
    print(circuit_bv)
    print()
    
    # Example 2: Balanced oracle
    print("2. Balanced Oracle (always returns 0):")
    oracle_balanced = BalancedOracleConstantZero(3)
    circuit_balanced = oracle_balanced.build()
    print(circuit_balanced)
    print()
    
    # Example 3: Constant oracle
    print("3. Constant Oracle (always returns 1):")
    oracle_constant = BalancedOracleConstantOne(3)
    circuit_constant = oracle_constant.build()
    print(circuit_constant)
    print()
    
    # Example 4: Grover oracle
    print("4. Grover Oracle (marks states '101' and '110'):")
    oracle_grover = GroverOracleMarkedStates(3, ['101', '110'])
    circuit_grover = oracle_grover.build()
    print(circuit_grover)
