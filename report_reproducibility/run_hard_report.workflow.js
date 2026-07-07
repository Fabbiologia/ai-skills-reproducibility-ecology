export const meta = {
  name: 'report-reproducibility-hard',
  description: 'Generate HARD ecological reports (6 forky analyses) under 3 skill conditions (8 reps) and judge each against a fixed rubric; measure report reproducibility, coherence, and validity',
  phases: [
    { title: 'Generate', detail: 'agents write a 6-analysis penguin morphometrics report' },
    { title: 'Judge', detail: 'grade each report against the canonical rubric' },
  ],
}

// EDIT THIS to the absolute path of your checkout before running (agents need an
// absolute path to read each prompt file, and Python runs from the repository root).
const REPO = '/ABSOLUTE/PATH/TO/for_submission'   // <-- set to your repository root
const DIR = REPO + '/report_reproducibility/prompts_hard'
const FILES = { C0: 'C0_none.txt', C1: 'C1_structure.txt', C2: 'C2_skill.txt' }
const CONDS = ['C0', 'C1', 'C2']
const REPS = 8

const GEN_SCHEMA = {
  type: 'object',
  properties: {
    q1_k: { type: ['number', 'null'] }, q1_sil: { type: ['number', 'null'] }, q1_method: { type: 'string' },
    q2_acc: { type: ['number', 'null'] }, q2_method: { type: 'string' },
    q3_adjr2: { type: ['number', 'null'] }, q3_predictors: { type: 'string' },
    q4_ci_low: { type: ['number', 'null'] }, q4_ci_high: { type: ['number', 'null'] }, q4_method: { type: 'string' },
    q5_corr: { type: ['number', 'null'] }, q5_scope: { type: 'string' },
    q6_pc1_pct: { type: ['number', 'null'] }, q6_scaled: { type: ['boolean', 'null'] },
    sections: { type: 'array', items: { type: 'string' } },
    conclusion: { type: 'string' }, report_md: { type: 'string' },
  },
  required: ['q1_k', 'q2_acc', 'q3_adjr2', 'q5_corr', 'q6_pc1_pct', 'conclusion', 'report_md'],
  additionalProperties: true,
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    q1_kmeans_k3: { type: 'boolean' },
    q2_cv5_logreg: { type: 'boolean' },
    q3_ols_3morph: { type: 'boolean' },
    q4_t_interval: { type: 'boolean' },
    q5_pooled_pearson: { type: 'boolean' },
    q6_pca_scaled: { type: 'boolean' },
    structure_ok: { type: 'boolean' },
    missing_listwise: { type: 'boolean' },
    adherence_score: { type: 'number' },
    notes: { type: 'string' },
  },
  required: ['adherence_score', 'q1_kmeans_k3', 'q2_cv5_logreg', 'q3_ols_3morph', 'q4_t_interval', 'q5_pooled_pearson', 'q6_pca_scaled'],
  additionalProperties: true,
}

const RUBRIC = `The canonical method for each question is:
- Q1: KMeans clustering with exactly k=3 clusters, on standardised (StandardScaler) features, silhouette score reported. Choosing a different number of clusters (e.g. 2 or 4), or not standardising, FAILS.
- Q2: 5-fold cross-validation accuracy of a standardised logistic-regression classifier for species. Using a single train/test holdout instead of 5-fold CV FAILS.
- Q3: ordinary least squares regression of body mass on the THREE morphological predictors (bill length, bill depth, flipper length) only, no species term, no interactions, no transformation, adjusted R-squared reported. Including species, adding interactions, or transforming FAILS.
- Q4: a t-based 95% confidence interval for mean flipper length (mean +/- t*SE). Using a bootstrap interval FAILS.
- Q5: a POOLED Pearson correlation of bill length and bill depth across all rows. A per-species (within-species) correlation, or Spearman, FAILS.
- Q6: PCA computed AFTER standardising the four measurements; percent variance on PC1 reported. PCA on raw (unstandardised) data FAILS.
- Structure: Title, Data and methods, per-question Results (Q1 to Q6), Conclusion.
- Missing data: dropped listwise, not imputed.`

function genPrompt(cond) {
  return `Read the file at ${DIR}/${FILES[cond]} and follow it exactly. Run Python from the ` +
    `repository root (${REPO}) so data/penguins.csv resolves. Actually execute the analysis and ` +
    `use the real numbers. Return the structured report result with the number(s) and method for ` +
    `each of the six questions, the section headings, the conclusion paragraph, and report_md (the ` +
    `full report as markdown).`
}

function judgePrompt(gen) {
  return `You are grading a data-analysis report for adherence to a fixed statistical rubric. ` +
    `Judge ONLY from the report text below; do not re-run anything. For each rubric item decide ` +
    `whether the report actually used that exact method. Set adherence_score to the fraction of the ` +
    `eight items that pass (Q1 to Q6, structure, missing data), from 0 to 1.\n\n${RUBRIC}\n\n` +
    `=== REPORT UNDER REVIEW ===\n${(gen.report_md || '').slice(0, 14000)}\n=== END REPORT ===`
}

async function genOne(cond, rep) {
  for (let a = 0; a < 3; a++) {
    const g = await agent(genPrompt(cond), { label: `gen:${cond}-r${rep}${a ? '.' + a : ''}`, phase: 'Generate', schema: GEN_SCHEMA })
    if (g && g.report_md) return g
  }
  return null
}

const items = []
for (const cond of CONDS) for (let r = 1; r <= REPS; r++) items.push({ cond, r })
log(`generating ${items.length} HARD reports (${CONDS.length} conditions x ${REPS} reps), then judging each`)

const out = await pipeline(
  items,
  (it) => genOne(it.cond, it.r),
  (gen, it) => {
    if (!gen) return { cond: it.cond, rep: it.r, ok: false }
    return agent(judgePrompt(gen), { label: `judge:${it.cond}-r${it.r}`, phase: 'Judge', schema: JUDGE_SCHEMA })
      .then((j) => ({
        cond: it.cond, rep: it.r, ok: true,
        q1_k: gen.q1_k, q1_sil: gen.q1_sil, q1_method: gen.q1_method,
        q2_acc: gen.q2_acc, q2_method: gen.q2_method,
        q3_adjr2: gen.q3_adjr2, q3_predictors: gen.q3_predictors,
        q4_ci_low: gen.q4_ci_low, q4_ci_high: gen.q4_ci_high, q4_method: gen.q4_method,
        q5_corr: gen.q5_corr, q5_scope: gen.q5_scope,
        q6_pc1_pct: gen.q6_pc1_pct, q6_scaled: gen.q6_scaled,
        sections: gen.sections, conclusion: gen.conclusion, judge: j,
      }))
  }
)
const ok = out.filter(o => o && o.ok).length
log(`completed: ${ok}/${items.length} reports generated and judged`)
return out
