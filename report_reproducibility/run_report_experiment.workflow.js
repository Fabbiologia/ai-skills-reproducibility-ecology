export const meta = {
  name: 'report-reproducibility',
  description: 'Generate ecological data reports under 3 skill conditions (8 reps each) and judge each report against a fixed statistical rubric; measure report reproducibility and skill coherence',
  phases: [
    { title: 'Generate', detail: 'agents write a 4-analysis penguin report' },
    { title: 'Judge', detail: 'grade each report against the canonical rubric' },
  ],
}

// EDIT THIS to the absolute path of your checkout before running (agents need an
// absolute path to read each prompt file, and Python runs from the repository root).
const REPO = '/ABSOLUTE/PATH/TO/for_submission'   // <-- set to your repository root
const DIR = REPO + '/report_reproducibility/prompts'
const FILES = { C0: 'C0_none.txt', C1: 'C1_structure.txt', C2: 'C2_skill.txt' }
const CONDS = ['C0', 'C1', 'C2']
const REPS = 8
const RUN_PROVENANCE = {
  harness: 'REQUIRED: application and workflow-harness version',
  provider: 'REQUIRED: provider for generator and judge',
  generator_model: 'REQUIRED: exact generator model identifier/version',
  judge_model: 'REQUIRED: exact judge model identifier/version',
  decoding: 'REQUIRED: generator and judge decoding controls',
  run_date_utc: 'REQUIRED: ISO-8601 date/time',
}
if (Object.values(RUN_PROVENANCE).some(v => v.startsWith('REQUIRED:'))) {
  throw new Error('Complete RUN_PROVENANCE before launching a new report run set.')
}

const GEN_SCHEMA = {
  type: 'object',
  properties: {
    q1_r: { type: ['number', 'null'] }, q1_method: { type: 'string' },
    q2_p: { type: ['number', 'null'] }, q2_effect: { type: ['number', 'null'] },
    q2_test: { type: 'string' }, q2_effect_metric: { type: 'string' },
    q3_accuracy: { type: ['number', 'null'] }, q3_model: { type: 'string' },
    q3_seed: { type: ['number', 'null'] }, q3_scaled: { type: ['boolean', 'null'] },
    q4_means: { type: 'object', additionalProperties: { type: 'number' } },
    sections: { type: 'array', items: { type: 'string' } },
    conclusion: { type: 'string' }, report_md: { type: 'string' },
  },
  required: ['q1_r', 'q2_effect', 'q3_accuracy', 'q4_means', 'conclusion', 'report_md'],
  additionalProperties: true,
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    q1_pooled_pearson: { type: 'boolean' },
    q2_anova_eta2: { type: 'boolean' },
    q3_logreg_seed42_scaled: { type: 'boolean' },
    q4_species_means: { type: 'boolean' },
    structure_ok: { type: 'boolean' },
    missing_listwise: { type: 'boolean' },
    adherence_score: { type: 'number' },
    concl_gentoo_heaviest: { type: 'boolean' },
    concl_mass_differs: { type: 'boolean' },
    concl_sex_pred: { type: 'boolean' },
    concl_flipper_positive: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['adherence_score', 'q1_pooled_pearson', 'q2_anova_eta2', 'q3_logreg_seed42_scaled', 'q4_species_means'],
  additionalProperties: true,
}

const RUBRIC = `The canonical method for each question is:
- Q1: a POOLED Pearson correlation of flipper length and body mass (not Spearman, not per-species).
- Q2: a one-way ANOVA across the three species, with eta-squared as the effect size (not Kruskal-Wallis, not Cohen's d / omega / epsilon).
- Q3: a logistic-regression classifier on the four body measurements, with feature standardisation, an 80/20 split, and a fixed random seed of 42.
- Q4: the mean body mass reported separately for each of the three species.
- Structure: the report has Title, Data and methods, per-question Results, and a Conclusion.
- Missing data: rows with missing values were dropped listwise (not imputed).
The conclusion should state: body mass differs strongly/significantly among species with Gentoo heaviest; flipper length and body mass are positively correlated; and the sex-prediction accuracy.`

function genPrompt(cond) {
  return `Read the file at ${DIR}/${FILES[cond]} and follow it exactly. Run Python from the ` +
    `repository root (${REPO}) so the relative path data/penguins.csv resolves. Actually execute ` +
    `the analysis and use the real numbers. Then return the structured report result: the number ` +
    `and the method you used for each question (q1_r/q1_method, q2_p/q2_effect/q2_test/q2_effect_metric, ` +
    `q3_accuracy/q3_model/q3_seed/q3_scaled), q4_means as a map of species to mean body mass, the ` +
    `list of section headings you used, your conclusion paragraph, and report_md (the full report ` +
    `as markdown).`
}

function judgePrompt(gen) {
  return `You are grading a data-analysis report for adherence to a fixed statistical rubric. ` +
    `Judge ONLY from the report text below; do not re-run anything. For each rubric item, decide ` +
    `whether the report actually used that method. Also decide whether the conclusion states each ` +
    `required claim. Set adherence_score to the fraction of the six method/structure items that pass ` +
    `(q1, q2, q3, q4, structure, missing data), from 0 to 1.\n\n${RUBRIC}\n\n` +
    `=== REPORT UNDER REVIEW ===\n${(gen.report_md || '').slice(0, 12000)}\n=== END REPORT ===`
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
log(`generating ${items.length} reports (${CONDS.length} conditions x ${REPS} reps), then judging each`)

const out = await pipeline(
  items,
  (it) => genOne(it.cond, it.r),
  (gen, it) => {
    if (!gen) return { cond: it.cond, rep: it.r, ok: false }
    return agent(judgePrompt(gen), { label: `judge:${it.cond}-r${it.r}`, phase: 'Judge', schema: JUDGE_SCHEMA })
      .then((j) => ({
        cond: it.cond, rep: it.r, ok: true, provenance: RUN_PROVENANCE,
        q1_r: gen.q1_r, q1_method: gen.q1_method,
        q2_p: gen.q2_p, q2_effect: gen.q2_effect, q2_test: gen.q2_test, q2_effect_metric: gen.q2_effect_metric,
        q3_accuracy: gen.q3_accuracy, q3_model: gen.q3_model, q3_seed: gen.q3_seed, q3_scaled: gen.q3_scaled,
        q4_means: gen.q4_means, sections: gen.sections, conclusion: gen.conclusion,
        report_md: gen.report_md,
        judge: j,
      }))
  }
)
const ok = out.filter(o => o && o.ok).length
log(`completed: ${ok}/${items.length} reports generated and judged`)
return out
