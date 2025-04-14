from setuptools import setup, find_packages

setup(
    name="orbits-simulation",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0",
        "pandas>=1.1.0",  # Required for OrbitAnimation data loading
        "pillow>=8.0.0",  # Required for animation GIF creation
    ],
    author="Juanda Vasconez",
    author_email="juan.vasconez@yachaytech.edu.ec",
    description="A module for simulating orbital dynamics with classical and relativistic physics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/davas1410/orbits-simulation",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "orbits=orbits.orbits:main",
        ],
    },
)