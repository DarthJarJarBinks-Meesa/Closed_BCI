import matplotlib.pyplot as plt
import numpy as np
from neuron import n
from neuron.units import ms, mV

n.nrnmpi_init()
pc = n.ParallelContext()
pc.gid_clear()

class extracell_cell:
    def __init__(self, gid, x, y, z, theta):
        self._gid = gid
        self.x = x
        self.y = y
        self.z = z
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        
        # Each cell records its own spikes locally
        self.spike_times = n.Vector()
        self._spike_detector = n.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self._spike_detector.record(self.spike_times)

        n.define_shape()
        self._rotate_z(theta)
        self._set_position(x, y, z)

    def _set_position(self, x, y, z):
        for sec in self.all:
            for i in range(sec.n3d()):
                sec.pt3dchange(
                    i,
                    x - self.x + sec.x3d(i),
                    y - self.y + sec.y3d(i),
                    z - self.z + sec.z3d(i),
                    sec.diam3d(i),
                )
        self.x, self.y, self.z = x, y, z

    def _rotate_z(self, theta):
        for sec in self.all:
            for i in range(sec.n3d()):
                x, y = sec.x3d(i), sec.y3d(i)
                c, s = np.cos(theta), np.sin(theta)
                sec.pt3dchange(i, x * c - y * s, x * s + y * c, sec.z3d(i), sec.diam3d(i))

class extracell_BallAndStick(extracell_cell):
    def _setup_morphology(self):
        self.soma = n.Section(name="soma", cell=self)
        self.dend = n.Section(name="dend", cell=self)
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 12.6157
        self.dend.L = 200
        self.dend.diam = 1

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100
            sec.cm = 1
        self.soma.insert('hh')
        self.dend.insert('pas')
        for sec in self.all:
            sec.insert('extracellular')
        self.syn = n.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms

class extracell_Ring:
    def __init__(self, N=7, r=50):
        self._N = N
        self.cells = []
        self._ncs = []
        self.gidlist = list(range(pc.id(), self._N, pc.nhost()))
        
        for gid in self.gidlist:
            pc.set_gid2node(gid, pc.id())
            theta = gid * 2 * np.pi / self._N
            z_range = n.Random()
            z_range.Random123(gid, 0, 0)      # reproducible across runs
            z = z_range.uniform(-50, 50)    # microns
            cell = extracell_BallAndStick(gid, np.cos(theta) * r, np.sin(theta) * r, z, theta)
            self.cells.append(cell)
            pc.cell(gid, cell._spike_detector)

        self._connect_cells()

    def _connect_cells(self):
        for target_cell in self.cells:
            source_gid = (target_cell._gid - 1 + self._N) % self._N
            nc = pc.gid_connect(source_gid, target_cell.syn)
            nc.weight[0] = 0.05
            nc.delay = 5 * ms
            self._ncs.append(nc)

ring = extracell_Ring(N=7)

soma_v = dend_v = syn_i = None

if pc.gid_exists(0):
    tvec = n.Vector([0, 9, 9.1, 10, 10.1, 25])

    # Extracellular potential waveform (mV)
    # Simple pulse: 0 mV -> +5 mV for ~1 ms -> 0 mV
    vvec = n.Vector([0,0,0,0, 30, 0])

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
pc.psolve(100 * ms)

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