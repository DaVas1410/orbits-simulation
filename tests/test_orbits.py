import pytest
import numpy as np
from orbits import Orbits

# Test a) Correct input values from the user
def test_initialize_orbit_correct_inputs():
    orbit = Orbits("test_orbit")
    M = 1.989e30  # Mass of the Sun in kg
    a = 1.496e11  # 1 AU in meters
    e = 0.0167  # Eccentricity of Earth's orbit
    N = 1000  # Number of steps
    orbit.initialize_orbit(M, a, e, N)
    assert orbit.orbit_data["x0"] == 0
    assert orbit.orbit_data["y0"] == pytest.approx(a * (1 - e))
    assert orbit.orbit_data["vx0"] < 0  # Initial velocity should be negative
    assert orbit.orbit_data["vy0"] == 0

# Test b) Handling of invalid input methods
def test_invalid_integration_method():
    orbit = Orbits("test_orbit")
    M = 1.989e30  # Mass of the Sun in kg
    a = 1.496e11  # 1 AU in meters
    e = 0.0167  # Eccentricity of Earth's orbit
    N = 1000  # Number of steps
    orbit.initialize_orbit(M, a, e, N)
    t_span = (0, 31536000)  # 1 year in seconds
    t_eval = np.linspace(0, 31536000, N)

    with pytest.raises(ValueError, match="Unknown integration method"):
        orbit.run_simulation(orbit.classical_slope, "invalid_method", t_span, t_eval)

# Test c) Whether different inputs lead to different outputs
def test_different_inputs_different_outputs():
    orbit1 = Orbits("orbit1")
    orbit2 = Orbits("orbit2")
    M = 1.989e30  # Mass of the Sun in kg
    a1 = 1.496e11  # 1 AU in meters
    a2 = 2.0 * 1.496e11  # 2 AU in meters
    e = 0.0167  # Eccentricity of Earth's orbit
    N = 1000  # Number of steps

    orbit1.initialize_orbit(M, a1, e, N)
    orbit2.initialize_orbit(M, a2, e, N)

    t_span = (0, 31536000)  # 1 year in seconds
    t_eval = np.linspace(0, 31536000, N)

    result1 = orbit1.run_simulation(orbit1.classical_slope, "scipy", t_span, t_eval)
    result2 = orbit2.run_simulation(orbit2.classical_slope, "scipy", t_span, t_eval)

    # Ensure the outputs are different for different semi-major axes
    assert not np.array_equal(result1, result2)