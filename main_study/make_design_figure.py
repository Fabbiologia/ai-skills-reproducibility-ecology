#!/usr/bin/env python3
"""Schematic of the experimental design.

The task grid, the kinds of open choice, the dataset behind every task and the
run counts are read from references.json and the archived records, so the
diagram cannot describe a study other than the one that was run.

Colours are safe for colour vision deficiency. No title is drawn; the caption
carries it.
"""
import csv, json
from collections import Counter
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

HERE = Path(__file__).parent
REFS = json.loads((HERE / "references.json").read_text())
rows = list(csv.DictReader(open(HERE / "run_records.csv")))

INK, MUTED, RULE, PANEL = "#1F2D3A", "#5B6570", "#D5DBE0", "#F5F7F9"
ORANGE, PURPLE, BLUE, GREEN = "#D55E00", "#CC79A7", "#0072B2", "#009E73"

DATA_COL = {"iris": "#E69F00", "penguins": "#56B4E9",
            "portal": "#6A9E5B", "reef": "#8C6BB1"}
DATA_NAME = {"iris": "iris", "penguins": "penguins",
             "portal": "rodents", "reef": "reef fish"}
FORKS = [
    ("aggregation", "Sampling unit", "what is averaged over\nbefore a mean is taken"),
    ("scope", "Scope", "pooled across groups,\nor computed within them"),
    ("missing", "Missing records", "absent values, and rows\nabsent altogether"),
    ("randomness", "Fitting a model", "the split, the seed,\nthe scaling"),
]
SHORT = {
    "A1_reef_biomass": "mean biomass per transect",
    "A2_portal_abundance": "mean catch per plot-year",
    "A3_portal_richness": "mean richness per plot-year",
    "S1_iris_corr": "sepal length vs width",
    "S2_penguin_bill_corr": "bill length vs depth",
    "S3_portal_hf_weight_corr": "hindfoot vs weight",
    "M1_penguin_gentoo_mass": "mass of female Gentoo",
    "M2_portal_dm_weight": "weight of one species",
    "M3_portal_implicit_zeros": "mean catch, counting\nempty plot-years",
    "R1_penguin_sex_clf": "penguin sex classifier",
    "R2_iris_species_clf": "iris species classifier",
    "R3_portal_species_clf": "rodent species classifier",
}

n_runs = len(rows)
n_models = len({r["model"] for r in rows})
reps = n_runs // (len(REFS) * 3 * n_models)

W, H = 11.0, 11.4
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
ASPECT = W / H
SPINE_X = 3.6


def box(x, y, w, h, fc="white", ec=RULE, lw=1.0, r=1.0, z=2, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                mutation_aspect=ASPECT, facecolor=fc, edgecolor=ec,
                                linewidth=lw, zorder=z, alpha=alpha))


def txt(x, y, s, size=9, color=INK, weight="normal", ha="center", va="center",
        style="normal", z=4):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            style=style, zorder=z, linespacing=1.4)


def arrow(x1, y1, x2, y2, color=MUTED, lw=1.2, z=3):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=11, color=color, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0))


def stage(y, n, title, sub=None):
    ax.add_patch(Circle((SPINE_X, y), 1.25, facecolor=INK, edgecolor="white",
                        linewidth=1.6, zorder=6))
    txt(SPINE_X, y, str(n), size=9, color="white", weight="bold", z=7)
    txt(7.2, y, title, size=11.5, weight="bold", ha="left")
    if sub:
        txt(7.2, y - 2.6, sub, size=8.6, color=MUTED, ha="left")


# the sequence spine, drawn behind the numbered markers
ax.plot([SPINE_X, SPINE_X], [3.9, 96.8], color=RULE, lw=1.6, zorder=1,
        solid_capstyle="round")

# ══════════════════ 1  TWELVE TASKS ══════════════════
stage(96.8, 1, "Twelve analysis tasks on four ecological datasets",
      "three tasks for each of four kinds of open choice, and no kind confined to one dataset")

GX, GY, GW, GH = 27.0, 67.6, 67.0, 23.4
cw, ch = GW / 3 - 1.5, GH / 4 - 1.1
for i, (fork, name, gloss) in enumerate(FORKS):
    y = GY + GH - (i + 1) * (ch + 1.1) + 1.1
    txt(25.2, y + ch / 2 + 1.05, name, size=9.2, weight="bold", ha="right")
    txt(25.2, y + ch / 2 - 1.75, gloss, size=7.3, color=MUTED, ha="right")
    for j, t in enumerate([t for t in REFS if REFS[t]["fork"] == fork]):
        x, ds = GX + j * (cw + 1.5), REFS[t]["dataset"]
        box(x, y, cw, ch, fc=DATA_COL[ds], ec="none", alpha=0.15, r=0.85)
        box(x, y, cw, ch, fc="none", ec=DATA_COL[ds], lw=1.1, r=0.85, z=3)
        # a two-line label needs lifting clear of the dataset caption beneath it
        txt(x + cw / 2, y + (3.15 if "\n" in SHORT[t] else 2.85), SHORT[t], size=7.7)
        txt(x + cw / 2, y + 0.95, DATA_NAME[ds], size=6.7, color=MUTED, style="italic")

