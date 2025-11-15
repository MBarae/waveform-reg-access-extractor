#!/usr/bin/env python3
"""Setup script for waveform-reg-access-extractor."""

import os
from pathlib import Path
from setuptools import setup, find_packages

# Get the directory containing setup.py
here = Path(__file__).parent

# Read README
readme_path = here / "README.md"
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
requirements_path = here / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    # Fallback if requirements.txt is not found
    requirements = ["pyvcd>=0.3.0", "PyYAML>=6.0", "lxml>=4.6.0"]

setup(
    name="waveform-reg-access-extractor",
    version="0.1.0",
    author="Mohamed Barae Buri",
    author_email="mbaraeburi@outlook.com",
    description="A modular tool for reverse engineering register accesses from digital waveforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mbarae/waveform-reg-access-extractor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "waveform-reg-access-extractor=waveform_reg_access_extractor.cli:main",
            "wreg-extract=waveform_reg_access_extractor.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
