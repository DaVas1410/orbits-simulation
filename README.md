# Orbits Simulation Module

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)


This README provides comprehensive documentation for the `orbits.py` module, which simulates and visualizes two-body orbital dynamics in both classical Newtonian and relativistic contexts.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Module Structure](#module-structure)
- [Project Structure](#project-structure)
- [Usage Examples](#usage-examples)
  - [Jupyter Notebook Example](#jupyter-notebook-example)
  - [Command Line Example](#command-line-example)
- [Orbits Class](#orbits-class)
- [OrbitAnimation Class](#orbitanimation-class)
- [Command Line Interface](#command-line-interface)
- [Scientific Background](#scientific-background)
- [Examples and Use Cases](#examples-and-use-cases)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Limitations](#limitations)
- [Future Development](#future-development)
- [Contributing](#contributing)

## Overview

The Orbits module allows you to:
- Simulate planetary or satellite orbits around a central mass (like a star or black hole)
- Choose between classical Newtonian or relativistic equations of motion
- Utilize different numerical integration methods
- Visualize orbits through static plots and animations
- Export simulation data for further analysis

## Installation

### Prerequisites
- Python 3.7+
- NumPy
- SciPy
- Matplotlib
- Pillow (for GIF animations)
- Pandas (for data handling)

### Using pip

Install required packages:
```bash
pip install numpy scipy matplotlib pillow pandas
```

Alternatively, use the provided requirements file:
```bash
pip install -r requirements.txt
```

### Note on Animation Support

The animation functionality uses Matplotlib's animation module with Pillow for GIF creation. No external dependencies like Imagemagick are required.

## Quick Start

Here's a simple example to get you started with a basic Earth orbit simulation:

```python
from orbits import Orbits

# Create Earth orbit simulation
earth = Orbits("earth_orbit")

# Initialize orbit parameters (Sun-Earth system)
earth.initialize_orbit(
    M=1.989e30,  # Sun's mass (kg)
    a=1.496e11,  # 1 AU in meters
    e=0.0167,    # Earth's eccentricity
    N=1000       # Number of steps
)

# Calculate orbital period
orbital_period = 2 * np.pi * np.sqrt((1.496e11)**3 / (6.67430e-11 * 1.989e30))

# Run simulation and get trajectory
trajectory = earth.run_simulation(
    earth.classical_slope,
    "scipy",
    (0, orbital_period),
    np.linspace(0, orbital_period, 1000)
)

# Create animation
from orbits import OrbitAnimation
animation = OrbitAnimation("output/earth_orbit_history.csv", output_gif="earth_orbit.gif")
animation.create_animation()
```

## Module Structure

The module contains two main classes:
1. `Orbits`: Handles orbit initialization, integration, and simulation
2. `OrbitAnimation`: Creates animations from simulation data

## Project Structure

The repository is organized as follows:

```
orbits-simulation/
├── README.md               # This documentation file
├── requirements.txt        # Project dependencies
├── setup.py                # Installation configuration
├── orbits/                 # Main package directory
│   ├── orbits.py           # Core module with simulation logic
│   └── __init__.py         # Package initialization
├── tests/                  # Unit tests for the module
│   ├── test_orbits.py      # Test cases for Orbits and OrbitAnimation classes
│   └── __init__.py         # Test package initialization
├── Examples/               # Example usage and demonstrations
│   ├── Analysis/           # Computational Physics analysis examples
│   │   ├── output/         # Output files from analysis
│   │   └── analysis.ipynb  # Jupyter Notebook for analysis
│   ├── bash_examples/      # Bash scripts for running simulations
│   │   ├── earth_orbit.sh  # Example script for Earth orbit simulation
│   │   └── README.md       # Documentation for bash examples
│   ├── notebook_examples/  # Jupyter Notebook examples
│   │   ├── output/         # Output files from notebooks
│   │   └── notebook_example.ipynb  # Example notebook for simulations
```
     

### Key Files:

- **orbits.py**: Contains the main `Orbits` and `OrbitAnimation` classes for simulation and visualization
- **setup.py**: Defines package metadata and dependencies for pip installation
- **requirements.txt**: Lists all project dependencies with version specifications

To install the package for development:
```bash
git clone https://github.com/davas1410/orbits-simulation.git
cd orbits-simulation
pip install -e .
```

## Usage Examples

### Command Line Example

```bash
# Earth orbit around the Sun (Classical mechanics)
python orbits.py --name "earth_orbit" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method scipy --save

# Mercury with relativistic effects (to observe perihelion precession)
python orbits.py --name "mercury_relativistic" --mass 1.989e30 --axis 0.387 --eccentricity 0.206 --steps 1000 --method scipy --relativ --anim --save

# Extreme orbit around a black hole
python orbits.py --name "black_hole_orbit" --mass 4.0e6 --axis 0.1 --eccentricity 0.9 --steps 2000 --method scipy --relativ --anim --save

# Compare different integration methods (Classical mechanics)
python orbits.py --name "earth_trapz" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method trapz --save
python orbits.py --name "earth_rk3" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method rk3 --save
python orbits.py --name "earth_scipy" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method scipy --save
```


### Orbits Class

#### Initialization
```python
orbit = Orbits(name)
```
- `name`: String identifier for the simulation

#### Methods

##### `initialize_orbit(M, a, e, N, save=False, G=6.67430e-11)`
Sets up the initial conditions for the orbit.

Parameters:
- `M`: Mass of the central body (kg)
- `a`: Semi-major axis (meters)
- `e`: Eccentricity (dimensionless, 0 ≤ e < 1)
- `N`: Number of simulation steps
- `save`: Whether to save the initialization plot (boolean)
- `G`: Gravitational constant (default: 6.67430e-11 m³/kg·s²)

##### `classical_slope(t, y, M, G=6.67430e-11)`
Implements the Newtonian equations of motion.

Parameters:
- `t`: Time variable (not used in time-independent gravity)
- `y`: State vector [x, y, vx, vy]
- `M`: Mass of the central body
- `G`: Gravitational constant

Returns:
- Array of derivatives [dx/dt, dy/dt, dvx/dt, dvy/dt]

##### `relativistic_slope(t, y, M, G=6.67430e-11, c=3e8)`
Implements relativistic corrections to orbital motion.

Parameters:
- `t`: Time variable
- `y`: State vector [x, y, vx, vy]
- `M`: Mass of the central body
- `G`: Gravitational constant
- `c`: Speed of light (m/s)

Returns:
- Array of derivatives with relativistic corrections

##### `trapezoidal_euler(f, y0, t)`
Trapezoidal Euler integration method.

##### `runge_kutta_3(f, y0, t)`
Third-order Runge-Kutta integration method.

##### `scipy_integrator(f, y0, t_span, t_eval)`
Wrapper for SciPy's `solve_ivp` function, using RK45 method.

##### `run_simulation(slope_function, integration_method, t_span, t_eval, output_folder="output")`
Runs the orbital simulation with specified parameters.

Parameters:
- `slope_function`: Function defining the equations of motion
- `integration_method`: One of "trapz", "rk3", or "scipy"
- `t_span`: Tuple (t_start, t_end) defining simulation time span
- `t_eval`: Array of times at which to evaluate the solution
- `output_folder`: Directory to save output files

Returns:
- Array of trajectory points [x, y, vx, vy] at each time step

### OrbitAnimation Class

#### Initialization
```python
animation = OrbitAnimation(csv_file, output_gif="orbit_animation.gif")
```
- `csv_file`: Path to the CSV file with orbit data
- `output_gif`: Filename for the output animation

#### Methods

##### `create_animation()`
Creates a GIF animation from the orbit data.

## Command Line Interface

The module can be run from the command line with the following arguments:

```bash
python orbits.py [-h] -n NAME -M MASS -a AXIS -e ECCENTRICITY -N STEPS [-s] [-r] -m {trapz,rk3,scipy} [-A]
```

### Required Arguments
- `-n, --name`: Name of the orbit simulation
- `-M, --mass`: Mass of the central body in kg
- `-a, --axis`: Semi-major axis in AU
- `-e, --eccentricity`: Eccentricity of the orbit
- `-N, --steps`: Number of steps for the simulation
- `-m, --method`: Integration method (trapz, rk3, or scipy)

### Optional Arguments
- `-s, --save`: Save the initial orbit map as an image
- `-r, --relativ`: Use relativistic equations of motion
- `-A, --anim`: Generate a GIF animation of the orbit
- `-h, --help`: Show help message

## Scientific Background

### Classical Orbital Mechanics
The module implements Newton's law of universal gravitation:
```
F = G * M * m / r²
```

### Relativistic Corrections
The module implements a simplified form of relativistic corrections to account for orbital precession as predicted by General Relativity. The relativistic factor is incorporated through the angular momentum term:
```
relativistic_factor = 1 + (3 * l²) / (r² * c²)
```

This approximation captures the perihelion precession effect seen in Mercury's orbit and is more pronounced for objects orbiting close to massive bodies like black holes.

### Schwarzschild Radius
For black holes, the module visualizes the Schwarzschild radius:
```
Rs = 2 * G * M / c²
```

## Examples and Use Cases

1. **Mercury's Perihelion Precession**: Observe the famous relativistic effect that helped confirm Einstein's General Relativity
2. **Black Hole Orbits**: Visualize extreme relativistic effects near black holes
3. **Comparing Integration Methods**: Test the accuracy and performance of different numerical integrators
4. **Educational Demonstrations**: Create animations for teaching orbital mechanics

## Output Files

All simulations generate:
1. CSV file with orbit data (time, position, velocity)
2. Initialization plot showing the starting conditions
3. Optional animation GIF

## Troubleshooting

### Common Issues
- **AnimationError**: Ensure Imagemagick is installed for GIF creation
- **Numerical Instability**: For highly eccentric orbits, increase the number of steps or use the "scipy" method
- **Memory Issues**: For very long simulations, reduce the number of steps or split into multiple runs

## Advanced Usage

### Custom Integration Methods
You can implement your own integration methods by following the pattern of the existing ones (trapezoidal_euler, runge_kutta_3).

### Extended Simulations
For multi-body simulations or more complex physics, you can extend the `slope_function` to include additional forces or interactions.

## Limitations

1. The relativistic model is a simplified approximation and not a full implementation of General Relativity
2. The simulation is limited to 2D orbital motion
3. For extremely close approaches to black holes, more sophisticated models would be required

## Future Development

Potential enhancements:
- 3D orbital simulations
- N-body capability for multiple gravitational interactions
- Full General Relativistic treatment using geodesic equations
- Improved visualization options

## Contributing

Contributions to this project are welcome! Here's how you can contribute:

1. **Report bugs and issues:** Open an issue in the repository
2. **Suggest new features:** Create a feature request
3. **Submit pull requests:** Implement new features or fix bugs

When contributing code, please ensure:
- Code follows PEP 8 style guide
- New features include appropriate tests
- Documentation is updated to reflect changes

