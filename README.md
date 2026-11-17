# fatawa-jild9-merge

Merge workspace for Fatawa Razviya Jild 9 easy-Urdu tashreeh.

- 18 chunk files (`jild-09-chunk-01.json` … `jild-09-chunk-18.json`), 325 items, 863 pages (volume_id 49).
- `merge_jild9.py` merges them into `jild-09.json` (validates unique ids, page coverage, no empty tashreeh_jawab).
- GitHub Actions (`.github/workflows/merge.yml`) runs the merge on push, verifies the output, and publishes `jild-09.json` as the v1.0 release asset.
