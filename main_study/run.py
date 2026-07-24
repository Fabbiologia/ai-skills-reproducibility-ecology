#!/usr/bin/env python3
"""Confirmatory run: 12 tasks x 3 instruction arms x N providers x R repeats.

Design points that answer the criticisms of the pilot study:

  * The unit of replication is the TASK. Twelve tasks span four fork types and
    four datasets, three tasks per fork type, so no mechanism rests on one task
    and no fork type is confounded with one dataset.
  * Three arms. `none` is the question alone; `skill` adds the written
    specification; `code` supplies a reference implementation for a DIFFERENT
    task of the same fork type, which the agent may adapt. The code arm is the
    rival explanation ("a skill is just code in prose") tested directly.
  * One uniform harness for every provider: each model returns a complete
    script and every script is executed identically.

Every model sees the same data preview an analyst would see, so the test is
about specification rather than about guessing column names.

Usage (needs OPENAI_API_KEY and GEMINI_API_KEY):
  run.py <reps> <out csv>
"""
import os, sys, re, json, subprocess, tempfile, time, csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).parent
REPO = HERE.parent
EXEC_PY = "/opt/homebrew/bin/python3"
TEMPERATURE = 1.0
TIMEOUT = 180

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 5
OUT = HERE / (sys.argv[2] if len(sys.argv) > 2 else "run_records.csv")

PROVIDERS = [
    {"provider": "openai", "model": "gpt-4.1"},
    {"provider": "google", "model": "gemini-pro-latest"},
]
REFS = json.loads((HERE / "references.json").read_text())

# A worked implementation of one task per fork type, given to the `code` arm for
# the OTHER tasks of that fork type. This mirrors real code reuse: you are handed
# a script that solves a problem of the same shape, not of the same dataset.
DONOR = {
    "aggregation": [
        ("A1_reef_biomass", """import pandas as pd
df = pd.read_csv("<file>")
per_unit = df.groupby(["Reef", "Transect"])["Biomass"].sum()
print(per_unit.mean())"""),
        ("A2_portal_abundance", """import pandas as pd
df = pd.read_csv("<file>")
r = df[df["taxa"] == "Rodent"]
print(r.groupby(["plot_id", "year"]).size().mean())"""),
    ],
    "scope": [
        ("S1_iris_corr", """import pandas as pd
from scipy import stats
df = pd.read_csv("<file>")
r, p = stats.pearsonr(df["sepal length (cm)"], df["sepal width (cm)"])
print(r)"""),
        ("S2_penguin_bill_corr", """import pandas as pd
from scipy import stats
df = pd.read_csv("<file>").dropna(subset=["bill_length_mm", "bill_depth_mm"])
r, p = stats.pearsonr(df["bill_length_mm"], df["bill_depth_mm"])
print(r)"""),
    ],
    "missing": [
        ("M1_penguin_gentoo_mass", """import pandas as pd
df = pd.read_csv("<file>")
d = df[df["species"] == "Gentoo"].dropna(subset=["sex", "body_mass_g"])
print(d[d["sex"] == "Female"]["body_mass_g"].mean())"""),
        ("M2_portal_dm_weight", """import pandas as pd
df = pd.read_csv("<file>")
print(df[df["species_id"] == "DM"]["weight"].dropna().mean())"""),
    ],
    "randomness": [
        ("R1_penguin_sex_clf", """import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
df = pd.read_csv("<file>").dropna(subset=cols + ["sex"])
Xtr, Xte, ytr, yte = train_test_split(df[cols], df["sex"], test_size=0.2,
                                      random_state=42, stratify=df["sex"])
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
print(accuracy_score(yte, m.predict(Xte)))"""),
        ("R2_iris_species_clf", """import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
cols = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
df = pd.read_csv("<file>")
Xtr, Xte, ytr, yte = train_test_split(df[cols], df["target"], test_size=0.2,
                                      random_state=42, stratify=df["target"])
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
print(accuracy_score(yte, m.predict(Xte)))"""),
    ],
}


def pick_donor(task_id, fork):
    """Never hand a task its own solution: use a donor from a different task of
    the same fork type."""
    for did, code in DONOR[fork]:
        if did != task_id:
            return did, code
    raise RuntimeError(f"no donor available for {task_id}")

