#!/usr/bin/env python3
import itertools
import ast
import numpy as np
import matplotlib.pyplot as plt
from common import (load_data, filter_platform, normalize_segments,
                    seg_range, video_length)

plt.style.use("tableau-colorblind10")

OUT_M0 = "youtube_style_retention_m0.pdf"
OUT_M1 = "youtube_style_retention_m1.pdf"
STEP_PCT = 0.01
N_BINS = 10000
SMOOTH = True
SMOOTH_WINDOW_PCT = 1.0
CAP_PER_SESSION_BIN = False

TOP5_SET = ["qkX5r9-MTZs", "zsMjJMdukjg", "aLzhVH7KRFQ", "ZD3x7_TGOaM", "pCA1FH49WzY"]

def bins_watch_time(segments_frames, video_len_sec, fps=30.0):
    watched = np.zeros(N_BINS, dtype=float)
    if not segments_frames or video_len_sec <= 0:
        return watched
    bin_width = float(video_len_sec) / N_BINS
    for seg in segments_frames:
        if not isinstance(seg, (list, tuple)) or len(seg) < 2:
            continue
        lo_f, hi_f = seg_range(list(seg))
        s = max(0.0, min(float(video_len_sec), lo_f / fps))
        e = max(0.0, min(float(video_len_sec), hi_f / fps))
        if e <= s:
            continue
        i0 = max(0, min(int(s // bin_width), N_BINS - 1))
        i1 = max(0, min(int((e - 1e-9) // bin_width), N_BINS - 1))
        for i in range(i0, i1 + 1):
            bin_s = i * bin_width
            bin_e = (i + 1) * bin_width
            watched[i] += max(0.0, min(e, bin_e) - max(s, bin_s))
    return watched

def smooth_curve(y, win):
    if win <= 1: return y
    kernel = np.ones(win) / float(win)
    return np.convolve(y, kernel, mode="same")

def compute_curves(data, modified, all_vids):
    curves = {}
    for vid in all_vids:
        vlen = video_length[vid]
        sub = data[(data["video_id"] == vid) & (data["modified"] == modified)]
        n = len(sub)
        total_watch = np.zeros(N_BINS, dtype=float)
        bin_width = float(vlen) / N_BINS
        for raw in sub["apiCatchWatchSegments"].tolist():
            segs = normalize_segments(ast.literal_eval(raw) if isinstance(raw, str) else raw)
            ws = bins_watch_time(segs, float(vlen))
            if CAP_PER_SESSION_BIN:
                ws = np.minimum(ws, bin_width)
            total_watch += ws
        curves[vid] = (total_watch, n, bin_width)
    return curves

def plot_retention(x_pct, curves, top5_by_count, out_path):
    fig, ax = plt.subplots()
    top5_lookup = set(TOP5_SET)

    for vid, (tw, n, bw) in curves.items():
        if vid in top5_lookup:
            continue
        y = tw / (n * bw) * 100 if n > 0 and bw > 0 else np.zeros_like(tw)
        if SMOOTH:
            y = smooth_curve(y, max(1, int(round(SMOOTH_WINDOW_PCT / STEP_PCT))))
        ax.plot(x_pct, y, color="0.75", alpha=0.43, linewidth=0.8, zorder=1)

    cycle_colors = [d["color"] for d in plt.rcParams["axes.prop_cycle"]]
    color_iter = itertools.cycle(cycle_colors)
    top_lines = {}

    for vid in top5_by_count:
        if vid not in curves:
            continue
        tw, n, bw = curves[vid]
        y = tw / (n * bw) * 100 if n > 0 and bw > 0 else np.zeros_like(tw)
        if SMOOTH:
            y = smooth_curve(y, max(1, int(round(SMOOTH_WINDOW_PCT / STEP_PCT))))
        line, = ax.plot(x_pct, y, linewidth=1.4, color=next(color_iter), label=vid, zorder=3)
        top_lines[vid] = line

    ax.set_xlabel("Video Progress (%)", fontsize=16)
    ax.set_ylabel("Audience Retention (%)", fontsize=16)
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.set_xlim(0, 100)
    ax.grid(True)
    ax.set_ylim(bottom=0, top=120)

    ordered_handles = [top_lines[v] for v in TOP5_SET if v in top_lines]
    ordered_labels = [v for v in TOP5_SET if v in top_lines]
    ax.legend(ordered_handles, ordered_labels, loc="upper right", fontsize=10)

    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {out_path}")

def main():
    df = load_data()
    data = filter_platform(df)

    top5_by_count = [str(x) for x in df["video_id"].value_counts().head(5).index.tolist()]
    top5_by_count = [v for v in top5_by_count if v in video_length]

    bin_starts = np.arange(N_BINS, dtype=float) * STEP_PCT
    x_pct = bin_starts + (STEP_PCT / 2.0)

    all_vids = [str(v) for v in data["video_id"].unique() if str(v) in video_length]

    curves_m0 = compute_curves(data, modified=0, all_vids=all_vids)
    plot_retention(x_pct, curves_m0, top5_by_count, OUT_M0)

    curves_m1 = compute_curves(data, modified=1, all_vids=all_vids)
    plot_retention(x_pct, curves_m1, top5_by_count, OUT_M1)

if __name__ == "__main__":
    main()
