#!/usr/bin/env python3
"""Figures for the specification study.

Figure 1 draws one line per task across the three conditions, which mirrors the
paired analysis: the comparison is made within a task, and the eye follows the
same task from one condition to the next.

Figure 2 shows the values themselves, for the five tasks where the question alone
did not reach the reference. All three conditions appear, because the point is
that the condition whose runs agree with each other most closely is not the
condition that is right most often. Each panel keeps its own scale, since the
errors that matter are a few per cent from the reference.

Provider errors are dropped throughout, matching the primary analysis. Colours
are safe for colour vision deficiency. No titles are drawn; the captions carry
them.
"""
import csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).parent
REFS = json.loads((HERE / "references.json").read_text())
rows = [r for r in csv.DictReader(open(HERE / "run_records.csv"))
        if not r["error"].startswith("api")]

ARMS = ["none", "code", "skill"]
ALAB = {"none": "Question\nalone", "code": "With a\nscript", "skill": "With a\nspecification"}
GREY, BLUE, ORANGE, GREEN, PURPLE, INK = (
    "#B0B7BE", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#1F2D3A")
ACOL = {"none": ORANGE, "code": PURPLE, "skill": BLUE}
SHORT = {
    "A1_reef_biomass": "reef biomass", "A2_portal_abundance": "rodent abundance",
    "A3_portal_richness": "rodent richness", "S1_iris_corr": "iris correlation",
    "S2_penguin_bill_corr": "penguin bill correlation",
    "S3_portal_hf_weight_corr": "rodent size correlation",
    "M1_penguin_gentoo_mass": "penguin body mass", "M2_portal_dm_weight": "rodent weight",
    "M3_portal_implicit_zeros": "rodent abundance, empty plot-years",
    "R1_penguin_sex_clf": "penguin sex model", "R2_iris_species_clf": "iris species model",
    "R3_portal_species_clf": "rodent species model",
}

cell = defaultdict(list)
for r in rows:
    cell[(r["task"], r["arm"])].append(r)
rate = {k: 100 * np.mean([x["correct"] == "True" for x in v]) for k, v in cell.items()}
tasks = list(REFS)
moved = [t for t in tasks if rate[(t, "none")] < 90]
flat = [t for t in tasks if t not in moved]


def vals(task, arm):
    return [float(x["value"]) for x in cell[(task, arm)] if x["value"] not in ("", "None")]


def consensus(values, tol):
    """Largest group of values agreeing within the task's own tolerance."""
    if not values:
        return 0, 0, None
    groups = []
    for v in sorted(values):
        for g in groups:
            if abs(v - g[0]) <= tol:
                g.append(v); break
        else:
            groups.append([v])
    best = max(groups, key=len)
    return len(best), len(values), float(np.mean(best))


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

ends = sorted([(rate[(t, "skill")], SHORT[t], BLUE) for t in moved] +
              [(mean[2], "mean of all twelve tasks", ORANGE)])
gap, placed = 6.2, []
for y, txt, col in ends:
    if placed and y - placed[-1][0] < gap:
        y = placed[-1][0] + gap
    placed.append((y, txt, col))
# labels are pushed upward to separate them, which can carry the topmost ones off
# the panel when several tasks finish at 100; slide the whole stack back down
overshoot = max(0.0, placed[-1][0] - 103)
placed = [(y - overshoot, txt, col) for y, txt, col in placed]
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
show = moved                      # the five tasks with a genuinely open choice
ncol = 3
nrow = int(np.ceil((len(show) + 1) / ncol))
fig2, axes = plt.subplots(nrow, ncol, figsize=(12.4, 3.6 * nrow))
axes = np.atleast_1d(axes).ravel()

for ax2, t in zip(axes, show):
    ref, tol = REFS[t]["reference"], REFS[t]["tolerance"]
    rng = np.random.default_rng(5)
    # Window on the errors that carry the message. A run that is wrong by orders
    # of magnitude would otherwise compress the few-per-cent errors to a point,
    # so the span comes from the bulk of the returned values and the rest is
    # counted at the corner instead of drawn.
    allv = [v for arm in ARMS for v in vals(t, arm)]
    dev = np.abs(np.asarray(allv) - ref)
    span = max(3 * np.percentile(dev, 75), 5 * tol) if len(dev) else max(5 * tol, 1.0)
    xlo, xhi = ref - span, ref + span

    off = 0
    for y, arm in enumerate(ARMS[::-1]):        # specification at the bottom
        v = vals(t, arm)
        if not v:
            continue
        ax2.scatter(v, y + rng.normal(0, 0.055, len(v)), s=74, color=ACOL[arm],
                    alpha=0.82, edgecolor="white", lw=0.8, zorder=3)
        off += sum(1 for z in v if not (xlo <= z <= xhi))
        n, tot, modal = consensus(v, tol)
        if n / tot >= 0.5 and xlo <= modal <= xhi:
            ok = abs(modal - ref) <= tol
            ax2.text(modal, y - 0.30, f"{n} of {tot}", ha="center", va="top", fontsize=7.4,
                     color=GREEN if ok else ACOL[arm], fontweight="normal" if ok else "bold",
                     zorder=6, bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax2.axvline(ref, ls="--", lw=1.6, color=GREEN, zorder=2)
    ax2.set_xlim(xlo, xhi)
    if off:
        ax2.text(0.99, 0.985, f"{off} run{'s' if off > 1 else ''} off scale",
                 transform=ax2.transAxes, ha="right", va="top", fontsize=7.2,
                 color="#5b6570", style="italic")
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["with a\nspecification", "with a\nscript", "question\nalone"],
                        fontsize=8.2)
    ax2.set_ylim(-0.8, 2.55)
    ax2.set_title(SHORT[t], fontsize=9.6, loc="left", fontweight="bold", color=INK)
    ax2.set_xlabel("value returned", fontsize=8.6)
    ax2.tick_params(axis="both", labelsize=8)
    ax2.grid(axis="x", ls=":", alpha=0.4)
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.tick_params(axis="y", length=0)

for ax2 in axes[len(show):]:
    ax2.axis("off")
axes[len(show)].legend(handles=[
    Line2D([0], [0], ls="--", color=GREEN, lw=1.6, label="reference value"),
    Line2D([0], [0], marker="o", ls="", ms=8, color=ORANGE, label="question alone"),
    Line2D([0], [0], marker="o", ls="", ms=8, color=PURPLE, label="with a script"),
    Line2D([0], [0], marker="o", ls="", ms=8, color=BLUE, label="with a specification"),
], loc="center", frameon=False, fontsize=9.4,
    title="counts give how many runs agreed\non one value, in green where that\nvalue is the reference",
    title_fontsize=8.4)

fig2.tight_layout()
fig2.savefig(HERE / "fig2_consensus.png", dpi=200)
print("wrote fig1_trajectories.png and fig2_consensus.png")
