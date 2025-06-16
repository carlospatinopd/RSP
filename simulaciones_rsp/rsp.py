from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, execute
import numpy as np
import matplotlib.pyplot as plt

def preparar_estado_bell(qc, q):
    """Prepara el estado de Bell |0⟩|1⟩-|1⟩|0⟩ en los qubits q[0] y q[1]"""
    qc.x(q[0])
    qc.x(q[1])
    qc.h(q[0])
    qc.cx(q[0], q[1])
    qc.barrier()

def medir_en_base_arbitraria(qc, q, c, theta, phi):
    """Mide q[0] en una base arbitraria"""
    qc.rz(theta, q[0])
    qc.p(phi, q[0])
    qc.measure(q[0], c[0])
    qc.barrier()

def correcciones_en_bob(qc, q, c, theta, phi):
    """Aplica correcciones en Bob y mide en la base arbitraria para comparacion"""
    qc.z(q[1]).c_if(c, 0)
    qc.x(q[1]).c_if(c, 0)
    qc.barrier()
    qc.rz(-theta, q[1])
    qc.p(-phi, q[1])
    qc.measure(q[1], c[0])

def simular_circuito(qc, shots=1024):
    """Ejecuta el circuito y devuelve los resultados de conteo"""
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(qc, simulator, shots=shots).result()
    return result.get_counts(qc)

def calcular_fidelidad(counts, shots=1024):
    """Calcula la fidelidad como la probabilidad de obtener |0⟩"""
    return counts.get('0', 0) / shots

def RSP(theta, phi, shots=1024):
    """Ejecucion del protocolo RSP"""
    q = QuantumRegister(2, 'q')
    c = ClassicalRegister(1, 'c')
    qc = QuantumCircuit(q, c)
    preparar_estado_bell(qc, q)
    medir_en_base_arbitraria(qc, q, c, theta, phi)
    correcciones_en_bob(qc, q, c, theta, phi)
    counts = simular_circuito(qc, shots)
    fidelity = calcular_fidelidad(counts, shots)
    return fidelity

# Angulos para describir la esfera de Bloch
phi = np.arange(0, 2*np.pi, np.pi/96)
theta = np.arange(0, np.pi, np.pi/96)

# Ejecutar el protocolo RSP sobre toda la esfera de Bloch y calcula la fidelidad
fidelities = np.zeros((len(theta), len(phi)))
for ip in range(len(phi)):
    for it in range(len(theta)):
        fidelities[it, ip] = RSP(theta[it], phi[ip])
        print(f"theta={theta[it]:.2f}, phi={phi[ip]:.2f}, P(0)={fidelities[it, ip]:.4f}")

# Resultados
plt.imshow(fidelities, extent=[0, 2*np.pi, 0, np.pi], origin='lower', aspect='auto', cmap='viridis', vmax=1, vmin=0)
plt.colorbar(label='Fidelidad')
plt.xlabel(r'$\phi$')
plt.ylabel(r'$\theta$')
plt.title('Fidelidad de RSP')
plt.savefig('fidelidad.png')