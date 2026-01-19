# Closed_BCI
This is a closed BCI system that incorporates the NEURON library; this project includes modeling, FEM, biophysics, machine learning, and much more.

This repository contains a Phase 1 neuroengineering simulation framework built
using the NEURON Python API.

The project implements:
- Multicompartment ball-and-stick neuron models
- Ring-network connectivity using event-based synapses
- MPI-parallel simulation using NEURON ParallelContext
- Extracellular electrical stimulation via e_extracellular
- Reproducible spike and voltage recordings

## Features
- Runs in serial or with MPI (`mpiexec`)
- Deterministic 3D neuron placement using Random123
- Script-based experiments (no notebooks)
- Raster plots, voltage traces, and synaptic current recording

## Example
```bash
mpiexec -n 4 python extracell_stim_ring.py
