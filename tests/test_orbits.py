import pytest
import numpy as np
from orbits import Orbits, G, C, AU

# Constants for testing
M_SUN = 1.989e30  # Solar mass in kg
EARTH_ORBITAL_PERIOD = 365.25 * 24 * 3600  # Earth's orbital period in seconds

# Fixture for basic Earth-like orbit
@pytest.fixture
def earth_orbit():
    orbit = Orbits("test_earth")
    orbit.initialize_orbit(M=M_SUN, a=AU, e=0.0167, N=1000)
    return orbit

# Test a) Correct initialization of orbit parameters
def test_initialize_orbit_correct_inputs():
    """Test that orbit parameters are correctly processed and stored."""
    orbit = Orbits("test_orbit")
    orbit.initialize_orbit(M=M_SUN, a=AU, e=0.0167, N=1000)
    
    # Check initial conditions at perihelion
    assert orbit.orbit_data["x0"] == 0
    assert orbit.orbit_data["y0"] == pytest.approx(AU * (1 - 0.0167))
    assert orbit.orbit_data["vx0"] < 0  # Initial velocity should be negative
    assert orbit.orbit_data["vy0"] == 0
    
    # Check mass and orbital parameters stored correctly
    assert orbit.orbit_data["M"] == M_SUN
    assert orbit.orbit_data["a"] == AU
    assert orbit.orbit_data["e"] == 0.0167
    
    # Verify Schwarzschild radius calculation
    assert orbit.schwarzschild_radius == pytest.approx(2 * G * M_SUN / (C**2))

# Test b) Handling of invalid integration method
def test_invalid_integration_method(earth_orbit):
    """Test that an invalid integration method raises a ValueError."""
    t_span = (0, EARTH_ORBITAL_PERIOD)
    t_eval = np.linspace(0, EARTH_ORBITAL_PERIOD, 100)

    # Try to run simulation with invalid method
    with pytest.raises(ValueError, match="Unknown integration method"):
        earth_orbit.run_simulation(
            earth_orbit.classical_slope, 
            "invalid_method",  # This should trigger the error
            t_span, 
            t_eval
        )

# Test c) Different inputs lead to different outputs
def test_different_inputs_different_outputs():
    """Test that different orbit parameters produce different simulation results."""
    # Create two orbits with different semi-major axes
    orbit1 = Orbits("orbit1")
    orbit2 = Orbits("orbit2")
    
    a1 = 1.0 * AU  # Earth-like orbit
    a2 = 2.0 * AU  # Mars-like orbit
    
    orbit1.initialize_orbit(M=M_SUN, a=a1, e=0.0167, N=1000)
    orbit2.initialize_orbit(M=M_SUN, a=a2, e=0.0167, N=1000)

    # Set up simulation parameters
    t_span = (0, EARTH_ORBITAL_PERIOD)
    t_eval = np.linspace(0, EARTH_ORBITAL_PERIOD, 100)

    # Run simulations
    result1 = orbit1.run_simulation(
        orbit1.classical_slope, 
        "scipy", 
        t_span, 
        t_eval
    )
    
    result2 = orbit2.run_simulation(
        orbit2.classical_slope, 
        "scipy", 
        t_span, 
        t_eval
    )

    # Ensure the outputs are different
    assert not np.allclose(result1, result2)
    
    # More specifically, the orbits should have different average radii
    r1 = np.mean(np.sqrt(result1[:, 0]**2 + result1[:, 1]**2))
    r2 = np.mean(np.sqrt(result2[:, 0]**2 + result2[:, 1]**2))
    assert r2 > r1  # The orbit with larger semi-major axis should have larger radius