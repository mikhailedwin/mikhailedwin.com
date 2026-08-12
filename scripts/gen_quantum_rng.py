"""
Generates 200 quantum-random floats [0,1] using a simulated 8-qubit circuit.
Qiskit Aer runs the simulation locally — no cloud account, no cost.
Each qubit is put in superposition via Hadamard before measurement.
Output: quantum_rng.json consumed by the site for glitch timing seeds.
"""
import json
from datetime import datetime, timezone

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

SHOTS = 200
QUBITS = 8

sim = AerSimulator()

qc = QuantumCircuit(QUBITS)
for i in range(QUBITS):
    qc.h(i)
qc.measure_all()

job = sim.run(transpile(qc, sim), shots=SHOTS, memory=True)
memory = job.result().get_memory()

vals = [round(int(b.replace(' ', ''), 2) / (2 ** QUBITS - 1), 4) for b in memory]

out = {
    'values': vals,
    'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'shots': SHOTS,
    'qubits': QUBITS,
    'circuit': f'H^{QUBITS} measure_all'
}

with open('quantum_rng.json', 'w') as f:
    json.dump(out, f)

print(f'[quantum_rng] generated {len(vals)} values from {QUBITS}-qubit circuit')
