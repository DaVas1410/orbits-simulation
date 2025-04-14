#!/bin/bash
# Example script for running orbit simulations using the command-line interface

# Create output directories
mkdir -p output/earth output/mercury output/blackhole output/comparisons

# Set constants
M_SUN=1.989e30  # Mass of the Sun in kg
M_BH=4.3e6      # Sagittarius A* black hole mass in solar masses
AU=1.496e11     # Astronomical Unit in meters

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${BLUE}===== Orbits Simulation Examples =====${NC}"

# Example 1: Basic Earth Orbit Simulation
echo -e "\n${GREEN}Running Earth orbit simulation...${NC}"
python -m orbits.orbits \
    -n "earth_orbit" \
    -M $M_SUN \
    -a 1 \
    -e 0.01671 \
    -N 1000 \
    -s \
    -r \
    -m rk3 \
    -A \
    -o output/earth

echo "Earth simulation completed. Check output/earth directory for results."

# Example 2: Mercury (Classical vs Relativistic)
echo -e "\n${GREEN}Running Mercury orbit comparison (classical vs relativistic)...${NC}"

# Classical Mercury orbit
python -m orbits.orbits \
    -n "mercury_classical" \
    -M $M_SUN \
    -a 0.387 \
    -e 0.206 \
    -N 2000 \
    -m scipy \
    -o output/mercury

# Relativistic Mercury orbit
python -m orbits.orbits \
    -n "mercury_relativistic" \
    -M $M_SUN \
    -a 0.387 \
    -e 0.206 \
    -N 2000 \
    -r \
    -m scipy \
    -o output/mercury

# Create a side-by-side animation of both
echo "Mercury simulations completed."
echo "Note: The relativistic orbit will show precession over time."

# Example 3: High Eccentricity Orbit
echo -e "\n${GREEN}Running high-eccentricity orbit simulation...${NC}"
python -m orbits.orbits \
    -n "high_eccentricity" \
    -M $M_SUN \
    -a 2.5 \
    -e 0.7 \
    -N 1500 \
    -r \
    -m rk3 \
    -A \
    -o output/comparisons

echo "High eccentricity simulation completed."

# Example 4: Black Hole System
echo -e "\n${GREEN}Running black hole orbit simulation...${NC}"
python -m orbits.orbits \
    -n "blackhole_orbit" \
    -M $(echo "$M_BH * $M_SUN" | bc -l) \
    -a 0.1 \
    -e 0.5 \
    -N 2000 \
    -r \
    -m scipy \
    -A \
    -s \
    -o output/blackhole

echo "Black hole simulation completed. Watch for effects near the Schwarzschild radius."

# Example 5: Batch simulation comparing different integration methods
echo -e "\n${GREEN}Running integration method comparison batch...${NC}"

METHODS=("trapz" "rk3" "scipy")
for method in "${METHODS[@]}"; do
    echo "Testing $method integration..."
    python -m orbits.orbits \
        -n "comparison_$method" \
        -M $M_SUN \
        -a 1 \
        -e 0.1 \
        -N 500 \
        -r \
        -m $method \
        -o output/comparisons
done

echo -e "\n${BLUE}All simulations completed!${NC}"
echo "Results are saved in the respective output directories."
echo "You can visualize the CSV files or view the generated animations."

# Optional: Create a simple analysis report
echo -e "\n${GREEN}Creating summary of all simulations...${NC}"
echo "Simulation Summary" > simulation_summary.txt
echo "==================" >> simulation_summary.txt
echo "Date: $(date)" >> simulation_summary.txt
echo "" >> simulation_summary.txt

echo "Earth Orbit: standard conditions" >> simulation_summary.txt
echo "Mercury Orbit: shows relativistic precession" >> simulation_summary.txt
echo "High Eccentricity: demonstrates Kepler's laws" >> simulation_summary.txt
echo "Black Hole: extreme relativistic effects" >> simulation_summary.txt
echo "Method Comparison: accuracy vs performance tradeoffs" >> simulation_summary.txt

echo "Summary created in simulation_summary.txt"