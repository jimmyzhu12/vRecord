# Script Description 

Plotting scripts for the vRecord user study dataset. Each script reads from `data_2025.csv` and generates one PDF figure.

## Data files

- `data_mm.csv` -- 5448 video playback traces 
- `plotting_scripts/network_summary` -- server-side buffer waste data per session (used by `bytes_wasted_cdf.py`)

## How to run

All scripts must be run from this directory:

```
cd plotting_scripts
python3 qoe_cdf.py
python3 stall_cdf.py
python3 seek_distance_cdf.py
python3 bytes_wasted_cdf.py
python3 seeks_per_session_cdf.py
python3 time_between_seeks_cdf.py
python3 avg_retention.py
python3 retention_curves.py
```


