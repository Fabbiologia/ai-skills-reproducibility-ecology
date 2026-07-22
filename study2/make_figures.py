#!/usr/bin/env python3
"""Figures for the specification study.

Figure 1 draws one line per task across the three conditions, which mirrors the
paired analysis: the comparison is within a task, and the eye follows the same
task from one condition to the next.

Figure 2 shows the values themselves for the tasks where runs converged on a
wrong number. Each panel keeps its own scale, because the errors that matter are
a few per cent from the reference and a shared axis would hide them behind the
larger ones.

Colours are safe for colour vision deficiency. No titles are drawn; the captions
carry them.
"""
import csv, json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).parent
REFS = json.loads((HERE / "references.json").read_text())
rows = list(csv.DictReader(open(HERE / "study2_records.csv")))

ARMS = ["none", "code", "skill"]
ALAB = {"none": "Question\nalone", "code": "With a\nscript", "skill": "With a\nspecification"}
GREY, BLUE, ORANGE, GREEN, INK = "#B0B7BE", "#0072B2", "#D55E00", "#009E73", "#1F2D3A"
SHORT = {
    "A1_reef_biomass": "reef biomass", "A2_portal_abundance": "rodent abundance",
    "A3_portal_richness": "rodent richness", "S1_iris_corr": "iris correlation",
    "S2_penguin_bill_corr": "penguin bill correlation", "S3_portal_hf_weight_corr": "rodent size correlation",
    "M1_penguin_gentoo_mass": "penguin body mass", "M2_portal_dm_weight": "rodent weight",
    "M3_portal_implicit_zeros": "rodent abundance, empty plot-years",
    "R1_penguin_sex_clf": "penguin sex model", "R2_iris_species_clf": "iris species model",
    "R3_portal_species_clf": "rodent species model",
}

cell = defaultdict(list)
for r in rows:
    cell[(r["task"], r["arm"])].append(r)
rate = {k: 100 * np.mean([1.0 if x["correct"] == "True" else 0.0 for x in v])
        for k, v in cell.items()}
tasks = list(REFS.keys())
moved = [t for t in tasks if rate[(t, "none")] < 90]
flat = [t for t in tasks if t not in moved]


def vals(task, arm):
    return [float(x["value"]) for x in cell[(task, arm)] if x["value"] not in ("", "None")]


# ============================ FIGURE 1 ============================
fig, ax = plt.subplots(figsize=(10.2, 5.8))
x = np.arange(3)
for t in flat:
    ax.plot(x, [rate[(t, a)] for a in ARMS], color=GREY, lw=1.5, marker="o",
            ms=4.5, alpha=0.7, zorder=2)
for t in moved:
    ax.plot(x, [rate[(t, a)] for a in ARMS], color=BLUE, lw=2.4, marker="o", ms=6.5, zorder=3)
mean = [np.mean([rate[(t, a)] for t in tasks]) for a in ARMS]
ax.plot(x, mean, color=ORANGE, lw=3.4, marker="D", ms=8, zorder=5)

# right-hand labels, pushed apart so they do not overlap
ends = sorted([(rate[(t, "skill")], SHORT[t], BLUE) for t in moved] +
              [(mean[2], "mean of all twelve tasks", ORANGE)])
gap, placed = 6.2, []
for y, txt, col in ends:
    if placed and y - placed[-1][0] < gap:
        y = placed[-1][0] + gap
    placed.append((y, txt, col))
for (yadj, txt, col), (ytrue, _, _) in zip(placed, ends):
    ax.plot([2.0, 2.09], [ytrue, yadj], color=col, lw=0.8, alpha=0.55, zorder=1)
    ax.text(2.12, yadj, txt, va="center", fontsize=8.8, color=col,
            fontweight="bold" if col == ORANGE else "normal", zorder=6)

