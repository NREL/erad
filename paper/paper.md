---
title: 'ERAD: A Graph-Based Tool for Equity and Resilience Analysis of electric Distribution systems.'
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

Understanding the impact of extreme events on people's ability to access critical service is key to designing appropriate programs to minimize the overall impact. In the event of a disaster, damage to the electric system and related infrastructure (e.g. downed power lines, flooded equipment, hacked communication systems, damaged roads,  etc.) can impact people's access to critical services including not just electricity but also shelter, food, healthcare, and more.  Moreover, the individual and community's ease of service access--both before and during such events--may be correlated with household income and other demographics, with some historically disadvantaged communities potentially experiencing more difficult access to critical services. There is a key need to better understand such impacts and evaluate options to improve resilience and equity. The Equity and Resilience Analysis for electric Distribution systems (ERAD) tool is a free and open-source software package designed to be used by researchers, utilities, local governments, community groups, and other stakeholders to fill this need.

# Statement of Need

Much of the past work in evaluating equity and resilience have looked at historical data. For instance, Alper, et al. [@alper2021heat] used historical power outage complaint calls in New York city to understand heat vulnerability, Carvallo, et al. [@carvallo2021frozen] used satellite images to understand the impact of winter storm in minority communities in the state of Texas, Román, et al. [@roman2019satellite] used satellite images of Puerto Rico following hurricane maria to understand disparities in electric system recovery for disadvantaged communities. In another example Brockway, et al. [@brockway_inequitable_2021] show how existing grid infrastructure constraints may hinder the ability of  disadvantaged communities to charge electric vehicles and their access to DERs by looking at the geospatial intersection of demographics and grid hosting capacity data. ERAD instead provides a way to look ahead at possible future outages and service access challenges. ERAD also offers the unique feature of assessing access to multiple services and under multiple disaster event scenarios.

Many of the software tools developed for forward-looking understanding of grid resilience have been focused on the bulk power system. For example, Panteli, et. al [@panteli2016power] used fragility curves to assess the impact of extreme events in transmission system components, Liu, et. al [@liu2017quantified] developed resilience assesment indices to understand the impact of multiple transmission line outages, Wang et. al [@wang2019impact] proposed resilience constrained economic dispatch model for bulk system.However, this larger scale cannot capture critical service access or outage impacts at the neighborhood, let alone individual customer scale. Existing bulk scale tools, which focus on the integrity of the high-voltage regional, national, and continental scale grid also can not adequately capture the local resilience and equity values of distributed energy resources (DERs) that can provide power to critical service facilities and keep the lights on for customers even when there is a challenges getting power from the bulk system. ERAD's enables capturing these local effects at the neighborhood level or even down to the customer level.

There have been some recent efforts that consider resilience at the distribution system. For instance the REPAIR tool [@repair-paper] optimizes distribution system expansion planning considering both routine operations reliability and resilience to extreme events. However, it requires users to supply outage rate information and does not consider any equity metrics or look across critical services. The ReNCAT tool [@wachtel_rencat_2022] does consider multi-service-based equity using the social burden metric introduced in Wachtel, et al. [@wachtel_measuring_2022] (also available as an option in ERAD), however it only considers microgrids as a resilience strategy and it's optimization-based approach may struggle to scale to the very large regions ERAD can evaluate. ReNCAT also currently requires the .Net framework (nominally under the Windows operating system) and though open source, does not currently maintain a publicly accessible code repository to enable outside contributions or issue reporting. Both REPAIR and ReNCAT also require exogenous equipment damage risk data and patterns. In contrast, ERAD endogenously models damage patterns; computes a range of equity metrics, including multi-service access social burden; and enables open engagement in development through github.com.

# Implementation Overview

ERAD is a free, open-source Python toolkit for computing equity and resilience measures in the face of hazards like earthquakes and flooding. It uses a graph database to store data and perform computation down to the household level for a variety of critical services that are connected by the electric grid, with an initial focus on the local, distribution system. 

Users provide geospatial data on the location of customers and grid infrastructure along with their connectivity, such as from an OpenDSS [@opendss] model. It also uses critical infrastructure location data, such as from Homeland Infrastructure Foundation Level Data , [HIFLD](https://hifld-geoplatform.opendata.arcgis.com/) , and demographic data, such as from [U.S. Census Bureau](https://www.census.gov/). This enables ERAD to compute user-configurable baseline social burden-style metrics for each household's access to the suite of services as a function of distance or other ease of access metric. ERAD hazard models then simulate a range of disaster events and their damage to grid equipment and corresponding outages to households and critical services providers alike--unless there is a local electricity supply such as on-site backup storage or microgrids that can keep intentional islands of the grid energized. For scalability this evaluation is not only based on connectivity and supply/demand balance for each potentially isolated electrical island, rather than the more time-consuming power flow analysis used in engineering studies. The same service access metrics can then be computed for the disaster scenario to identify both the absolute level of service access during a disaster and the relative impacts compared to pre-disaster. ERAD also provides user-configurable methods to computed aggregated resiliency metrics and distributions at the community level (e.g. for each neighborhood) and to evaluate correlations with various demographics to assess equity in service access and resilience.

For outage simulations, ERAD uses asset fragility curves [@buritica_hierarchical_2017],[@kongar_seismic_2017], [@kongar_seismic_2014], [@mo_seismic_2017], [@jeddi_multi-hazard_2022], [@baghmisheh_seismic_2021], [@williams_tsunami_2020], [@bennett_extending_2021] which are functions that relate hazard severity to survival probability for power system assets including cables, transformers, substations, roof-mounted solar panels, etc. [@rajabzadeh_improving_2022], [@fema_hazus_2020], [@farahani_earthquake_2020], [@cirone_valutazione_2013], [@sanchez-munoz_electrical_2020]. Outage scenarios are then generated based on Monte Carlo samples across these individual equipment survival probabilities.

Grid or service resilience enhancement programs such as undergrounding, microgrids [@10.1145/3575813.3595196], and electricity backup units for critical infrastructures can also be applied, enabling users to compare metrics across options to assess their effects on equity and resilience and help identify the best approaches.

# Example Usage

ERAD has been used as part of multiple high-impact research efforts. Specifically it was used to analyze equitable access to critical services for 8 neighborhoods in the city of Los Angeles [@la100-es-chapter12] as it transitions to a 100% renewable energy future as part of the LA100 Equity Strategies project [@la100-equity-strategy]. It has also been used to generate distribution system outage scenarios for transmission distribution cosimulation following flooding event as part of North American Energy Resilience Model (NAERM) [@naerm] projects.

# Next Steps

We plan to enhance our features by including the capability to simulate additional threats, such as storms, heat waves, and cold spells, and by making the result visualization process more efficient.

# Acknowledgements

Thank you to Bobby Jeffers of NREL for his metric insights and other advice during the development of ERAD.

This work was authored by the National Renewable Energy Laboratory (NREL), operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. Funding provided by NREL license revenue under the provisions of the Bayh-Dole Act. The views expressed in the article do not necessarily represent the views of the DOE or the U.S. Government. The U.S. Government retains and the publisher, by accepting the article for publication, acknowledges that the U.S. Government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this work, or allow others to do so, for U.S. Government purposes.

# References