WRAP = ("Write a COMPLETE, self-contained Python 3 script that answers the question below and "
        "prints ONLY a single JSON object on the very last line of standard output, with keys: "
        "value (the requested number), method (string), params (string). You may use pandas, "
        "numpy, scipy and scikit-learn. Output only the script inside one ```python code block, "
        "with no explanation before or after.\n\n")


def preview(path, n=6):
    with open(path, newline="") as f:
        r = csv.reader(f)
        header = next(r)
        rows = [row for _, row in zip(range(n), r)]
    body = "\n".join([",".join(header)] + [",".join(x) for x in rows])
    return ("\nThe file's columns are: " + ", ".join(header) +
            f"\nThe first {n} rows are:\n" + body + "\n")


def build_prompt(task_id, arm):
    t = REFS[task_id]
    # paths in references.json are repo-relative; scripts run with cwd at the root
    data_file = REPO / t["file"]
    body = f"QUESTION\n{t['question']}\n\nThe data are in the file {t['file']}."
    body += preview(data_file)
    if arm == "skill":
        body += ("\nSPECIFICATION (follow it exactly)\n" + t["spec"] + "\n")
    elif arm == "code":
        donor_id, donor_code = pick_donor(task_id, t["fork"])
        body += ("\nREFERENCE IMPLEMENTATION\nHere is a script that answers a question of the same "
                 "kind on a different dataset. Adapt it as necessary.\n```python\n"
                 + donor_code.replace("<file>", REFS[donor_id]["file"]) + "\n```\n")
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


def run_one(spec, task_id, arm, rep):
    t = REFS[task_id]
    rid = f"{task_id}|{arm}|{spec['provider']}|r{rep}"
    rec = {"run_id": rid, "task": task_id, "fork": t["fork"], "dataset": t["dataset"],
           "arm": arm, "provider": spec["provider"], "model": spec["model"], "rep": rep,
           "value": None, "correct": None, "error": ""}
    prompt = build_prompt(task_id, arm)
    try:
        for attempt in range(3):
            try:
                text = CALL[spec["provider"]](spec["model"], prompt); break
            except Exception as e:
                if attempt == 2:
                    rec["error"] = f"api:{repr(e)[:100]}"; return rec
                time.sleep(3 * (attempt + 1))
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir="/tmp") as f:
            f.write(get_code(text)); tmp = f.name
        p = subprocess.run([EXEC_PY, tmp], cwd=str(REPO), capture_output=True,
                           text=True, timeout=TIMEOUT)
        os.unlink(tmp)
        val = parse_value(p.stdout)
        if val is None:
            rec["error"] = "noparse:" + (p.stderr.strip()[-100:] or p.stdout.strip()[-100:])
        else:
            rec["value"] = float(val["value"])
            rec["correct"] = abs(rec["value"] - t["reference"]) <= t["tolerance"]
    except subprocess.TimeoutExpired:
        rec["error"] = "timeout"
    except Exception as e:
        rec["error"] = f"exec:{repr(e)[:100]}"
    return rec


def main():
    items = [(s, tid, arm, r) for s in PROVIDERS for tid in REFS
             for arm in ("none", "skill", "code") for r in range(1, REPS + 1)]
    print(f"launching {len(items)} runs = {len(REFS)} tasks x 3 arms x "
          f"{len(PROVIDERS)} providers x {REPS} reps")
    recs = []
    # write incrementally so a interrupted run keeps everything already finished
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["run_id", "task", "fork", "dataset", "arm", "provider", "model",
                    "rep", "value", "correct", "error"])
        fh.flush()
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(run_one, s, t, a, r) for (s, t, a, r) in items]
            for i, fut in enumerate(as_completed(futs), 1):
                rec = fut.result(); recs.append(rec)
                w.writerow([rec["run_id"], rec["task"], rec["fork"], rec["dataset"], rec["arm"],
                            rec["provider"], rec["model"], rec["rep"], rec["value"],
                            rec["correct"], rec["error"]])
                fh.flush()
                tag = ("ok" if rec["correct"] else "WRONG") if rec["value"] is not None \
                      else f"FAIL({rec['error'][:26]})"
                if i % 20 == 0 or rec["value"] is None:
                    print(f"  [{i}/{len(items)}] {rec['run_id'][:44]:46} {tag}", flush=True)
    ok = sum(1 for r in recs if r["correct"])
    print(f"\ndone: {ok}/{len(recs)} correct -> {OUT}")


if __name__ == "__main__":
    main()
