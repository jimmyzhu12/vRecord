#!/usr/bin/env python3
import matplotlib.pyplot as plt
from common import load_data, filter_platform, detect_jumps, empirical_cdf_xy

OUT = "seeks_per_session_cdf.pdf"

def main():
    df = load_data()
    data = filter_platform(df)

    seeks_m0, seeks_m1 = [], []
    for _, r in data.iterrows():
        segs = r['updatedinfo']
        _, nj, _ = detect_jumps(segs)
        if int(r['modified']) == 0:
            seeks_m0.append(nj)
        else:
            seeks_m1.append(nj)

    x0, y0 = empirical_cdf_xy(sorted(seeks_m0))
    x1, y1 = empirical_cdf_xy(sorted(seeks_m1))

    plt.figure()
    if x0: plt.plot(x0, y0, label="Unmodified Dash.js")
    else: plt.plot([], [], label="Unmodified Dash.js (n=0)")
    if x1: plt.plot(x1, y1, label="Stall-reducing Dash.js")
    else: plt.plot([], [], label="Stall-reducing Dash.js (n=0)")
    plt.xlabel("Seeks per session (count)", fontsize=16)
    plt.ylabel("CDF", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=13)
    plt.ylim(0, 1)
    plt.xlim(left=0, right=40)
    plt.legend(loc="lower right", fontsize=16)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(OUT, dpi=200)
    plt.close()
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
