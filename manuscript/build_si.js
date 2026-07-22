const T = require("./theme.js");
const { P, TITLE, H1, H2, H3, CAP, BULLET, NUM, REFP, HR, GAP, PB, img, buildDoc, write, rt, setSpacing, COLORS } = T;
setSpacing(240); // supporting information is single-spaced
const docx = require("docx");
const { Paragraph, TextRun, Table, TableRow, TableCell, BorderStyle, WidthType, ShadingType } = docx;
const fs = require("fs"), path = require("path");
const DIR = path.resolve(__dirname, "..");
const RES = path.join(DIR, "results");
const rd = (p) => fs.readFileSync(p, "utf8");

// compact table with adjustable font (for dense SI tables)
function ctable(headers, rows, colWidths, sz = 16) {
  const accent = { style: BorderStyle.SINGLE, size: 6, color: COLORS.TEAL };
  const sub = { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE };
  const hc = (t, w) => new TableCell({ borders: { bottom: accent }, width: { size: w, type: WidthType.DXA }, margins: { top: 70, bottom: 70, left: 90, right: 90 }, shading: { fill: COLORS.FILL, type: ShadingType.CLEAR }, children: [new Paragraph({ spacing: { line: 250 }, children: rt(t, { size: sz + 1, bold: true, color: COLORS.HEAD }) })] });
  const bc = (t, w) => new TableCell({ borders: { bottom: sub }, width: { size: w, type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 }, children: [new Paragraph({ spacing: { line: 245 }, children: rt(String(t), { size: sz }) })] });
  const trs = [new TableRow({ tableHeader: true, children: headers.map((h, i) => hc(h, colWidths[i])) })];
  rows.forEach(r => trs.push(new TableRow({ children: r.map((cc, i) => bc(cc, colWidths[i])) })));
  return new Table({ width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: colWidths, rows: trs });
}
// monospace verbatim block: one paragraph per line
function mono(text) {
  return text.replace(/\r/g, "").split("\n").map(line =>
    new Paragraph({ spacing: { line: 235, after: 0 }, shading: { fill: "F7F7F8", type: ShadingType.CLEAR },
      children: [new TextRun({ text: line || " ", font: "Courier New", size: 15, color: "1F2937" })] }));
}
function promptBlock(id, title, folder = "prompts") {
  const out = [H3(`${id} (${title})`)];
  mono(rd(path.join(DIR, folder, `${id}.txt`))).forEach(p => out.push(p));
  out.push(GAP(80));
  return out;
}

const c = [];
c.push(TITLE("Supporting Information"));
c.push(P("**Reusable instructions make AI ecological analyses reproducible when they remove analytical choices**", { spacing: { after: 40 } }));
c.push(P("Supporting Information for a manuscript prepared for double-anonymous review. Target journal: Methods in Ecology and Evolution.", { size: 20 }));
c.push(P("Contents: S1 Earlier work we drew on · S2 Experiment 1 prompts · S3 Full results and statistics · S4 Additional figures · S5 Software, data, and archive audit · S6 Experiment 2 report materials and results · S7 Proposed Skill Evidence Manifest · S8 Token cost of instruction detail · S9 Replication across models and providers.", { size: 20 }));
c.push(HR());

