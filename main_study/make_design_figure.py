#!/usr/bin/env python3
"""Figure 1, the schematic of the experimental design.

The task grid, the kinds of open choice, the dataset behind every task and the
run counts are read from references.json and the archived records, so the
diagram cannot describe a study other than the one that was run.

The canvas is 9.6 by 13.0 inches, close to the proportions of a journal page, so
that placing the figure at full page width scales it by about 0.7 rather than by
0.6, and the smallest type still prints at around seven points.

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

# one place to change the type scale
FS = dict(stage=14.5, sub=11.0, row=11.5, gloss=9.2, task=10.0, data=8.5,
          legend=9.5, ref=10.5, refbox=9.8, note=9.5, cond=11.5, condbody=10.0,
          step=10.2, headline=11.5, body=10.0)

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
    "A1_reef_biomass": "mean biomass\nper transect",
    "A2_portal_abundance": "mean catch\nper plot-year",
    "A3_portal_richness": "mean richness\nper plot-year",
    "S1_iris_corr": "sepal length\nvs width",
    "S2_penguin_bill_corr": "bill length\nvs depth",
    "S3_portal_hf_weight_corr": "hindfoot\nvs weight",
    "M1_penguin_gentoo_mass": "mass of\nfemale Gentoo",
    "M2_portal_dm_weight": "weight of\none species",
    "M3_portal_implicit_zeros": "mean catch, counting\nempty plot-years",
    "R1_penguin_sex_clf": "penguin sex\nclassifier",
    "R2_iris_species_clf": "iris species\nclassifier",
    "R3_portal_species_clf": "rodent species\nclassifier",
}

n_runs = len(rows)
n_models = len({r["model"] for r in rows})
reps = n_runs // (len(REFS) * 3 * n_models)

W, H = 9.6, 13.0
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
ASPECT = W / H
SPINE_X = 4.0


def box(x, y, w, h, fc="white", ec=RULE, lw=1.0, r=1.0, z=2, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                mutation_aspect=ASPECT, facecolor=fc, edgecolor=ec,
                                linewidth=lw, zorder=z, alpha=alpha))


def txt(x, y, s, size=10, color=INK, weight="normal", ha="center", va="center",
        style="normal", z=4):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            style=style, zorder=z, linespacing=1.35)


def arrow(x1, y1, x2, y2, color=MUTED, lw=1.3, z=3):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, color=color, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0))


def stage(y, n, title, sub=None):
    ax.add_patch(Circle((SPINE_X, y), 1.25, facecolor=INK, edgecolor="white",
                        linewidth=1.6, zorder=6))
    txt(SPINE_X, y, str(n), size=FS["sub"], color="white", weight="bold", z=7)
    txt(8.0, y, title, size=FS["stage"], weight="bold", ha="left")
    if sub:
        txt(8.0, y - 2.7, sub, size=FS["sub"], color=MUTED, ha="left")


ax.plot([SPINE_X, SPINE_X], [3.3, 97.5], color=RULE, lw=1.8, zorder=1,
        solid_capstyle="round")

# ══════════════════ 1  TWELVE TASKS ══════════════════
stage(97.5, 1, "Twelve analysis tasks on four ecological datasets",
      "three tasks for each of four kinds of open choice, and no kind confined to one dataset")

GX, GY, GW, GH = 29.0, 68.0, 66.0, 21.8
cw, ch = GW / 3 - 1.4, GH / 4 - 1.05
for i, (fork, name, gloss) in enumerate(FORKS):
    y = GY + GH - (i + 1) * (ch + 1.05) + 1.05
    txt(27.4, y + ch / 2 + 1.15, name, size=FS["row"], weight="bold", ha="right")
    txt(27.4, y + ch / 2 - 1.55, gloss, size=FS["gloss"], color=MUTED, ha="right")
    for j, t in enumerate([t for t in REFS if REFS[t]["fork"] == fork]):
        x, ds = GX + j * (cw + 1.4), REFS[t]["dataset"]
        box(x, y, cw, ch, fc=DATA_COL[ds], ec="none", alpha=0.15, r=0.8)
        box(x, y, cw, ch, fc="none", ec=DATA_COL[ds], lw=1.2, r=0.8, z=3)
        txt(x + cw / 2, y + 2.95, SHORT[t], size=FS["task"])
        txt(x + cw / 2, y + 0.95, DATA_NAME[ds], size=FS["data"], color=MUTED, style="italic")

counts = Counter(REFS[t]["dataset"] for t in REFS)
lx = GX + 0.5
for ds in ["iris", "penguins", "portal", "reef"]:
    box(lx, 64.5, 1.9, 1.5, fc=DATA_COL[ds], ec=DATA_COL[ds], lw=1.0, alpha=0.5, r=0.5)
    txt(lx + 2.8, 65.25, f"{DATA_NAME[ds]} ({counts[ds]})", size=FS["legend"],
        color=MUTED, ha="left")
    lx += 16.0

# ══════════════════ 2  REFERENCE VALUES ══════════════════
stage(59.0, 2, "A reference value for each task",
      "so that a number returned by a run can be judged right or wrong")

RY = 48.0
box(29.0, RY, 17.0, 6.0, fc=PANEL, ec=RULE, r=0.8)
txt(37.5, RY + 3.0, "the quantity\nstated in words", size=FS["ref"])
arrow(46.8, RY + 3.0, 49.2, RY + 3.0)
box(50.0, RY + 3.4, 23.5, 2.6, fc="white", ec=GREEN, lw=1.2, r=0.7)
txt(61.75, RY + 4.7, "implementation using a library", size=FS["refbox"], color=GREEN)
box(50.0, RY, 23.5, 2.6, fc="white", ec=GREEN, lw=1.2, r=0.7)
txt(61.75, RY + 1.3, "implementation as a direct loop", size=FS["refbox"], color=GREEN)
arrow(74.3, RY + 3.0, 76.7, RY + 3.0)
box(77.5, RY, 17.5, 6.0, fc="white", ec=GREEN, lw=1.6, r=0.8)
txt(86.25, RY + 4.1, "accepted only", size=FS["ref"], color=GREEN, weight="bold")
txt(86.25, RY + 1.9, "where the two agree", size=FS["ref"], color=GREEN)
txt(62.0, RY - 2.3, "the two implementations were written independently of one another",
    size=FS["note"], color=MUTED, style="italic")

# ══════════════════ 3  THREE CONDITIONS ══════════════════
stage(39.5, 3, "Every task presented under three conditions",
      "the second gives the standing recommendation to share code a fair trial")

CY, CW2, CH2 = 25.0, 21.5, 10.0
for x, col, name, what in [
    (29.0, ORANGE, "Question alone", "the question, the column\nnames and the first rows"),
    (51.5, PURPLE, "With a script", "the same, and a working\nscript for a different task\nof the same kind"),
    (74.0, BLUE, "With a specification", "the same, and the method\nwritten out in words,\nwith no code"),
]:
    box(x, CY, CW2, CH2, fc="white", ec=col, lw=1.6, r=0.8)
    box(x, CY + CH2 - 2.4, CW2, 2.4, fc=col, ec="none", alpha=0.15, r=0.8)
    txt(x + CW2 / 2, CY + CH2 - 1.2, name, size=FS["cond"], color=col, weight="bold")
    txt(x + CW2 / 2, CY + (CH2 - 2.4) / 2, what, size=FS["condbody"])
txt(62.0, CY - 2.3, "no run ever received a script that solves the task in front of it",
    size=FS["note"], color=MUTED, style="italic")

# ══════════════════ 4  RUNS ══════════════════
stage(19.0, 4, "One uniform procedure for every run",
      f"{reps} runs on each of {n_models} models for every task and condition, "
      f"giving {n_runs} runs in all")

SY = 8.8
for s, x in [("the model returns\na complete script", 29.0),
             ("the script is executed\nin the same environment", 51.5),
             ("the number it prints\nis recorded", 74.0)]:
    box(x, SY, 20.0, 5.0, fc=PANEL, ec=RULE, r=0.8)
    txt(x + 10.0, SY + 2.5, s, size=FS["step"])
for x in (49.3, 71.8):
    arrow(x, SY + 2.5, x + 2.0, SY + 2.5)

# ══════════════════ 5  ANALYSIS ══════════════════
ax.add_patch(Circle((SPINE_X, 3.3), 1.25, facecolor=INK, edgecolor="white",
                    linewidth=1.6, zorder=6))
txt(SPINE_X, 3.3, "5", size=FS["sub"], color="white", weight="bold", z=7)
box(8.0, 0.4, 87.0, 7.4, fc="white", ec=INK, lw=1.4, r=0.8)
txt(10.0, 6.4, "The task is the unit of replication.", size=FS["headline"],
    weight="bold", ha="left")
txt(10.0, 3.0, "Each task gives one proportion per condition, the share of its runs that reached the\n"
               "reference, and the conditions are compared across the twelve tasks with paired tests.\n"
               "Whether runs agreed with one another is measured separately from whether they were right.",
    size=FS["body"], ha="left")

fig.tight_layout(pad=0.3)
fig.savefig(HERE / "fig_design.png", dpi=300)
print("wrote fig_design.png")
