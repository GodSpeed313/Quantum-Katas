"""
Main Entry Point for Quantum-Katas - Bernstein-Vazirani Algorithm

This module orchestrates complete Bernstein-Vazirani execution:
1. Ideal Simulation (Statevector - noise-free, "ideal math")
2. Noisy Simulation (Reality Gap measurement using Hellinger Distance)
3. Shadow Oracle Validation (prevents wasting resources on problematic circuits)
4. Scalability Testing (3-bit, 4-bit, 8-bit examples)

Key Concepts from LEXICON:
- Statevector Simulation: Theoretical perfect execution, entirely noise-free
- Reality Gap: Measurable difference between ideal output and noisy hardware results
- Hellinger Distance: Mathematical metric quantifying probability distribution similarity
"""

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.quantum_info import hellinger_distance
import quanta.oracle as quanta
from quanta.oracle import ShadowOracleValidator, ExecutionAbortedError
from bernstein_vazirani.circuit import build_bv_circuit, test_scalability


def get_mock_noise_model():
    """
    Creates a basic noise model to represent hardware errors.
    
    Reality Gap measurement: Simulates errors on CNOT gates (2-qubit gates) at 5% error rate,
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
    """
    Execute Reality Gap Analysis: Compare Ideal vs Noisy simulation.
    
    Uses Shadow Oracle Validation to prevent resource waste on problematic circuits.
    
    Args:
        secret_string: The binary secret to discover with Bernstein-Vazirani
        
    Returns:
        Dictionary with analysis results
    """
    # 1. Initialize BV circuit
    qc = build_bv_circuit(secret_string)
    
    # 2. IDEAL RUN (IDEAL Path) - Statevector Simulation
    # Statevector Simulation: Theoretical perfect execution of quantum program,
    # entirely noise-free. The "ideal math" world shows what should happen.
    ideal_sim = AerSimulator(method='statevector')
    ideal_result = ideal_sim.run(qc, shots=1024).result()
    ideal_counts = ideal_result.get_counts()
    ideal_answer = max(ideal_counts, key=ideal_counts.get)
    
    # 3. NOISY RUN (NOISY Path) - Shadow Oracle Simulation
    # Reality Gap: The measurable difference between ideal theoretical output
    # and results produced by real, noisy hardware. Simulated here before QPU.
    noise_model = get_mock_noise_model()
    noisy_sim = AerSimulator(noise_model=noise_model)
    noisy_result = noisy_sim.run(qc, shots=1024).result()
    noisy_counts = noisy_result.get_counts()
    noisy_answer = max(noisy_counts, key=noisy_counts.get)
    
    # 4. Calculate the Gap (Hellinger Distance)
    # Hellinger Distance: Mathematical metric used to quantify similarity
    # between probability distributions of ideal vs noisy quantum outputs.
    gap = hellinger_distance(ideal_counts, noisy_counts)
    
    # Display results
    print(f"\n[ANALYSIS] REALITY GAP FOR SECRET '{secret_string}'")
    print(f"{'='*70}")
    print(f"\n[IDEAL] Statevector Simulation - Noise-Free:")
    print(f"   Result: {ideal_answer}")
    print(f"   Top Probabilities: {sorted(ideal_counts.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    print(f"\n[NOISY] Actual Simulation - 5% CNOT Error Rate:")
    print(f"   Result: {noisy_answer}")
    print(f"   Top Probabilities: {sorted(noisy_counts.items(), key=lambda x: x[1], reverse=True)[:3]}")
    
    print(f"\n[METRICS] HELLINGER DISTANCE (Reality Gap):")
    print(f"   Distance: {gap:.4f}")
    print(f"   Interpretation: {gap*100:.1f}% degradation from ideal")
    print(f"   Health: {ShadowOracleValidator.get_health_status(gap)}")
    
    # 5. SHADOW ORACLE VALIDATION
    # Shadow Oracle Validation Rule: If reality gap > 0.20, abort QPU execution
    # and suggest error mitigation instead. Prevents resource waste.
    print(f"\n[VALIDATION] SHADOW ORACLE:")
    try:
        ShadowOracleValidator.validate_execution(gap, circuit_name=f"BV_{secret_string}")
        print(f"   [OK] Circuit ready for Blue (QPU) Execution")
        execution_safe = True
    except ExecutionAbortedError:
        print(f"   [BLOCKED] Reality Gap too high - recommended error mitigation")
        execution_safe = False
    
    print(f"{'='*70}")
    
    return {
        'secret': secret_string,
        'ideal_answer': ideal_answer,
        'noisy_answer': noisy_answer,
        'ideal_counts': ideal_counts,
        'noisy_counts': noisy_counts,
        'reality_gap': gap,
        'execution_safe': execution_safe
    }


def run_comprehensive_analysis():
    """
    Run comprehensive Bernstein-Vazirani analysis including scalability testing.
    """
    print("\n" + "="*70)
    print("BERNSTEIN-VAZIRANI ALGORITHM: COMPREHENSIVE ANALYSIS")
    print("="*70)
    
    # Test examples at different scales
    test_secrets = ['101', '1011', '11010111']
    all_results = []
    
    for secret in test_secrets:
        result = run_reality_check(secret)
        all_results.append(result)
    
    # Summary
    print("\n\n" + "="*70)
    print("[SUMMARY] REALITY GAP ACROSS SCALES")
    print("="*70)
    for result in all_results:
        status = "[SAFE]" if result['execution_safe'] else "[UNSAFE]"
        print(f"Secret: {result['secret']:10} | Gap: {result['reality_gap']:.4f} | {status}")
    
    # Scalability test
    print("\n\n" + "="*70)
    print("SCALABILITY TEST: 3-BIT, 4-BIT, 8-BIT BERNSTEIN-VAZIRANI")
    print("="*70)
    scalability_results = test_scalability([3, 4, 8])
    
    print("\n\nSCALABILITY RESULTS:")
    print("-"*70)
    for n_bits, result in scalability_results.items():
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"{n_bits}-BIT | {status} | Secret={result['secret']} | Result={result['result']}")


if __name__ == "__main__":
    # Run comprehensive analysis with Reality Gap measurement and Scalability testing
    run_comprehensive_analysis()