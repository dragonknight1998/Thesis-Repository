# Thesis-Repository
Code used for SeQUeNCe and SimQN simulations

How to install:
1. Clone or download folder directly as .zip and extract on a directory of your choosing.
2. Cut and Paste SeQUeNCe and SimQN files to the same directory the simulators are installed. Replace all files when asked to.

Simulators used:
https://github.com/sequence-toolbox/SeQUeNCe (v0.7.0, commit c68eef7) 
https://github.com/QNLab-USTC/SimQN (v0.2.1, commit 7218f35)

Related works:
X. Wu et al., “SeQUeNCe: a customizable discrete-event simulator of quantum networks,” Quantum Science and Technology, Sep. 2021, doi: https://doi.org/10.1088/2058-9565/ac22f6.
L. Chen et al., “SimQN: A Network-Layer Simulator for the Quantum Network Investigation,” IEEE network, vol. 37, no. 5, pp. 182–189, Sep. 2023, doi: https://doi.org/10.1109/mnet.130.2200481.

Modifications:
  SimQN: Created new topologies for testing, created an A-Star routing algorithm, added random topology generation scripts baseed on previously mentioned changes.
  SeQUeNCe: Updated existing scripts to use Hefei's MDI-QKD testbed parameters. Extended range of variables for three-node-eg-ep-es.ipynb script.
