#!/usr/bin/env python3
"""Regenerate the informal background-search diagram (Figure S1).

The search was not systematic and did not retain a deduplicated screening log, so
the diagram intentionally reports process rather than PRISMA-style flow counts.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).parent
fig, ax = plt.subplots(figsize=(8.2, 7)); ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
TEAL = "#0F766E"; GRID = "#111827"

def box(x, y, w, h, txt, fill="#F3F4F6"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                 linewidth=1.2, edgecolor=TEAL, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=9.3, color=GRID, wrap=True)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, color=GRID, lw=1.2))

box(2.2, 10.2, 5.6, 1.2, "Google Scholar, general web search,\njournals, and preprint servers")
box(2.2, 8.0, 5.6, 1.2, "Single reviewer screened for relevance to\nAI/agent reliability or computational reproducibility")
box(2.2, 5.8, 5.6, 1.2, "Nineteen studies read closely and\nsummarised narratively in Table S4")
box(2.2, 3.3, 5.6, 1.5, "Interpretive context only\nNo preregistration • no auditable screening log • no completeness claim", "#D9F2EE")
arrow(5, 10.2, 5, 9.2); arrow(5, 8.0, 5, 7.0); arrow(5, 5.8, 5, 4.8)
ax.text(5, 11.75, "Informal background-search process (July 2026)",
        ha="center", fontsize=11, fontweight="bold", color=GRID)
fig.tight_layout()
out = HERE / "results" / "figS1_prisma_flow.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("wrote", out)
