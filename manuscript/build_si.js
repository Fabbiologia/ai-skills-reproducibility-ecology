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
c.push(P("**Skills as the new packages: an evidence-based standard for good AI analysis skills and a curated repository for ecology**", { spacing: { after: 40 } }));
c.push(P("Supporting Information for a manuscript prepared for double-anonymous review. Target journal: Methods in Ecology and Evolution.", { size: 20 }));
c.push(P("Contents: S1 How we reviewed the literature · S2 Search terms · S3 What we recorded for each study · S4 Studies we read (with the selection summary) · S5 Experiment prompts (full text) · S6 Full results and statistics · S7 Additional figures · S8 Software environment, code, and data availability · S9 Experiment 2 report materials and results.", { size: 20 }));
c.push(HR());

// ---- S1 ----
c.push(H1("S1  How we reviewed the literature"));
c.push(P("The literature review sets the context for the experiment and is not a formal systematic review. We searched for evidence on AI skills and the output reproducibility of ecological and computational analyses in July 2026, using Google Scholar, general web search, and targeted searching of journals and preprint servers. Screening was done by one reviewer. We read 19 studies closely and recorded a short set of items from each one (S3). A larger, pre-registered search with two independent reviewers could be run later to give a complete count, but it was not needed for the aims here. The studies are listed in S4, and the search terms are in S2."));
c.push(PB());

// ---- S2 ----
c.push(H1("S2  Search terms"));
c.push(P("The main search terms are below. They can be adapted for each database. We searched from 2015 to present, in English. For transferable (non-ecological) evidence on LLMs and agents, we dropped the ecology terms and checked each result for relevance."));
c.push(H3("Main terms"));
mono('("large language model*" OR LLM OR "AI agent*" OR "agent skill*" OR "prompt engineering"\n OR "workflow" OR "reporting standard*" OR "reporting guideline*")\nAND (reproducib* OR replicab* OR "consistency" OR "re-execution" OR "repeatab*")\nAND (ecolog* OR environment* OR conservation OR biodiversity OR "species distribution"\n OR "remote sensing")').forEach(p => c.push(p));

// ---- S3 ----
c.push(H1("S3  What we recorded for each study"));
c.push(P("For each study we recorded the citation, the venue, the year, the domain (ecological or general), the study design, the skill-like feature it tested (for example a step sequence, an input and output contract, worked examples, a validation check list, a tool-use contract, an environment specification, or a reporting protocol), the comparison, the reproducibility or consistency outcome and how it was measured, the reported result, and whether the evidence was direct or indirect for our question."));
c.push(PB());

