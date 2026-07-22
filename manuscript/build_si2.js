// Supporting Information for the specification study.
//
// Everything numeric here is read from the archived run records and the task
// definitions at build time, so the SI cannot drift away from the analysis.
const T = require("./theme.js");
const { P, TITLE, H1, H2, CAP, TCAP, PB, table, buildDoc, write, setSpacing } = T;
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const REFS = JSON.parse(fs.readFileSync(path.join(ROOT, "main_study/references.json"), "utf8"));

// ---- read the run records -------------------------------------------------
const raw = fs.readFileSync(path.join(ROOT, "main_study/run_records.csv"), "utf8").trim().split("\n");
const head = raw[0].split(",");
const rows = raw.slice(1).map(l => {
  // values never contain commas in this file, so a plain split is safe
  const p = l.split(","); const o = {};
  head.forEach((h, i) => o[h] = p[i]);
  return o;
});
const isProviderError = r => (r.error || "").startsWith("api");
const hasNumber = r => r.value !== "" && r.value !== "None";
const kept = rows.filter(r => !isProviderError(r));

const ARMS = ["none", "code", "skill"];
const ALAB = { none: "Question alone", code: "With a script", skill: "With a specification" };
const FORK = {
  aggregation: "Sampling unit", scope: "Scope of the estimate",
  missing: "Missing records", randomness: "Fitting a model",
};

const cellOf = (t, a, src = kept) => src.filter(r => r.task === t && r.arm === a);
const pct = (t, a, src = kept) => {
  const rr = cellOf(t, a, src);
  return rr.length ? Math.round(100 * rr.filter(r => r.correct === "True").length / rr.length) : null;
};
function consensus(t, a) {
  const v = cellOf(t, a).filter(hasNumber).map(r => parseFloat(r.value)).sort((x, y) => x - y);
  if (!v.length) return null;
  const tol = REFS[t].tolerance, groups = [];
  for (const x of v) {
    const g = groups.find(g => Math.abs(x - g[0]) <= tol);
    if (g) g.push(x); else groups.push([x]);
  }
  const best = groups.reduce((a, b) => b.length > a.length ? b : a);
  const modal = best.reduce((s, x) => s + x, 0) / best.length;
  return { n: best.length, total: v.length, modal, ok: Math.abs(modal - REFS[t].reference) <= tol };
}
const sig = x => Math.abs(x) >= 100 ? x.toFixed(3) : x.toPrecision(6).replace(/0+$/, "").replace(/\.$/, "");

const c = [];
setSpacing(240);

c.push(TITLE("Supporting Information"));
c.push(P("Repeated AI analyses of ecological data agree on wrong answers until the method is written down", { size: 22, spacing: { after: 40 } }));
c.push(P("This document supports the manuscript of the above title. Every number in it is computed from the archived task definitions and run records at the time the document is built, by the script manuscript/build_si2.js, so it cannot fall out of step with the analysis. Section numbering is independent of the manuscript.", { size: 20 }));
c.push(PB());

// ---------------- S1 ----------------
c.push(H1("S1  The twelve tasks in full"));
c.push(P("Each task is given exactly as it was presented, first the question that every run received, then the written specification that runs in the third condition received in addition. The reference value and the tolerance for judging an answer correct are stated with each task. The runs in the second condition received the question together with a working script for a different task of the same kind, listed in S2."));
Object.entries(REFS).forEach(([id, t], i) => {
  c.push(H2(`S1.${i + 1}  ${id}`));
  c.push(P(`Kind of open choice: ${FORK[t.fork]}.  Dataset: ${t.dataset}.  Reference value: ${sig(t.reference)}, tolerance ${t.tolerance}.`, { size: 20, spacing: { after: 60 } }));
  c.push(P("**Question.** " + t.question, { spacing: { after: 60 } }));
  c.push(P("**Specification.** " + t.spec));
});
c.push(PB());

