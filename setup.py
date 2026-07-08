from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mssv-eeg-analysis",
    version="1.0.0",
    author="EEG Analysis System",
    description="Complete EEG analysis pipeline for MSSV dataset with M365 Copilot integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dinnin-wq/copilot-mssv-analysis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "mne>=0.24.0",
        "matplotlib>=3.4.0",
        "requests>=2.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.7b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ]
    },
)
