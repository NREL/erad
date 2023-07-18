---
title: 'ERAD: A Graph-Based Tool for Equity and Resilience Analysis for Power Distribution Systems.'
tags:
  - python
  - neo4j
  - power distribution systems
  - equity and resilince
  - disaster modeling
authors:
  - name: Kapil Duwadi
    orcid: 0000-0002-0589-5187
    affiliation: 1
  - name: Bryan Palmintier
    affiliation: 1
  - name: Aadil Latif
    affiliation: 1
  - name: Kwami Senam Sedzro
    affiliation: 1
  - name: Sherin Ann Abraham
    affiliation: 1
  
affiliations:
 - name: National Renewable Energy Laboratory (NREL), Golden, CO, USA
   index: 1
date: 1 August 2023
bibliography: paper.bib
---

# Summary

Understanding the impact of disaster events on people's ability to access critical service is key to designing appropriate programs to minimize the overall impact. Flooded roads, downed power lines, flooded power substation etc. could impact access to critical servies like electricity, food, health and more. The field of disaster modeling is still evolving and so is our understanding of how these events would impact our critical infrastrctures such power grid, hospitals, groceries, banks etc.

ERAD is a free, open-source Python toolkit for computing equity and resilience measures in the face of hazards like earthquakes and flooding. It uses graph database to store data and perform computation at the household level for a variety of critical services that are connected by power distribution network. It uses asset fragility curves, which are functions that relate hazard severity to survival probability for power system assets including cables, transformers, substations, roof-mounted solar panels, etc. recommended in top literature. Programs like undergrounding, microgrid, and electricity backup units for critical infrastructures may all be evaluated using metrics and compared across different neighborhoods to assess their effects on equity and resilience.

ERAD is designed to be used by researchers, students, community stakeholders, distribution utilities to understand and possibly evaluate effectiveness of different post disaster programs to improve resilience and equity. It was funded by National Renewable Energy Laboratory (NREL) and made publicy available with open license.

# Statement of need

In last few years, we have seen surge in disaster events affecting power system grid thanks to climate change. Lot of the research and software tools developed for understanding grid resilience have been focused on power transmission system. Recently we have seen increased intetrest in understanding equity and resilience in distribution power system. ERAD is developed and made publicy available to understand distribution grid resilience and equity impacts due to hazard events. You can also evaluate effectiveness of different post disaster resilience and equity improvement programs using this software.


# Acknowledgements

We acknowledge contributions from Bobby Jeffers from NREL during the software development duration.

# References