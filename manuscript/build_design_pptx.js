// An editable PowerPoint version of the design schematic.
//
// Every element is a native shape or text box, so the diagram can be rearranged,
// retyped and recoloured in PowerPoint. The task names, the kinds of open choice,
// the dataset behind each task and the run counts are read from the analysis
// summary, so the deck cannot describe a study other than the one that was run.
//
// The slide is the same physical size as main_study/fig_design.png (11 x 11.4
// inches), so point sizes and positions match the published figure exactly.
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const SUM = JSON.parse(fs.readFileSync(path.join(ROOT, "main_study/analysis_summary.json"), "utf8"));
const REFS = SUM.tasks, D = SUM.design;

const SW = 11.0, SH = 11.4;
const X = v => (v / 100) * SW;                 // data x  -> inches from the left
const Y = v => ((100 - v) / 100) * SH;         // data y  -> inches from the top
const WD = v => (v / 100) * SW;
const HT = v => (v / 100) * SH;

const INK = "1F2D3A", MUTED = "5B6570", RULE = "D5DBE0", PANEL = "F5F7F9";
const ORANGE = "D55E00", PURPLE = "CC79A7", BLUE = "0072B2", GREEN = "009E73";
const FONT = "Arial";

const DATA_COL = { iris: "E69F00", penguins: "56B4E9", portal: "6A9E5B", reef: "8C6BB1" };
const DATA_NAME = { iris: "iris", penguins: "penguins", portal: "rodents", reef: "reef fish" };
const FORKS = [
  ["aggregation", "Sampling unit", "what is averaged over\nbefore a mean is taken"],
  ["scope", "Scope", "pooled across groups,\nor computed within them"],
  ["missing", "Missing records", "absent values, and rows\nabsent altogether"],
  ["randomness", "Fitting a model", "the split, the seed,\nthe scaling"],
];
const SHORT = {
  A1_reef_biomass: "mean biomass per transect",
  A2_portal_abundance: "mean catch per plot-year",
  A3_portal_richness: "mean richness per plot-year",
  S1_iris_corr: "sepal length vs width",
  S2_penguin_bill_corr: "bill length vs depth",
  S3_portal_hf_weight_corr: "hindfoot vs weight",
  M1_penguin_gentoo_mass: "mass of female Gentoo",
  M2_portal_dm_weight: "weight of one species",
  M3_portal_implicit_zeros: "mean catch, counting\nempty plot-years",
  R1_penguin_sex_clf: "penguin sex classifier",
  R2_iris_species_clf: "iris species classifier",
  R3_portal_species_clf: "rodent species classifier",
};

const pres = new pptxgen();
pres.defineLayout({ name: "FIGURE", width: SW, height: SH });
pres.layout = "FIGURE";
pres.author = "Favoretto et al.";
pres.title = "Design of the specification study";
const s = pres.addSlide();

// ---- helpers -------------------------------------------------------------
// A rounded rectangle placed by its bottom-left corner, as in the matplotlib figure.
function box(x, y, w, h, o = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x: X(x), y: Y(y + h), w: WD(w), h: HT(h), rectRadius: o.r || 0.07,
    fill: o.fill ? { color: o.fill, transparency: o.transparency || 0 } : { color: "FFFFFF" },
    line: { color: o.line || RULE, width: o.lw === undefined ? 1 : o.lw },
  });
}
// Text centred on a point, in a box wide and tall enough not to wrap unexpectedly.
function tc(cx, cy, w, h, text, o = {}) {
  s.addText(text, {
    x: X(cx - w / 2), y: Y(cy + h / 2), w: WD(w), h: HT(h), margin: 0,
    align: "center", valign: "middle", fontFace: FONT, lineSpacingMultiple: 1.15,
    fontSize: o.size || 9, color: o.color || INK, bold: !!o.bold, italic: !!o.italic,
  });
}
// Text anchored at a left or right edge, centred vertically on cy.
function ta(x, cy, w, h, text, o = {}) {
  s.addText(text, {
    x: X(o.align === "right" ? x - w : x), y: Y(cy + h / 2), w: WD(w), h: HT(h), margin: 0,
    align: o.align || "left", valign: "middle", fontFace: FONT, lineSpacingMultiple: 1.15,
    fontSize: o.size || 9, color: o.color || INK, bold: !!o.bold, italic: !!o.italic,
  });
}
function hArrow(x1, x2, y) {
  s.addShape(pres.ShapeType.line, {
    x: X(x1), y: Y(y), w: WD(x2 - x1), h: 0,
    line: { color: MUTED, width: 1.2, endArrowType: "triangle" },
  });
}
const SPINE_X = 3.6;
function stage(y, n, title, sub) {
  s.addShape(pres.ShapeType.ellipse, {
    x: X(SPINE_X) - 0.125, y: Y(y) - 0.125, w: 0.25, h: 0.25,
    fill: { color: INK }, line: { color: "FFFFFF", width: 1.5 },
  });
  tc(SPINE_X, y, 6, 2.4, String(n), { size: 9, color: "FFFFFF", bold: true });
  ta(7.2, y, 80, 3.2, title, { size: 11.5, bold: true });
  if (sub) ta(7.2, y - 2.6, 85, 2.6, sub, { size: 8.6, color: MUTED });
}

