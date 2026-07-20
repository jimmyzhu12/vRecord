import ast
import math
import numpy as np
import pandas as pd
from typing import Any, List, Tuple

CSV_PATH = "../data_mm.csv"
OUT_111_PATH = "network_summary"

FPS = 30.0
MIN_JUMP_FRAMES = 50

video_length = {
    "ZD3x7_TGOaM":14*60+51, "zsMjJMdukjg":3*60+26, "w2px-XboDCs":4*60+13,
    "sbwr5eAISJk":2*60+38, "rSCrbR02RqM":16*60+40, "r-N2Ewdvrvk":10*60+32,
    "QfmystA3BrY":12*60+50, "QBEtOo_DIcQ":8*60+43, "pCA1FH49WzY":22*60+41,
    "i_fEJZY97Xg":25*60+52, "fqp1samj35c":9*60+4, "FJoKPVcwk_s":12*60+22,
    "f4EOPiORcq8":9*60+21, "ccFmyKcvl3Y":12*60+29, "a7CxlDZztGI":7*60+36,
    "9TE_XE4zk_w":9*60+20, "9qCPGzmDWC8":5*60+23, "6nPVObRrbc0":6*60+34,
    "oU-YtUSibIE":2*60+56, "Fhk6t0YTpDw":3*60+36, "wS0PYmutaJ0":5*60+41,
    "2HnsH_xN_lo":4*60+10, "NfBquSEM_S8":2*60+33, "jlnLg_z9F08":11*60+55,
    "qkX5r9-MTZs":4*60+45, "aLzhVH7KRFQ":12*60+7, "KX9MT0QB6jw":8*60+34,
    "9M6QwuYjLBU":3*60+3, "egBpAEZa40I":4*60+28, "j4aO0o-W6hE":60+29,
    "l8XtMJ-otn4":7*60+38, "Vkygw5Q4QQQ":4*60+41, "3u1RchLj8Ts":5*60+37,
    "a6CyPj-Xbzs":4*60+59, "xVRTV22zhS8":4*60+10, "FKXypA7faTA":5*60+34,
    "T7t9AQ2VVfg":6*60+41, "R2g5-Y2m4cM":8*60+4, "0ZeKzSxybLo":3*60+57,
    "kB685AJ-8TA":2*60+32, "ej8E10-tCo":16*60+17, "omFODpN8828":14*60+26,
    "gTqZrYEedrc":15*60+34, "RSxTpOy5DTQ":15*60+22, "Mk-GdV8rxJc":7*60+31,
    "H7udEe2sH1Q":5*60+57, "D5QhGzT4hPQ":18*60+54, "YcbgNORZLmw":3*60+29,
    "fKfnSZgH0Rc":11*60+43, "qk3YPRtO-6Q":4*60+29, "ghhhrhgQcgs":5*60+40,
    "5iUWLkZEZPo":15*60+3, "rw6LzepJjb8":5*60+41, "9rnl46deXRg":22*60+54,
    "r9f3IId4kPU":22*60+46, "EBQhcTSITq0":26*60+38, "7dTl9z3OymM":10*60+3,
    "DgRkrpU1c0A":10*60+21, "crxxA2o9muE":25*60+11, "lUxTJqlsKBU":6*60+52,
    "2jBerC8xuSE":19*60+2,
}