// ---- S1  Earlier work ----
c.push(H1("S1  Earlier work we drew on"));
c.push(P("We looked for earlier evidence on AI skills and on the reproducibility of ecological and computational analyses, and read the studies below closely. The first table gives each study and how it bears on our question. The second groups the parts of a skill by the kind of evidence that supports them, which the experiment then refines."));
c.push(H2("Table S1. Studies we drew on (n = 19)"));
c.push(ctable(
  ["Study (year)", "Venue", "Domain", "Skill-like feature", "Output-reproducibility finding", "Evidence"],
  [
    ["Gallois et al. (2025)", "Methods Ecol. Evol.", "Ecology (birds)", "Bespoke quantitative LLM querying data", "Roadmap and case study stressing iterative evaluation", "Indirect"],
    ["Dorm et al. (2026)", "Ecological Informatics", "Ecology (species)", "General LLM benchmark", "Performance varied substantially across five ecological tasks", "Indirect"],
    ["Yagubyan (2026, pre)", "arXiv", "Agents", "Repeated identical tool-calling runs", "Behavioural reproducibility imperfect; tool/order/arg drift", "Direct"],
    ["LongDS-Bench (2026, pre)", "arXiv", "Data analysis", "Long-horizon agentic analysis", "High failure/variance on multi-step tasks", "Direct"],
    ["DataSciBench (2025, pre)", "arXiv", "Data science", "LLM data-science agents", "Success and consistency vary; structured eval needed", "Direct"],
    ["ReliabilityBench (2026, pre)", "arXiv", "Agents", "Reliability under input perturbation", "Output reliability degrades under variation", "Direct"],
    ["ARA (2026, pre)", "arXiv", "Peer review", "Agentic reproducibility assessment", "Agents can assess reproducibility (feasibility)", "Direct"],
    ["He et al. (2024)", "arXiv/NAACL", "LLM", "Prompt template / formatting", "Up to 40% performance swing from format alone", "Direct"],
    ["Wang et al. (2023)", "ICLR", "LLM", "Self-consistency (multi-run vote)", "Aggregating runs stabilises outputs", "Direct"],
    ["Yuan et al. (2025, pre)", "arXiv", "LLM", "Batch-invariant kernels; precision", "Bit-identical over 1,000 runs at ~61.5% throughput cost", "Direct"],
    ["Rollout Cards (2026, pre)", "arXiv", "Agents", "Complete rollout and reporting record", "Preserved rollouts expose score sensitivity and dropped runs", "Direct"],
    ["Culina et al. (2020)", "PLOS Biology", "Ecology", "Code availability", "Code available for a minority; key reproduction barrier", "Indirect"],
    ["Kellner et al. (2025)", "Ecology", "Ecology (SDM/abund.)", "Functional code", "Functional R code rare; re-execution often fails", "Indirect"],
    ["Kambouris et al. (2024)", "PLOS ONE", "EcoEvo meta-analyses", "Shared data + code", "15% shared both; 27% to 73% of 26 reproduced by strictness", "Indirect"],
    ["Cooper et al. (2026)", "Methods Ecol. Evol.", "Ecology (BES)", "Data/code archiving", "97% archived data but only 35% archived code", "Indirect"],
    ["O'Dea et al. (2021)", "Biological Reviews", "EcoEvo", "PRISMA-EcoEvo checklist", "Guideline use (~16%) linked to higher reporting quality", "Indirect"],
    ["Zurell et al. (2020)", "Ecography", "Ecology (SDM)", "ODMAP structured protocol", "Structured protocol supports documentation & reproduction", "Indirect"],
    ["Trisovic et al. (2022)", "Scientific Data", "General (R code)", "Environment standardisation", "Re-execution 26% to 44%; environment fix helped most", "Indirect"],
    ["Pimentel et al. (2019)", "MSR", "General (notebooks)", "Execution order / hidden state", "24.1% run; only 4.0% reproduce results", "Indirect"],
  ],
  [1500, 1150, 1200, 1900, 2910, 700], 14
));
c.push(GAP(120));
c.push(H2("Table S2. Skill parts ranked by their expected contribution to output reproducibility, from the literature"));
c.push(ctable(
  ["Skill characteristic", "Mechanism for output reproducibility", "Evidence"],
  [
    ["Input/output contract + explicit step sequence", "Fixes what is produced and in what order; removes ambiguity behind execution and notebook failures", "Strong (indirect + analogical)"],
    ["Tool-use contract", "Constrains how data and tools are called, cutting agent run-to-run drift", "Strong (LLM/agent evidence)"],
    ["Environment & provenance specification", "Pins the runtime and records what produced each result", "Strong (Trisovic; workflows)"],
    ["Validation checklist + failure-mode warnings", "Forces completeness and catches known error patterns", "Moderate (reporting standards)"],
    ["Worked examples", "Guide the model like a novice learner, reducing variance in approach", "Moderate (learning sciences)"],
    ["Domain references / metadata", "Aid trust, reuse, and correctness more than bit-level reproducibility", "Moderate (FAIR)"],
  ],
  [3000, 4560, 1800], 16
));
c.push(P("Note. The experiment (main Section 4) refines this ranking. The parts that mattered most were the input and method contract and the random settings (seed, split, scaling). Length on its own gave no benefit, and the part that matters depends on the task.", { size: 19, spacing: { before: 120 } }));
c.push(PB());