// ---- the sequence spine --------------------------------------------------
s.addShape(pres.ShapeType.line, {
  x: X(SPINE_X), y: Y(96.8), w: 0, h: HT(96.8 - 3.9),
  line: { color: RULE, width: 1.6 },
});

// ---- 1  twelve tasks -----------------------------------------------------
stage(96.8, 1, "Twelve analysis tasks on four ecological datasets",
  "three tasks for each of four kinds of open choice, and no kind confined to one dataset");

const GX = 27.0, GY = 67.6, GW = 67.0, GH = 23.4;
const cw = GW / 3 - 1.5, ch = GH / 4 - 1.1;
FORKS.forEach(([fork, name, gloss], i) => {
  const y = GY + GH - (i + 1) * (ch + 1.1) + 1.1;
  ta(25.2, y + ch / 2 + 1.05, 22, 2.4, name, { size: 9.2, bold: true, align: "right" });
  ta(25.2, y + ch / 2 - 1.75, 22, 3.2, gloss, { size: 7.3, color: MUTED, align: "right" });
  Object.keys(REFS).filter(t => REFS[t].fork === fork).forEach((t, j) => {
    const x = GX + j * (cw + 1.5), ds = REFS[t].dataset;
    box(x, y, cw, ch, { fill: DATA_COL[ds], transparency: 85, line: DATA_COL[ds], lw: 1.1, r: 0.09 });
    tc(x + cw / 2, y + (SHORT[t].includes("\n") ? 3.15 : 2.85), cw - 0.6, 3.2, SHORT[t], { size: 7.7 });
    tc(x + cw / 2, y + 0.95, cw - 0.6, 1.6, DATA_NAME[ds], { size: 6.7, color: MUTED, italic: true });
  });
});

const counts = {};
Object.keys(REFS).forEach(t => { counts[REFS[t].dataset] = (counts[REFS[t].dataset] || 0) + 1; });
["iris", "penguins", "portal", "reef"].forEach((ds, k) => {
  const lx = GX + 1.0 + k * 15.5;
  box(lx, 64.2, 1.9, 1.9, { fill: DATA_COL[ds], transparency: 50, line: DATA_COL[ds], lw: 1, r: 0.05 });
  ta(lx + 2.7, 65.15, 13, 1.8, `${DATA_NAME[ds]} (${counts[ds]})`, { size: 7.5, color: MUTED });
});

// ---- 2  reference values -------------------------------------------------
stage(59.0, 2, "A reference value for each task",
  "so that a number returned by a run can be judged right or wrong");

