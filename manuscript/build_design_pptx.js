// An editable PowerPoint version of the design schematic.
//
// Every element is a native shape or text box, so the diagram can be rearranged,
// retyped and recoloured in PowerPoint. The task names, the kinds of open choice,
// the dataset behind each task and the run counts are read from the analysis
// summary, so the deck cannot describe a study other than the one that was run.
//
// The slide is the same physical size as main_study/fig_design.png (9.6 x 13.0
// inches), so point sizes and positions match the published figure exactly.
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const SUM = JSON.parse(fs.readFileSync(path.join(ROOT, "main_study/analysis_summary.json"), "utf8"));
const REFS = SUM.tasks, D = SUM.design;

const SW = 9.6, SH = 13.0;
const X = v => (v / 100) * SW;                 // data x  -> inches from the left
const Y = v => ((100 - v) / 100) * SH;         // data y  -> inches from the top
const WD = v => (v / 100) * SW;
const HT = v => (v / 100) * SH;

const INK = "1F2D3A", MUTED = "5B6570", RULE = "D5DBE0", PANEL = "F5F7F9";
const ORANGE = "D55E00", PURPLE = "CC79A7", BLUE = "0072B2", GREEN = "009E73";
const FONT = "Arial";
// one place to change the type scale, matching main_study/make_design_figure.py
const FS = { stage: 14.5, sub: 11.0, row: 11.5, gloss: 9.2, task: 10.0, data: 8.5,
             legend: 9.5, ref: 10.5, refbox: 9.8, note: 9.5, cond: 11.5, condbody: 10.0,
             step: 10.2, headline: 11.5, body: 10.0 };

const DATA_COL = { iris: "E69F00", penguins: "56B4E9", portal: "6A9E5B", reef: "8C6BB1" };
const DATA_NAME = { iris: "iris", penguins: "penguins", portal: "rodents", reef: "reef fish" };
const FORKS = [
  ["aggregation", "Sampling unit", "what is averaged over\nbefore a mean is taken"],
  ["scope", "Scope", "pooled across groups,\nor computed within them"],
  ["missing", "Missing records", "absent values, and rows\nabsent altogether"],
  ["randomness", "Fitting a model", "the split, the seed,\nthe scaling"],
];
const SHORT = {
  A1_reef_biomass: "mean biomass\nper transect",
  A2_portal_abundance: "mean catch\nper plot-year",
  A3_portal_richness: "mean richness\nper plot-year",
  S1_iris_corr: "sepal length\nvs width",
  S2_penguin_bill_corr: "bill length\nvs depth",
  S3_portal_hf_weight_corr: "hindfoot\nvs weight",
  M1_penguin_gentoo_mass: "mass of\nfemale Gentoo",
  M2_portal_dm_weight: "weight of\none species",
  M3_portal_implicit_zeros: "mean catch, counting\nempty plot-years",
  R1_penguin_sex_clf: "penguin sex\nclassifier",
  R2_iris_species_clf: "iris species\nclassifier",
  R3_portal_species_clf: "rodent species\nclassifier",
};

const pres = new pptxgen();
pres.defineLayout({ name: "FIGURE", width: SW, height: SH });
pres.layout = "FIGURE";
pres.author = "Anonymous";
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
    align: "center", valign: "middle", fontFace: FONT, lineSpacingMultiple: 1.2,
    fontSize: o.size || 9, color: o.color || INK, bold: !!o.bold, italic: !!o.italic,
  });
}
// Text anchored at a left or right edge, centred vertically on cy.
function ta(x, cy, w, h, text, o = {}) {
  s.addText(text, {
    x: X(o.align === "right" ? x - w : x), y: Y(cy + h / 2), w: WD(w), h: HT(h), margin: 0,
    align: o.align || "left", valign: "middle", fontFace: FONT, lineSpacingMultiple: 1.2,
    fontSize: o.size || 9, color: o.color || INK, bold: !!o.bold, italic: !!o.italic,
  });
}
function hArrow(x1, x2, y) {
  s.addShape(pres.ShapeType.line, {
    x: X(x1), y: Y(y), w: WD(x2 - x1), h: 0,
    line: { color: MUTED, width: 1.2, endArrowType: "triangle" },
  });
}
const SPINE_X = 4.0;
function stage(y, n, title, sub) {
  s.addShape(pres.ShapeType.ellipse, {
    x: X(SPINE_X) - 0.135, y: Y(y) - 0.135, w: 0.27, h: 0.27,
    fill: { color: INK }, line: { color: "FFFFFF", width: 1.5 },
  });
  tc(SPINE_X, y, 6, 2.2, String(n), { size: FS.sub, color: "FFFFFF", bold: true });
  ta(8.0, y, 82, 2.6, title, { size: FS.stage, bold: true });
  if (sub) ta(8.0, y - 2.7, 88, 2.4, sub, { size: FS.sub, color: MUTED });
}