// ---- S5 ----
c.push(H1("S2  Experiment prompts (full text)"));
c.push(P("The 40 prompt files below are the variable we changed, 20 for Python and 20 for R. Within each task and language, the four skilled levels add structure step by step, so each level contains the one before it. Each file also sets a fixed output format, and agents ran the analysis and returned the value named at the foot of the file. The R files name R functions (cor, glm, aov, and dplyr) in place of the Python ones, but the task and the skill ladder are the same. The text is shown exactly as it was given to the agents."));
c.push(H2("S2.1  Python prompts"));
const TN = { T1: "iris sepal correlation", T2: "penguin sex classifier", T3: "penguin body-mass ANOVA", T4: "LTEM reef-fish biomass" };
const CN = { C0: "C0 none", C1: "C1 basic", C2: "C2 contract", C3: "C3 +controls", C4: "C4 full" };
for (const t of ["T1", "T2", "T3", "T4"]) {
  c.push(H2(`Task ${t} (${TN[t]})`));
  for (const cc of ["C0", "C1", "C2", "C3", "C4"]) promptBlock(`${t}_${cc}`, CN[cc], "prompts").forEach(p => c.push(p));
  c.push(PB());
}
c.push(H2("S2.2  R prompts"));
for (const t of ["T1", "T2", "T3", "T4"]) {
  c.push(H2(`Task ${t} (${TN[t]})`));
  for (const cc of ["C0", "C1", "C2", "C3", "C4"]) promptBlock(`${t}_${cc}`, CN[cc], "prompts_r").forEach(p => c.push(p));
  c.push(PB());
}

// ---- S6 ----
c.push(H1("S3  Full results and statistics"));
c.push(H2("Table S3. Per-cell reproducibility and validity in Python (10 runs per cell)"));
const summ = JSON.parse(rd(path.join(RES, "summary_v2.json"))).cells;
const rowsS6 = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const s = summ[`${t}_${cc}`]; if (!s) continue;
  rowsS6.push([`${t} ${cc}`, s.n, s.sd.toFixed(4), s.cv.toFixed(3), s.n_distinct,
    (s.modal_agreement_rate * 100).toFixed(0) + "%",
    (s.validity_rate * 100).toFixed(0) + "%", s.abs_err_ref.toFixed(4)]);
}
c.push(ctable(["Cell", "n", "SD", "CV", "#dist.", "modal agree", "valid", "|Δref|"], rowsS6,
  [1350, 650, 1200, 1050, 1000, 1550, 1100, 1460], 15));

const XL = JSON.parse(rd(path.join(RES, "cross_language_summary.json")));
c.push(GAP(120));
c.push(H2("Table S4. Per-cell reproducibility and validity in R (10 runs per cell)"));
const rowsR = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const s = XL.within[`r_${t}_${cc}`]; if (!s) continue;
  rowsR.push([`${t} ${cc}`, s.n, s.sd.toFixed(4), s.n_distinct,
    (s.agreement * 100).toFixed(0) + "%", (s.valid * 100).toFixed(0) + "%"]);
}
c.push(ctable(["Cell", "n", "SD", "#distinct", "modal agree", "valid"], rowsR, [1760, 900, 1700, 1700, 1650, 1650], 15));
c.push(GAP(120));
c.push(H2("Table S5. Cross-implementation comparison (Python modal value vs R modal value)"));
const rowsX = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const x = XL.cross[`${t}_${cc}`]; if (!x) continue;
  rowsX.push([`${t} ${cc}`, x.py.toFixed(4), x.r.toFixed(4), x.diff.toFixed(4), x.agree ? "Yes" : "No"]);
}
c.push(ctable(["Cell", "Python", "R", "|difference|", "Agree within tolerance?"], rowsX, [1560, 1700, 1700, 1900, 2500], 15));
c.push(P("The deterministic tasks (T1, T3, T4) give the same value in Python and R at every level, including the wrong value for T4 before the contract. The classifier (T2) does not match across languages, because the two use different models and random number generators.", { size: 20, spacing: { before: 100 } }));
c.push(GAP(120));
c.push(H2("Task-specific contrasts (Python)"));
c.push(BULLET("**T2 modal agreement.** Low skill (C0 to C2) 16 of 30, high skill (C3 and C4) 20 of 20. Exploratory Fisher exact P = 2.2×10⁻⁴. Pooled low-skill SD = 0.0086; high-skill SD = 0.0000."));
c.push(BULLET("**T2 validity against the reference.** Low skill 12 of 30, high skill 20 of 20. Fisher's exact P = 8.4×10⁻⁶."));
c.push(BULLET("**T4 validity against the reference.** Before the contract (C0 and C1) 0 of 20, with the contract and above (C2 to C4) 30 of 30. Fisher's exact P = 2.1×10⁻¹⁴. Run to run reproducibility was 100% at every level."));
c.push(P("R showed the same transition points but not the same effect size. T2 low-level modal agreement was 26/30 in R versus 16/30 in Python; C3 and C4 reached 20/20 in both languages. No R T2 run at C0–C2 matched the R reference, whereas every C3–C4 run did. T4 was reproducible but invalid until C2 in both languages. The Fisher tests above describe selected Python contrasts and do not support population-wide inference over tasks. The full scalar archives contain 400 records with values, free-text methods, parameters, and sample sizes, but no exact model or decoding metadata (S5).", { size: 20, spacing: { before: 120 } }));
c.push(PB());

