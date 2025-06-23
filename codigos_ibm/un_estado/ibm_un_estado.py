from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import numpy as np

# input de angulos a utilizar
theta = float(input("Ingrese el ángulo theta en radianes [0, pi]: "))
phi = float(input("Ingrese el ángulo phi en radianes [0, 2pi]: "))

# iniciar IBM Quantum service
service = QiskitRuntimeService()
backend = service.least_busy(
    operational=True,
    simulator=False,
    min_num_qubits=2
)
print(f"Using backend: {backend.name}")

def preparar_estado_bell(qc, q):
    """Prepara el estado de Bell |0⟩|1⟩-|1⟩|0⟩ en los qubits q[0] y q[1]"""
    qc.x(q[0])
    qc.x(q[1])
    qc.h(q[0])
    qc.cx(q[0], q[1])
    qc.barrier()

def medir_en_base_arbitraria(qc, q, c, theta, phi):
    """Mide q[0] en una base arbitraria"""
    qc.p(-phi, q[0])
    qc.ry(-theta, q[0])
    qc.measure(q[0], c)
    qc.barrier()

def correcciones_en_bob(qc, q, c, theta, phi):
    """Aplica correcciones en Bob y mide en la base arbitraria para comparacion"""
    with qc.if_test((c, 0)):
        qc.x(q[1])
        qc.z(q[1])
        # qc.p(2*phi, q[1])
    qc.barrier()
    qc.p(-phi, q[1])
    qc.ry(-theta, q[1])
    qc.measure(q[1], c)

def simular_circuito(qc, backend):
    """Ejecuta el circuito y devuelve los resultados de conteo"""
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=1024)
    print(f"\nJob submitted to {backend.name}. Job ID: {job.job_id()}")
    print("Waiting for results... (Check status at https://quantum.ibm.com/jobs)")
    result = job.result()
    return result[0].data.c0.get_counts()

def RSP(theta, phi):
    """Ejecucion del protocolo RSP"""
    c = ClassicalRegister(1, 'c0')
    q = QuantumRegister(2, 'q')
    qc = QuantumCircuit(q, c)
    preparar_estado_bell(qc, q)
    medir_en_base_arbitraria(qc, q, c, theta, phi)
    correcciones_en_bob(qc, q , c, theta, phi)
    counts = simular_circuito(qc, backend)
    counts_0 = counts.get('0', 0)
    counts_1 = counts.get('1', 0)
    total_counts = counts_0 + counts_1
    fidelity = counts_0 / total_counts if total_counts > 0 else 0
    print(f"\nResults for θ=π/2, φ=π/2:")
    print(f"Counts: {counts}")
    print(f"Fidelity: {fidelity:.4f} (probability of |0⟩)")
    print(f"Standard error: ±{np.sqrt(fidelity*(1-fidelity)/total_counts):.4f}")

RSP(theta, phi)

# qc = create_rsp_circuit()
# print("Circuito RSP:")
# print(qc.draw())