counts = Counter(REFS[t]["dataset"] for t in REFS)
lx = GX + 1.0
for ds in ["iris", "penguins", "portal", "reef"]:
    box(lx, 64.2, 1.9, 1.9, fc=DATA_COL[ds], ec=DATA_COL[ds], lw=1.0, alpha=0.5, r=0.55)
    txt(lx + 2.7, 65.15, f"{DATA_NAME[ds]} ({counts[ds]})", size=7.5, color=MUTED, ha="left")
    lx += 15.5

# ══════════════════ 2  REFERENCE VALUES ══════════════════
stage(59.0, 2, "A reference value for each task",
      "so that a number returned by a run can be judged right or wrong")

RY = 48.0
box(27.0, RY, 18.5, 6.8, fc=PANEL, ec=RULE, r=0.95)
txt(36.25, RY + 3.4, "the quantity\nstated in words", size=8.3)
arrow(46.2, RY + 3.4, 50.3, RY + 3.4)
box(51.0, RY + 3.9, 20.5, 2.9, fc="white", ec=GREEN, lw=1.1, r=0.8)
txt(61.25, RY + 5.35, "implementation using a library", size=7.7, color=GREEN)
box(51.0, RY, 20.5, 2.9, fc="white", ec=GREEN, lw=1.1, r=0.8)
txt(61.25, RY + 1.45, "implementation as a direct loop", size=7.7, color=GREEN)
arrow(72.2, RY + 3.4, 76.3, RY + 3.4)
box(77.0, RY, 17.0, 6.8, fc="white", ec=GREEN, lw=1.5, r=0.95)
txt(85.5, RY + 4.5, "accepted only", size=8.4, color=GREEN, weight="bold")
txt(85.5, RY + 2.2, "where the two agree", size=8.4, color=GREEN)
txt(61.25, RY - 2.2, "the two implementations were written independently of one another",
    size=7.5, color=MUTED, style="italic")

# ══════════════════ 3  THREE CONDITIONS ══════════════════
stage(40.0, 3, "Every task presented under three conditions",
      "the second gives the standing recommendation to share code a fair trial")

CY, CW2, CH2 = 25.2, 21.0, 10.6
for x, col, name, what in [
    (27.0, ORANGE, "Question alone", "the question, the column\nnames and the first rows"),
    (49.5, PURPLE, "With a script", "the same, and a working script\nfor a different task of\nthe same kind"),
    (72.0, BLUE, "With a specification", "the same, and the method\nwritten out in words,\nwith no code"),
]:
    box(x, CY, CW2, CH2, fc="white", ec=col, lw=1.5, r=0.95)
    box(x, CY + CH2 - 2.6, CW2, 2.6, fc=col, ec="none", alpha=0.15, r=0.95)
    txt(x + CW2 / 2, CY + CH2 - 1.3, name, size=9.0, color=col, weight="bold")
    txt(x + CW2 / 2, CY + (CH2 - 2.6) / 2, what, size=7.7)
txt(60.0, CY - 2.3, "no run ever received a script that solves the task in front of it",
    size=7.5, color=MUTED, style="italic")

# ══════════════════ 4  RUNS ══════════════════
stage(18.5, 4, "One uniform procedure for every run",
      f"{reps} runs on each of {n_models} models for every task and condition, "
      f"giving {n_runs} runs in all")

SY = 8.2
for s, x in [("the model returns\na complete script", 27.0),
             ("the script is executed\nin the same environment", 50.0),
             ("the number it prints\nis recorded", 73.0)]:
    box(x, SY, 21.0, 5.6, fc=PANEL, ec=RULE, r=0.9)
    txt(x + 10.5, SY + 2.8, s, size=8.1)
for x in (48.4, 71.4):
    arrow(x, SY + 2.8, x + 1.4, SY + 2.8)

# ══════════════════ 5  ANALYSIS ══════════════════
ax.add_patch(Circle((SPINE_X, 3.9), 1.25, facecolor=INK, edgecolor="white",
                    linewidth=1.6, zorder=6))
txt(SPINE_X, 3.9, "5", size=9, color="white", weight="bold", z=7)
box(7.2, 0.6, 86.8, 6.6, fc="white", ec=INK, lw=1.3, r=0.95)
txt(9.4, 5.5, "The task is the unit of replication.", size=9.2, weight="bold", ha="left")
txt(9.4, 2.9, "Each task gives one proportion per condition, the share of its runs that reached the reference, and the\n"
              "conditions are compared across the twelve tasks with paired tests. Whether the runs agreed with one\n"
              "another is measured separately from whether they were right.",
    size=8.0, ha="left")

fig.tight_layout(pad=0.35)
fig.savefig(HERE / "fig_design.png", dpi=220)
print("wrote fig_design.png")
