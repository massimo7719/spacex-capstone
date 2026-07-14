#!/usr/bin/env python3
"""Simple flowchart diagrams for the Data Collection slides (8 and 9)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

IMG = "/home/claude/spacex_capstone/images"


def draw_flowchart(steps, out_name, title):
    fig, ax = plt.subplots(figsize=(6.2, 6.8))
    n = len(steps)
    box_h = 0.7
    gap = 0.35
    total_h = n * box_h + (n - 1) * gap
    y0 = total_h
    for i, text in enumerate(steps):
        y = y0 - i * (box_h + gap) - box_h
        box = FancyBboxPatch((0.5, y), 5.0, box_h, boxstyle="round,pad=0.08",
                              linewidth=1.5, edgecolor="#1565C0",
                              facecolor="#E3F2FD" if i % 2 == 0 else "#BBDEFB")
        ax.add_patch(box)
        ax.text(3.0, y + box_h / 2, text, ha="center", va="center", fontsize=9.5, wrap=True)
        if i < n - 1:
            arrow = FancyArrowPatch((3.0, y), (3.0, y - gap + 0.02),
                                     arrowstyle="-|>", mutation_scale=18, color="#1565C0", linewidth=1.5)
            ax.add_patch(arrow)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, total_h + 0.3)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{IMG}/{out_name}", dpi=150)
    plt.close()
    print(f"salvato {out_name}")


draw_flowchart(
    ["GET api.spacexdata.com/v4/launches/past",
     "JSON response (array of launch records)",
     "pd.json_normalize() -> raw DataFrame",
     "GET /v4/launchpads, /v4/payloads (join)",
     "Enrich: site name, coordinates, payload mass",
     "Structured launches DataFrame\n(NOT reachable from this sandbox - Cloudflare 525)"],
    "15_flowchart_api.png",
    "SpaceX API data collection pipeline",
)

draw_flowchart(
    ["requests.get() on 5 Wikipedia pages\n(main + 2010-19, 2020-22, 2023, 2024)",
     "pandas.read_html() -> raw HTML tables",
     "Keep tables with Flight No./Launch outcome/\nBooster landing columns",
     "Concatenate + drop footnote/'note' rows",
     "Filter to Falcon 9 only, dedupe by flight number",
     "663 real launches, 2010-06-04 to 2026-07-11"],
    "16_flowchart_scraping.png",
    "Web scraping data collection pipeline (used)",
)
