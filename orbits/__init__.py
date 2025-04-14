# Import main classes to make them available directly from the package
from orbits.orbits import Orbits, OrbitAnimation

# Define version
__version__ = "0.1.0"

# Define what gets imported with "from orbits import *"
__all__ = ["Orbits", "OrbitAnimation"]

# You can add package-level documentation here
"""
Orbits Simulation Package

This package provides tools for simulating and visualizing orbital dynamics
in both classical Newtonian and relativistic contexts.

Main classes:
- Orbits: Handles orbit initialization, integration, and simulation
- OrbitAnimation: Creates animations from simulation data
"""
