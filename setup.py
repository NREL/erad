
#!/usr/bin/env python
from setuptools import find_packages

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open("README.md","r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('requirements_dev.txt') as f:
    dev_requires = f.read().splitlines()


setup(
    name='NREL-erad',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.0a0", # MAJOR.MINOR.PATCH (https://semver.org/)
    description='Graph based scalable tool for computing equitable \
        resilience metrics for distribution systems.',
    author='Kapil Duwadi, Aadil Latif, Kwami Sedzro,  Sherin Ann Abraham, Bryan Palmintier',
    author_email='kapil.duwadi@nrel.gov, aadil.altif@nrel.gov, sherinann.abraham@nrel.gov, kwami.sedzro@nrel.gov, bryan.palmintier@nrel.gov',
    url='https://github.com/nrel/erad',
    packages=find_packages(),
    keywords="Resilience, Equity, Python, Power Distribution Systems, Earthquake, Flooding, Fire",
    install_requires=requirements,
    python_requires='>=3.8',
    include_package_data=True,
    package_data={
        'erad': [
            'cypher_queries/*.cypher',
            'data/*.csv',
        ]
    },
    extras_require={
        "dev": dev_requires,
    },
     classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ]
)
