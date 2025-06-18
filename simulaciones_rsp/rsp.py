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
    qc.p(-phi, q[0])
    qc.ry(-theta, q[0])
    qc.measure(q[0], c[0])
    qc.barrier()

def correcciones_en_bob(qc, q, c, theta, phi, phi2):
    """Aplica correcciones en Bob y mide en la base arbitraria para comparacion"""
    qc.x(q[1]).c_if(c, 0)
    qc.z(q[1]).c_if(c, 0)
    qc.p(2*phi2, q[1]).c_if(c, 0) # solo aplica para caso no RSP
    qc.barrier()
    qc.p(-phi, q[1])
    qc.ry(-theta, q[1])
    qc.measure(q[1], c[0])

def simular_circuito(qc, shots=1024):
    """Ejecuta el circuito y devuelve los resultados de conteo"""
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(qc, simulator, shots=shots).result()
    return result.get_counts(qc)

def calcular_fidelidad(counts, shots=1024):
    """Calcula la fidelidad como la probabilidad de obtener |0⟩"""
    return counts.get('0', 0) / shots

def RSP(theta, phi, phi2, shots=1024):
    """Ejecucion del protocolo RSP"""
    q = QuantumRegister(2, 'q')
    c = ClassicalRegister(1, 'c')
    qc = QuantumCircuit(q, c)
    preparar_estado_bell(qc, q)
    medir_en_base_arbitraria(qc, q, c, theta, phi)
    correcciones_en_bob(qc, q, c, theta, phi, phi2)
    counts = simular_circuito(qc, shots)
    fidelity = calcular_fidelidad(counts, shots)
    return fidelity

def fidelity_map(theta, phi, phi2):
    '''Ejecutar el protocolo RSP sobre toda la esfera de Bloch y calcula la fidelidades'''
    fidelities = np.zeros((len(theta), len(phi)))
    for ip in range(len(phi)):
        for it in range(len(theta)):
            fidelities[it, ip] = RSP(theta[it], phi[ip], phi2[ip])
            print(f"theta={theta[it]:.2f}, phi={phi[ip]:.2f}, P(0)={fidelities[it, ip]:.4f}")
    return fidelities

# Angulos para describir la esfera de Bloch
phi = np.arange(0, 2*np.pi, np.pi/128)
theta = np.arange(0, np.pi, np.pi/128)
zero = np.zeros(len(phi))

# Fidelidad RSP
fidelities1 = fidelity_map(theta, phi, zero)
# Fidelidad con correccion completa (no RSP)
fidelities2 = fidelity_map(theta, phi, phi)

# Resultados
fig, axs = plt.subplots(1, 2, figsize=(15, 6))
axs[0].imshow(fidelities1, extent=[0, 2*np.pi, 0, np.pi], origin='lower', aspect='auto', cmap='plasma', vmax=1, vmin=0)
axs[0].set_xlabel(r'$\phi$', size=20)
axs[0].set_ylabel(r'$\theta$', size=20)
axs[0].tick_params(axis='both', labelsize=12)
im2 = axs[1].imshow(fidelities2, extent=[0, 2*np.pi, 0, np.pi], origin='lower', aspect='auto', cmap='plasma', vmax=1, vmin=0)
axs[1].set_xlabel(r'$\phi$', size=20)
axs[1].set_ylabel(r'$\theta$', size=20)
axs[1].tick_params(axis='both', labelsize=12)
cbar = fig.colorbar(im2, ax=axs, orientation='vertical', fraction=0.0265, pad=0.04)
cbar.set_label('Fidelidad', size=22)
cbar.ax.tick_params(labelsize=14)
# plt.savefig('RSP/simulaciones_rsp/fidelidades.png')
plt.show()