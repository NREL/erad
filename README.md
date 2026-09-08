

[![CodeFactor](https://www.codefactor.io/repository/github/nlr-distribution-suite/erad/badge)](https://www.codefactor.io/repository/github/nlr-distribution-suite/erad) • [![codecov](https://codecov.io/gh/NLR-Distribution-Suite/erad/graph/badge.svg?token=FtAWhS5svb)](https://codecov.io/gh/NLR-Distribution-Suite/erad) • [![GitHub license](https://img.shields.io/github/license/NLR-Distribution-Suite/erad)](https://github.com/NLR-Distribution-Suite/erad/blob/main/LICENSE.txt) • [![GitHub issues](https://img.shields.io/github/issues/NLR-Distribution-Suite/erad)](https://github.com/NLR-Distribution-Suite/erad/issues) • ![PyPI - Downloads](https://img.shields.io/pypi/dm/NREL-erad) • [![Upload to PyPi](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/publish.yml/badge.svg)](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/publish.yml) • [![deploy-book](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/deploy.yml/badge.svg)](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/deploy.yml) • [![Pytest](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/pull_request_tests.yml/badge.svg)](https://github.com/NLR-Distribution-Suite/erad/actions/workflows/pull_request_tests.yml) • [![DOI](https://joss.theoj.org/papers/10.21105/joss.08782/status.svg)](https://doi.org/10.21105/joss.08782) • ![MCP Server](https://img.shields.io/badge/MCP_Server-enabled-brightgreen) • ![MCP Tools](https://img.shields.io/badge/MCP_Tools-26-blue)

<p align="center"> 
<img src="docs/_static/light.png" width="400" style="display:flex;justify-content:center;">
</p>

# ERAD (<u>E</u>nergy <u>R</u>esilience <u>A</u>nalysis for electric <u>D</u>istribution systems)

[Visit full documentation here.](https://nlr-distribution-suite.github.io/erad/)

ERAD is a free, open-source Python toolkit for assessing distribution-system asset resilience under hazard scenarios. It models physical infrastructure using graph-based connectivity and computes hazard-specific exposure and survival probabilities for assets such as poles, lines, cables, transformers, substations, junction boxes, switches, and rooftop solar installations. Asset fragility curves relate hazard severity to failure probability for power-system components using relationships established in the literature for flood, wind, wildfire, and earthquake conditions.

ERAD is designed for researchers, students, utilities, and other stakeholders who want to evaluate the performance of electric distribution systems under extreme events and compare asset hardening or mitigation strategies. It supports scenario-based analysis, uncertainty sampling, and export of asset-level results for downstream analysis and system comparison. It was funded by the National Laboratory of the Rockies (NLR) and made publicly available with an open license.

```mermaid
flowchart TD
A([Start])
B[Select entry point<br/>CLI or Python API or MCP tools]
C[Load Asset System<br/>Distribution model from file or cache]
D{Hazard input available?}
E[Load Hazard Model<br/>from JSON or model reference]
F[Create Empty Hazard System]
G[Add Historic Hazard Events<br/>Earthquake, Hurricane, Wildfire]
H[Validate fragility curve set<br/>DEFAULT_CURVES or custom]
I[Run Simulation<br/>asset system id plus hazard system id]
J[Simulation Result ID<br/>asset states and probabilities]
K[Analyze Results<br/>query assets, stats, topology]
L{Need uncertainty scenarios?}
M[Generate Monte Carlo Scenarios<br/>num samples and seed]
N[Tracked Changes Output]
O{Need exports?}
P[Export to SQLite<br/>for downstream analytics]
Q[Export to JSON<br/>asset and hazard systems]
R[Export Tracked Changes<br/>scenario deltas]
S[Clear loaded systems<br/>free memory and reset state]
T([End])

A --> B --> C --> D
D -- Yes --> E --> H
D -- No --> F --> G --> H
H --> I --> J --> K --> L
L -- Yes --> M --> N --> O
L -- No --> O
O -- Yes --> P
O -- Yes --> Q
O -- Yes --> R
O -- No --> S
P --> S
Q --> S
R --> S
S --> T

classDef startEnd fill:#0f172a,color:#ffffff,stroke:#0f172a,stroke-width:2px
classDef intake fill:#e0f2fe,color:#0c4a6e,stroke:#0284c7,stroke-width:1.5px
classDef decision fill:#fff7ed,color:#9a3412,stroke:#f97316,stroke-width:2px
classDef output fill:#f5f3ff,color:#4c1d95,stroke:#8b5cf6,stroke-width:1.5px
classDef cleanup fill:#f1f5f9,color:#334155,stroke:#64748b,stroke-width:1.5px

class A,T startEnd
class B,C,E,F,G,H,I,K,M intake
class D,L,O decision
class J,N,P,Q,R output
class S cleanup
```
