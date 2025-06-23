from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

# 1. Initialize IBM Quantum service
service = QiskitRuntimeService()

# 2. Get the least busy backend with 2 qubits that supports dynamic circuits
backend = service.least_busy(
    operational=True,
    simulator=False,
    min_num_qubits=2
)
print(f"Using backend: {backend.name}")

# 3. Define the RSP circuit generator function
def create_rsp_circuit(theta, phi):
    q = QuantumRegister(2, 'q')
    c = ClassicalRegister(1, 'c0')
    qc = QuantumCircuit(q, c)
    
    # Prepare Bell state (|01⟩-|10⟩)/√2
    qc.x(q[0])
    qc.x(q[1])
    qc.h(q[0])
    qc.cx(q[0], q[1])
    
    # Measure first qubit in specified basis
    qc.p(-phi, q[0])    # -φ
    qc.ry(-theta, q[0]) # -θ
    qc.measure(q[0], c)
    
    # Apply corrections based on measurement
    with qc.if_test((c, 0)):
        qc.x(q[1])
        qc.z(q[1])
    
    # Prepare second qubit for measurement in same basis
    qc.p(-phi, q[1])    # -φ
    qc.ry(-theta, q[1]) # -θ
    qc.measure(q[1], c)
    
    return qc

# 4. Define angle grid
theta_values = np.arange(0, np.pi + np.pi/6, np.pi/6)  # 0 to π in steps of π/6
phi_values = np.arange(0, 2*np.pi + np.pi/6, np.pi/6)  # 0 to 2π in steps of π/6
fidelities = np.zeros((len(theta_values), len(phi_values)))

# 5. Prepare output file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"rsp_results_{timestamp}.txt"
with open(output_filename, 'w') as f:
    f.write("Theta\tPhi\tFidelity\tCounts_0\tCounts_1\n")

# 6. Prepare circuit transpilation
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)

# 7. Configure Sampler
sampler = Sampler(mode=backend)

# 8. Run experiments
for i, theta in enumerate(theta_values):
    for j, phi in enumerate(phi_values):
        print(f"\nRunning RSP protocol for θ={theta:.3f}, φ={phi:.3f}")
        
        # Create circuit for current angles
        qc = create_rsp_circuit(theta, phi)
        
        # Transpile for backend
        isa_circuit = pm.run(qc)
        
        # Run on hardware
        job = sampler.run([isa_circuit], shots=1024)
        print(f"Job submitted. Job ID: {job.job_id()}")
        print("Waiting for results...")
        
        # Get results
        result = job.result()
        counts = result[0].data.c0.get_counts()
        
        # Calculate fidelity
        counts_0 = counts.get('0', 0)
        counts_1 = counts.get('1', 0)
        total_counts = counts_0 + counts_1
        fidelity = counts_0 / total_counts if total_counts > 0 else 0
        fidelities[i, j] = fidelity
        
        # Save results to file
        with open(output_filename, 'a') as f:
            f.write(f"{theta:.4f}\t{phi:.4f}\t{fidelity:.4f}\t{counts_0}\t{counts_1}\n")
        
        print(f"Results for θ={theta:.3f}, φ={phi:.3f}:")
        print(f"Counts: 0={counts_0}, 1={counts_1}")
        print(f"Fidelity: {fidelity:.4f}")
        
        # Add delay between jobs (30 seconds)
        if not (i == len(theta_values)-1 and j == len(phi_values)-1):
            print("Waiting 30 seconds before next job...")
            time.sleep(30)

fig, ax = plt.subplots(figsize=(8, 6))
ax.imshow(fidelities, extent=[0, 2*np.pi, 0, np.pi], origin='lower', aspect='auto', cmap='plasma', vmax=1, vmin=0)
ax.set_xlabel(r'$\phi$', size=20)
ax.set_ylabel(r'$\theta$', size=20)
ax.tick_params(axis='both', labelsize=12)
cbar = fig.colorbar(ax.imshow(fidelities, extent=[0, 2*np.pi, 0, np.pi], origin='lower', aspect='auto', cmap='plasma', vmax=1, vmin=0), ax=ax, orientation='vertical', fraction=0.065, pad=0.12)
cbar.set_label('Fidelidad', size=22)
cbar.ax.tick_params(labelsize=14)
plt.savefig('fidelidad_real.png')
plt.show()

print(f"\nAll results saved to {output_filename}")