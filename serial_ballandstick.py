import matplotlib.pyplot as plt
import numpy as np
from neuron import h as n  # Importing as n per your request
from neuron.units import ms, mV

# Load standard run libraries
n.load_file("stdrun.hoc")

class Cell:
    def __init__(self, gid, x, y, z, theta):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        
        # Position and rotation
        self.x = self.y = self.z = 0
        n.define_shape()
        self._rotate_z(theta)
        self._set_position(x, y, z)
        
        # Part 3: Each cell manages its own spike recording
        self.spike_times = n.Vector()
        self._spike_detector = n.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
        self._spike_detector.record(self.spike_times)

    def __repr__(self):
        return f"{self.name}[{self._gid}]"

    def _set_position(self, x, y, z):
        for sec in self.all:
            for i in range(sec.n3d()):
                sec.pt3dchange(i, x - self.x + sec.x3d(i), y - self.y + sec.y3d(i), 
                               z - self.z + sec.z3d(i), sec.diam3d(i))
        self.x, self.y, self.z = x, y, z

    def _rotate_z(self, theta):
        for sec in self.all:
            for i in range(sec.n3d()):
                x, y = sec.x3d(i), sec.y3d(i)
                c, s = np.cos(theta), np.sin(theta)
                sec.pt3dchange(i, x * c - y * s, x * s + y * c, sec.z3d(i), sec.diam3d(i))

class BallAndStick(Cell):
    name = "BallAndStick"

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

        self.syn = n.ExpSyn(self.dend(0.5))
        self.syn.tau = 2 * ms

class Ring:
    """A network class to manage cell creation and connectivity (Part 3)."""
    def __init__(self, N=7, radius=50, weight=0.05, delay=5):
        self._N = N
        self._radius = radius
        self._weight = weight
        self._delay = delay
        self.cells = []
        self.connections = []
        self._create_cells()
        self._connect_cells()

    def _create_cells(self):
        for i in range(self._N):
            theta = i * 2 * np.pi / self._N
            self.cells.append(BallAndStick(i, np.cos(theta) * self._radius, 
                                           np.sin(theta) * self._radius, 0, theta))

    def _connect_cells(self):
        for i in range(self._N):
            source = self.cells[i]
            target = self.cells[(i + 1) % self._N]
            # Connect soma of source to synapse of target
            nc = n.NetCon(source.soma(0.5)._ref_v, target.syn, sec=source.soma)
            nc.weight[0] = self._weight
            nc.delay = self._delay
            self.connections.append(nc)

# --- Simulation Execution ---

# 1. Instantiate the network
ring = Ring(N=7)

# 2. Stimulate Cell 0 to trigger the ring activity
stim = n.NetStim()
stim.number = 1
stim.start = 9
nc_stim = n.NetCon(stim, ring.cells[0].syn)
nc_stim.delay = 1 * ms
nc_stim.weight[0] = 0.04

# 3. Setup global recording
soma_v = n.Vector().record(ring.cells[0].soma(0.5)._ref_v)
dend_v = n.Vector().record(ring.cells[0].dend(0.5)._ref_v)
t = n.Vector().record(n._ref_t)
syn_a = n.Vector().record(ring.cells[0].syn._ref_i)

# 4. Run
n.finitialize(-65 * mV)
n.continuerun(100 * ms)

# 5. Plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8))

# Voltage trace for Cell 0
ax1.plot(t, soma_v, color="black")
ax1.set_title("Voltage Trace (Cell 0)")
ax1.set_ylabel("mV")

# Raster Plot for all cells in the ring
for i, cell in enumerate(ring.cells):
    ax2.vlines(list(cell.spike_times), i + 0.5, i + 1.5, color="blue")
ax2.set_title("Network Raster Plot")
ax2.set_xlabel("Time (ms)")
ax2.set_ylabel("Cell ID")

ax3.plot(t, syn_a, color='green')
ax3.set_title("Synpatic Input")
ax3.set_xlabel("Time (ms)")
ax3.set_ylabel("Current (nA)")

plt.tight_layout()
plt.show()

