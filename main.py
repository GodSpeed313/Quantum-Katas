"""
Main Entry Point for Quantum-Katas

This module serves as the main entry point for running quantum algorithm implementations.
It orchestrates the various quantum circuits and telemetry monitoring.
"""

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.quantum_info import hellinger_distance
import quanta.oracle as quanta
from quanta.oracle import ShadowOracleValidator, ExecutionAbortedError
from bernstein_vazirani.circuit import build_bv_circuit


def get_mock_noise_model():
    """
    Creates a basic noise model to represent hardware errors.
    
    Simulates errors on CNOT gates (2-qubit gates) at 5% error rate,
    representative of real quantum hardware like IBM Brisbane.
    
    Returns:
        NoiseModel with depolarizing errors on CNOT gates
    """
    noise_model = NoiseModel()
    # Add a 5% error rate to all CNOT gates (2-qubit gates)
    error_gate = depolarizing_error(0.05, 2)
    noise_model.add_all_qubit_quantum_error(error_gate, ["cx"])
    return noise_model


def run_reality_check(secret_string):
    # 1. Initialize BV circuit
    qc = build_bv_circuit(secret_string)
    
    # 2. IDEAL RUN (🟢 Green) - Perfect simulation
    ideal_sim = AerSimulator(method='statevector')
    ideal_counts = ideal_sim.run(qc, shots=1024).result().get_counts()
    
    # 3. NOISY RUN (🟡 Yellow) - Simulating a real device like IBM Brisbane
    # Now with a real Noise Model representing hardware errors
    noise_model = get_mock_noise_model()
    noisy_sim = AerSimulator(noise_model=noise_model)
    noisy_counts = noisy_sim.run(qc, shots=1024).result().get_counts()
    
    # 4. Calculate the Gap (Reality Gap: Ideal vs Hardware)
    gap = hellinger_distance(ideal_counts, noisy_counts)
    
    print(f"\n[Quanta Analysis for '{secret_string}']")
    print(f"Ideal Results: {ideal_counts}")
    print(f"Noisy Results: {noisy_counts}")
    print(f"Reality Gap (Hellinger Distance): {gap:.4f}")
    print(f"Health Status: {ShadowOracleValidator.get_health_status(gap)}")
    
    # 5. SHADOW ORACLE VALIDATION: Validate before QPU execution
    try:
        ShadowOracleValidator.validate_execution(gap, circuit_name=f"BV_{secret_string}")
        print(f"\n✅ APPROVED: Ready for Blue (QPU) Execution")
        return gap
    except ExecutionAbortedError:
        print(f"\n🚫 Blue (QPU) execution blocked by Shadow Oracle")
        return gap

if __name__ == "__main__":
    run_reality_check("1101")