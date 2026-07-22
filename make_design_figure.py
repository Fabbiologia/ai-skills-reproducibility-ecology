#!/usr/bin/env python3
"""Schematic overview of the experimental design (methods diagram).

This is a hand-drawn schematic, not generated from data. It shows the skill
ablation, the run process, the factorial design, the two outcomes, the report
experiment, and the two robustness checks. Output: results/fig_design.png.
Colours are colour-vision-deficiency safe (Okabe-Ito plus neutrals).
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

HERE = Path(__file__).parent
BLUE, ORANGE, GREEN, SKY = "#0072B2", "#D55E00", "#009E73", "#56B4E9"
INK, GREY, LINE, PANEL = "#1F2D3A", "#5b6570", "#c8cfd7", "#eef3f8"
# cumulative-instruction colour sequence (dark -> teal), CVD-safe
COND = ["#3f4451", "#4f6785", "#4b86a6", "#3f9fb8", "#2f9e8f"]

fig, ax = plt.subplots(figsize=(13.6, 9.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def rbox(x, y, w, h, fc="white", ec=INK, lw=1.3, r=1.1, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z, mutation_aspect=0.72))


def labelbox(x, y, w, h, title, sub=None, fc="white", ec=INK, lw=1.3,
             ts=10, ss=8.4, tc=INK, sc=GREY, r=1.1):
    rbox(x, y, w, h, fc=fc, ec=ec, lw=lw, r=r)
    if sub:
        ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center",
                fontsize=ss, color=sc, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=ts, color=tc, zorder=3)


def arrow(x1, y1, x2, y2, color=GREY, lw=1.8, style="-|>", ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                shrinkA=1, shrinkB=1, linestyle=ls), zorder=1)


def section(x, y, text):
    ax.text(x, y, text, ha="left", va="center", fontsize=12.5,
            fontweight="bold", color=INK)


def chip(cx, y, text, fc=BLUE, w=54, h=3.6):
    rbox(cx - w / 2, y - h / 2, w, h, fc=fc, ec=fc, r=1.8, z=2)
    ax.text(cx, y, text, ha="center", va="center", fontsize=9.5,
            fontweight="bold", color="white", zorder=3)


def hrule(y):
    ax.plot([2, 98], [y, y], color=LINE, lw=1.1, zorder=0)


# ======================= BAND 1 : EXPERIMENT 1 =======================
section(2, 98.4, "Experiment 1   ·   one number per task, computed many times over")

# --- the ablation ladder: a rising staircase C0 -> C4 ---
ax.text(2, 94.0, "The instruction (a “skill”) is built up one level at a time, each level keeping the one before:",
        ha="left", va="center", fontsize=9.4, color=INK)
ladder = [
    ("C0  none", "bare task"),
    ("C1  basic", "+ generic steps"),
    ("C2  contract", "+ data & method"),
    ("C3  controls", "+ seed & split"),
    ("C4  full", "+ checks & warnings"),
]
lw_, lh_ = 16.6, 4.6
x0, ystep = 4.0, 0.95
for i, (t, s) in enumerate(ladder):
    lx = x0 + i * (lw_ + 2.3)
    ly = 84.6 + i * ystep
    labelbox(lx, ly, lw_, lh_, t, s, fc=COND[i], ec=COND[i], tc="white", sc="#e8edf2",
             ts=9.6, ss=7.9, r=0.9)
    if i > 0:
        arrow(lx - 2.2, ly + lh_ / 2 - 0.5, lx - 0.2, ly + lh_ / 2 - 0.2, color=GREY, lw=1.5)

# --- the run pipeline ---
py = 74.5   # pipeline row y
ph = 8.2
labelbox(3, py, 16, ph, "Task on real data", "one open analytical choice", fc=PANEL, ec=INK)
labelbox(24.5, py, 13.5, ph, "+ one instruction", "level (C0–C4)", fc="white", ec=INK)
labelbox(43.5, py, 17.5, ph, "AI agent", "writes & runs code (Python or R)", fc="white", ec=BLUE, lw=1.6)
labelbox(66.5, py, 12.5, ph, "one number", "× 10 repeated runs", fc=PANEL, ec=INK)
# outcomes (two stacked)
labelbox(83.3, 80.1, 15.2, 3.5, "Reproducibility", "do the runs agree?",
         fc="white", ec=BLUE, lw=1.6, ts=8.8, ss=7.3)
labelbox(83.3, 74.3, 15.2, 3.5, "Validity", "match the reference?",
         fc="white", ec=ORANGE, lw=1.6, ts=8.8, ss=7.3)
for xa, xb in [(19, 24.5), (38, 43.5), (61, 66.5)]:
    arrow(xa, py + ph / 2, xb, py + ph / 2)
arrow(79, py + ph / 2, 83.1, 81.85)
arrow(79, py + ph / 2, 83.1, 76.05)
# link ladder down into the "+ instruction" box
arrow(31, 84.4, 31, py + ph, color=GREY, lw=1.5, ls="--")
# datasets note under the first box
ax.text(11, py - 2.4, "iris · Palmer Penguins · reef fish (LTEM);  tasks T1–T4",
        ha="center", va="center", fontsize=8.2, color=GREY)
ax.text(90.9, 72.0, "(the two can come apart)", ha="center", va="center",
        fontsize=7.6, fontstyle="italic", color=INK)

chip(50, 69.2, "4 tasks  ×  5 levels  ×  2 languages  ×  10 runs   =   400 runs", fc=BLUE)

hrule(65.0)

# ======================= BAND 2 : EXPERIMENT 2 =======================
section(2, 62.2, "Experiment 2   ·   a whole written report")
ry, rh = 47.0, 8.6
labelbox(3, ry, 15, rh, "Palmer Penguins", "one dataset", fc=PANEL, ec=INK)
labelbox(21.5, ry, 19, rh, "Write a data report", "no / structure-only / full skill", fc="white", ec=INK)
labelbox(44, ry, 19.5, rh, "Two templates", "standard: 4 analyses\nhard: 6 analyses with forks",
         fc="white", ec=INK, ts=9.4, ss=7.9)
labelbox(67, ry, 15.5, rh, "Judge agent", "grades method use", fc="white", ec=GREEN, lw=1.6)
labelbox(85.5, ry, 12.5, rh, "Coherence", "agreement · validity", fc="white", ec=ORANGE, lw=1.4,
         ts=9.0, ss=7.6)
for xa, xb in [(18, 21.5), (40.5, 44), (63.5, 67), (82.5, 85.5)]:
    arrow(xa, ry + rh / 2, xb, ry + rh / 2)
chip(50, 41.5, "2 templates  ×  3 conditions  ×  8 reports   =   48 reports", fc=GREEN, w=48)

hrule(37.0)

# ======================= BAND 3 : ROBUSTNESS CHECKS =======================
section(2, 34.2, "Two robustness checks   ·   does the effect hold, and what does it cost?")
by, bh = 15, 15
# token cost
labelbox(3, by, 45, bh, "", fc=PANEL, ec=INK, r=1.4)
ax.text(25.5, by + bh - 3.2, "Token cost", ha="center", fontsize=11, fontweight="bold", color=INK)
ax.text(25.5, by + bh / 2 - 1.9,
        "Re-run the four tasks across the five levels and weigh\n"
        "the size of the instruction (a fixed cost) against the\n"
        "number of tokens the agent generates (a running cost).",
        ha="center", va="center", fontsize=8.8, color=INK)
# cross-model / provider
labelbox(52, by, 45, bh, "", fc=PANEL, ec=INK, r=1.4)
ax.text(74.5, by + bh - 3.2, "Other models and providers", ha="center", fontsize=11,
        fontweight="bold", color=INK)
ax.text(74.5, by + bh / 2 - 1.9,
        "Run no skill versus the full skill on five models\n"
        "from three companies. Do independent models\n"
        "converge on the reference once the skill is full?",
        ha="center", va="center", fontsize=8.8, color=INK)

ax.text(50, 8.5, "Every run is a fresh agent that cannot see the other runs; the reference value for each task is computed independently and no run can see it.",
        ha="center", va="center", fontsize=8.0, fontstyle="italic", color=GREY)

fig.tight_layout(pad=0.4)
fig.savefig(HERE / "results" / "fig_design.png", dpi=200, bbox_inches="tight")
print("Wrote results/fig_design.png")
