# vRecord Dataset

This repository hosts the dataset associated with the paper **vRecord: A User Study Dataset on Video Watching Behavior**.

Comprehensive details regarding the dataset, including its collection process, structure, and analysis, are available in the accompanying paper.

## Current Release

This repository is intended to be updated continuously.
The current release contains the data collected for the course ece220 provided in UIUC, corresponding exactly to the dataset discussed in the paper.

## Repository layout

- `data_mm.csv`, `data_waste.csv`: the paper release (ece220, 5,448 sessions)
- `data_latest/`: newest snapshot from the live experiment, with more sessions and new server-side **network stats** (see `data_latest/README.md`)
- `p1203_metadata/`: per-video metadata for ITU-T P.1203 QoE
- `plotting_scripts/`: scripts for the paper figures (see `script_instruction.md`)
- `poster/`: ACM MM 2026 poster

## Reference

For a detailed description and analysis of the dataset, please consult the paper, which is in the repo.
vRecord: A User Study dataset on video watching behavior