// ---- S7 ----
c.push(H1("S4  Additional figures"));
c.push(img(path.join(RES, "fig1_value_strips.png"), 600, 400, "Value strips"));
c.push(CAP("Figure S1. All 200 Python outputs by task and level (10 runs per cell, with horizontal jitter). The dashed line shows the reference. T1 and T3 fall on the reference at every level, T2 scatters until C3, and T4 sits consistently away from the reference (3.2952) at C0 and C1 and moves to the reference (3.4642) from C2."));
c.push(img(path.join(RES, "fig4_python_vs_r.png"), 600, 400, "Python versus R"));
c.push(CAP("Figure S2. All Python (blue) and R (red) outputs by skill level, 10 runs per cell per language. Dashed lines show the reference for each language. T1, T3, and T4 sit on one shared line in both languages, while T2 sits on two different lines because the contracts use language-native estimators and split generators. Main-text Figure 2 instead summarizes the task-specific before-to-after transitions."));
c.push(img(path.join(RES, "fig3_heatmaps.png"), 600, 210, "Complete agreement and validity heatmaps"));
c.push(CAP("Figure S3. Complete Python-arm modal-agreement and reference-validity matrices for all four tasks and five instruction levels. The many ceiling cells obscure the binding transitions in a main-text display but document the full design: T1 and T3 are ceiling tasks, T2 reaches 100% agreement and validity at C3, and T4 is consistently wrong until C2."));

// ---- S8 ----
c.push(H1("S5  Software environment, code and data availability"));
c.push(P("**Environment.** Python 3 (scikit-learn 1.9.0, scipy 1.16.3, numpy 2.4.6, pandas, matplotlib) and R (stats, dplyr, readr). The archival records do not retain the exact LLM, provider release, harness version, decoding settings, or exact R version used by the agents; these must not be reconstructed retrospectively."));
c.push(P("**Datasets.** iris (150 rows; built into R and from scikit-learn); penguins.csv (344 rows; Palmer Penguins, Horst et al. 2020); and a restricted LTEM Cabo Pulmo 2023 file (2,798 reef-fish records, 10 reefs, 41 transect units). The LTEM CSV is excluded from the public repository and available on request."));
c.push(P("**Materials archived (OSF/Zenodo on submission).**"));
c.push(BULLET("references.json and references_R.json hold the design and the reference values for each language."));
c.push(BULLET("prompts/ and prompts_r/ hold the 20 Python and 20 R condition prompts (S2)."));
c.push(BULLET("run_experiment.workflow.js and run_experiment_r.workflow.js orchestrated the 200 Python and 200 R runs (4 tasks by 5 levels by 10 replicates each), with up to 3 retries per cell and enforced structured output."));
c.push(BULLET("results_v2.json and results_v2_R.json hold every run's structured output (200 records each)."));
c.push(BULLET("analyze_v2.py scores the Python arm; analyze_cross_language.py scores R and the Python-versus-R comparison and draws the comparison figure."));
c.push(BULLET("generate_prompts.py and generate_prompts_r.py regenerate the prompt files; data/ publicly holds iris, Palmer Penguins, reference files, and the LTEM access note."));
c.push(BULLET("audit_archive.py checks cell counts, prompt counts, report retention, provenance fields, and restricted-data status; PROVENANCE.md records known gaps."));
c.push(BULLET("repository_standard/ contains the proposed Skill Evidence Manifest schema, validator, and a worked T2 skill entry."));
c.push(P("These materials are provided for peer review in an anonymised repository, the link to which is shared with the editors; the repository will be de-anonymised and archived with a DOI on acceptance. The restricted reef fish file for Task T4 is not included and is available on request.", { spacing: { before: 100 } }));
c.push(P("The deterministic downstream layer regenerates tables, figures, and documents from the archival JSON. Agent-level rerunning requires the original harness and restricted T4 file and will not exactly reconstruct the historical configuration because model provenance was not retained. Updated workflows require and store provenance for future run sets.", { spacing: { before: 100 } }));