// ---- S4 ----
c.push(H1("S4  Studies we read"));
c.push(img(path.join(RES, "figS1_prisma_flow.png"), 470, 400, "Study selection"));
c.push(CAP("Figure S1. Summary of how studies were found and selected in the July 2026 background search. Counts are from an informal search by one reviewer."));
c.push(H2("Table S4. Studies we read (n = 19)"));
c.push(ctable(
  ["Study (year)", "Venue", "Domain", "Skill-like feature", "Output-reproducibility finding", "Evidence"],
  [
    ["Gallois et al. (2025)", "Methods Ecol. Evol.", "Ecology (birds)", "Bespoke quantitative LLM querying data", "Accurate ecological interpretations; reliability task-dependent", "Direct"],
    ["Dorm et al. (2026)", "J. Nat. Conserv.", "Ecology (IUCN spp.)", "General LLM outputs", "94.9% taxonomic vs 27.2% conservation-status accuracy", "Direct"],
    ["Yagubyan (2026, pre)", "arXiv", "Agents", "Repeated identical tool-calling runs", "Behavioural reproducibility imperfect; tool/order/arg drift", "Direct"],
    ["LongDS-Bench (2026, pre)", "arXiv", "Data analysis", "Long-horizon agentic analysis", "High failure/variance on multi-step tasks", "Direct"],
    ["DataSciBench (2025, pre)", "arXiv", "Data science", "LLM data-science agents", "Success and consistency vary; structured eval needed", "Direct"],
    ["ReliabilityBench (2026, pre)", "arXiv", "Agents", "Reliability under input perturbation", "Output reliability degrades under variation", "Direct"],
    ["ARA (2026, pre)", "arXiv", "Peer review", "Agentic reproducibility assessment", "Agents can assess reproducibility (feasibility)", "Direct"],
    ["He et al. (2024)", "arXiv/NAACL", "LLM", "Prompt template / formatting", "Up to 40% performance swing from format alone", "Direct"],
    ["Wang et al. (2023)", "ICLR", "LLM", "Self-consistency (multi-run vote)", "Aggregating runs stabilises outputs", "Direct"],
    ["Yuan et al. (2025, pre)", "arXiv", "LLM", "Batch-invariant kernels; precision", "Bit-identical over 1,000 runs at ~61.5% throughput cost", "Direct"],
    ["Beyond Reproducibility (2026, pre)", "arXiv", "LLM", "Token-probability nondeterminism", "Nondeterminism affects text at temperature > 0", "Direct"],
    ["Culina et al. (2020)", "PLOS Biology", "Ecology", "Code availability", "Code available for a minority; key reproduction barrier", "Indirect"],
    ["Kellner et al. (2025)", "Ecology", "Ecology (SDM/abund.)", "Functional code", "Functional R code rare; re-execution often fails", "Indirect"],
    ["Kambouris et al. (2024)", "PLOS ONE", "EcoEvo meta-analyses", "Shared data + code", "15% shared both; 27% to 73% of 26 reproduced by strictness", "Indirect"],
    ["Cooper et al. (2025)", "Methods Ecol. Evol.", "Ecology (BES)", "Data/code archiving", "Archiving improving; code sharing lags", "Indirect"],
    ["O'Dea et al. (2021)", "Biological Reviews", "EcoEvo", "PRISMA-EcoEvo checklist", "Guideline use (~16%) linked to higher reporting quality", "Indirect"],
    ["Zurell et al. (2020)", "Ecography", "Ecology (SDM)", "ODMAP structured protocol", "Structured protocol supports documentation & reproduction", "Indirect"],
    ["Trisovic et al. (2022)", "Scientific Data", "General (R code)", "Environment standardisation", "Re-execution 26% to 44%; environment fix helped most", "Indirect"],
    ["Pimentel et al. (2019)", "MSR", "General (notebooks)", "Execution order / hidden state", "24.1% run; only 4.0% reproduce results", "Indirect"],
  ],
  [1500, 1150, 1200, 1900, 2910, 700], 14
));
c.push(GAP(120));
c.push(H2("Table S5. Skill parts ranked by their expected contribution to output reproducibility, from the literature"));
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
c.push(H1("S5  Experiment prompts (full text)"));
c.push(P("The 40 prompt files below are the variable we changed, 20 for Python and 20 for R. Within each task and language, the four skilled levels add structure step by step, so each level contains the one before it. Each file also sets a fixed output format, and agents ran the analysis and returned the value named at the foot of the file. The R files name R functions (cor, glm, aov, and dplyr) in place of the Python ones, but the task and the skill ladder are the same. The text is shown exactly as it was given to the agents."));
c.push(H2("S5.1  Python prompts"));
const TN = { T1: "iris sepal correlation", T2: "penguin sex classifier", T3: "penguin body-mass ANOVA", T4: "LTEM reef-fish biomass" };
const CN = { C0: "C0 none", C1: "C1 basic", C2: "C2 contract", C3: "C3 +controls", C4: "C4 full" };
for (const t of ["T1", "T2", "T3", "T4"]) {
  c.push(H2(`Task ${t} (${TN[t]})`));
  for (const cc of ["C0", "C1", "C2", "C3", "C4"]) promptBlock(`${t}_${cc}`, CN[cc], "prompts").forEach(p => c.push(p));
  c.push(PB());
}
c.push(H2("S5.2  R prompts"));
for (const t of ["T1", "T2", "T3", "T4"]) {
  c.push(H2(`Task ${t} (${TN[t]})`));
  for (const cc of ["C0", "C1", "C2", "C3", "C4"]) promptBlock(`${t}_${cc}`, CN[cc], "prompts_r").forEach(p => c.push(p));
  c.push(PB());
}

