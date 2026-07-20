#!/usr/bin/env python3
import ast
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from common import load_data, filter_platform, empirical_cdf_xy, OUT_111_PATH

OUT = "bytes_wasted_cdf.pdf"
BYTES_PER_MB = 1_000_000

def load_waste_map():
    uuid_waste = {}
    with open(OUT_111_PATH, 'r') as f:
        for line in f:
            if "RUN WASTE:" in line:
                parts = line.split()
                uuid_waste[parts[2]] = int(parts[3])
    return uuid_waste

def main():
    df = load_data()
    data = filter_platform(df)

    data['stallDiffsString'] = data['stallDiffsString'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['totalStall'] = data['stallDiffsString'].apply(sum)
    data['play_time'] = data['updatedinfo'].apply(
        lambda ui: sum((e[1] - e[0]) / 30 for e in ui) if ui else 0)

    data = data[data['play_time'] != 0.0]

    data['stallLength'] = data['stallDiffsString'].apply(len)
    def cat(length):
        if length == 0: return None
        elif length == 1: return "1"
        elif 2 <= length <= 3: return "2-3"
        elif 4 <= length <= 5: return "4-5"
        else: return "6+"
    data['stallLengthCategory'] = data['stallLength'].apply(cat)
    data = data[data['stallLengthCategory'].notnull()]

    waste_map = load_waste_map()
    data['bytes_wasted'] = data['uuid'].map(waste_map).fillna(0).astype(int)
    data['bytes_wasted'] = pd.to_numeric(data['bytes_wasted'], errors='coerce').clip(lower=0)
    data['bytes_wasted_mb'] = data['bytes_wasted'] / BYTES_PER_MB

    b0 = data.loc[data['modified'] == 0, 'bytes_wasted_mb'].dropna().tolist()
    b1 = data.loc[data['modified'] == 1, 'bytes_wasted_mb'].dropna().tolist()
    x0, y0 = empirical_cdf_xy(b0)
    x1, y1 = empirical_cdf_xy(b1)

    fig, ax = plt.subplots()
    if x0: ax.step(x0, y0, where="post", label="Unmodified Dash.js")
    if x1: ax.step(x1, y1, where="post", label="Stall-reducing Dash.js")
    ax.set_xlabel("Bytes Wasted in log scale (MB)", fontsize=16)
    ax.set_ylabel("CDF", fontsize=16)
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.set_ylim(0, 1)
    ax.grid(True)
    ax.set_xscale("log")
    ax.legend(loc="upper left", fontsize=16)
    ax.set_xlim(left=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:g}"))
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
