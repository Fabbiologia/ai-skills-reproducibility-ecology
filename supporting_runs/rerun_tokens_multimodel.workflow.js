export const meta = {
  name: 'skills-repro-tokens-multimodel',
  description: 'Re-run the 4-task skill ablation to measure (a) token cost across C0-C4 on one model and (b) cross-model convergence at C0/C4 for three models; ~216 analysis agents that each execute real Python',
  phases: [
    { title: 'token', detail: 'opus: 4 tasks x 5 conditions x 6 reps = 120' },
    { title: 'multimodel', detail: 'sonnet + haiku: 4 tasks x {C0,C4} x 6 reps = 96' },
  ],
}

const REPO = '/Users/fabiofavoretto/Library/CloudStorage/OneDrive-UniversityofPlymouth/Projects/skills/for_submission'
const TASKS = ['T1', 'T2', 'T3', 'T4']
const ALLC = ['C0', 'C1', 'C2', 'C3', 'C4']
const C04 = ['C0', 'C4']
const REPS = 6

const SCHEMA = {
  type: 'object',
  properties: {
    run_id:    { type: 'string', description: 'the run_id given to you; return it verbatim' },
    value:     { type: ['number', 'null'], description: 'the primary computed quantity named at the bottom of the prompt file' },
    secondary: { type: ['number', 'null'] },
    direction: { type: ['string', 'null'] },
    method:    { type: 'string' },
    params:    { type: 'string' },
    n:         { type: ['number', 'null'] },
    code_lines:{ type: ['number', 'null'], description: 'lines of Python you actually executed' },
  },
  required: ['run_id', 'value', 'method', 'params'],
  additionalProperties: true,
}

function jobPrompt(t, c, runId) {
  return `Work in the directory ${REPO} (all data files are under ${REPO}/data/). ` +
    `Read the file ${REPO}/prompts/${t}_${c}.txt and follow its instructions EXACTLY. ` +
    `You MUST actually execute Python 3 via the Bash tool using /opt/homebrew/bin/python3 ` +
    `(sklearn, scipy, pandas, numpy installed) to compute the REAL numbers — never guess or estimate. ` +
    `Your run_id is "${runId}"; return it verbatim in the run_id field. ` +
    `Report 'value' = the primary quantity named at the bottom of the file, plus method, params, ` +
    `n, and code_lines. Return the structured output only.`
}

async function runOne(t, c, model, r, phase) {
  const runId = `${t}_${c}_${model}_r${r}`
  let res = null
  try {
    res = await agent(jobPrompt(t, c, runId), {
      label: runId, phase, schema: SCHEMA, agentType: 'general-purpose', model,
    })
  } catch (e) { res = null }
  return {
    run_id: runId, task: t, condition: c, model, rep: r,
    value: res && res.value != null ? res.value : null,
    method: res ? (res.method || null) : null,
    params: res ? (res.params || null) : null,
    n: res ? (res.n ?? null) : null,
    code_lines: res ? (res.code_lines ?? null) : null,
    echoed_run_id: res ? (res.run_id || null) : null,
  }
}

const items = []
for (const t of TASKS) for (const c of ALLC) for (let r = 1; r <= REPS; r++)
  items.push({ t, c, model: 'opus', r, phase: 'token' })
for (const m of ['sonnet', 'haiku']) for (const t of TASKS) for (const c of C04) for (let r = 1; r <= REPS; r++)
  items.push({ t, c, model: m, r, phase: 'multimodel' })

log(`launching ${items.length} runs (token: opus x5 conds; multimodel: sonnet+haiku at C0/C4), ${REPS} reps each`)
const out = await parallel(items.map(it => () => runOne(it.t, it.c, it.model, it.r, it.phase)))
const ok = out.filter(o => o && o.value != null).length
const idmatch = out.filter(o => o && o.echoed_run_id === o.run_id).length
log(`completed ${ok}/${out.length} with a value; ${idmatch}/${out.length} echoed run_id correctly`)
return { n_launched: items.length, n_value: ok, n_idmatch: idmatch, runs: out }