// ---- S6 ----
c.push(H1("S6  Full results and statistics"));
c.push(H2("Table S6. Per-cell reproducibility and validity in Python (10 runs per cell)"));
const summ = JSON.parse(rd(path.join(RES, "summary_v2.json"))).cells;
const rowsS6 = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const s = summ[`${t}_${cc}`]; if (!s) continue;
  rowsS6.push([`${t} ${cc}`, s.n, s.sd.toFixed(4), s.cv.toFixed(3), s.n_distinct,
    (s.exact_match_rate * 100).toFixed(0) + "%", (s.cat_agreement * 100).toFixed(0) + "%",
    (s.validity_rate * 100).toFixed(0) + "%", s.abs_err_ref.toFixed(4)]);
}
c.push(ctable(["Cell", "n", "SD", "CV", "#dist.", "exact", "cat-agree", "valid", "|Δref|"], rowsS6,
  [1250, 620, 1150, 1000, 900, 900, 1200, 900, 1440], 15));

const XL = JSON.parse(rd(path.join(RES, "cross_language_summary.json")));
c.push(GAP(120));
c.push(H2("Table S7. Per-cell reproducibility and validity in R (10 runs per cell)"));
const rowsR = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const s = XL.within[`r_${t}_${cc}`]; if (!s) continue;
  rowsR.push([`${t} ${cc}`, s.n, s.sd.toFixed(4), s.n_distinct,
    (s.exact * 100).toFixed(0) + "%", (s.valid * 100).toFixed(0) + "%"]);
}
c.push(ctable(["Cell", "n", "SD", "#distinct", "exact", "valid"], rowsR, [1760, 900, 1700, 1700, 1650, 1650], 15));
c.push(GAP(120));
c.push(H2("Table S8. Cross-language agreement (Python modal value vs R modal value)"));
const rowsX = [];
for (const t of ["T1", "T2", "T3", "T4"]) for (const cc of ["C0", "C1", "C2", "C3", "C4"]) {
  const x = XL.cross[`${t}_${cc}`]; if (!x) continue;
  rowsX.push([`${t} ${cc}`, x.py.toFixed(4), x.r.toFixed(4), x.diff.toFixed(4), x.agree ? "Yes" : "No"]);
}
c.push(ctable(["Cell", "Python", "R", "|difference|", "Agree within tolerance?"], rowsX, [1560, 1700, 1700, 1900, 2500], 15));
c.push(P("The deterministic tasks (T1, T3, T4) give the same value in Python and R at every level, including the wrong value for T4 before the contract. The classifier (T2) does not match across languages, because the two use different models and random number generators.", { size: 20, spacing: { before: 100 } }));
c.push(GAP(120));
c.push(H2("Key inferential contrasts (Python)"));
c.push(BULLET("**T2 run to run agreement.** Low skill (C0 to C2) 16 of 30, high skill (C3 and C4) 20 of 20. Fisher's exact P = 2.2×10⁻⁴. Pooled low-skill SD = 0.0086, bootstrap 95% CI [0.0063, 0.0109] (excludes 0); high-skill SD = 0.0000."));
c.push(BULLET("**T2 validity against the reference.** Low skill 12 of 30, high skill 20 of 20. Fisher's exact P = 8.4×10⁻⁶."));
c.push(BULLET("**T4 validity against the reference.** Before the contract (C0 and C1) 0 of 20, with the contract and above (C2 to C4) 30 of 30. Fisher's exact P = 2.1×10⁻¹⁴. Run to run reproducibility was 100% at every level."));
c.push(P("The same contrasts hold in R. The R classifier (T2) moved from run to run at the low levels and reached exact agreement at C3 and C4 (at the R value 0.8657), and the R biomass task (T4) was reproducible but wrong until the contract at C2, exactly as in Python. We also ran Brown-Forsythe Levene tests for equal variance, but they are not meaningful here because the high-skill cells have exactly zero variance, so the proportion tests above are the right summary. The full run-level data (400 records across both languages, each with its value, method, parameters, and sample size) are in results_v2.json and results_v2_R.json (S8).", { size: 20, spacing: { before: 120 } }));
c.push(PB());