ax.set_xticks(x); ax.set_xticklabels([ALAB[a] for a in ARMS], fontsize=10)
ax.set_xlim(-0.35, 3.55); ax.set_ylim(-7, 108)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_ylabel("Runs reaching the reference value (%)")
ax.grid(axis="y", ls=":", alpha=0.45)
ax.spines[["top", "right"]].set_visible(False)
fig.legend(handles=[
    Line2D([0], [0], color=GREY, lw=1.5, marker="o", ms=4.5,
           label=f"already answered correctly ({len(flat)} tasks)"),
    Line2D([0], [0], color=BLUE, lw=2.4, marker="o", ms=6.5,
           label=f"a real open choice ({len(moved)} tasks)"),
    Line2D([0], [0], color=ORANGE, lw=3.4, marker="D", ms=7, label="mean"),
], loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=3, frameon=False, fontsize=9)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(HERE / "fig1_trajectories.png", dpi=200)

# ============================ FIGURE 2 ============================
# The tasks where the runs without a specification agreed most strongly on a
# value that is not the reference.
def consensus(task):
    v = vals(task, "none")
    if not v:
        return 0, None, 0
    c = Counter(round(z, 4) for z in v)
    val, n = c.most_common(1)[0]
    return n / len(v), val, n

cands = [(consensus(t)[0], t) for t in moved if consensus(t)[1] is not None
         and abs(consensus(t)[1] - REFS[t]["reference"]) > REFS[t]["tolerance"]]
show = [t for _, t in sorted(cands, reverse=True)[:3]]

fig2, axes = plt.subplots(1, len(show), figsize=(12.6, 4.2))
for ax2, t in zip(np.atleast_1d(axes), show):
    ref = REFS[t]["reference"]
    share, modal, n = consensus(t)
    rng = np.random.default_rng(5)
    for arm, y, col, lab in (("none", 1.0, ORANGE, "Question alone"),
                             ("skill", 0.0, BLUE, "With a specification")):
        v = vals(t, arm)
        if v:
            ax2.scatter(v, y + rng.normal(0, 0.045, len(v)), s=95, color=col,
                        alpha=0.8, edgecolor="white", lw=0.8, zorder=3)
    ax2.axvline(ref, ls="--", lw=1.8, color=GREEN, zorder=2)
    ax2.text(ref, 1.60, f"correct\n{ref:.4g}", color=GREEN, fontsize=8.6, ha="center",
             va="bottom", fontweight="bold", zorder=6,
             bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax2.annotate(f"{n} of {len(vals(t,'none'))} runs\nreturned {modal:.4g}",
                 xy=(modal, 1.0), xytext=(modal, 0.46), fontsize=8.6, color=ORANGE,
                 ha="center", va="top", zorder=6,
                 arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.2))
    # keep the panel on the range that carries the message; a single very large
    # error would otherwise compress the difference that matters into the axis
    lo, hi = min(ref, modal), max(ref, modal)
    span = (hi - lo) or (abs(ref) * 0.02) or 1.0
    xlo, xhi = lo - 0.95 * span, hi + 0.95 * span
    allv = vals(t, "none") + vals(t, "skill")
    off = [v for v in allv if not (xlo <= v <= xhi)]
    ax2.set_xlim(xlo, xhi)
    if off:
        ax2.text(0.99, 0.99, f"{len(off)} run{'s' if len(off) > 1 else ''} off scale\n"
                             f"(up to {max(off, key=abs):.4g})",
                 transform=ax2.transAxes, ha="right", va="top", fontsize=7.8,
                 color="#5b6570", style="italic")
    ax2.set_yticks([0, 1]); ax2.set_yticklabels(["with a\nspecification", "question\nalone"], fontsize=8.6)
    ax2.set_ylim(-0.5, 2.05)
    ax2.set_title(SHORT[t], fontsize=10, loc="left", fontweight="bold", color=INK)
    ax2.set_xlabel("value returned", fontsize=9)
    ax2.grid(axis="x", ls=":", alpha=0.4)
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.tick_params(axis="y", length=0)
fig2.tight_layout()
fig2.savefig(HERE / "fig2_consensus.png", dpi=200)
print("wrote fig1_trajectories.png and fig2_consensus.png")
