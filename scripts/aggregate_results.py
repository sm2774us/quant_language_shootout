"""Merges per-language results/*.json into results/combined.csv."""
from __future__ import annotations

import csv
import json
import pathlib

RESULTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "results"


def main() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        language = data.get("language", path.stem)
        for bench_name, seconds in data.get("benchmarks", {}).items():
            rows.append(
                {
                    "language": language,
                    "benchmark": bench_name,
                    "seconds": seconds,
                }
            )

    if not rows:
        print("No results/*.json files found; nothing to aggregate.")
        return

    out_path = RESULTS_DIR / "combined.csv"
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["language", "benchmark", "seconds"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path} with {len(rows)} rows.")


if __name__ == "__main__":
    main()
