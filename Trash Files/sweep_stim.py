import matplotlib.pyplot as plt
import numpy as np
from neuron import n
from neuron.units import ms, mV
from extracell_stim_ring import extracell_BallAndStick, extracell_cell, extracell_Ring

n.nrnmpi_init()
pc = n.ParallelContext()
pc.gid_clear()

ring=extracell_Ring(10)

soma_v = dend_v = syn_i = None

sweep_amplitude = [0, -10, -20, -30, 0, 10, 30]

sweep_amplitude_time = [0]
for i in range(1, len(sweep_amplitude)):
    sweep_amplitude_time.append(int(0.5*i + 9))

stim_time = len(sweep_amplitude)

if pc.gid_exists(0):
    tvec = n.Vector(sweep_amplitude_time)

    # Extracellular potential waveform (mV)
    # Simple pulse: 0 mV -> +5 mV for ~1 ms -> 0 mV
    vvec = n.Vector(sweep_amplitude)

    cell0 = pc.gid2cell(0)
    cell0._stim_tvec = tvec
    cell0._stim_vvec = vvec
    vvec.play(cell0.soma(0.5)._ref_e_extracellular, tvec, 1)
    
    # SETUP RECORDINGS for GID 0 specifically
    soma_v = n.Vector().record(pc.gid2cell(0).soma(0.5)._ref_v)
    dend_v = n.Vector().record(pc.gid2cell(0).dend(0.5)._ref_v)
    syn_i = n.Vector().record(pc.gid2cell(0).syn._ref_i)

t = n.Vector().record(n._ref_t)

# Parallel Run
pc.set_maxstep(10 * ms)
n.finitialize(-65 * mV)
pc.psolve(20 * stim_time * ms)

# --- Gathering Data & Plotting ---

# 1. Gather spikes from all nodes
local_spikes = {cell._gid: list(cell.spike_times) for cell in ring.cells}
all_spikes_list = pc.py_alltoall([local_spikes] + [None] * (pc.nhost() - 1))

# 2. Only Rank 0 handles the plotting
if pc.id() == 0:
    if pc.id() == 0:
        if soma_v is None:
            raise RuntimeError("Rank 0 does not own gid 0, so it can't plot its traces.")
    # Combine spike data
    all_spikes_combined = {}
    for p_data in all_spikes_list:
        all_spikes_combined.update(p_data)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

    # Plot 1: Voltage Trace (Cell 0)
    # Since Rank 0 owns GID 0 in round-robin, soma_v is available here
    ax1.plot(t, soma_v, color="black", label='soma(0.5)')
    ax1.plot(t, dend_v, color='red', label="dend(0.5)")
    ax1.set_title("Voltage Trace (Cell 0)")
    ax1.set_ylabel("mV")
    ax1.legend()

    # Plot 2: Raster Plot (All Cells)
    for gid, times in all_spikes_combined.items():
        ax2.vlines(times, gid + 0.5, gid + 1.5, color="blue")
    ax2.set_title("Network Raster Plot")
    ax2.set_ylabel("Cell GID")

    # Plot 3: Synaptic Current (Cell 0)
    ax3.plot(t, syn_i, color='green')
    ax3.set_title("Synaptic Input Current (Cell 0)")
    ax3.set_xlabel("Time (ms)")
    ax3.set_ylabel("nA")

    plt.tight_layout()
    plt.show()

pc.barrier()
pc.done()