// ---- S7 ----
c.push(H1("S7  Additional figures"));
c.push(img(path.join(RES, "fig1_value_strips.png"), 600, 400, "Value strips"));
c.push(CAP("Figure S2. All 200 Python outputs by task and level (10 runs per cell, with small horizontal jitter so points do not overlap). The dashed line shows the reference. T1 and T3 fall on the reference at every level, T2 scatters until C3, and T4 sits consistently away from the reference (3.2952) at C0 and C1 and moves to the reference (3.4642) from C2."));
c.push(img(path.join(RES, "fig4_python_vs_r.png"), 600, 400, "Python versus R"));
c.push(CAP("Figure S3. Python (blue) and R (red) outputs by skill level, 10 runs per cell per language. Dashed lines show the reference for each language. T1, T3, and T4 sit on one shared line in both languages, while T2 sits on two different lines. This is the same figure discussed in the main text (main Figure 2), shown here at full size."));

// ---- S8 ----
c.push(H1("S8  Software environment, code and data availability"));
c.push(P("**Environment.** Python 3 (scikit-learn 1.9.0, scipy 1.16.3, numpy 2.4.6, pandas, matplotlib) and R 4.6.0 (stats, dplyr, readr). Agents were general-purpose coding agents built on a single underlying LLM, each running Python or R in an isolated working context."));
c.push(P("**Datasets.** iris (150 rows; built into R and from scikit-learn); penguins.csv (344 rows; Palmer Penguins, Horst et al. 2020); ltem_cabo_pulmo_2023.csv (2,798 reef-fish records, 10 reefs, 41 transect units; Long-Term Ecological Monitoring programme, Cabo Pulmo National Park, Gulf of California, 2023)."));
c.push(P("**Materials archived (OSF/Zenodo on submission).**"));
c.push(BULLET("references.json and references_R.json hold the design and the reference values for each language."));
c.push(BULLET("prompts/ and prompts_r/ hold the 20 Python and 20 R condition prompts (S5)."));
c.push(BULLET("run_experiment.workflow.js and run_experiment_r.workflow.js orchestrated the 200 Python and 200 R runs (4 tasks by 5 levels by 10 replicates each), with up to 3 retries per cell and enforced structured output."));
c.push(BULLET("results_v2.json and results_v2_R.json hold every run's structured output (200 records each)."));
c.push(BULLET("analyze_v2.py scores the Python arm; analyze_cross_language.py scores R and the Python-versus-R comparison and draws the comparison figure."));
c.push(BULLET("generate_prompts.py and generate_prompts_r.py regenerate the prompt files; data/ holds the three input CSV files."));
c.push(P("These materials are provided for peer review in an anonymised repository, the link to which is shared with the editors; the repository will be de-anonymised and archived with a DOI on acceptance. The restricted reef fish file for Task T4 is not included and is available on request.", { spacing: { before: 100 } }));
c.push(P("Together these make the experiment fully reproducible end-to-end. Re-running each orchestration regenerates its run set, and the analysis scripts regenerate every number and figure reported here.", { spacing: { before: 100 } }));