// ---- the sequence spine --------------------------------------------------
s.addShape(pres.ShapeType.line, {
  x: X(SPINE_X), y: Y(97.5), w: 0, h: HT(97.5 - 3.3),
  line: { color: RULE, width: 1.8 },
});

// ---- 1  twelve tasks -----------------------------------------------------
stage(97.5, 1, "Twelve analysis tasks on four ecological datasets",
  "three tasks for each of four kinds of open choice, and no kind confined to one dataset");

const GX = 29.0, GY = 68.0, GW = 66.0, GH = 21.8;
const cw = GW / 3 - 1.4, ch = GH / 4 - 1.05;
FORKS.forEach(([fork, name, gloss], i) => {
  const y = GY + GH - (i + 1) * (ch + 1.05) + 1.05;
  ta(27.4, y + ch / 2 + 1.15, 24, 2.2, name, { size: FS.row, bold: true, align: "right" });
  ta(27.4, y + ch / 2 - 1.55, 24, 3.0, gloss, { size: FS.gloss, color: MUTED, align: "right" });
  Object.keys(REFS).filter(t => REFS[t].fork === fork).forEach((t, j) => {
    const x = GX + j * (cw + 1.4), ds = REFS[t].dataset;
    box(x, y, cw, ch, { fill: DATA_COL[ds], transparency: 85, line: DATA_COL[ds], lw: 1.2, r: 0.08 });
    tc(x + cw / 2, y + 2.95, cw - 0.6, 3.0, SHORT[t], { size: FS.task });
    tc(x + cw / 2, y + 0.95, cw - 0.6, 1.5, DATA_NAME[ds], { size: FS.data, color: MUTED, italic: true });
  });
});

const counts = {};
Object.keys(REFS).forEach(t => { counts[REFS[t].dataset] = (counts[REFS[t].dataset] || 0) + 1; });
["iris", "penguins", "portal", "reef"].forEach((ds, k) => {
  const lx = GX + 0.5 + k * 16.0;
  box(lx, 64.5, 1.9, 1.5, { fill: DATA_COL[ds], transparency: 50, line: DATA_COL[ds], lw: 1, r: 0.05 });
  ta(lx + 2.8, 65.25, 14, 1.7, `${DATA_NAME[ds]} (${counts[ds]})`, { size: FS.legend, color: MUTED });
});

// ---- 2  reference values -------------------------------------------------
stage(59.0, 2, "A reference value for each task",
  "so that a number returned by a run can be judged right or wrong");

const RY = 48.0;
box(29.0, RY, 17.0, 6.0, { fill: PANEL, line: RULE, r: 0.08 });
tc(37.5, RY + 3.0, 16, 3.2, "the quantity\nstated in words", { size: FS.ref });
hArrow(46.8, 49.2, RY + 3.0);
box(50.0, RY + 3.4, 23.5, 2.6, { line: GREEN, lw: 1.2, r: 0.07 });
tc(61.75, RY + 4.7, 23, 2.2, "implementation using a library", { size: FS.refbox, color: GREEN });
box(50.0, RY, 23.5, 2.6, { line: GREEN, lw: 1.2, r: 0.07 });
tc(61.75, RY + 1.3, 23, 2.2, "implementation as a direct loop", { size: FS.refbox, color: GREEN });
hArrow(74.3, 76.7, RY + 3.0);
box(77.5, RY, 17.5, 6.0, { line: GREEN, lw: 1.6, r: 0.08 });
tc(86.25, RY + 4.1, 17, 2.0, "accepted only", { size: FS.ref, color: GREEN, bold: true });
tc(86.25, RY + 1.9, 17, 2.0, "where the two agree", { size: FS.ref, color: GREEN });
tc(62.0, RY - 2.3, 62, 2.0, "the two implementations were written independently of one another",
  { size: FS.note, color: MUTED, italic: true });

