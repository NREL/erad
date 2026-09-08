# Energy Resilience Analysis for Distribution Power System

## Introduction

ERAD is a free, open-source Python toolkit for assessing distribution-system asset resilience under hazard scenarios. It models physical infrastructure using graph-based connectivity and computes hazard-specific exposure and survival probabilities for assets such as poles, lines, cables, transformers, substations, junction boxes, switches, and rooftop solar installations. Asset fragility curves relate hazard severity to failure probability for power-system components using relationships established in the literature for flood, wind, wildfire, and earthquake conditions.

To enhance data consistency and cross-platform compatibility, ERAD also integrates with the [Grid-Data-Models (GDM)](https://github.com/NLR-Distribution-Suite/grid-data-models) framework. GDM provides standardized, Pydantic-based data structures for representing distribution networks, ensuring that ERAD can seamlessly interoperate with other power system analysis tools. As a result, researchers and utilities can run hazard analyses in ERAD using the same distribution system models applied in power flow studies, planning tools, and other simulation platforms, significantly reducing data preparation effort and improving reproducibility.

ERAD is designed for researchers, students, utilities, and other stakeholders who want to evaluate the performance of electric distribution systems under extreme events and compare asset hardening or mitigation strategies. It was funded by the National Laboratory of the Rockies (NLR) and made publicly available with an open license.

## Table of Contents

```{tableofcontents}
```
