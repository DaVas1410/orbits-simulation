"""
Orbits Simulation Module
========================

A comprehensive module for simulating and visualizing orbital dynamics under both classical
and relativistic gravitational physics. This module provides tools for orbit initialization,
trajectory calculation, convergence analysis, and visualization.

Features:
- Classical and relativistic orbital dynamics simulation
- Multiple numerical integration methods with configurable parameters
- Automatic detection of near-Schwarzschild radius conditions
- Data export to CSV format for further analysis
- Static and animated visualization of orbital trajectories
- Command-line interface for quick simulations

Constants:
    G (float): Gravitational constant (6.67430e-11 m^3 kg^-1 s^-2)
    C (float): Speed of light in vacuum (3e8 m/s)
    AU (float): Astronomical Unit (1.496e11 m)

Classes:
    Orbits: Main simulation class for orbital dynamics
    OrbitAnimation: Visualization class for creating animated GIFs of orbital trajectories

Example:
    >>> from orbits import Orbits
    >>> # Set up Earth-like orbit around a massive black hole
    >>> orbit = Orbits("earth_orbit")
    >>> orbit.initialize_orbit(M=5e36, a=1.496e11, e=0.01671, N=1000)
    >>> # Run relativistic simulation using RK3 method
    >>> t_span = (0, 2*86400)  # Two days in seconds
    >>> t_eval = np.linspace(0, 2*86400, 1000)
    >>> trajectory = orbit.run_simulation(
    ...     slope_function=orbit.relativistic_slope,
    ...     integration_method="rk3",
    ...     t_span=t_span,
    ...     t_eval=t_eval
    ... )

Author: DAVAS
Date: 2025
"""

import os
import numpy as np
import argparse
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from typing import Callable, List, Optional, Tuple, Union
import pandas as pd
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from PIL import Image

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
C = 3e8          # Speed of light in vacuum (m/s)
AU = 1.496e11    # 1 Astronomical Unit (m)


