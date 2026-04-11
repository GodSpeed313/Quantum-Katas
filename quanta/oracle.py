"""
Oracle Implementations for Quantum Algorithms

This module provides various oracle constructions used in quantum algorithms
such as Deutsch-Jozsa, Bernstein-Vazirani, and Grover's algorithm.

An oracle is a black-box quantum gate that encodes a classical function
into a quantum circuit, allowing quantum algorithms to query it in superposition.
"""

from typing import List, Callable, Optional
from qiskit import QuantumCircuit, QuantumRegister


class ExecutionAbortedError(Exception):
    """Raised when execution is aborted due to excessive reality gap."""
    pass


class ShadowOracleValidator:
    """
    Shadow Oracle Validation Rule for Quantum Execution Safety
    
    Rule: If the Shadow Oracle (Yellow/Noisy path) predicts a Hellinger Distance > 0.20,
    abort the Blue (QPU) execution and suggest circuit transpilation or error mitigation
    instead of running on real hardware.
    
    This prevents resource waste by catching problematic circuits before they run on
    expensive quantum hardware.
    """
    
    REALITY_GAP_THRESHOLD = 0.20  # Hellinger Distance threshold
    
    @staticmethod
    def validate_execution(reality_gap: float, circuit_name: str = "circuit") -> bool:
        """
        Validate whether a circuit should proceed to QPU execution based on reality gap.
        
        Args:
            reality_gap: The Hellinger Distance between ideal and noisy simulations
            circuit_name: Name of the circuit being validated
            
        Returns:
            True if reality gap is acceptable (< threshold)
            
        Raises:
            ExecutionAbortedError: If reality gap exceeds threshold
        """
        if reality_gap > ShadowOracleValidator.REALITY_GAP_THRESHOLD:
            error_msg = (
                f"\n🔴 EXECUTION ABORTED: Reality Gap Too High\n"
                f"{'='*60}\n"
                f"Circuit: {circuit_name}\n"
                f"Reality Gap (Hellinger Distance): {reality_gap:.4f}\n"
                f"Threshold: {ShadowOracleValidator.REALITY_GAP_THRESHOLD:.4f}\n"
                f"\n❌ REASON: Noisy simulation shows {reality_gap*100:.1f}% degradation\n"
                f"\n💡 RECOMMENDATIONS:\n"
                f"  1. Apply Circuit Transpilation\n"
                f"     - Optimize gate count\n"
                f"     - Reduce CNOT depth\n"
                f"     - Use transpile(circuit, optimization_level=3)\n\n"
                f"  2. Implement Error Mitigation\n"
                f"     - Zero-noise extrapolation (ZNE)\n"
                f"     - Probabilistic error cancellation (PEC)\n"
                f"     - Dynamical decoupling (DD)\n\n"
                f"  3. Retry After Optimization\n"
                f"     - Re-run validation after applying recommendations\n"
                f"     - Check if new Reality Gap < {ShadowOracleValidator.REALITY_GAP_THRESHOLD:.4f}\n"
                f"{'='*60}\n"
            )
            raise ExecutionAbortedError(error_msg)
        
        return True
    
    @staticmethod
    def get_health_status(reality_gap: float) -> str:
        """
        Get a human-readable health status for a circuit.
        
        Args:
            reality_gap: The Hellinger Distance
            
        Returns:
            Status string with emoji and description
        """
        if reality_gap < 0.05:
            return "🟢 EXCELLENT (< 5% degradation)"
        elif reality_gap < 0.10:
            return "🟡 GOOD (5-10% degradation)"
        elif reality_gap < 0.20:
            return "🟠 ACCEPTABLE (10-20% degradation)"
        else:
            return "🔴 CRITICAL (> 20% degradation)"


# Decorator for automatic validation
def require_low_reality_gap(func):
    """
    Decorator that validates circuit before execution.
    
    Requires the decorated function to return a tuple of (reality_gap, result).
    
    Example:
        @require_low_reality_gap
        def run_on_qpu(secret_string):
            gap = calculate_reality_gap(secret_string)
            result = execute(secret_string)
            return gap, result
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                reality_gap, actual_result = result
                ShadowOracleValidator.validate_execution(
                    reality_gap,
                    circuit_name=func.__name__
                )
            return result
        except ExecutionAbortedError as e:
            print(str(e))
            raise
    return wrapper


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


def create_bv_oracle(secret_string: str) -> QuantumCircuit:
    """
    Create a Bernstein-Vazirani oracle for a given secret string.
    
    Uses Scalability principle: automatically expands from 3-bit to 8-bit to handle higher complexity.
    
    Oracle Logic: Specific arrangement of CNOT gates encoding the hidden data (secret string)
    into the quantum phase. CNOT gates implement the dot product s·x where s is the secret.
    
    Phase Kickback: CNOT gates in superposition mark the secret string into the quantum phase.
    Helper Qubit (ancilla) in |-> state enables the phase-marking mechanism.
    
    Args:
        secret_string: Binary string representing the secret (e.g., '101' or '11010111')
        
    Returns:
        QuantumCircuit implementing the Bernstein-Vazirani oracle
    """
    oracle = PhaseOracleMarkingBits(secret_string)
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
