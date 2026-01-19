"""
from neuron import h
import matplotlib.pyplot as plt

# Load NEURON standard run system
h.load_file("stdrun.hoc")

# Create a single compartment neuron
soma = h.Section(name='soma')
soma.L = soma.diam = 12.6157  # ~500 µm² surface area
soma.insert('hh')            # Hodgkin-Huxley channels

# Inject current
stim = h.IClamp(soma(0.5))
stim.delay = 100   # ms
stim.dur = 500     # ms
stim.amp = 0.1    # nA

# Record time and voltage
t = h.Vector().record(h._ref_t)
v = h.Vector().record(soma(0.5)._ref_v)

# Run simulation
h.tstop = 700
h.run()

# Plot results
plt.figure(figsize=(8,4))
plt.plot(t, v)
plt.xlabel("Time (ms)")
plt.ylabel("Membrane potential (mV)")
plt.title("Single Neuron Response to Current Injection")
plt.tight_layout()
plt.show()

"""

from neuron import n
from neuron.units import ms, mV
import matplotlib.pyplot as plt
from bokeh.io import output_notebook

h.load_file('stdrun.hoc')

soma = h.Section(name='Soma')
soma.L = soma.diam = 10.0
soma.insert('hh')

stimu = h.IClamp(soma(0.5))
stimu.delay = 10
stimu.dur = 400
stimu.amp = 0.1

t = h.Vector().record(h._ref_t)
v = h.Vector().record(soma(0.5)._ref_v)

h.tstop = 1000
h.run()

plt.figure(figsize=(8,4))
plt.plot(t,v)
plt.xlabel('Time')
plt.ylabel('Voltage')
plt.title('Single Neuron after Stimulation')
plt.show()
