Day 1 - 1/13/26 - single_neuron.py
First project!
Created the neuron conda environment and used "conda install c- conda-forge neuron matplotlib numpy scipy" to import everything
Ran into trouble with neuron not installing so i just used pip install instead
then i opened the file in vs code, had trouble running then i realized that it was using the wrong interpreter so i switched
ran the program

Here's what i learned (TL/DR)
- Neuron is a library built on an holder language Hoc
    - h is the control panel to do whatever you want
- created a neuron and inserted Hodgkin huxley ion channels ('hh)
- then gave it stimulation and plotted in matplotlib
    - parameters: stim = 
        h.IClamp(soma(0.5))
        stim.delay = 100   # ms
        stim.dur = 500     # ms
        stim.amp = 0.1    # nA

Code Breakdown 
- first from neuron import h as well as import matplotlib.pyplot as plt
- then pull up the standard neuron running system
    h.load_file('stdrun.hoc')
- then create your soma (which is a secion object) and its dimensions and insert hh channels
    soma = h.Section(name='soma)
    soma_L = soma_diam = 10
    soma.insert('hh')
- then create your stimulation with an intracellular clamp in the middle of the soma and set parameter
    stim = h.IClamp(soma(0.5))
    stim.delay = x
    stim.run = y
    stim.amp = z
- then tell it to record the two vectors (time and voltage)
    t = h.Vector(h._ref_t)
    v = h.Vector(soma(0.5)._ref_v)
- then tell it how long to record for and to run
    h.tstop = x
    h.run()
- then just plot your results

Day 2 - 1/15/26 - ball_stick.py + close_loop_bci.py
today i learned about how classes and objects work
classes eventually have a preset script so when you create the object, it has a couple things attached to it 
you can assign the things through:
- here i added a GID (a global ID/name tag) and created a soma and dendrite for every neuron
class BallAndStick:
    def __init__(self, gid):
        self._gid = gid
        self.soma = n.Section(name='soma', cell = 'self')
        self.dend = n.Section(name='dend', cell = 'self)
        self.dend.connect(self.soma)
        self.soma.l = self.soma.diam = 10
        self.dend.l = 100
        self.dend.diam = 1
- you can then create an identifier for a cleaner look
    def __repr__(self):
        return BallAndStick
to assign, just write the object name = classname 

- also learned that to initialize the electrode recording, use 
n.finitialize(-65 * mV) sets starting mV to -65
n.continuerun(40 * ms) sets how long the recording lasts

you also should import units to make it cleaner
from neuron.units import ms, mV, µm

for close_loop_bci, i nailed down the objectives i want to hit (should be relatively easy)
    Implement a single spiking neuron model
    Extend to a small neural population
    Define a virtual electrode that records population activity
    Apply static extracellular stimulation and characterize response
    Apply time-varying (open-loop) stimulation
    Extract interpretable neural state variables from recordings
    Define a control objective on those state variables
    Implement autonomous feedback that adjusts stimulation based on inferred state
    Demonstrate improved regulation vs open-loop stimulation
    Test robustness under noise and perturbations