min_max_bitrate = {
    "zsMjJMdukjg":[1910,3707,6482], "ZD3x7_TGOaM":[2507,4940,8011],
    "w2px-XboDCs":[2397,4743,6981], "sbwr5eAISJk":[2602,5215,8360],
    "rSCrbR02RqM":[2487,4915,8107], "r-N2Ewdvrvk":[2289,4495,7987],
    "QfmystA3BrY":[2569,5134,8200], "QBEtOo_DIcQ":[2159,4224,7195],
    "pCA1FH49WzY":[2278,4598,7843], "i_fEJZY97Xg":[2498,4997,8002],
    "fqp1samj35c":[2541,5079,8131], "FJoKPVcwk_s":[2448,4835,7888],
    "f4EOPiORcq8":[2544,5097,8159], "ccFmyKcvl3Y":[2513,5020,8017],
    "a7CxlDZztGI":[2540,5071,8097], "9TE_XE4zk_w":[2649,5271,8533],
    "9qCPGzmDWC8":[2612,5244,8327], "6nPVObRrbc0":[2376,4744,7684],
    "oU-YtUSibIE":[2476,4960,7951], "Fhk6t0YTpDw":[2555,5113,8184],
    "wS0PYmutaJ0":[2574,5147,8226], "2HnsH_xN_lo":[2449,4893,7860],
    "NfBquSEM_S8":[2547,5088,8145], "jlnLg_z9F08":[2550,5100,8145],
    "qkX5r9-MTZs":[2452,4895,7848], "aLzhVH7KRFQ":[2501,4997,8008],
    "KX9MT0QB6jw":[2509,5017,8052], "9M6QwuYjLBU":[2486,4960,7936],
    "egBpAEZa40I":[2494,4974,7957], "j4aO0o-W6hE":[2447,4829,8103],
    "l8XtMJ-otn4":[2097,4120,7183], "Vkygw5Q4QQQ":[2293,4500,7893],
    "3u1RchLj8Ts":[2581,5151,8226], "a6CyPj-Xbzs":[2466,4887,7942],
    "xVRTV22zhS8":[2223,4333,7548], "FKXypA7faTA":[2005,3891,6784],
    "T7t9AQ2VVfg":[2545,5088,8130], "R2g5-Y2m4cM":[2481,4951,7937],
    "0ZeKzSxybLo":[2517,5002,8077], "kB685AJ-8TA":[2532,5062,8118],
    "ej8E10-tCo":[2525,5043,8078], "omFODpN8828":[2526,5048,8080],
    "gTqZrYEedrc":[2506,5003,8012], "RSxTpOy5DTQ":[2466,4914,7781],
    "Mk-GdV8rxJc":[2151,4152,7107], "H7udEe2sH1Q":[2330,4555,7974],
    "D5QhGzT4hPQ":[2416,4830,7712], "YcbgNORZLmw":[2472,4888,7880],
    "fKfnSZgH0Rc":[2562,5116,8150], "qk3YPRtO-6Q":[1995,3906,6859],
    "ghhhrhgQcgs":[2004,3930,6925], "5iUWLkZEZPo":[2472,4851,8074],
    "rw6LzepJjb8":[2280,4405,7542], "9rnl46deXRg":[2454,4905,7894],
    "r9f3IId4kPU":[2552,5014,8180], "EBQhcTSITq0":[2501,5010,8041],
    "7dTl9z3OymM":[2545,5080,8115], "DgRkrpU1c0A":[2528,5050,8102],
    "crxxA2o9muE":[2494,4980,7975], "lUxTJqlsKBU":[2554,5115,8258],
    "2jBerC8xuSE":[2505,5007,8033],
}

VIDEO_MAP = {
    "ZD3x7_TGOaM":1, "zsMjJMdukjg":2, "pCA1FH49WzY":3, "QBEtOo_DIcQ":4,
    "sbwr5eAISJk":5, "ccFmyKcvl3Y":6, "9TE_XE4zk_w":7, "f4EOPiORcq8":8,
    "rSCrbR02RqM":9, "fqp1samj35c":10, "r-N2Ewdvrvk":11, "6nPVObRrbc0":12,
    "QfmystA3BrY":13, "a7CxlDZztGI":14, "9qCPGzmDWC8":15, "w2px-XboDCs":16,
    "i_fEJZY97Xg":17, "FJoKPVcwk_s":18, "oU-YtUSibIE":19, "Fhk6t0YTpDw":20,
    "wS0PYmutaJ0":21, "2HnsH_xN_lo":22, "NfBquSEM_S8":23, "jlnLg_z9F08":24,
    "qkX5r9-MTZs":25, "aLzhVH7KRFQ":26, "KX9MT0QB6jw":27, "9M6QwuYjLBU":28,
    "egBpAEZa40I":29, "j4aO0o-W6hE":30, "l8XtMJ-otn4":31, "Vkygw5Q4QQQ":32,
    "3u1RchLj8Ts":33, "a6CyPj-Xbzs":34, "xVRTV22zhS8":35, "FKXypA7faTA":36,
    "T7t9AQ2VVfg":37, "R2g5-Y2m4cM":38, "0ZeKzSxybLo":39, "kB685AJ-8TA":40,
    "-ej8E10-tCo":41, "omFODpN8828":42, "gTqZrYEedrc":43, "RSxTpOy5DTQ":44,
    "Mk-GdV8rxJc":45, "H7udEe2sH1Q":46, "D5QhGzT4hPQ":47, "YcbgNORZLmw":48,
    "fKfnSZgH0Rc":49, "qk3YPRtO-6Q":50, "ghhhrhgQcgs":51, "5iUWLkZEZPo":52,
    "rw6LzepJjb8":53, "9rnl46deXRg":54, "r9f3IId4kPU":55, "EBQhcTSITq0":56,
    "7dTl9z3OymM":57, "DgRkrpU1c0A":58, "crxxA2o9muE":59, "lUxTJqlsKBU":60,
    "2jBerC8xuSE":61,
}
TOTAL_LECTURES = 61
LECTURE_TO_VIDEO = {v: k for k, v in VIDEO_MAP.items()}