// ---- 3  three conditions -------------------------------------------------
stage(39.5, 3, "Every task presented under three conditions",
  "the second gives the standing recommendation to share code a fair trial");

const CY = 25.0, CW = 21.5, CH = 10.0;
[
  [29.0, ORANGE, "Question alone", "the question, the column\nnames and the first rows"],
  [51.5, PURPLE, "With a script", "the same, and a working\nscript for a different task\nof the same kind"],
  [74.0, BLUE, "With a specification", "the same, and the method\nwritten out in words,\nwith no code"],
].forEach(([x, col, name, what]) => {
  box(x, CY, CW, CH, { line: col, lw: 1.6, r: 0.08 });
  box(x, CY + CH - 2.4, CW, 2.4, { fill: col, transparency: 85, line: col, lw: 1.6, r: 0.08 });
  tc(x + CW / 2, CY + CH - 1.2, CW - 1, 2.0, name, { size: FS.cond, color: col, bold: true });
  tc(x + CW / 2, CY + (CH - 2.4) / 2, CW - 1.5, 5.6, what, { size: FS.condbody });
});
tc(62.0, CY - 2.3, 64, 2.0, "no run ever received a script that solves the task in front of it",
  { size: FS.note, color: MUTED, italic: true });

// ---- 4  runs -------------------------------------------------------------
stage(19.0, 4, "One uniform procedure for every run",
  `${D.reps} runs on each of ${D.n_models} models for every task and condition, `
  + `giving ${D.n_runs} runs in all`);

const SY = 8.8;
[["the model returns\na complete script", 29.0],
 ["the script is executed\nin the same environment", 51.5],
 ["the number it prints\nis recorded", 74.0]].forEach(([label, x]) => {
  box(x, SY, 20.0, 5.0, { fill: PANEL, line: RULE, r: 0.08 });
  tc(x + 10.0, SY + 2.5, 19.5, 3.2, label, { size: FS.step });
});
[49.3, 71.8].forEach(x => hArrow(x, x + 2.0, SY + 2.5));

// ---- 5  analysis ---------------------------------------------------------
s.addShape(pres.ShapeType.ellipse, {
  x: X(SPINE_X) - 0.135, y: Y(3.3) - 0.135, w: 0.27, h: 0.27,
  fill: { color: INK }, line: { color: "FFFFFF", width: 1.5 },
});
tc(SPINE_X, 3.3, 6, 2.2, "5", { size: FS.sub, color: "FFFFFF", bold: true });
box(8.0, 0.4, 87.0, 7.4, { line: INK, lw: 1.4, r: 0.08 });
ta(10.0, 6.4, 84, 2.0, "The task is the unit of replication.", { size: FS.headline, bold: true });
ta(10.0, 3.0, 84, 4.6,
  "Each task gives one proportion per condition, the share of its runs that reached the reference, and the "
  + "conditions are compared across the twelve tasks with paired tests. Whether runs agreed with one "
  + "another is measured separately from whether they were right.", { size: FS.body });

s.addNotes("Editable version of Figure 1, the design schematic. Generated by "
  + "manuscript/build_design_pptx.js from main_study/analysis_summary.json. "
  + "Re-running that script overwrites this file, so save edits under a new name.");

pres.writeFile({ fileName: path.join(__dirname, "Design_Schematic_Editable.pptx") })
  .then(f => console.log("wrote " + f));
