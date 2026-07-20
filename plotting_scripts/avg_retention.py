#!/usr/bin/env python3
from collections import defaultdict
import matplotlib.pyplot as plt
from common import (load_data, filter_platform, seg_range,
                    video_length, VIDEO_MAP, LECTURE_TO_VIDEO, TOTAL_LECTURES,
                    MIN_JUMP_FRAMES, FPS)

OUT = "avg_watch_percentage_vs_course_progress_m0_vs_m1.pdf"

def merged_total_frames(segments, min_gap):
    if not segments: return 0
    intervals = []
    for seg in segments:
        if not isinstance(seg, (list, tuple)) or len(seg) < 2: continue
        lo, hi = seg_range(seg)
        intervals.append((lo, hi))
    if not intervals: return 0
    intervals.sort()
    clo, chi = intervals[0]
    total = 0
    for lo, hi in intervals[1:]:
        if lo - chi < min_gap:
            chi = max(chi, hi)
        else:
            total += chi - clo
            clo, chi = lo, hi
    total += chi - clo
    return total

def main():
    df = load_data()
    data = filter_platform(df)

    frames_m0 = defaultdict(int)
    frames_m1 = defaultdict(int)
    count_m0 = defaultdict(int)
    count_m1 = defaultdict(int)

    for _, r in data.iterrows():
        vid = r['video_id']
        if vid not in VIDEO_MAP or vid not in video_length:
            continue
        lecture = VIDEO_MAP[vid]
        segs = r['updatedinfo']
        frames = merged_total_frames(segs, MIN_JUMP_FRAMES)
        mod = int(r['modified'])
        if mod == 0:
            frames_m0[lecture] += frames
            count_m0[lecture] += 1
        else:
            frames_m1[lecture] += frames
            count_m1[lecture] += 1

    xs = sorted(set(frames_m0) | set(frames_m1))
    y0, y1 = [], []
    for x in xs:
        vid = LECTURE_TO_VIDEO[x]
        vf = video_length[vid] * FPS
        y0.append((frames_m0.get(x, 0) / count_m0.get(x, 1) / vf) * 100)
        y1.append((frames_m1.get(x, 0) / count_m1.get(x, 1) / vf) * 100)

    xs_pct = [(x / TOTAL_LECTURES) * 100 for x in xs]

    plt.figure(figsize=(8, 6))
    plt.plot(xs_pct, y0, marker="o", label="Unmodified Dash.js")
    plt.plot(xs_pct, y1, marker="o", label="Stall-reducing Dash.js")
    plt.xlabel("Course Progress (%)", fontsize=16)
    plt.ylabel("Average Watch Time (% of Video)", fontsize=16)
    plt.xlim(0, 100)
    plt.xticks([0, 20, 40, 60, 80, 100])
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT, dpi=200)
    plt.close()
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
