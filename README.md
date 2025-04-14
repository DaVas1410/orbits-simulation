# Orbits Simulation Module - README

This README provides comprehensive documentation for the `orbits.py` module, which simulates and visualizes two-body orbital dynamics in both classical Newtonian and relativistic contexts.

## Overview

The Orbits module allows you to:
- Simulate planetary or satellite orbits around a central mass (like a star or black hole)
- Choose between classical Newtonian or relativistic equations of motion
- Utilize different numerical integration methods
- Visualize orbits through static plots and animations
- Export simulation data for further analysis

## Installation

### Prerequisites
- Python 3.x
- NumPy
- SciPy
- Matplotlib
- Imagemagick (for GIF animations)

Install required packages:
```bash
pip install numpy scipy matplotlib
```

For animations, install Imagemagick according to your operating system.

## Module Structure

The module contains two main classes:
1. `Orbits`: Handles orbit initialization, integration, and simulation
2. `OrbitAnimation`: Creates animations from simulation data

## Usage Examples

### Jupyter Notebook Example

```python
# Orbits Simulation Module - Example Notebook

import os
import numpy as np
import matplotlib.pyplot as plt
from orbits import Orbits, OrbitAnimation

# 1. Create an orbit instance with a descriptive name
mercury_orbit = Orbits("mercury_perihelion")

# 2. Initialize the orbit parameters
#    - Sun's mass in kg
#    - Mercury's semi-major axis in meters (0.387 AU)
#    - Mercury's eccentricity (0.206)
#    - Number of simulation steps
mercury_orbit.initialize_orbit(
    M=1.989e30,  # Sun's mass in kg
    a=0.387 * 1.496e11,  # Mercury's semi-major axis (0.387 AU converted to meters)
    e=0.206,  # Mercury's eccentricity
    N=1000,  # Number of steps
    save=True  # Save the initialization plot
)

# 3. Define the simulation time span
orbital_period = 2 * np.pi * np.sqrt((0.387 * 1.496e11)**3 / (6.67430e-11 * 1.989e30))
t_span = (0, orbital_period)
t_eval = np.linspace(0, orbital_period, 1000)

# 4. Run simulation with classical mechanics
classical_trajectory = mercury_orbit.run_simulation(
    mercury_orbit.classical_slope,
    "scipy",  # Using SciPy's RK45 integrator
    t_span,
    t_eval,
    output_folder="mercury_classical"
)

# 5. Run simulation with relativistic corrections
relativistic_trajectory = mercury_orbit.run_simulation(
    mercury_orbit.relativistic_slope,
    "scipy",  # Using SciPy's RK45 integrator
    t_span,
    t_eval,
    output_folder="mercury_relativistic"
)

# 6. Compare the trajectories
plt.figure(figsize=(10, 8))
plt.plot(0, 0, 'ko', markersize=10, label="Sun")
plt.plot(classical_trajectory[:, 0], classical_trajectory[:, 1], 'b-', label="Classical")
plt.plot(relativistic_trajectory[:, 0], relativistic_trajectory[:, 1], 'r-', label="Relativistic")
plt.grid(True)
plt.xlabel("x (AU)")
plt.ylabel("y (AU)")
plt.title("Mercury's Orbit: Classical vs Relativistic")
plt.legend()
plt.axis('equal')
plt.savefig("mercury_comparison.png")
plt.show()

# 7. Create an animation from the relativistic simulation
animation = OrbitAnimation("mercury_relativistic/mercury_perihelion_orbit_history.csv", 
                          output_gif="mercury_orbit.gif")
animation.create_animation()

# 8. Example: Black hole orbit
#    This demonstrates a more extreme case where relativistic effects are significant
black_hole_orbit = Orbits("black_hole_test")

# Initialize orbit around a 4.3 million solar mass black hole (like Sgr A*)
black_hole_orbit.initialize_orbit(
    M=4.3e6 * 1.989e30,  # 4.3 million solar masses in kg
    a=1.0 * 1.496e11,    # 1 AU semi-major axis
    e=0.8,               # High eccentricity to see strong relativistic effects
    N=2000,              # More steps for better resolution
    save=True
)

# Calculate orbital period and run for longer to see precession
bh_orbital_period = 2 * np.pi * np.sqrt((1.0 * 1.496e11)**3 / (6.67430e-11 * 4.3e6 * 1.989e30))
bh_t_span = (0, 5 * bh_orbital_period)  # Simulate for 5 orbital periods
bh_t_eval = np.linspace(0, 5 * bh_orbital_period, 2000)

# Run both classical and relativistic simulations
bh_classical = black_hole_orbit.run_simulation(
    black_hole_orbit.classical_slope,
    "scipy",
    bh_t_span,
    bh_t_eval,
    output_folder="bh_classical"
)

bh_relativistic = black_hole_orbit.run_simulation(
    black_hole_orbit.relativistic_slope,
    "scipy",
    bh_t_span,
    bh_t_eval,
    output_folder="bh_relativistic"
)

# Visualize the relativistic precession
plt.figure(figsize=(12, 10))
plt.plot(0, 0, 'ko', markersize=12, label="Black Hole")

# Plot the Schwarzschild radius
G = 6.67430e-11
c = 3e8
M = 4.3e6 * 1.989e30
schwarzschild_radius = 2 * G * M / c**2 / 1.496e11  # Convert to AU
circle = plt.Circle((0, 0), schwarzschild_radius, color='black', fill=True, alpha=0.3)
plt.gca().add_artist(circle)

plt.plot(bh_classical[:, 0], bh_classical[:, 1], 'b-', label="Classical", alpha=0.7)
plt.plot(bh_relativistic[:, 0], bh_relativistic[:, 1], 'r-', label="Relativistic", alpha=0.7)
plt.grid(True)
plt.xlabel("x (AU)")
plt.ylabel("y (AU)")
plt.title("Orbit Around a Supermassive Black Hole: Classical vs Relativistic")
plt.legend()
plt.axis('equal')
plt.savefig("black_hole_precession.png")
plt.show()

# Create an animation of the relativistic black hole orbit
bh_animation = OrbitAnimation("bh_relativistic/black_hole_test_orbit_history.csv", 
                             output_gif="black_hole_orbit.gif")
bh_animation.create_animation()
```

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

## License

This module is provided for educational and research purposes.