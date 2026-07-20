#!/usr/bin/env python3
import ast
import matplotlib.pyplot as plt
from common import load_data, filter_platform, empirical_cdf_xy

OUT = "stall_cdf.pdf"

def main():
    df = load_data()
    data = filter_platform(df)
    data['stallDiffsString'] = data['stallDiffsString'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    stalls_m0, stalls_m1 = [], []
    for _, r in data.iterrows():
        stalls = [float(x) for x in r['stallDiffsString']]
        if int(r['modified']) == 0:
            stalls_m0.extend(stalls)
        else:
            stalls_m1.extend(stalls)

    x0, y0 = empirical_cdf_xy(stalls_m0)
    x1, y1 = empirical_cdf_xy(stalls_m1)

    fig, ax = plt.subplots()
    if x0: ax.step(x0, y0, where="post", label="Unmodified Dash.js")
    if x1: ax.step(x1, y1, where="post", label="Stall-reducing Dash.js")
    ax.set_ylim(0, 1)
    ax.set_xlim(1, 50000)
    ax.set_xlabel("stall time (ms)", fontsize=16)
    ax.set_ylabel("CDF", fontsize=16)
    ax.set_xscale("log")
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.grid(True)
    ax.legend(loc="lower right", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
