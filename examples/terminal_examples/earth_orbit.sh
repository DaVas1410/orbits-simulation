#!/bin/bash

# Example script to run Earth orbit simulation

# Earth orbit around the Sun (Classical mechanics)
python -m orbits.orbits --name "earth_orbit" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method scipy --save

# Earth orbit with relativistic effects
python -m orbits.orbits --name "earth_relativistic" --mass 1.989e30 --axis 1.0 --eccentricity 0.0167 --steps 1000 --method scipy --relativ --anim --save

echo "Earth orbit simulations completed. Check output folder for results."