// ---- S9 (Experiment 2) ----
c.push(H1("S6  Experiment 2 materials: report prompts and results"));
c.push(P("The second experiment asked agents to write a short data report on the Palmer Penguins dataset and then graded each report with a second judge agent. Two report versions were used, a standard report with four common analyses and a hard report with six analyses that each have a real method fork. Each version had three conditions (no skill, a structure-only skill, and a full methods skill) with 8 reports per condition. The judge scored each report against one fixed rubric, the same for every condition."));
c.push(P("Important audit limitation: the archival JSON retains structured numeric fields and judge grades but not the full report text supplied to the judge. The grades cannot be independently rechecked from this archive. Corrected workflows now retain report_md and generator/judge provenance; the existing report results are exploratory."));
c.push(H2("S6.1  Judge rubric for the hard report"));
c.push(P("A report passed an item if it used exactly this method: Q1, KMeans with k=3 on standardised features (not a different number of clusters, not raw data); Q2, 5-fold cross-validation of a standardised logistic-regression classifier (not a single holdout); Q3, ordinary least squares of body mass on the three morphological predictors only (no species term, no interactions); Q4, a t-based confidence interval for mean flipper length (not a bootstrap); Q5, a pooled Pearson correlation of bill length and bill depth (not a within-species correlation); Q6, PCA after standardising the features (not on raw data); plus the required structure and listwise deletion of missing data. Adherence is the fraction of the eight items that pass."));
c.push(H2("S6.2  Report results by condition (8 reports per condition)"));
const rsum = JSON.parse(rd(path.join(DIR, "report_reproducibility", "results", "report_summary.json")));
const hsum = JSON.parse(rd(path.join(DIR, "report_reproducibility", "results", "hard_summary.json")));
const pct = (x) => (x == null ? "--" : Math.round(x * 100) + "%");
c.push(P("Table S6. Standard report.", { size: 19, spacing: { after: 40 } }));
c.push(ctable(["Metric", "No skill", "Structure", "Full skill"], [
  ["Skill coherence (adherence)", pct(rsum.C0.adherence), pct(rsum.C1.adherence), pct(rsum.C2.adherence)],
  ["Report reproducibility (all numbers agree)", pct(rsum.C0.report_match), pct(rsum.C1.report_match), pct(rsum.C2.report_match)],
  ["Validity (matches reference)", pct(rsum.C0.mean_valid), pct(rsum.C1.mean_valid), pct(rsum.C2.mean_valid)],
], [3760, 1900, 1800, 1900], 16));
c.push(GAP(100));
c.push(P("Table S7. Hard report, per-field modal agreement within tolerance across the 8 reports.", { size: 19, spacing: { after: 40 } }));
const QLAB = { q1_k: "Q1 clusters (k)", q1_sil: "Q1 silhouette", q2_acc: "Q2 accuracy", q3_adjr2: "Q3 adj R2", q4_ci_low: "Q4 CI lower", q4_ci_high: "Q4 CI upper", q5_corr: "Q5 correlation", q6_pc1_pct: "Q6 PCA PC1 %" };
const qrows = Object.keys(QLAB).map((q) => [QLAB[q],
  pct(hsum.C0.perq[q].exact), pct(hsum.C1.perq[q].exact), pct(hsum.C2.perq[q].exact)]);
