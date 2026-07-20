#!/usr/bin/env python3
import matplotlib.pyplot as plt
from common import load_data, filter_platform, detect_jumps, empirical_cdf_xy

OUT = "jump_length_cdf.pdf"

def main():
    df = load_data()
    data = filter_platform(df)

    lengths_m0, lengths_m1 = [], []
    for _, r in data.iterrows():
        segs = r['updatedinfo']
        _, _, jumps = detect_jumps(segs)
        js = [j[2] for j in jumps]
        if int(r['modified']) == 0:
            lengths_m0.extend(js)
        else:
            lengths_m1.extend(js)

    x0, y0 = empirical_cdf_xy(sorted(lengths_m0))
    x1, y1 = empirical_cdf_xy(sorted(lengths_m1))

    plt.figure()
    if x0: plt.plot(x0, y0, label="Unmodified Dash.js")
    if x1: plt.plot(x1, y1, label="Stall-reducing Dash.js")
    plt.xlabel("seek distance in log scale (seconds)", fontsize=16)
    plt.ylabel("CDF", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=13)
    plt.ylim(0, 1)
    plt.xscale("log")
    plt.xlim(left=0)
    plt.legend(loc="lower right", fontsize=16)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(OUT, dpi=200)
    plt.close()
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
