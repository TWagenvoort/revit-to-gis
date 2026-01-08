"""
Setup configuration for revit-to-gis package
Install via: pip install git+https://github.com/TWagenvoort/revit-to-gis.git
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="revit-to-gis",
    version="1.0.0",
    author="Thijs Wagenvoort",
    author_email="",
    description="Bidirectional sync: Revit → Grasshopper → ArcGIS Online",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TWagenvoort/revit-to-gis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pyproj>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ]
    },
    include_package_data=True,
    package_data={
        "revit_gis": ["data/", "config/"],
    },
)