const RY = 48.0;
box(27.0, RY, 18.5, 6.8, { fill: PANEL, line: RULE, r: 0.08 });
tc(36.25, RY + 3.4, 17, 3.4, "the quantity\nstated in words", { size: 8.3 });
hArrow(46.2, 50.3, RY + 3.4);
box(51.0, RY + 3.9, 20.5, 2.9, { line: GREEN, lw: 1.1, r: 0.07 });
tc(61.25, RY + 5.35, 19.5, 2.4, "implementation using a library", { size: 7.7, color: GREEN });
box(51.0, RY, 20.5, 2.9, { line: GREEN, lw: 1.1, r: 0.07 });
tc(61.25, RY + 1.45, 19.5, 2.4, "implementation as a direct loop", { size: 7.7, color: GREEN });
hArrow(72.2, 76.3, RY + 3.4);
box(77.0, RY, 17.0, 6.8, { line: GREEN, lw: 1.5, r: 0.08 });
tc(85.5, RY + 4.5, 16, 2.2, "accepted only", { size: 8.4, color: GREEN, bold: true });
tc(85.5, RY + 2.2, 16, 2.2, "where the two agree", { size: 8.4, color: GREEN });
tc(61.25, RY - 2.2, 60, 2.2, "the two implementations were written independently of one another",
  { size: 7.5, color: MUTED, italic: true });

// ---- 3  three conditions -------------------------------------------------
stage(40.0, 3, "Every task presented under three conditions",
  "the second gives the standing recommendation to share code a fair trial");

const CY = 25.2, CW = 21.0, CH = 10.6;
[
  [27.0, ORANGE, "Question alone", "the question, the column\nnames and the first rows"],
  [49.5, PURPLE, "With a script", "the same, and a working script\nfor a different task of\nthe same kind"],
  [72.0, BLUE, "With a specification", "the same, and the method\nwritten out in words,\nwith no code"],
].forEach(([x, col, name, what]) => {
  box(x, CY, CW, CH, { line: col, lw: 1.5, r: 0.08 });
  box(x, CY + CH - 2.6, CW, 2.6, { fill: col, transparency: 85, line: col, lw: 1.5, r: 0.08 });
  tc(x + CW / 2, CY + CH - 1.3, CW - 1, 2.2, name, { size: 9, color: col, bold: true });
  tc(x + CW / 2, CY + (CH - 2.6) / 2, CW - 1.5, 5.5, what, { size: 7.7 });
});
tc(60.0, CY - 2.3, 62, 2.2, "no run ever received a script that solves the task in front of it",
  { size: 7.5, color: MUTED, italic: true });

// ---- 4  runs -------------------------------------------------------------
stage(18.5, 4, "One uniform procedure for every run",
  `${D.reps} runs on each of ${D.n_models} models for every task and condition, `
  + `giving ${D.n_runs} runs in all`);

const SY = 8.2;
[["the model returns\na complete script", 27.0],
 ["the script is executed\nin the same environment", 50.0],
 ["the number it prints\nis recorded", 73.0]].forEach(([label, x]) => {
  box(x, SY, 21.0, 5.6, { fill: PANEL, line: RULE, r: 0.08 });
  tc(x + 10.5, SY + 2.8, 20, 3.6, label, { size: 8.1 });
});
[48.4, 71.4].forEach(x => hArrow(x, x + 1.4, SY + 2.8));

// ---- 5  analysis ---------------------------------------------------------
s.addShape(pres.ShapeType.ellipse, {
  x: X(SPINE_X) - 0.125, y: Y(3.9) - 0.125, w: 0.25, h: 0.25,
  fill: { color: INK }, line: { color: "FFFFFF", width: 1.5 },
});
tc(SPINE_X, 3.9, 6, 2.4, "5", { size: 9, color: "FFFFFF", bold: true });
box(7.2, 0.6, 86.8, 6.6, { line: INK, lw: 1.3, r: 0.08 });
ta(9.4, 5.5, 83, 2.2, "The task is the unit of replication.", { size: 9.2, bold: true });
ta(9.4, 2.9, 83, 4.2,
  "Each task gives one proportion per condition, the share of its runs that reached the reference, and the "
  + "conditions are compared across the twelve tasks with paired tests. Whether the runs agreed with one "
  + "another is measured separately from whether they were right.", { size: 8 });

s.addNotes("Editable version of Figure S1, the design schematic. Generated by "
  + "manuscript/build_design_pptx.js from main_study/analysis_summary.json. "
  + "Re-running that script overwrites this file, so save edits under a new name.");

pres.writeFile({ fileName: path.join(__dirname, "Design_Schematic_Editable.pptx") })
  .then(f => console.log("wrote " + f));
