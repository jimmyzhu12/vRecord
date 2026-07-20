#!/usr/bin/env python3
import ast
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from common import (load_data, filter_platform, empirical_cdf_xy, min_max_bitrate)

OUT = "qoe_cdf.pdf"

def calculate_play_time(updated_info):
    if not updated_info: return 0
    return sum((e[1] - e[0]) / 30 for e in updated_info)

def calculate_mean_utility(updated_info, video_id):
    if not updated_info or video_id not in min_max_bitrate: return 0
    br = min_max_bitrate[video_id]
    twu = td = 0
    for e in updated_info:
        res = e[2] if len(e) > 2 else 0
        if res == 480: b = br[0]
        elif res == 720: b = br[1]
        elif res == 1080: b = br[2]
        else: continue
        rs, re_ = round(e[0]/30)*30, round(e[1]/30)*30
        for _ in range(rs, re_, 30):
            twu += math.log(b / br[0]) / math.log(br[2] / br[0])
            td += 1
    return twu / td if td > 0 else 0

def calculate_rebuffer_ratio(play_time, total_stall):
    if play_time == 0: return None
    return (total_stall / 1000) / (play_time + total_stall / 1000)

def calculate_bitrate_switches(updated_info):
    if not updated_info: return 0
    bs = 0
    prev_res = updated_info[0][2] if len(updated_info[0]) > 2 else 0
    tf = 0
    for e in updated_info:
        tf += e[1] - e[0]
        if e != updated_info[0]:
            cr = e[2] if len(e) > 2 else 0
            if cr != prev_res: bs += 1
            prev_res = cr
    tfr = round(tf / 30) * 30
    return bs / tfr if tfr > 0 else 0

def main():
    df = load_data()
    data = filter_platform(df)
    data['raw_segs'] = data['apiCatchWatchSegments'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['play_time'] = data['raw_segs'].apply(calculate_play_time)
    data['stallDiffsString'] = data['stallDiffsString'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['totalStall'] = data['stallDiffsString'].apply(sum)

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

    data['mean_utility'] = data.apply(
        lambda r: calculate_mean_utility(r['raw_segs'], r['video_id']), axis=1)
    data['rebuffer_ratio'] = data.apply(
        lambda r: calculate_rebuffer_ratio(r['play_time'], r['totalStall']), axis=1)
    data['bitrate_switch'] = data['raw_segs'].apply(calculate_bitrate_switches)
    data['QoE_score'] = data.apply(
        lambda r: 100 * (r['mean_utility'] - 10 * r['rebuffer_ratio'] - 1 * r['bitrate_switch'])
        if r['rebuffer_ratio'] is not None else None, axis=1)

    q0 = data.loc[data['modified'] == 0, 'QoE_score'].dropna().tolist()
    q1 = data.loc[data['modified'] == 1, 'QoE_score'].dropna().tolist()
    x0, y0 = empirical_cdf_xy(q0)
    x1, y1 = empirical_cdf_xy(q1)

    fig, ax = plt.subplots()
    if x0: ax.step(x0, y0, where="post", label="Unmodified Dash.js")
    if x1: ax.step(x1, y1, where="post", label="Stall-reducing Dash.js")
    ax.set_xlabel("QoE (%)", fontsize=16)
    ax.set_ylabel("CDF", fontsize=16)
    ax.set_ylim(0, 1)
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=16)
    ticks = list(ax.get_xticks())
    ticks = [t for t in ticks if t <= 100 + 1e-9]
    if not any(abs(t - 100) < 1e-9 for t in ticks): ticks.append(100)
    ax.set_xticks(sorted(set(ticks)))
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:g}"))
    ax.set_xlim(left=-400, right=100)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