class Orbits:
    """
    Main class for simulating orbital dynamics with various physical models and integration methods.
    
    This class handles the initialization, simulation, and analysis of orbits around a central mass.
    It supports both classical Newtonian mechanics and relativistic corrections for more accurate
    modeling near massive objects like black holes.
    
    Attributes:
        name (str): Identifier for the simulation instance
        orbit_data (dict): Dictionary storing orbital parameters and initial conditions
        schwarzschild_radius (float): Schwarzschild radius of the central mass (m)
    
    Methods:
        initialize_orbit: Set up orbital parameters and initial conditions
        classical_slope: Calculate derivatives using classical Newtonian gravity
        relativistic_slope: Calculate derivatives with relativistic corrections
        run_simulation: Execute the orbital simulation with specified parameters
        trapezoidal_euler: Integration using the trapezoidal method
        runge_kutta_3: Integration using 3rd-order Runge-Kutta method
        scipy_integrator: Integration using SciPy's ODE solvers
        schwarzschild_stop_condition: Check if orbit is too close to the Schwarzschild radius
    """

    def __init__(self, name: str):
        """
        Initialize an Orbits simulation instance.
        
        Args:
            name (str): Identifier for this simulation instance, used for output filenames
        """
        self.name = name
        self.orbit_data = {}
        self.schwarzschild_radius = None

    def initialize_orbit(self, M: float, a: float, e: float, N: int, save: bool = False) -> None:
        """
        Initialize orbital parameters and calculate initial conditions.
        
        This method sets up the initial conditions for an orbit with given parameters.
        It calculates the initial position and velocity for a body at perihelion
        (closest approach to the central mass), and also determines the Schwarzschild
        radius of the central mass.
        
        Args:
            M (float): Mass of central body (kg)
            a (float): Semi-major axis of the orbit (m)
            e (float): Eccentricity of the orbit (0 ≤ e < 1)
            N (int): Number of simulation steps
            save (bool, optional): Whether to save the initialization plot to file. Defaults to False.
            
        Notes:
            - The initial position is set at perihelion (closest approach)
            - Initial velocity is perpendicular to the position vector
            - A visualization of the initial configuration is displayed and optionally saved
        """
        # Initial conditions at perihelion
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

        # Calculate Schwarzschild radius
        self.schwarzschild_radius = 2 * G * M / C**2
        
        # Visualization of initial configuration
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.plot(0, 0, 'ko', label="Black Hole")
        circle = plt.Circle((0, 0), self.schwarzschild_radius / AU, color='red', 
                          fill=False, linestyle='--', label="Schwarzschild Radius")
        ax.add_artist(circle)
        ax.plot(x0 / AU, y0 / AU, 'ro', label="Initial Position")
        ax.set_aspect('equal', adjustable='datalim')
        ax.legend()
        plt.xlabel("x (AU)")
        plt.ylabel("y (AU)")
        plt.title("Orbit Initialization with Schwarzschild Radius")
        plt.grid()

        if save:
            plt.savefig(f"{self.name}_orbit_initialization.png")
        plt.show()

    def classical_slope(self, t: float, y: np.ndarray, M: float) -> np.ndarray:
        """
        Calculate the derivatives for classical (Newtonian) orbital mechanics.
        
        Implements the differential equations for motion under an inverse-square 
        gravitational field following Newton's law of universal gravitation.
        
        Args:
            t (float): Current time (not used, but required for ODE solver interface)
            y (np.ndarray): Current state vector [x, y, vx, vy]
            M (float): Mass of the central body (kg)
            
        Returns:
            np.ndarray: Derivatives [dx/dt, dy/dt, dvx/dt, dvy/dt]
            
        Notes:
            This function calculates acceleration as a = -GM*r/|r|^3
        """
        x, y, vx, vy = y
        r = np.sqrt(x**2 + y**2)
        
        # Avoid division by zero
        if r < 1e-10:
            return np.array([vx, vy, 0, 0])
            
        ax = -G * M * x / r**3
        ay = -G * M * y / r**3
        return np.array([vx, vy, ax, ay])
    
    def relativistic_slope(self, t: float, y: np.ndarray, M: float) -> np.ndarray:
        """
        Calculate the derivatives for relativistic orbital mechanics.
        
        Implements the differential equations for motion with first-order 
        relativistic corrections to Newtonian gravity, accounting for effects
        predicted by General Relativity.
        
        Args:
            t (float): Current time (not used, but required for ODE solver interface)
            y (np.ndarray): Current state vector [x, y, vx, vy]
            M (float): Mass of the central body (kg)
            
        Returns:
            np.ndarray: Derivatives [dx/dt, dy/dt, dvx/dt, dvy/dt]
            
        Notes:
            This function adds a relativistic correction factor to the
            classical acceleration formula: a = -GM*r/|r|^3 * (1 + 3L²/(r²c²))
            where L is the specific angular momentum.
        """
        x, y, vx, vy = y
        r = np.sqrt(x**2 + y**2)
        
        # Avoid division by zero
        if r < 1e-10:
            return np.array([vx, vy, 0, 0])
            
        # Calculate specific angular momentum (per unit mass)
        l = x * vy - y * vx
            
        # The relativistic correction term with angular momentum
        relativistic_factor = 1 + (3 * l**2) / (r**2 * C**2)
            
        # Calculate accelerations with relativistic correction
        ax = -G * M * x / r**3 * relativistic_factor
        ay = -G * M * y / r**3 * relativistic_factor
            
        return np.array([vx, vy, ax, ay])

    def schwarzschild_stop_condition(self, y: np.ndarray, safety_factor: float = 1.5) -> bool:
        """
        Check if the particle is too close to the Schwarzschild radius.
        
        This condition prevents the simulation from entering non-physical regimes
        where the orbit approaches the event horizon of a black hole.
        
        Args:
            y (np.ndarray): Current state vector [x, y, vx, vy]
            safety_factor (float, optional): Multiple of Schwarzschild radius to use as safety boundary.
                                           Defaults to 1.5.
            
        Returns:
            bool: True if the simulation should stop, False otherwise
            
        Notes:
            When the condition triggers, warning messages are printed with details
            about the proximity to the Schwarzschild radius.
        """
        if self.schwarzschild_radius is None:
            return False
        
        x, y, _, _ = y
        r = np.sqrt(x**2 + y**2)
        
        if r < safety_factor * self.schwarzschild_radius:
            print(f"WARNING: Orbit approaching Schwarzschild radius.")
            print(f"Distance: {r/AU:.6e} AU, Schwarzschild radius: {self.schwarzschild_radius/AU:.6e} AU")
            print(f"Stopping simulation to avoid non-physical results.")
            return True
            
        return False

    def trapezoidal_euler(self, f: Callable, y0: np.ndarray, t: np.ndarray, 
                        stop_condition: Optional[Callable] = None) -> np.ndarray:
        """
        Integrate using the trapezoidal (modified Euler) method.
        
        This second-order integration method uses a predictor-corrector approach:
        1. Predict using forward Euler (first-order)
        2. Correct using the average of slopes at initial and predicted points
        
        Args:
            f (Callable): Function to integrate, returns derivatives
            y0 (np.ndarray): Initial state vector
            t (np.ndarray): Time points for evaluation
            stop_condition (Callable, optional): Function that returns True to stop integration.
                                              Defaults to None.
            
        Returns:
            np.ndarray: Solution at each time point, shape (len(t), len(y0))
            
        Notes:
            This method has O(h²) global error convergence rate.
            If a stop condition is triggered, returns partial results up to that point.
        """
        y = np.zeros((len(t), len(y0)))
        y[0] = y0
        
        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            y_pred = y[i - 1] + dt * f(t[i - 1], y[i - 1])
            y_next = y[i - 1] + (dt / 2) * (f(t[i - 1], y[i - 1]) + f(t[i], y_pred))
            
            # Apply stop condition if provided
            if stop_condition is not None and stop_condition(y_next):
                return y[:i]
                
            y[i] = y_next
        return y

    def runge_kutta_3(self, f: Callable, y0: np.ndarray, t: np.ndarray, 
                    stop_condition: Optional[Callable] = None) -> np.ndarray:
        """
        Integrate using third-order Runge-Kutta method.
        
        This method evaluates the derivative function at three carefully chosen points
        to achieve higher accuracy than simpler methods.
        
        Args:
            f (Callable): Function to integrate, returns derivatives
            y0 (np.ndarray): Initial state vector
            t (np.ndarray): Time points for evaluation
            stop_condition (Callable, optional): Function that returns True to stop integration.
                                              Defaults to None.
            
        Returns:
            np.ndarray: Solution at each time point, shape (len(t), len(y0))
            
        Notes:
            This method has O(h³) global error convergence rate.
            If a stop condition is triggered, returns partial results up to that point.
        """
        y = np.zeros((len(t), len(y0)))
        y[0] = y0
        
        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            k1 = f(t[i - 1], y[i - 1])
            k2 = f(t[i - 1] + dt / 2, y[i - 1] + dt * k1 / 2)
            k3 = f(t[i - 1] + dt, y[i - 1] - dt * k1 + 2 * dt * k2)
            y_next = y[i - 1] + (dt / 6) * (k1 + 4 * k2 + k3)
            
            # Apply stop condition if provided
            if stop_condition is not None and stop_condition(y_next):
                return y[:i]
                
            y[i] = y_next
        return y

    def scipy_integrator(self, f: Callable, y0: np.ndarray, t_span: Tuple[float, float], 
                        t_eval: np.ndarray, stop_condition: Optional[Callable] = None) -> np.ndarray:
        """
        Integrate using SciPy's adaptive ODE solvers.
        
        Uses SciPy's solve_ivp function with the adaptive Runge-Kutta method (RK45)
        for high-accuracy integration.
        
        Args:
            f (Callable): Function to integrate, returns derivatives
            y0 (np.ndarray): Initial state vector
            t_span (Tuple[float, float]): Time span (start, end)
            t_eval (np.ndarray): Time points for evaluation
            stop_condition (Callable, optional): Function that returns True to stop integration.
                                              Defaults to None.
            
        Returns:
            np.ndarray: Solution at each time point in t_eval, shape (len(t_eval), len(y0))
            
        Notes:
            This method uses adaptive step size control for error management.
            Recommended for high-accuracy reference solutions.
            The stop condition is implemented as an event function if provided.
        """
        if stop_condition is None:
            sol = solve_ivp(f, t_span, y0, t_eval=t_eval, method='RK45')
            return sol.y.T
        
        # Define event function for stopping condition
        def event(t, y):
            return -1 if not stop_condition(y) else 1
        event.terminal = True
        
        sol = solve_ivp(f, t_span, y0, t_eval=t_eval, method='RK45', events=event)
        return sol.y.T

    def run_simulation(self, slope_function: Callable, integration_method: str, 
                     t_span: Tuple[float, float], t_eval: np.ndarray, 
                     output_folder: str = "output",
                     stop_condition: Optional[Callable] = None,
                     schwarzschild_safety: float = 1.5) -> np.ndarray:
        """
        Run the orbital simulation with specified parameters.
        
        This is the main method for executing simulations. It handles integration method
        selection, stopping conditions, and output file generation.
        
        Args:
            slope_function (Callable): Function to calculate the derivative (classical_slope or relativistic_slope)
            integration_method (str): Method to use for integration ("trapz", "rk3", or "scipy")
            t_span (Tuple[float, float]): Time span for simulation (start, end)
            t_eval (np.ndarray): Time points for evaluation
            output_folder (str, optional): Folder to save output. Defaults to "output".
            stop_condition (Callable, optional): Custom stopping condition function. Defaults to None.
            schwarzschild_safety (float, optional): Safety factor for Schwarzschild radius stopping condition.
                                                 Defaults to 1.5.
            
        Returns:
            np.ndarray: Orbital trajectory in AU units, shape (n_points, 4) with columns [x, y, vx, vy]
            
        Raises:
            ValueError: If an unknown integration method is specified
            
        Notes:
            Results are saved to a CSV file in the specified output folder.
            The method automatically adds a Schwarzschild radius stopping condition.
        """
        os.makedirs(output_folder, exist_ok=True)

        y0 = [self.orbit_data["x0"], self.orbit_data["y0"], 
             self.orbit_data["vx0"], self.orbit_data["vy0"]]
        M = self.orbit_data["M"]

        def f(t, y):
            return slope_function(t, y, M)
            
        # Create combined stopping condition
        def combined_stop_condition(y):
            # Check Schwarzschild radius condition
            if self.schwarzschild_stop_condition(y, schwarzschild_safety):
                return True
                
            # Check custom condition if provided
            if stop_condition is not None and stop_condition(y):
                return True
                
            return False

        # Select integration method
        if integration_method == "trapz":
            y = self.trapezoidal_euler(f, y0, t_eval, combined_stop_condition)
        elif integration_method == "rk3":
            y = self.runge_kutta_3(f, y0, t_eval, combined_stop_condition)
        elif integration_method == "scipy":
            y = self.scipy_integrator(f, y0, t_span, t_eval, combined_stop_condition)
        else:
            raise ValueError(f"Unknown integration method: {integration_method}")

        # Ensure output is valid
        if len(y) == 0:
            print("WARNING: No valid orbit points generated before stopping condition triggered!")
            return np.array([])

        # Create output file
        output_file = os.path.join(output_folder, f"{self.name}_orbit_history.csv")
        
        # Save trajectory in AU
        output_data = np.copy(y)
        output_data[:, 0] /= AU  # x
        output_data[:, 1] /= AU  # y
        
        # Save results
        np.savetxt(output_file, np.column_stack((t_eval[:len(y)], output_data)), delimiter=",", 
                 header="time,x,y,vx,vy", comments="")
        print(f"Simulation results saved to {output_file}")

        return output_data