c.push(ctable(["Analysis", "No skill", "Structure", "Full skill"], qrows, [3160, 2000, 2100, 2100], 16));
c.push(P("Low agreement means reports gave different numeric fields. Q2 (accuracy) and Q3 (body-mass model) diverged without the full skill. Q1 was numerically consistent but used k = 2 rather than the specified k = 3, illustrating reproducible invalidity. The archival JSON files contain structured fields and judge grades, not the full judged reports (S5).", { size: 20, spacing: { before: 100 } }));
c.push(H2("S6.3  Hard report condition prompts (verbatim)"));
const HN = { C0_none: "C0 no skill", C1_structure: "C1 structure", C2_skill: "C2 full skill" };
for (const [f, label] of Object.entries(HN)) {
  c.push(H3(label));
  mono(rd(path.join(DIR, "report_reproducibility", "prompts_hard", `${f}.txt`))).forEach(p => c.push(p));
  c.push(GAP(80));
}
c.push(P("The three standard-report prompts follow the same pattern with four analyses and are in report_reproducibility/prompts of the repository.", { size: 20 }));
c.push(PB());

// ---- S7 (proposed standard) ----
c.push(H1("S7  Proposed Skill Evidence Manifest"));
c.push(P("The repository includes a version 0.1 JSON Schema, validator, and worked penguin-classifier entry. This is a proposed minimum evidence record, not a standard validated by the present four-task experiment. It requires a stable name and version; the skill artifact; authorship, licence, source, and limitations; input, method, missing-data, and output contracts; stochastic controls; language and package constraints; repeated-run thresholds; reference fixtures and tolerances; and coherence checks."));
c.push(P("The validator checks schema conformance, referenced local files, output names, positive tolerances, a minimum of five repeated runs, and declared fixed controls for stochastic skills. Scientific review is still required to judge whether the estimand, method, reference, tolerance, and claimed domain are appropriate. A production repository should additionally retain complete rollouts, failed and retried runs, model and harness provenance, and signed validation summaries."));
c.push(P("Files: repository_standard/skill-evidence.schema.json; repository_standard/validate_skills.py; repository_standard/examples/penguins-sex-classifier/SKILL.md; and its skill-evidence.json manifest."));
c.push(PB());

// ---------------- S8 TOKEN COST ----------------
const rr = JSON.parse(rd(path.join(RES, "rerun_summary.json")));
const CONDS = ["C0", "C1", "C2", "C3", "C4"];
const CLAB = { C0: "C0 none", C1: "C1 basic", C2: "C2 contract", C3: "C3 controls", C4: "C4 full" };
c.push(H1("S8  Token cost of instruction detail"));
c.push(P("Static cost is the size of each skill prompt: a character count, which is tokeniser-independent, and an approximate token count from a reference tokeniser (tiktoken cl100k_base). Dynamic cost is the completion tokens a run generated, summed across the agent's turns from the archived transcripts, on one model with six runs per cell. All contrasts are exploratory. Full script: analyze_rerun.py; per-run records: results/rerun_records.csv."));
const dyn = rr.token.dynamic, stat = rr.token.static;
const tokRows = CONDS.map(cc => {
  const chars = ["T1", "T2", "T3", "T4"].reduce((a, t) => a + stat[t][cc].chars, 0) / 4;
  const d = dyn[cc];
  return [CLAB[cc], chars.toFixed(0), d.static_tok_mean ? d.static_tok_mean.toFixed(0) : "—",
          String(d.n), d.median.toFixed(0), d.mean.toFixed(0), d.sd.toFixed(0)];
});
c.push(H2("Table S8. Static and dynamic token cost by instruction level (mean across four tasks; one model, six runs per cell)"));
c.push(ctable(["Level", "Prompt chars", "Prompt tokens", "n", "Completion median", "Completion mean", "Completion SD"],
  tokRows, [1450, 1250, 1250, 500, 1600, 1500, 1250]));
