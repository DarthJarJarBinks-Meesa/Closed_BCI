
from neuron import n
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from neuron.units import ms, mV, µm
from neuron import gui

n.load_file('stdrun.hoc')

class Cell:
    def __init__(self, gid, x, y, z, theta):
        self._gid = gid
        self._setup_morphology()
        self.all = self.soma.wholetree()
        self._setup_biophysics()
        self.x = self.y = self.z = 0 
        n.define_shape()
        self._rotate_z(theta)  
        self._set_position(x, y, z)  
    def __repr__(self):
        return "{}[{}]".format(self.name, self._gid)
    
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
                x = sec.x3d(i)
                y = sec.y3d(i)
                c = n.cos(theta)
                s = n.sin(theta)
                xprime = x * c - y * s
                yprime = x * s + y * c
                sec.pt3dchange(i, xprime, yprime, sec.z3d(i), sec.diam3d(i))

class BallAndStick(Cell):
    name = "BallAndStick"
    
    def _setup_morphology(self):
        self.soma = n.Section(name='soma', cell = self)
        self.dend = n.Section(name='dend', cell = self)
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 10
        self.dend.L = 200
        self.dend.diam = 1

    def _setup_biophysics(self):
        for sec in self.all:
           self.Ra = 100
           sec.cm = 1 
           
        self.soma.insert(n.hh)
        for seg in self.soma:
            seg.hh.gnabar = 0.12  
            seg.hh.gkbar = 0.036  
            seg.hh.gl = 0.0003  
            seg.hh.el = -54.3 * mV  
        self.dend.insert(n.pas)  
        for seg in self.dend:  
            seg.pas.g = 0.001  
            seg.pas.e = -65 * mV  

        #self._set_3d_geometry()
"""
    def _set_3d_geometry(self):
        # Soma as a short cylinder centered at origin
        self.soma.pt3dclear()
        self.soma.pt3dadd(0, 0, 0, self.soma.diam)
        self.soma.pt3dadd(self.soma.L, 0, 0, self.soma.diam)

        # Dend extends from soma end along +x
        self.dend.pt3dclear()
        self.dend.pt3dadd(self.soma.L, 0, 0, self.dend.diam)
        self.dend.pt3dadd(self.soma.L + self.dend.L, 0, 0, self.dend.diam)
"""


"""
def plot_morphology_3d(ax=None, lw_scale=0.15):

    #Plot morphology using NEURON's 3D point data (x3d/y3d/z3d/diam3d).
    #lw_scale controls how thick lines appear relative to diam3d.
  
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

    for sec in n.allsec():
        npts = int(sec.n3d())
        if npts <= 0:
            # Some sections may not have 3D points
            continue

        xs = [sec.x3d(i) for i in range(npts)]
        ys = [sec.y3d(i) for i in range(npts)]
        zs = [sec.z3d(i) for i in range(npts)]
        ds = [sec.diam3d(i) for i in range(npts)]  # diameters in um-ish units

        # Draw as connected segments so linewidth can vary with diameter
        for i in range(npts - 1):
            lw = max(0.5, ds[i] * lw_scale)
            ax.plot(xs[i:i+2], ys[i:i+2], zs[i:i+2], linewidth=lw)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("NEURON morphology (matplotlib)")

    try:
        all_xyz = []
        for sec in n.allsec():
            npts = int(sec.n3d())
            for i in range(npts):
                all_xyz.append((sec.x3d(i), sec.y3d(i), sec.z3d(i)))
        if all_xyz:
            all_xyz = np.array(all_xyz)
            mins = all_xyz.min(axis=0)
            maxs = all_xyz.max(axis=0)
            ranges = maxs - mins
            max_range = ranges.max() if ranges.max() > 0 else 1.0
            centers = (maxs + mins) / 2
            ax.set_xlim(centers[0] - max_range/2, centers[0] + max_range/2)
            ax.set_ylim(centers[1] - max_range/2, centers[1] + max_range/2)
            ax.set_zlim(centers[2] - max_range/2, centers[2] + max_range/2)
    except Exception:
        pass

    return ax
"""
def create_n_BallAndStick(num, r):
    cells = []
    for i in range(num):
        theta = i * 2 * n.PI / num
        cells.append(BallAndStick(i, n.cos(theta)*r, n.sin(theta)*r, 0, ))
    return cells

my_cells = create_n_BallAndStick(10,50)

stim = n.NetStim()
syn_ = n.ExpSyn(my_cells[0].dend(0.5))
syn_.tau = 2 * ms
stim.number = 1
stim.start = 9
ncstim = n.NetCon(stim, syn_)
ncstim.delay = 1 * ms
ncstim.weight[0] = 0.04 


print("Reversal potential = {} mV".format(syn_.e))

recording_of_cells = my_cells[0]
soma_v = n.Vector().record(recording_of_cells.soma(0.5)._ref_v)
dend_v = n.Vector().record(recording_of_cells.dend(0.5)._ref_v)
t = n.Vector().record(n._ref_t)

n.finitialize(-65 * mV)
n.continuerun(25 * ms)

plt.plot(t, soma_v, label="soma(0.5)")
plt.plot(t, dend_v, label="dend(0.5)")
plt.legend()
plt.show()

#ax = plot_morphology_3d(lw_scale=0.2)
#plt.show()
