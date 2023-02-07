
#!/usr/bin/env python
import io
import os
import re

from setuptools import find_packages

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('requirements_dev.txt') as f:
    dev_requires = f.read().splitlines()


setup(name='erad',
    version="0.1.0-alpha", # MAJOR.MINOR.PATCH (https://semver.org/)
    description='Graph based scalable tool for computing equitable resilience metrics',
    author='Aadil Latif, Kapil Duwadi, Sherin Ann Abraham, Kwami Sedzro, Jeremy Keen, Bryan Palmintier',
    author_email='sherinann.abraham@nrel.gov, kwami.sedzro@nrel.gov, aadil.latif@nrel.gov, kapil.duwadi@nre.gov, jeremy.keen@nrel.gov, bryan.palmintier@nrel.gov',
    url='https://github.nrel.gov/ERAD/erad',
    packages=find_packages("src"),
    install_requires=requirements,
    python_requires='>=3.8',
    package_dir={"erad": "erad"},
    extras_require={
        "dev": dev_requires,
    }
)
