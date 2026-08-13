"""Builds a Plotly dark-theme HTML tearsheet from results/combined.csv."""
from __future__ import annotations

import csv
import pathlib

import plotly.graph_objects as go

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
COMBINED_CSV = RESULTS_DIR / "combined.csv"
OUT_HTML = RESULTS_DIR / "report.html"

LANGUAGE_COLORS = {
    "python": "#3776AB",
    "cpp": "#00599C",
    "rust": "#DEA584",
    "q": "#F5A623",
}


def load_rows() -> list[dict[str, str]]:
    if not COMBINED_CSV.exists():
        return []
    with COMBINED_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def build_figure(rows: list[dict[str, str]]) -> go.Figure:
    benchmarks = sorted({r["benchmark"] for r in rows})
    languages = sorted({r["language"] for r in rows})

    fig = go.Figure()
    for language in languages:
        y_values = []
        for bench in benchmarks:
            match = next(
                (r for r in rows if r["language"] == language and r["benchmark"] == bench),
                None,
            )
            y_values.append(float(match["seconds"]) if match else None)
        fig.add_trace(
            go.Bar(
                name=language,
                x=benchmarks,
                y=y_values,
                marker_color=LANGUAGE_COLORS.get(language, "#888888"),
            )
        )

    fig.update_layout(
        title="Systematic Trading Language Shootout — Benchmark Results",
        xaxis_title="Benchmark",
        yaxis_title="Best-of-N wall-clock time (seconds, log scale)",
        yaxis_type="log",
        barmode="group",
        template="plotly_dark",
        legend_title_text="Language",
    )
    return fig


def main() -> None:
    rows = load_rows()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if not rows:
        OUT_HTML.write_text(
            "<html><body style='background:#111;color:#eee;font-family:sans-serif;"
            "padding:2rem'><h1>No benchmark results found</h1>"
            "<p>Run scripts/run_all.sh (or the CI workflow) to generate "
            "results/combined.csv before building the report.</p></body></html>"
        )
        print(f"No results found; wrote placeholder to {OUT_HTML}")
        return

    fig = build_figure(rows)
    fig.write_html(str(OUT_HTML), include_plotlyjs="cdn")
    print(f"Wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