def safe_parse_list(s: Any) -> List[Any]:
    if s is None: return []
    if isinstance(s, list): return s
    s = str(s).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}: return []
    try: return ast.literal_eval(s)
    except Exception: return []

def normalize_segments(raw: Any) -> List[List[int]]:
    parsed = safe_parse_list(raw)
    if not parsed: return []
    if (isinstance(parsed, list) and len(parsed) >= 2
            and all(isinstance(x, (int, float)) for x in parsed[:2])):
        return [[int(parsed[0]), int(parsed[1]), int(parsed[2]) if len(parsed) > 2 else 0]]
    segs = []
    for item in parsed:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            segs.append([int(item[0]), int(item[1]), int(item[2]) if len(item) > 2 else 0])
    return segs

def seg_start_end(seg): return int(seg[0]), int(seg[1])

def seg_range(seg):
    a, b = seg_start_end(seg)
    return (a, b) if a <= b else (b, a)

def is_forced_o_html_platform_row(r: pd.Series) -> bool:
    osinfo = str(r.get("osInfo", "")).strip().lower()
    browser = str(r.get("browserInfo", "")).strip().lower()
    is_ios = "ios" in osinfo
    is_macos = ("macos" in osinfo) or ("os x" in osinfo) or ("osx" in osinfo)
    is_safari = ("safari" in browser) and not any(
        x in browser for x in ["chrome", "chromium", "crios", "fxios", "edg", "edgios", "opr", "opera"])
    return is_ios or (is_macos and is_safari)

def empirical_cdf_xy(samples):
    samples = [float(x) for x in samples if x is not None and np.isfinite(x)]
    if not samples: return [], []
    x = sorted(samples)
    n = len(x)
    y = [(i + 1) / n for i in range(n)]
    return x, y

def load_data():
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip() for c in df.columns]
    df['updatedinfo'] = df['watchRangeFrames'].apply(ast.literal_eval)
    df['video_id'] = df['videoId']
    return df

def filter_platform(df):
    mask = df.apply(is_forced_o_html_platform_row, axis=1)
    return df[~mask].copy()

def detect_jumps(combined_segments, min_jump_frames=MIN_JUMP_FRAMES, fps=FPS):
    total_played = sum(abs(seg[1] - seg[0]) for seg in combined_segments)
    if len(combined_segments) < 2:
        return total_played, 0, []

    first = combined_segments[0]
    block_lo, block_hi = seg_range(first)
    _, prev_end_pos = seg_start_end(first)
    jumps = []

    for seg in combined_segments[1:]:
        cur_start, cur_end = seg_start_end(seg)
        cur_lo, cur_hi = seg_range(seg)
        if block_lo <= cur_start <= block_hi:
            block_lo = min(block_lo, cur_lo)
            block_hi = max(block_hi, cur_hi)
            prev_end_pos = max(prev_end_pos, cur_end, block_hi)
            continue
        discontinuity = abs(cur_start - prev_end_pos)
        if discontinuity >= min_jump_frames:
            jumps.append((int(prev_end_pos), int(cur_start), float(discontinuity) / fps))
        block_lo, block_hi = cur_lo, cur_hi
        prev_end_pos = cur_end

    return total_played, len(jumps), jumps
