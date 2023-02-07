# ERAD

---
## Installation Instruction

We recommend using Anaconda or Miniconda to create the environment for windows user. 
Use the commands below to create environment and install the ERAD tool.

=== ":fontawesome-brands-windows: Windows 10"

    ``` cmd
    conda create -n erad python==3.8
    conda activate erad
    conda install shapely
    git clone https://github.nrel.gov/ERAD/erad.git
    cd erad
    pip install -e.
    ```

=== ":fontawesome-brands-apple: + :fontawesome-brands-linux: Mac OS & linux"

    ``` cmd
    conda create -n erad python==3.8
    conda activate erad
    git clone https://github.nrel.gov/ERAD/erad.git
    cd erad
    pip install -e.
    ```