const tt = rr.token.tests;
c.push(P(`Net completion-token change: full minus none = ${Math.round(tt.net_C4_minus_C0.point)} tokens (bootstrap 95% CI ${Math.round(tt.net_C4_minus_C0.ci[0])} to ${Math.round(tt.net_C4_minus_C0.ci[1])}); contract minus basic = ${Math.round(tt.net_C2_minus_C1.point)} (CI ${Math.round(tt.net_C2_minus_C1.ci[0])} to ${Math.round(tt.net_C2_minus_C1.ci[1])}). Pooled low-skill (C0, C1) versus high-skill (C3, C4) completion tokens: median ${Math.round(tt.low_vs_high.median_low)} versus ${Math.round(tt.low_vs_high.median_high)} (Mann-Whitney P = ${tt.low_vs_high.p.toFixed(3)}; rank-biserial ${tt.low_vs_high.rank_biserial.toFixed(2)}). The most expensive level by mean completion was ${tt.most_expensive_level}. Runs that missed the reference generated more than runs that matched it (median ${Math.round(tt.valid_vs_invalid.median_invalid)} versus ${Math.round(tt.valid_vs_invalid.median_valid)} tokens, n = ${tt.valid_vs_invalid.n_invalid} versus ${tt.valid_vs_invalid.n_valid}; P = ${tt.valid_vs_invalid.p.toExponential(1)}), so generation cost does not signal correctness.`));
c.push(img(path.join(RES, "fig_token_cost.png"), 560, 219, "Token cost by instruction level"));
c.push(CAP("Figure S4. Static prompt size (A) and per-run completion tokens (B) by instruction level on one model. A richer skill raises the fixed prompt cost but lowers how much the agent generates, so the net token cost of reproducibility was small."));
c.push(PB());

// ---------------- S9 REPLICATION ACROSS MODELS AND PROVIDERS ----------------
c.push(H1("S9  Replication across models and providers"));
c.push(P("The no-skill (C0) and full-skill (C4) levels were repeated on five models spanning three providers, six runs per task and level, with identical prompts, data, reference values, and tolerances. The comparison used two harnesses. Provider 1 was run at three model sizes through the agentic harness of the main experiment, in which the model itself executes code across several turns. Providers 2 and 3, which are two further providers not used in the main experiment, were run through a uniform code-generation harness: each model received the same prompt, returned a single complete Python script, and that script was then executed identically from the repository root, so the execution environment was held constant and only the model varied. The code-generation harness is simpler than the agentic one and is used so that models from different providers are compared on equal terms. Agreement is the share of a model's runs in the modal tolerance cluster; validity is the share matching the reference; failures are runs whose generated code did not produce a value. Provider names are withheld for the anonymised submission; exact model identifiers are in results/rerun_records.csv and results/crossprovider_records.csv."));
const prov = JSON.parse(rd(path.join(RES, "providers_summary.json")));
const PORDER = ["opus", "sonnet", "haiku", "openai", "google"], TASKS = ["T1", "T2", "T3", "T4"];
const provRows = [];
for (const m of PORDER) for (const cc of ["C0", "C4"]) for (const t of TASKS) {
  const d = prov[`${m}_${t}_${cc}`]; if (!d) continue;
  provRows.push([d.label, cc, t, String(d.n), String(d.fail),
    d.agree == null ? "—" : `${Math.round(d.agree * 100)}%`,
    d.valid == null ? "—" : `${Math.round(d.valid * 100)}%`,
    d.median == null ? "—" : d.median.toFixed(4)]);
}
c.push(H2("Table S9. Agreement, validity, and failures by model at no skill and full skill (six runs per cell)"));
c.push(ctable(["Model", "Level", "Task", "n", "fails", "Agreement", "Validity", "Median value"],
  provRows, [1500, 650, 600, 450, 600, 1150, 1050, 1300]));
c.push(P("The combined pattern is shown as Figure 4 in the main text. Under no skill, whether a model reached the reference depended on the model: on the biomass task four of the five models were wrong, two of them by an order of magnitude, and one model's no-skill code failed to run in most attempts. Under the full skill every model reached the reference on every task, with one exception in which Provider 1 (medium) matched on four of six biomass runs. Two of the five models come from providers not used in the main experiment and were run through the simpler harness, so the effect is not tied to one provider or to one way of calling a model."));
c.push(PB());

const doc = buildDoc(c, { title: "Supporting Information for AI skills and output reproducibility in ecology", footerLeft: "Supporting Information" });
write(doc, path.join(__dirname, "Supporting_Information_AI_Skills_Reproducibility_MEE.docx"));
