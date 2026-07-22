#!/usr/bin/env python3
"""Cross-provider replication harness for the skill-ablation experiment.

Each model from a different provider is given the same task prompt and asked to
return a complete, self-contained Python script. Every returned script is then
executed identically (same interpreter, same working directory, same timeout),
so the execution environment is held constant and only the model varies. This is
a uniform code-generation harness, deliberately simpler than the agentic harness
of the main experiment, so that two providers can be compared on equal terms.

Providers and models are read from PROVIDERS below; keys come from the
environment (OPENAI_API_KEY, GEMINI_API_KEY). Model id, provider, and decoding
temperature are recorded with every run. Nothing is written outside the results
directory, and no key is stored on disk by this script.

Usage (run under the venv that has openai + google-genai installed):
  crossprovider_harness.py <reps> <tasks csv> <conds csv> <out csv>
"""
import os, sys, re, json, subprocess, tempfile, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).parent
PROMPTS = HERE / "prompts"
EXEC_PY = "/opt/homebrew/bin/python3"   # interpreter with pandas/numpy/scipy/sklearn
TEMPERATURE = 1.0                        # fixed for both providers; allows run-to-run variation
TIMEOUT = 90

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TASKS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["T1", "T2", "T3", "T4"]
CONDS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["C0", "C4"]
OUT = HERE / "results" / (sys.argv[4] if len(sys.argv) > 4 else "crossprovider_records.csv")

PROVIDERS = [
    {"provider": "openai", "model": "gpt-4.1"},
    {"provider": "google", "model": "gemini-pro-latest"},
]

WRAP = (
    "You are given a data-analysis task. Write a COMPLETE, self-contained Python 3 "
    "script that performs it and prints ONLY a single JSON object on the very last "
    "line of standard output, with keys: value (the primary numeric quantity named "
    "at the end of the task), method (string), params (string), n (integer). "
    "The script runs from the repository root, so read data files at the exact "
    "relative paths named in the task. You may use pandas, numpy, scipy and "
    "scikit-learn. Output only the script inside one ```python code block, with no "
    "explanation before or after.\n\nTASK:\n"
)

def get_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()

def parse_value(stdout):
    """Return the last dict on stdout that carries a 'value' key. Accepts JSON or
    a Python-repr dict (single quotes)."""
    import ast
    cands = re.findall(r"\{[^{}]*\}", stdout)
    for c in reversed(cands):
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

def run_one(spec, task, cond, rep):
    run_id = f"{task}_{cond}_{spec['provider']}_r{rep}"
    prompt = WRAP + (PROMPTS / f"{task}_{cond}.txt").read_text()
    rec = {"run_id": run_id, "task": task, "condition": cond, "provider": spec["provider"],
           "model": spec["model"], "temperature": TEMPERATURE, "rep": rep,
           "value": None, "n": None, "error": ""}
    try:
        for attempt in range(3):
            try:
                text = CALL[spec["provider"]](spec["model"], prompt)
                break
            except Exception as e:
                if attempt == 2:
                    rec["error"] = f"api:{repr(e)[:120]}"; return rec
                time.sleep(3 * (attempt + 1))
        code = get_code(text)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
            f.write(code); tmp = f.name
        p = subprocess.run([EXEC_PY, tmp], cwd=str(HERE), capture_output=True, text=True, timeout=TIMEOUT)
        os.unlink(tmp)
        val = parse_value(p.stdout)
        if val is None:
            rec["error"] = "noparse:" + (p.stderr.strip()[-120:] or p.stdout.strip()[-120:])
        else:
            rec["value"] = val.get("value"); rec["n"] = val.get("n")
    except subprocess.TimeoutExpired:
        rec["error"] = "timeout"
    except Exception as e:
        rec["error"] = f"exec:{repr(e)[:120]}"
    return rec

def main():
    items = [(s, t, c, r) for s in PROVIDERS for t in TASKS for c in CONDS for r in range(1, REPS + 1)]
    print(f"launching {len(items)} runs: {[p['model'] for p in PROVIDERS]} x {TASKS} x {CONDS} x {REPS} reps")
    recs = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(run_one, s, t, c, r): (s, t, c, r) for (s, t, c, r) in items}
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result(); recs.append(rec)
            tag = "ok" if rec["value"] is not None else f"FAIL({rec['error'][:40]})"
            print(f"  [{i}/{len(items)}] {rec['run_id']}: value={rec['value']} {tag}", flush=True)
    import csv
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["run_id", "task", "condition", "provider", "model", "temperature", "rep", "value", "n", "error"])
        for r in recs:
            w.writerow([r["run_id"], r["task"], r["condition"], r["provider"], r["model"],
                        r["temperature"], r["rep"], r["value"], r["n"], r["error"]])
    ok = sum(1 for r in recs if r["value"] is not None)
    print(f"done: {ok}/{len(recs)} produced a value -> {OUT}")

if __name__ == "__main__":
    main()
