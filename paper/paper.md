---
title: 'ERAD: A Graph-Based Tool for Equity and Resilience Analysis for electric Distribution systems.'
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
    orcid: 0000-0002-1452-0715
    affiliation: 1
  - name: Aadil Latif
    affiliation: 1
  - name: Kwami Senam Sedzro
    orcid: 0000-0002-2107-8662
    affiliation: 1
  - name: Sherin Ann Abraham
    orcid: 0000-0002-4214-3267
    affiliation: 1
  
affiliations:
 - name: National Renewable Energy Laboratory (NREL), Golden, CO, USA
   index: 1
date: 1 February 2024
bibliography: paper.bib
---

# Summary

In the event of a disaster, damage to the electric system and related infrastructure (e.g. downed power lines, flooded equipment, hacked communication systems, damaged roads,  etc.) can impact people's access to critical services including not just electricity but also shelter, food, healthcare, and more.  Moreover, the individual and community ease of service access--both before and during such events--may be correlated with household income and other demographics, with some historically disadvantaged communities potentially experiencing more difficult access to critical services. 

Researchers, utilities, local governments, and other stakeholders

The Equity and Resilience Analysis for electric Distribution systems (ERAD) tool

ERAD is a free, open-source Python toolkit for computing equity and resilience measures in the face of hazards like earthquakes and flooding. It uses graph database to store data and perform computation at the household level for a variety of critical services that are connected by power distribution network. It uses asset fragility curves [@buritica_hierarchical_2017],[@kongar_seismic_2017], [@kongar_seismic_2014], [@mo_seismic_2017], [@jeddi_multi-hazard_2022], [@baghmisheh_seismic_2021], [@williams_tsunami_2020], [@bennett_extending_2021] which are functions that relate hazard severity to survival probability for power system assets including cables, transformers, substations, roof-mounted solar panels, etc. recommended in top literature [@rajabzadeh_improving_2022], [@fema_hazus_2020], [@farahani_earthquake_2020], [@cirone_valutazione_2013], [@sanchez-munoz_electrical_2020]. Programs like undergrounding, microgrid [@10.1145/3575813.3595196], and electricity backup units for critical infrastructures may all be evaluated using metrics and compared across different neighborhoods to assess their effects on equity and resilience.

ERAD is designed to be used by researchers, students, community stakeholders, distribution utilities to understand and possibly evaluate effectiveness of different post disaster programs to improve resilience and equity. It was funded by National Renewable Energy Laboratory (NREL) and made publicly available with open license.

# Statement of need

In last few years, we have seen surge in disaster events affecting power system grid thanks to climate change. Lot of the research and software tools developed for understanding grid resilience have been focused on power transmission system. Recently we have seen increased intetrest in understanding equity and resilience in distribution power system. ERAD is developed and made publicy available to understand distribution grid resilience and equity impacts due to hazard events. You can also evaluate effectiveness of different post disaster resilience and equity improvement programs using this software.

# Example usage

ERAD has already been used as part of multiple high-impact research efforts. In LA100 Equity Strategy [@la100-equity-strategy] and North American Energy Resilience Model (NAERM) [@naerm] projects, ERAD is utilized to understand the impact during flooding and earthquake events across communities with and with out vulnerable population.


# Acknowledgements

Thank you to Bobby Jeffers of NREL for his metric insights and other advisory contributions during the development of ERAD.

This work was authored by the National Renewable Energy Laboratory (NREL), operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. Funding provided by NREL license revenue under the provisions of the Bayh-Dole Act. The views expressed in the article do not necessarily represent the views of the DOE or the U.S. Government. The U.S. Government retains and the publisher, by accepting the article for publication, acknowledges that the U.S. Government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this work, or allow others to do so, for U.S. Government purposes.

# References