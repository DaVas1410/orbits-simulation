"""
Orbits Simulation Package
=========================

A comprehensive package for simulating and visualizing orbital dynamics
under both classical Newtonian and relativistic gravitational physics.

Features:
- Classical and relativistic orbital dynamics simulation
- Multiple numerical integration methods (RK3, Trapezoidal, SciPy integrators)
- Automatic detection of near-Schwarzschild radius conditions
- Data export to CSV format for further analysis
- Static and animated visualization of orbital trajectories

Main Classes:
    Orbits: Main simulation class for orbital dynamics
    OrbitAnimation: Visualization class for creating animated GIFs of orbital trajectories

Physical Constants:
    G: Gravitational constant (6.67430e-11 m^3 kg^-1 s^-2)
    C: Speed of light in vacuum (3e8 m/s)
    AU: Astronomical Unit (1.496e11 m)

Example:
    >>> from orbits import Orbits, G, AU
    >>> # Set up Earth-like orbit around a solar-mass object
    >>> orbit = Orbits("earth_orbit")
    >>> orbit.initialize_orbit(M=1.989e30, a=1*AU, e=0.01671, N=1000)
"""

# Import main classes and constants to make them available directly from the package
from orbits.orbits import Orbits, OrbitAnimation
from orbits.orbits import G, C, AU

# Define version
__version__ = "0.2.0"

# Define what gets imported with "from orbits import *"
__all__ = [
    "Orbits", 
    "OrbitAnimation",
    "G",  # Gravitational constant
    "C",  # Speed of light
    "AU"  # Astronomical Unit
]

# Package configuration defaults (can be modified by users)
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_INTEGRATION_METHOD = "rk3"
DEFAULT_SCHWARZSCHILD_SAFETY = 2.0

def cite():
    """
    Print citation information for the package.
    
    Returns:
        str: Citation text for the Orbits simulation package
    """
    citation = """
    To cite the Orbits Simulation Package in your work, please use:
    
    DAVAS (2025). Orbits Simulation: A Python package for orbital dynamics. 
    GitHub: https://github.com/davas1410/orbits-simulation
    """
    print(citation)
    return citation