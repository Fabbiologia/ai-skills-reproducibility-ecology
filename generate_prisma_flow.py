#!/usr/bin/env python3
"""Regenerate the literature search-and-selection diagram (Figure S1) from the
background search counts. Output: results/figS1_prisma_flow.png"""
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

box(2.2, 10.4, 5.6, 1.1, "Records identified from\ndatabases & registers (n = 96)")
box(2.2, 8.6, 5.6, 1.0, "Records screened (n = 72)")
box(2.2, 6.8, 5.6, 1.0, "Reports sought for retrieval (n = 30)")
box(2.2, 5.0, 5.6, 1.0, "Reports assessed for eligibility (n = 28)")
box(2.2, 2.9, 5.6, 1.3, "Studies included (n = 19)\n11 direct • 8 indirect/mechanistic", "#D9F2EE")
box(8.0, 8.75, 1.9, 0.9, "Duplicates\nremoved (n = 24)")
box(8.0, 6.95, 1.9, 0.9, "Not retrieved\n(n = 2)")
box(8.0, 5.15, 1.9, 0.9, "Excluded (n = 9):\nno reprod. outcome")
arrow(5, 10.4, 5, 9.6); arrow(5, 8.6, 5, 7.8); arrow(5, 6.8, 5, 6.0); arrow(5, 5.0, 5, 4.2)
arrow(7.8, 9.1, 8.0, 9.1); arrow(7.8, 7.3, 8.0, 7.4); arrow(7.8, 5.5, 8.0, 5.6)
ax.text(5, 11.75, "Literature search and selection (background search, July 2026)",
        ha="center", fontsize=11, fontweight="bold", color=GRID)
fig.tight_layout()
out = HERE / "results" / "figS1_prisma_flow.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("wrote", out)
