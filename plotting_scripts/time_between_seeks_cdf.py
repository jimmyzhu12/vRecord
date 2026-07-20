#!/usr/bin/env python3
import ast
import matplotlib.pyplot as plt
from common import (load_data, filter_platform, seg_start_end, seg_range,
                    empirical_cdf_xy, MIN_JUMP_FRAMES, FPS)

OUT = "time_between_jumps_cdf.pdf"

def extract_intervals(rows_iter, min_jump_frames=MIN_JUMP_FRAMES, fps=FPS):
    intervals = []
    for _, r in rows_iter:
        raw = r['apiCatchWatchSegments']
        combined = ast.literal_eval(raw) if isinstance(raw, str) else raw
        if len(combined) < 2:
            continue

        first = combined[0]
        block_lo, block_hi = seg_range(first)
        first_start, first_end = seg_start_end(first)
        prev_end_pos = first_end
        played_since_last_jump = abs(first_end - first_start)
        seen_first_jump = False

        for seg in combined[1:]:
            cur_start, cur_end = seg_start_end(seg)
            cur_lo, cur_hi = seg_range(seg)

            if block_lo <= cur_start <= block_hi:
                block_lo = min(block_lo, cur_lo)
                block_hi = max(block_hi, cur_hi)
                prev_end_pos = max(prev_end_pos, cur_end, block_hi)
                played_since_last_jump += abs(cur_end - cur_start)
                continue

            discontinuity = abs(cur_start - prev_end_pos)
            if discontinuity >= min_jump_frames:
                if seen_first_jump:
                    intervals.append(float(played_since_last_jump) / fps)
                else:
                    seen_first_jump = True
                played_since_last_jump = 0

            block_lo, block_hi = cur_lo, cur_hi
            prev_end_pos = cur_end
            played_since_last_jump += abs(cur_end - cur_start)

    return [x for x in intervals if x > 0]

def main():
    df = load_data()
    data = filter_platform(df)

    m0 = data[data['modified'] == 0]
    m1 = data[data['modified'] == 1]

    intervals0 = sorted(extract_intervals(m0.iterrows()))
    intervals1 = sorted(extract_intervals(m1.iterrows()))

    x0, y0 = empirical_cdf_xy(intervals0)
    x1, y1 = empirical_cdf_xy(intervals1)

    plt.figure()
    plt.plot(x0, y0, label="Unmodified Dash.js" if x0 else "Unmodified Dash.js (n=0)")
    plt.plot(x1, y1, label="Stall-reducing Dash.js" if x1 else "Stall-reducing Dash.js (n=0)")
    plt.xlabel("Time between seeks in log scale (seconds)", fontsize=16)
    plt.ylabel("CDF", fontsize=16)
    plt.tick_params(axis="both", which="major", labelsize=13)
    plt.ylim(0, 1)
    plt.xscale("log")
    plt.xlim(left=0, right=75)
    plt.legend(loc="lower right", fontsize=16)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(OUT, dpi=200)
    plt.close()
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
