# Latest data snapshot

Exported from the live experiment dashboard (`video.yihchun.com/samples/dashboard`) on 2026-11-18.
This snapshot is a superset of the paper release (`../data_mm.csv`, 5,448 sessions) and keeps growing; re-export to refresh.

## `video_data.csv` — client-side playback traces

6,319 sessions, 2025-01-18 → 2026-11-18. Same schema as `../data_mm.csv`:

| column | meaning |
|---|---|
| `browserInfo`, `osInfo` | client browser / OS |
| `timeSincePageLoad` | seconds since page load when the record was sent |
| `modified` | 0 = original player, 1 = modified (stall-free seek) player |
| `uuid` | session id (joins with `network_stats.csv`) |
| `stallDiffsString` | stall durations |
| `videoId` | YouTube video id (see `../p1203_metadata/`) |
| `timestamp` | record time |
| `totalWatchTimeSeconds` | total watch time |
| `watchRangeFrames` / `watchRangeSeconds` | watched ranges `[start, end, resolution]` |
| `apiCatchWatchSegments` | segments reported by the player API |

## `network_stats.csv` — server-side TCP statistics (new)

60,765 samples across 590 sessions (collection started 2026-09-02). One row per sampled TCP_INFO snapshot.

| column | meaning |
|---|---|
| `id` | row id |
| `log_timestamp` | sample time |
| `uuid`, `video_id`, `modified` | session / video / player variant |
| `resolution` | resolution being served |
| `sample_count` | number of kernel samples aggregated in the row |
| `rtt_us`, `rtt_var_us`, `min_rtt_us` | smoothed RTT, RTT variance, min RTT (µs) |
| `cwnd`, `mss` | congestion window (segments), MSS (bytes) |
| `delivery_rate`, `pacing_rate` | bytes/s |
| `retrans`, `lost` | retransmitted / lost segments |

The raw dashboard export duplicates every column (named + numeric index); this file keeps only the named columns.
