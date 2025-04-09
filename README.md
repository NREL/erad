# ERAD (<u>E</u>nergy <u>R</u>esilience <u>A</u>nalysis for electric <u>D</u>istribution systems)
<p align="center"> 
<img src="docs/images/logo.svg" width="250" style="display:flex;justify-content:center;">
<p align="center">Graph based python tool for computing energy resilience. </p>
</p>

![GitHub all releases](https://img.shields.io/github/downloads/NREL/erad/total?logo=Github&logoColor=%2300ff00&style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/nrel/erad?style=flat-square)
[![CodeFactor](https://www.codefactor.io/repository/github/nrel/erad/badge)](https://www.codefactor.io/repository/github/nrel/erad)
[![GitHub license](https://img.shields.io/github/license/NREL/erad?style=flat-square)](https://github.com/NREL/erad/blob/main/LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues/NREL/erad?style=flat-square)](https://github.com/NREL/erad/issues)
![GitHub top language](https://img.shields.io/github/languages/top/nrel/erad?style=flat-square)

[Visit full documentation here.](https://nrel.github.io/erad/)

Understanding the impact of disaster events on people's ability to access critical service is key to designing appropriate programs to minimize the overall impact. Flooded roads, downed power lines, flooded power substation etc. could impact access to critical services like electricity, food, health and more. The field of disaster modeling is still evolving and so is our understanding of how these events would impact our critical infrastructures such power grid, hospitals, groceries, banks etc.

ERAD is a free, open-source Python toolkit for computing energy resilience measures in the face of hazards like earthquakes and flooding. It uses graph database to store data and perform computation at the household level for a variety of critical services that are connected by power distribution network. It uses asset fragility curves, which are functions that relate hazard severity to survival probability for power system assets including cables, transformers, substations, roof-mounted solar panels, etc. recommended in top literature. Programs like undergrounding, microgrid, and electricity backup units for critical infrastructures may all be evaluated using metrics and compared across different neighborhoods to assess their effects on energy resilience.

ERAD is designed to be used by researchers, students, community stakeholders, distribution utilities to understand and possibly evaluate effectiveness of different post disaster programs to improve energy resilience. It was funded by National Renewable Energy Laboratory (NREL) and made publicly available with open license.
