# Remote State Preparation (RSP) en Qiskit

Este repositorio contiene la implementación y análisis del protocolo de **Preparación Remota de Estados (RSP)** para un solo qubit, utilizando **Qiskit**, simuladores cuánticos y hardware real de IBM Quantum.

---

## 🧠 Contexto y motivación

El protocolo RSP permite preparar un estado cuántico en un receptor (**Bob**) haciendo uso de entrelazamiento y un único bit clásico. A diferencia de la teleportación, no se requiere un estado desconocido: Alice debe conocer previamente el estado a preparar. Esta variante es especialmente interesante para dispositivos NISQ, donde la reducción de qubits y comunicación clásica representa una clara ventaja.

---

## 🧩 Componentes principales

1. **MATLAB**  
   - `matlab/rsp_fidelity.m`: usa variables simbólicas para calcular la fidelidad teórica:  
     `F(θ,φ) = ½ [cos²θ sin²φ + cos²φ + 1]`.  
   - Genera mapas de calor esperados.

2. **Qiskit (Python)**  
   - `qiskit/rsp.py`: implementación de la función `RSP(theta, phi, phase_correction=False)`  
   - Incluye entanglement, medición en base arbitraria, correcciones condicionales, medidas inversas y cálculo de fidelidad.  
   - Permite activar la compuerta de fase opcional para eliminar errores por conjugado complejo.

3. **Hardware real (IBM Quantum)**  
   - Ejecución en `ibm_sherbrooke` mediante `SamplerV2` y un `PresetPassManager`.  
   - Resultados en grid de θ,φ con paso π/6 y 1024 shots.  
   - Mapas de calor generados y comparados con simulaciones.

---

## 📈 Resultados

- **Simulación ideal:** mapas con fidelidad mínima ~0.5 (zonas de colapso ortogonal).  
- **Con corrección de fase:** fidelidad uniforme = 1.0 sobre la esfera.  
- **Hardware real:** fidelidad entre ~0.5 y 0.8, con máximos cerca de 0.85 y preservación del patrón teórico.

---

## 🛠️ Requisitos e instalación

- **Software**  
  - MATLAB 
  - Python ≥ 3.8, Qiskit ≥ 1.0 

- **Instalación**  
  ```sh
  git clone https://github.com/carlospatinopd/RSP.git
  cd RSP

  # Instala dependencias de Python
  pip install -r requirements.txt

  # Instala Qiskit:
  pip install qiskit qiskit_ibm_runtime

  # (MATLAB se ejecuta directamente desde el IDE)