// ---- S9 (Experiment 2) ----
c.push(H1("S9  Experiment 2 materials: report prompts and results"));
c.push(P("The second experiment asked agents to write a short data report on the Palmer Penguins dataset and then graded each report with a second judge agent. Two report versions were used, a standard report with four common analyses and a hard report with six analyses that each have a real method fork. Each version had three conditions (no skill, a structure-only skill, and a full methods skill) with 8 reports per condition. The judge scored each report against one fixed rubric, the same for every condition."));
c.push(H2("S9.1  Judge rubric for the hard report"));
c.push(P("A report passed an item if it used exactly this method: Q1, KMeans with k=3 on standardised features (not a different number of clusters, not raw data); Q2, 5-fold cross-validation of a standardised logistic-regression classifier (not a single holdout); Q3, ordinary least squares of body mass on the three morphological predictors only (no species term, no interactions); Q4, a t-based confidence interval for mean flipper length (not a bootstrap); Q5, a pooled Pearson correlation of bill length and bill depth (not a within-species correlation); Q6, PCA after standardising the features (not on raw data); plus the required structure and listwise deletion of missing data. Adherence is the fraction of the eight items that pass."));
c.push(H2("S9.2  Report results by condition (8 reports per condition)"));
const rsum = JSON.parse(rd(path.join(DIR, "report_reproducibility", "results", "report_summary.json")));
const hsum = JSON.parse(rd(path.join(DIR, "report_reproducibility", "results", "hard_summary.json")));
const pct = (x) => (x == null ? "--" : Math.round(x * 100) + "%");
c.push(P("Table S9. Standard report.", { size: 19, spacing: { after: 40 } }));
c.push(ctable(["Metric", "No skill", "Structure", "Full skill"], [
  ["Skill coherence (adherence)", pct(rsum.C0.adherence), pct(rsum.C1.adherence), pct(rsum.C2.adherence)],
  ["Report reproducibility (all numbers agree)", pct(rsum.C0.report_match), pct(rsum.C1.report_match), pct(rsum.C2.report_match)],
  ["Validity (matches reference)", pct(rsum.C0.mean_valid), pct(rsum.C1.mean_valid), pct(rsum.C2.mean_valid)],
], [3760, 1900, 1800, 1900], 16));
c.push(GAP(100));
c.push(P("Table S10. Hard report, per-analysis run-to-run agreement (exact-match rate across the 8 reports).", { size: 19, spacing: { after: 40 } }));
const QLAB = { q1_k: "Q1 clusters (k)", q1_sil: "Q1 silhouette", q2_acc: "Q2 accuracy", q3_adjr2: "Q3 adj R2", q4_ci_low: "Q4 CI lower", q4_ci_high: "Q4 CI upper", q5_corr: "Q5 correlation", q6_pc1_pct: "Q6 PCA PC1 %" };
const qrows = Object.keys(QLAB).map((q) => [QLAB[q],
  pct(hsum.C0.perq[q].exact), pct(hsum.C1.perq[q].exact), pct(hsum.C2.perq[q].exact)]);
c.push(ctable(["Analysis", "No skill", "Structure", "Full skill"], qrows, [3160, 2000, 2100, 2100], 16));
c.push(P("Low agreement means independent reports gave different numbers for that analysis. Q2 (accuracy) and Q3 (body-mass model) diverge without the full skill; the other four do not, because the agents' default already matched the specified method. The full run-level report outputs and judge grades are in results_report.json and results_hard.json in the report_reproducibility folder of the repository (S8).", { size: 20, spacing: { before: 100 } }));
c.push(H2("S9.3  Hard report condition prompts (verbatim)"));
const HN = { C0_none: "C0 no skill", C1_structure: "C1 structure", C2_skill: "C2 full skill" };
for (const [f, label] of Object.entries(HN)) {
  c.push(H3(label));
  mono(rd(path.join(DIR, "report_reproducibility", "prompts_hard", `${f}.txt`))).forEach(p => c.push(p));
  c.push(GAP(80));
}
c.push(P("The three standard-report prompts follow the same pattern with four analyses and are in report_reproducibility/prompts of the repository.", { size: 20 }));
c.push(PB());

const doc = buildDoc(c, { title: "Supporting Information for AI skills and output reproducibility in ecology", footerLeft: "Supporting Information" });
write(doc, path.join(__dirname, "Supporting_Information_AI_Skills_Reproducibility_MEE.docx"));