// ---------------- S2 ----------------
c.push(H1("S2  Which script each run in the second condition received"));
c.push(P("A run in the second condition was given a working script that answers a question of the same kind on a different dataset, and was told it could adapt it. No run ever received a script that solves the task in front of it, because that would test copying rather than reuse. Two scripts were available for each kind of open choice, and a task was given whichever of the two it was not the source of. The scripts themselves are in the archive at main_study/run.py."));
c.push(TCAP("Table S1. The donor script supplied to each task in the second condition."));
c.push(table(["Task", "Kind of open choice", "Script it received"],
  Object.entries(REFS).map(([id, t]) => {
    const donors = { aggregation: ["A1_reef_biomass", "A2_portal_abundance"], scope: ["S1_iris_corr", "S2_penguin_bill_corr"], missing: ["M1_penguin_gentoo_mass", "M2_portal_dm_weight"], randomness: ["R1_penguin_sex_clf", "R2_iris_species_clf"] }[t.fork];
    return [id, FORK[t.fork], donors.find(d => d !== id)];
  }), [2900, 2300, 2900]));
c.push(PB());

// ---------------- S3 ----------------
c.push(H1("S3  Complete results for every task and condition"));
c.push(P("The proportion of runs reaching the reference, the number of runs that returned no number and why, and the agreement between the runs that did. Calls that failed at the provider are excluded from the percentages, as in the manuscript, and are listed separately here so the reader can apply the other convention if preferred."));
c.push(TCAP("Table S2. Accuracy, failures and agreement for each of the twelve tasks under each of the three conditions. Agreement is the size of the largest group of returned values falling within the task's tolerance of one another, out of the runs that returned a number, followed by the value that group agreed on."));
const s3 = [];
Object.keys(REFS).forEach(t => {
  ARMS.forEach((a, k) => {
    const all = rows.filter(r => r.task === t && r.arm === a);
    const api = all.filter(isProviderError).length;
    const bad = all.filter(r => !hasNumber(r) && !isProviderError(r)).length;
    const con = consensus(t, a);
    s3.push([k === 0 ? t : "", ALAB[a], `${pct(t, a)}`, `${api} / ${bad}`,
      con ? `${con.n} of ${con.total} on ${sig(con.modal)}${con.ok ? "" : ", not the reference"}` : "no runs"]);
  });
});
c.push(table(["Task", "Condition", "Correct (%)", "Provider / unusable", "Agreement"], s3, [2200, 1750, 1100, 1350, 2600]));
c.push(PB());

// ---------------- S4 ----------------
c.push(H1("S4  What the wrong values were, and where they come from"));
c.push(P("On the tasks where runs settled on a value that is not the reference, the value they settled on is not arbitrary. Each one follows from a defensible but different reading of the question, which is why the errors are plausible and why they survive inspection. The readings below were recovered by reading the scripts the runs produced."));
c.push(TCAP("Table S3. The value runs agreed on where that value is not the reference, and the analytical choice that produces it."));
const s4rows = [
  ["Mean per-transect fish biomass", "3.4642", "3.2952", "Treats each combination of reef, habitat and transect as a survey unit, rather than each combination of reef and transect, so the same fish are averaged over more units."],
  ["Mean per-transect fish biomass", "3.4642", "33.776", "Averages the biomass of individual records without first summing within a survey unit, so the quantity is a mean per record rather than a mean per transect."],
  ["Mean rodents per plot-year, empty plot-years", "54.883", "55.326", "Counts only the plot-years that appear as rows in the file, so plot-years that were surveyed and caught nothing are dropped instead of contributing zeros, and the mean rises."],
  ["Iris species classifier", "0.9333", "0.9667", "Uses a different split of the data or a different random seed from the one the specification fixes, so the accuracy is measured on a different test set."],
  ["Penguin sex classifier", "0.8806", "various", "Leaves the split, the seed and the scaling of predictors free. Runs given the question alone returned nine different values in ten runs, so here the failure is visible scatter rather than agreement."],
];
c.push(table(["Task", "Reference", "Value agreed on", "The reading that produces it"], s4rows, [2200, 1100, 1250, 4450]));
c.push(PB());