class OrbitAnimation:
    """
    Create animations of orbital simulations from CSV data.
    
    This class loads orbital trajectory data from CSV files and generates
    animated GIFs showing the evolution of orbits over time.
    
    Attributes:
        csv_files (List[str]): List of paths to CSV files containing orbit data
        output_filename (str): Filename for the output animation
        output_folder (str): Directory where the animation will be saved
        mass (float, optional): Mass of the central body (kg), used to draw Schwarzschild radius
        labels (List[str], optional): Custom labels for each orbit
        colors (List[str], optional): Custom colors for each orbit
        fps (int): Frames per second for the animation
        data (List[np.ndarray]): Loaded trajectory data
        max_frames (int): Maximum number of frames across all trajectories
    """
    
    def __init__(self, csv_files, output_filename="orbit_animation.gif", output_folder="./output", 
                 mass=None, labels=None, colors=None, fps=10):
        """
        Initialize the OrbitAnimation object.
        
        Args:
            csv_files (List[str]): List of paths to CSV files containing orbit data
            output_filename (str, optional): Filename for the output animation. Defaults to "orbit_animation.gif".
            output_folder (str, optional): Directory where the animation will be saved. Defaults to "./output".
            mass (float, optional): Mass of the central body in kg. Defaults to None.
            labels (List[str], optional): Custom labels for each orbit. Defaults to None.
            colors (List[str], optional): Custom colors for each orbit. Defaults to None.
            fps (int, optional): Frames per second for the animation. Defaults to 10.
        """
        self.csv_files = csv_files
        self.data = []
        self.max_frames = 0
        self.output_filename = output_filename
        self.output_folder = output_folder
        self.mass = mass
        self.labels = labels
        self.colors = colors
        self.fps = fps
        self._load_data()
        
    def _load_data(self):
        """
        Load orbital data from CSV files.
        
        Each CSV file should contain columns for time, x, y, vx, and vy.
        The method stores the loaded data and determines the maximum number of frames.
        
        Raises:
            ValueError: If a CSV file is empty or invalid.
        """
        for csv_file in self.csv_files:
            df = pd.read_csv(csv_file, header=0)
            if df.empty:
                raise ValueError(f"CSV file {csv_file} is empty or invalid.")
            self.data.append(df.values)
            self.max_frames = max(self.max_frames, len(df))
        
    def _init_plot(self):
        """
        Initialize the plot for animation.
        
        Creates a figure and sets up orbit trails, planet markers, and the central body.
        Also draws the Schwarzschild radius if mass is provided.
        
        Returns:
            list: List of artist objects to be animated.
        """
        # Clear any existing figures
        plt.clf()
        plt.close('all')
        
        # Create a new figure
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        
        # Plot central body
        self.ax.plot(0, 0, 'ko', markersize=8, label="Black Hole")
        
        # Create empty lines for each orbit
        self.planets = []
        self.trails = []
        
        # Default colors and labels if not provided
        default_colors = ['red', 'blue', 'green', 'orange', 'purple']
        default_labels = [f"Orbit {i+1}" for i in range(len(self.data))]
        
        # Use provided colors/labels or defaults
        colors = self.colors if self.colors else default_colors
        labels = self.labels if self.labels else default_labels
        
        for i, _ in enumerate(self.data):
            color = colors[i % len(colors)]
            label = labels[i] if i < len(labels) else default_labels[i]
            
            # Add a point for current position
            planet, = self.ax.plot([], [], 'o', color=color, 
                                  markersize=6, label=label)
            
            # Add a line for the trail
            trail, = self.ax.plot([], [], '-', color=color, alpha=0.7)
            
            self.planets.append(planet)
            self.trails.append(trail)
        
        # Calculate and add Schwarzschild radius
        if self.mass is not None:
            # Calculate Schwarzschild radius from mass
            schwarzschild_radius = 2 * G * self.mass / (C**2)
            # Convert to AU for visualization
            schwarzschild_radius_au = schwarzschild_radius / AU
            
            circle = plt.Circle((0, 0), schwarzschild_radius_au, color='red', 
                             fill=False, linestyle='--', label="Schwarzschild Radius")
            self.ax.add_artist(circle)
        
        # Set axis limits based on data
        max_extent = 1.5  # Default value in AU
        if self.data:
            for orbit_data in self.data:
                if len(orbit_data) > 0:
                    # The columns should be time, x, y, vx, vy
                    x_max = np.max(np.abs(orbit_data[:, 1])) if orbit_data.shape[1] > 1 else 0
                    y_max = np.max(np.abs(orbit_data[:, 2])) if orbit_data.shape[1] > 2 else 0
                    max_extent = max(max_extent, x_max * 1.2, y_max * 1.2)
        
        self.ax.set_xlim(-max_extent, max_extent)
        self.ax.set_ylim(-max_extent, max_extent)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.ax.set_xlabel('x (AU)')
        self.ax.set_ylabel('y (AU)')
        self.ax.set_title('Orbital Simulation')
        self.ax.legend(loc='upper right')
        
        return self.planets
        
    def _update(self, frame):
        """
        Update the animation for a specific frame.
        
        This method updates the position of each planet and its trail
        for the given frame number.
        
        Args:
            frame (int): Frame number to update.
            
        Returns:
            list: Updated artist objects.
        """
        # Don't update if we've run out of frames
        if frame >= self.max_frames:
            return self.planets
        
        # Update each orbit's position and trail
        for i, orbit_data in enumerate(self.data):
            if frame < len(orbit_data):
                # Get data for current frame - columns are time, x, y, vx, vy
                x = orbit_data[frame, 1] if orbit_data.shape[1] > 1 else 0
                y = orbit_data[frame, 2] if orbit_data.shape[1] > 2 else 0
                
                # Update planet position - ensure data is in list form
                self.planets[i].set_data([x], [y])
                
                # Update trail (show path up to current frame)
                trail_x = orbit_data[:frame+1, 1] if orbit_data.shape[1] > 1 else []
                trail_y = orbit_data[:frame+1, 2] if orbit_data.shape[1] > 2 else []
                self.trails[i].set_data(trail_x, trail_y)
        
        return self.planets + self.trails
        
    def animate(self, frames=None):
        """
        Create and save the animation.
        
        Args:
            frames (int, optional): Number of frames to use. If None, use all available frames.
                                  Defaults to None.
            
        Notes:
            This method creates an animation of the orbital trajectories and
            saves it as a GIF file in the specified output directory.
            If frames is not specified, it defaults to the lesser of max_frames or 200.
        """
        # Make sure output directory exists
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Set the number of frames to use (limit for performance)
        if frames is None:
            frames = min(self.max_frames, 200)  # Default limit to prevent too slow GIFs
        else:
            frames = min(frames, self.max_frames)
        
        # Initialize the plot
        self._init_plot()
        
        # Create animation using the figure reference
        ani = animation.FuncAnimation(
            self.fig,
            self._update,
            frames=frames,
            blit=True, 
            interval=int(1000 / self.fps)  # Convert fps to milliseconds per frame
        )
        
        # Save the animation
        writer = PillowWriter(fps=self.fps)
        ani.save(f"{self.output_folder}/{self.output_filename}", writer=writer)
        print(f"Animation saved to: {self.output_folder}/{self.output_filename}")
        
        # Clean up
        plt.close(self.fig)


