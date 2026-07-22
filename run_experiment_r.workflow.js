export const meta = {
  name: 'skills-reproducibility-v2-R',
  description: 'R arm: run 4 tasks x 5-rung skill ablation x 10 reps = 200 independent R agent runs (iris/penguins/LTEM); return structured results',
  phases: [{ title: 'Runs', detail: '200 independent R analysis agents' }],
}

// EDIT THIS to the absolute path of your checkout before running (agents need an
// absolute path to read each prompt file, and R runs from the repository root).
const REPO = '/ABSOLUTE/PATH/TO/for_submission'   // <-- set to your repository root
const DIR = REPO + '/prompts_r'
const TASKS = ['T1', 'T2', 'T3', 'T4']
const CONDS = ['C0', 'C1', 'C2', 'C3', 'C4']
const REPS = 10
// Required for new run sets. The 2026 archival run predates this guard and does
// not contain these fields; do not infer them retrospectively.
const RUN_PROVENANCE = {
  harness: 'REQUIRED: application and workflow-harness version',
  provider: 'REQUIRED: model provider',
  model: 'REQUIRED: exact model identifier/version',
  decoding: 'REQUIRED: temperature, top-p, seed, and any unavailable controls',
  run_date_utc: 'REQUIRED: ISO-8601 date/time',
}
if (Object.values(RUN_PROVENANCE).some(v => v.startsWith('REQUIRED:'))) {
  throw new Error('Complete RUN_PROVENANCE before launching a new experiment run set.')
}

const SCHEMA = {
  type: 'object',
  properties: {
    value:     { type: ['number', 'null'], description: 'the primary computed quantity' },
    secondary: { type: ['number', 'null'] },
    direction: { type: ['string', 'null'] },
    method:    { type: 'string' },
    params:    { type: 'string' },
    n:         { type: ['number', 'null'] },
  },
  required: ['value', 'method', 'params'],
  additionalProperties: true,
}

function jobPrompt(t, c) {
  return `Read the file at ${DIR}/${t}_${c}.txt and follow its instructions EXACTLY. ` +
    `You MUST actually execute R with Rscript (the packages stats, dplyr, and readr are available) ` +
    `to compute the real numbers, never guess or estimate. Run R from the repository root ` +
    `(${REPO}) so that the relative data paths resolve. Then report the result via the structured ` +
    `output with the exact fields requested in the file (value, secondary, direction, method, ` +
    `params, n). 'value' must be the primary quantity named at the bottom of the file.`
}

async function runOne(t, c, r) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const res = await agent(jobPrompt(t, c), {
      label: `R-${t}-${c}-r${r}${attempt ? '.' + attempt : ''}`,
      phase: 'Runs', schema: SCHEMA,
    })
    if (res && res.value !== undefined && res.value !== null) {
      return { task: t, condition: c, rep: r, provenance: RUN_PROVENANCE, ...res }
    }
  }
  return { task: t, condition: c, rep: r, provenance: RUN_PROVENANCE, value: null, method: 'FAILED', params: '', secondary: null, direction: null, n: null }
}

const items = []
for (const t of TASKS) for (const c of CONDS) for (let r = 1; r <= REPS; r++) items.push({ t, c, r })
log(`launching ${items.length} R runs (${TASKS.length} tasks x ${CONDS.length} conds x ${REPS} reps)`)

const out = await parallel(items.map(it => () => runOne(it.t, it.c, it.r)))
const ok = out.filter(o => o && o.value !== null).length
log(`completed: ${ok}/${items.length} successful`)
return out
