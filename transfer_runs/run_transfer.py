#!/usr/bin/env python3
"""Transfer pilot: does a prose skill survive a change of schema better than code?

Same data, same correct answer (3.4641913664166615) in every variant; only the
surface form changes. Three instruction arms, all written against the ORIGINAL
schema, so each is asked to transfer:

  none   the task alone, no guidance
  skill  the prose input/method contract (names the original columns)
  code   the reference implementation (hard-codes the original columns), which
         the agent is explicitly allowed to adapt

Every arm goes through one uniform harness: the model returns a complete Python
script, and every script is executed identically. Any failure is a transfer
failure, not a data difference.

Usage (needs OPENAI_API_KEY and GEMINI_API_KEY in the environment):
  run_transfer.py <reps> <out csv>
"""
import os, sys, re, json, subprocess, tempfile, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).parent
DATA = HERE / "data"
EXEC_PY = "/opt/homebrew/bin/python3"
TEMPERATURE = 1.0
TIMEOUT = 120
REFERENCE = 3.4641913664166615
TOL = 1e-2

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
OUT = HERE / (sys.argv[2] if len(sys.argv) > 2 else "transfer_records.csv")

PROVIDERS = [
    {"provider": "openai", "model": "gpt-4.1"},
    {"provider": "google", "model": "gemini-pro-latest"},
]
DATASETS = {
    "home":    DATA / "reef_home.csv",
    "renamed": DATA / "reef_renamed.csv",
    "long":    DATA / "reef_long.csv",
}

TASK = (
    "The file at {path} contains reef-fish visual-transect survey data from Cabo Pulmo "
    "National Park (Gulf of California) for 2023. Inspect the file to understand how it is "
    "organised. Report the mean per-transect fish biomass for the reserve, that is, the total "
    "community biomass on a transect, averaged across transects."
)

SKILL = """
--- SKILL: ltem-reef-fish-biomass v1.0 (input + method contract) ---
INPUT CONTRACT: a transect survey unit = a unique (Reef, Transect) combination; use the
`Biomass` column as the per-record biomass; treat records carrying no biomass value as
contributing no biomass (skip them in sums, do not fill with zero-inflating rows). Do not
re-normalise by Area (Biomass is already the record's biomass, from a fixed transect).
METHOD: for each (Reef, Transect) survey unit, SUM the biomass across its records; then take
the MEAN of those per-transect totals across all survey units.
--- END SKILL ---
"""

CODE = """
--- REFERENCE IMPLEMENTATION (written for the original dataset) ---
```python
import pandas as pd
df = pd.read_csv("data/ltem_cabo_pulmo_2023.csv")
per_transect = df.groupby(["Reef", "Transect"])["Biomass"].sum()
print(per_transect.mean())
```
--- END REFERENCE IMPLEMENTATION ---
You may adapt this implementation as necessary for the file you have been given.
"""

WRAP = (
    "Write a COMPLETE, self-contained Python 3 script that performs the task below and prints "
    "ONLY a single JSON object on the very last line of standard output, with keys: value (the "
    "requested number), method (string), params (string), n (integer, the number of survey units "
    "used). You may use pandas and numpy. Output only the script inside one ```python code block, "
    "with no explanation before or after.\n\nTASK:\n"
)


def preview(path, n=6):
    """Show the schema and a few rows, as any analyst would see before starting.
    Without this the model must write a script blind and cannot map columns at
    all, which would test guessing rather than transfer."""
    import csv
    with open(path, newline="") as f:
        r = csv.reader(f)
        header = next(r)
        rows = [row for _, row in zip(range(n), r)]
    body = "\n".join([",".join(header)] + [",".join(x) for x in rows])
    return ("\nThe file's columns are: " + ", ".join(header) +
            f"\nThe first {n} rows are:\n" + body + "\n")


def build_prompt(arm, path):
    body = TASK.format(path=path) + preview(path)
    if arm == "skill":
        body += "\n" + SKILL
    elif arm == "code":
        body += "\n" + CODE
    return WRAP + body


def get_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def parse_value(stdout):
    import ast
    for c in reversed(re.findall(r"\{[^{}]*\}", stdout)):
        for loader in (json.loads, ast.literal_eval):
            try:
                o = loader(c)
                if isinstance(o, dict) and "value" in o and isinstance(o["value"], (int, float)):
                    return o
            except Exception:
                pass
    return None


def call_openai(model, prompt):
    from openai import OpenAI
    oc = OpenAI(api_key=os.environ["OPENAI_API_KEY"], project=os.environ.get("OPENAI_PROJECT"))
    r = oc.chat.completions.create(model=model, temperature=TEMPERATURE,
                                   messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content


def call_google(model, prompt):
    from google import genai
    from google.genai import types
    gc = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    r = gc.models.generate_content(model=model, contents=prompt,
                                   config=types.GenerateContentConfig(temperature=TEMPERATURE))
    return r.text


CALL = {"openai": call_openai, "google": call_google}


def run_one(spec, arm, ds, rep):
    rid = f"{arm}_{ds}_{spec['provider']}_r{rep}"
    rec = {"run_id": rid, "arm": arm, "dataset": ds, "provider": spec["provider"],
           "model": spec["model"], "rep": rep, "value": None, "n": None,
           "correct": None, "error": ""}
    prompt = build_prompt(arm, DATASETS[ds])
    try:
        for attempt in range(3):
            try:
                text = CALL[spec["provider"]](spec["model"], prompt); break
            except Exception as e:
                if attempt == 2:
                    rec["error"] = f"api:{repr(e)[:110]}"; return rec
                time.sleep(3 * (attempt + 1))
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
            f.write(get_code(text)); tmp = f.name
        p = subprocess.run([EXEC_PY, tmp], cwd=str(HERE), capture_output=True,
                           text=True, timeout=TIMEOUT)
        os.unlink(tmp)
        val = parse_value(p.stdout)
        if val is None:
            rec["error"] = "noparse:" + (p.stderr.strip()[-110:] or p.stdout.strip()[-110:])
        else:
            rec["value"] = val.get("value"); rec["n"] = val.get("n")
            rec["correct"] = abs(float(val["value"]) - REFERENCE) <= TOL
    except subprocess.TimeoutExpired:
        rec["error"] = "timeout"
    except Exception as e:
        rec["error"] = f"exec:{repr(e)[:110]}"
    return rec


def main():
    items = [(s, a, d, r) for s in PROVIDERS for a in ("none", "skill", "code")
             for d in DATASETS for r in range(1, REPS + 1)]
    print(f"launching {len(items)} runs  (3 arms x 3 datasets x {len(PROVIDERS)} providers x {REPS} reps)")
    recs = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(run_one, s, a, d, r) for (s, a, d, r) in items]
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result(); recs.append(rec)
            tag = ("correct" if rec["correct"] else "WRONG") if rec["value"] is not None \
                  else f"FAIL({rec['error'][:34]})"
            print(f"  [{i}/{len(items)}] {rec['run_id']:34} {str(rec['value'])[:20]:22} {tag}", flush=True)
    import csv
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["run_id", "arm", "dataset", "provider", "model", "rep", "value", "n", "correct", "error"])
        for r in recs:
            w.writerow([r["run_id"], r["arm"], r["dataset"], r["provider"], r["model"],
                        r["rep"], r["value"], r["n"], r["correct"], r["error"]])
    ok = sum(1 for r in recs if r["correct"])
    print(f"\ndone: {ok}/{len(recs)} correct -> {OUT}")


if __name__ == "__main__":
    main()