def main():
    """
    Command-line interface for the orbits module.
    
    This function parses command-line arguments and runs an orbit simulation
    with the specified parameters.
    
    Command-line arguments:
        -n, --name: Name of the orbit simulation
        -M, --mass: Mass of the central body (kg)
        -a, --axis: Semi-major axis of the orbit (AU)
        -e, --eccentricity: Eccentricity of the orbit (0-1)
        -N, --steps: Number of steps for the simulation
        -s, --save: Save the initial orbit map as an image
        -r, --relativ: Use relativistic equations of motion
        -m, --method: Integration method to use (trapz, rk3, scipy)
        -A, --anim: Generate a GIF animation of the orbit
        -o, --output: Output directory for simulation results
        
    Example:
        python orbits.py -n "earth_orbit" -M 1.989e30 -a 1 -e 0.017 -N 1000 -r -m rk3 -A -o output
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Simulate a two-body orbit on a 2D Cartesian grid.")
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the orbit simulation.")
    parser.add_argument("-M", "--mass", type=float, required=True, 
                      help="Mass of the central body (e.g., black hole) in kg.")
    parser.add_argument("-a", "--axis", type=float, required=True, 
                      help="Semi-major axis of the orbit in AU.")
    parser.add_argument("-e", "--eccentricity", type=float, required=True, 
                      help="Eccentricity of the orbit.")
    parser.add_argument("-N", "--steps", type=int, required=True, 
                      help="Number of steps for the simulation.")
    parser.add_argument("-s", "--save", action="store_true", 
                      help="Save the initial orbit map as an image.")
    parser.add_argument("-r", "--relativ", action="store_true", 
                      help="Use relativistic equations of motion.")
    parser.add_argument("-m", "--method", type=str, required=True, 
                      choices=["trapz", "rk3", "scipy"],
                      help="Integration method to use (trapz, rk3, scipy).")
    parser.add_argument("-A", "--anim", action="store_true", 
                      help="Generate a GIF animation of the orbit.")
    parser.add_argument("-o", "--output", type=str, default="output",
                      help="Output directory for simulation results")

    # Parse arguments
    args = parser.parse_args()

    # Convert semi-major axis from AU to meters
    a_meters = args.axis * AU

    # Initialize and run the orbit simulation
    orbit = Orbits(args.name)
    orbit.initialize_orbit(M=args.mass, a=a_meters, e=args.eccentricity, 
                         N=args.steps, save=args.save)

    # Select slope function based on user choice
    slope_function = orbit.relativistic_slope if args.relativ else orbit.classical_slope

    # Time span and evaluation points
    orbital_period = 2 * np.pi * np.sqrt((a_meters**3) / (G * args.mass))  # Kepler's 3rd law
    t_span = (0, orbital_period)
    t_eval = np.linspace(0, orbital_period, args.steps)

    # Run the simulation
    orbit.run_simulation(slope_function, args.method, t_span, t_eval, 
                       output_folder=args.output)

    # Generate animation if requested
    if args.anim:
        csv_file = os.path.join(args.output, f"{args.name}_orbit_history.csv")
        animation = OrbitAnimation([csv_file], 
                                  output_filename=f"{args.name}_animation.gif", 
                                  output_folder=args.output,
                                  mass=args.mass)  # Pass the mass parameter
        animation.animate()


if __name__ == "__main__":
    main()