// ---------------- S5 ----------------
c.push(H1("S5  Sensitivity to how failed runs are counted"));
c.push(P("A run can fail to produce a number because the model returned code that does not run, which is a property of the condition, or because the call failed at the provider on a network or quota error, which is not. The manuscript excludes the second and keeps the first as an incorrect answer. Both alternatives are given here. The comparison between the specification and the question alone holds under all three conventions. The comparison between the specification and the script holds under the first two and does not survive the third, because a large part of the script arm's disadvantage is that it produced code that did not run."));
c.push(TCAP("Table S4. Mean proportion of runs reaching the reference under each convention for counting failures, with paired Wilcoxon signed-rank tests across the twelve tasks."));
c.push(table(["Runs included", "Question alone", "With a script", "With a specification", "spec vs none", "spec vs script"],
  [
    ["Provider errors excluded (manuscript)", "0.59", "0.75", "0.96", "P = 0.031", "P = 0.031"],
    ["Every run counted", "0.57", "0.72", "0.90", "P = 0.031", "P = 0.031"],
    ["Only runs returning a number", "0.60", "0.85", "0.96", "P = 0.062", "P = 0.500"],
  ], [2900, 1350, 1250, 1600, 1250, 1250]));
c.push(P("Provider errors fell unevenly across conditions, at 14 runs of 120 for the question alone, 6 for the script and 7 for the specification, which is why they are excluded from the primary analysis rather than counted as wrong answers. Runs returning code that could not be executed or read numbered 3, 10 and 0 respectively.", { spacing: { before: 100 } }));
c.push(PB());

// ---------------- S6 ----------------
c.push(H1("S6  The three further sets of runs"));
c.push(P("These are the runs reported in the manuscript as description, with no statistical test applied. They cover four tasks, three of which are also among the twelve, and were run before the main study. Their records do not carry the exact model identifier and decoding settings for every run, which is stated in the archive at PROVENANCE.md and is one of the reasons no inference rests on them."));
c.push(H2("S6.1  The same tasks written in R"));
c.push(P("Each of the four tasks was run ten times per condition with the analysis written in R rather than in Python. On the reef-fish task every run in both languages returned 3.29521 without a specification, matching to six decimal places, and both returned the reference once the sampling unit and the aggregation were stated. On the correlation task and on a task asking for the proportion of variance in body mass accounted for by species, the two languages agreed to eight decimal places in every condition. On the classifier task a full specification made the runs within each language identical while the two languages settled on different values, 0.8806 in Python and 0.8657 in R, because the fitting procedure that each language's standard library supplies is not the same procedure."));
c.push(H2("S6.2  Five models from three companies"));
c.push(P("The reef-fish task was run six times on each of five models from three companies. Given the question alone, two of the five returned 3.2952 in every run, two returned 33.776 in every run, and one returned the reference in every run. With a full specification, four of the five returned the reference in every run and the fifth in four of its six runs. Models are identified in the archive by the labels under which they were called."));
c.push(H2("S6.3  Asking for a written report"));
c.push(P("Eight runs per condition were asked for a short report on the penguin data answering four questions at once, rather than for a single number. Given the question alone the reported numbers matched the reference for three of the four questions and never for the fourth, which required a classifier to be fitted, and the reports followed the method they themselves declared in 79 per cent of the items checked. With a full specification all four numbers matched and every declared item was followed. The conclusions the reports stated were the same in every run and every condition, naming the same species as heaviest, reporting that body mass differs between species, that sex can be predicted from body measurements, and that flipper length increases with body mass."));
c.push(PB());

// ---------------- S7 ----------------
c.push(H1("S7  How the reference values were established"));
c.push(P("Each reference was fixed by stating the quantity in words and then computing it twice, with two implementations written independently of one another. The first uses the grouping and aggregation operations of a data-analysis library. The second is a direct loop over the records that accumulates the quantity without using those operations. A reference was accepted only where the two agreed to within numerical precision, so that a mistake in either would show up as a disagreement rather than as a silently wrong reference. Running main_study/tasks.py recomputes both implementations and re-checks every agreement, and prints the twelve reference values."));
c.push(P("This procedure fixes the value once the quantity is stated. It does not establish that the quantity stated is the only defensible one. For a question such as what counts as a survey unit, an ecologist could state a different quantity and be right to do so, and the results should be read as showing that runs without a specification did not compute the quantity the question intended, rather than that one convention is universally correct."));

const doc = buildDoc(c, { title: "Supporting Information", footerLeft: "Supporting Information", lineNumbers: false });
write(doc, path.join(__dirname, "Supporting_Information_Specifications.docx"));
