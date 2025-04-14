import os
import numpy as np
import argparse
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Orbits:

    def __init__(self, name):
        self.name = name
        self.orbit_data = []

    def initialize_orbit(self, M, a, e, N, save=False, G=6.67430e-11):
        x0 = 0
        y0 = a * (1 - e)
        vx0 = -np.sqrt(G * M / a * (1 + e) / (1 - e))
        vy0 = 0

        self.orbit_data = {
            "x0": x0,
            "y0": y0,
            "vx0": vx0,
            "vy0": vy0,
            "M": M,
            "a": a,
            "e": e,
            "N": N
        }

        c = 3e8
        schwarzschild_radius = 2 * G * M / c**2

        fig, ax = plt.subplots()
        ax.plot(0, 0, 'ko', label="Black Hole")
        circle = plt.Circle((0, 0), schwarzschild_radius / 1.496e11, color='red', fill=False, linestyle='--', label="Schwarzschild Radius")
        ax.add_artist(circle)
        ax.plot(x0 / 1.496e11, y0 / 1.496e11, 'ro', label="Initial Position")
        ax.set_aspect('equal', adjustable='datalim')
        ax.legend()
        plt.xlabel("x (AU)")
        plt.ylabel("y (AU)")
        plt.title("Orbit Initialization with Schwarzschild Radius")
        plt.grid()

        if save:
            plt.savefig("orbit_initialization.png")
        plt.show()

    def classical_slope(self, t, y, M, G=6.67430e-11):
        x, y, vx, vy = y
        r = np.sqrt(x**2 + y**2)
        ax = -G * M * x / r**3
        ay = -G * M * y / r**3
        return np.array([vx, vy, ax, ay])
    
    def relativistic_slope(self, t, y, M, G=6.67430e-11, c=3e8):
        x, y, vx, vy = y
        r = np.sqrt(x**2 + y**2)
        
        # Avoid division by zero
        if r < 1e-10:
            return np.array([vx, vy, 0, 0])
            
        # Calculate specific angular momentum (per unit mass)
        # l = r × v (cross product of position and velocity vectors)
        l = x * vy - y * vx
            
        # The relativistic correction term with angular momentum
        # This accounts for orbital precession
        relativistic_factor = 1 + (3 * l**2) / (r**2 * c**2)
            
        # Calculate accelerations with relativistic correction
        ax = -G * M * x / r**3 * relativistic_factor
        ay = -G * M * y / r**3 * relativistic_factor
            
        return np.array([vx, vy, ax, ay])

    def trapezoidal_euler(self, f, y0, t):
        y = np.zeros((len(t), len(y0)))
        y[0] = y0
        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            y_pred = y[i - 1] + dt * f(t[i - 1], y[i - 1])
            y[i] = y[i - 1] + (dt / 2) * (f(t[i - 1], y[i - 1]) + f(t[i], y_pred))
        return y

    def runge_kutta_3(self, f, y0, t):
        y = np.zeros((len(t), len(y0)))
        y[0] = y0
        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            k1 = f(t[i - 1], y[i - 1])
            k2 = f(t[i - 1] + dt / 2, y[i - 1] + dt * k1 / 2)
            k3 = f(t[i - 1] + dt, y[i - 1] - dt * k1 + 2 * dt * k2)
            y[i] = y[i - 1] + (dt / 6) * (k1 + 4 * k2 + k3)
        return y

    def scipy_integrator(self, f, y0, t_span, t_eval):
        sol = solve_ivp(f, t_span, y0, t_eval=t_eval, method='RK45')
        return sol.y.T

    def run_simulation(self, slope_function, integration_method, t_span, t_eval, output_folder="output"):
        os.makedirs(output_folder, exist_ok=True)

        y0 = [self.orbit_data["x0"], self.orbit_data["y0"], self.orbit_data["vx0"], self.orbit_data["vy0"]]
        M = self.orbit_data["M"]

        def f(t, y):
            return slope_function(t, y, M)

        if integration_method == "trapz":
            y = self.trapezoidal_euler(f, y0, t_eval)
        elif integration_method == "rk3":
            y = self.runge_kutta_3(f, y0, t_eval)
        elif integration_method == "scipy":
            y = self.scipy_integrator(f, y0, t_span, t_eval)
        else:
            raise ValueError(f"Unknown integration method: {integration_method}")

        AU = 1.496e11
        y[:, 0] /= AU
        y[:, 1] /= AU

        output_file = os.path.join(output_folder, f"{self.name}_orbit_history.csv")
        np.savetxt(output_file, np.column_stack((t_eval, y)), delimiter=",", 
                   header="time,x,y,vx,vy", comments="")
        print(f"Simulation results saved to {output_file}")

        return y

class OrbitAnimation:
    def __init__(self, csv_file, output_gif="orbit_animation.gif"):
        self.csv_file = csv_file
        self.output_gif = output_gif

    def create_animation(self):
        data = np.loadtxt(self.csv_file, delimiter=",", skiprows=1)
        time, x, y, vx, vy = data.T

        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.grid()
        ax.set_xlabel("x (AU)")
        ax.set_ylabel("y (AU)")
        ax.set_title("Orbital Motion Animation")

        ax.plot(0, 0, 'ko', label="Black Hole")
        planet, = ax.plot([], [], 'ro', label="Planet")

        def update(frame):
            planet.set_data(x[frame], y[frame])
            return planet,

        ani = FuncAnimation(fig, update, frames=len(time), interval=50, blit=True)
        ani.save(self.output_gif, writer="imagemagick")
        print(f"Animation saved as {self.output_gif}")

if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Simulate a two-body orbit on a 2D Cartesian grid.")
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the orbit simulation.")
    parser.add_argument("-M", "--mass", type=float, required=True, help="Mass of the central body (e.g., black hole) in kg.")
    parser.add_argument("-a", "--axis", type=float, required=True, help="Semi-major axis of the orbit in AU.")
    parser.add_argument("-e", "--eccentricity", type=float, required=True, help="Eccentricity of the orbit.")
    parser.add_argument("-N", "--steps", type=int, required=True, help="Number of steps for the simulation.")
    parser.add_argument("-s", "--save", action="store_true", help="Save the initial orbit map as an image.")
    parser.add_argument("-r", "--relativ", action="store_true", help="Use relativistic equations of motion.")
    parser.add_argument("-m", "--method", type=str, required=True, choices=["trapz", "rk3", "scipy"],
                        help="Integration method to use (trapz, rk3, scipy).")
    parser.add_argument("-A", "--anim", action="store_true", help="Generate a GIF animation of the orbit.")

    # Parse arguments
    args = parser.parse_args()

    # Convert semi-major axis from AU to meters
    AU = 1.496e11  # 1 Astronomical Unit in meters
    a_meters = args.axis * AU

    # Initialize and run the orbit simulation
    orbit = Orbits(args.name)
    orbit.initialize_orbit(M=args.mass, a=a_meters, e=args.eccentricity, N=args.steps, save=args.save)

    # Select slope function
    slope_function = orbit.relativistic_slope if args.relativ else orbit.classical_slope

    # Time span and evaluation points
    orbital_period = 2 * np.pi * np.sqrt((a_meters**3) / (6.67430e-11 * args.mass))  # Kepler's 3rd law
    t_span = (0, orbital_period)
    t_eval = np.linspace(0, orbital_period, args.steps)

    # Run the simulation
    orbit.run_simulation(slope_function, args.method, t_span, t_eval)

    # Generate animation if requested
    if args.anim:
        csv_file = os.path.join("output", f"{args.name}_orbit_history.csv")
        animation = OrbitAnimation(csv_file)
        animation.create_animation()