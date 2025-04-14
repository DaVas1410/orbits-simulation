from setuptools import setup, find_packages

setup(
    name="orbits-simulation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
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
)