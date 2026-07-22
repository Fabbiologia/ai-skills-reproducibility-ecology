#!/usr/bin/env python3
"""Build schema variants of the reef-fish file for the transfer pilot.

Every variant contains exactly the same measurements as the original, so the
correct answer (mean per-transect community biomass, survey unit = reef x
transect, sum then mean) is identical in all of them: 3.4641913664166615.
Only the surface form changes. Any failure is therefore a transfer failure and
not a difference in the underlying data.

  home     original columns, blank cells for missing biomass
  renamed  synonymous column names, -999 sentinel for missing biomass
  long     tidy long format (one row per measurement), missing biomass absent

Derived from restricted LTEM data, so the outputs stay out of version control.
"""
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
REF = 3.4641913664166615

src = pd.read_csv(HERE.parent / "data" / "ltem_cabo_pulmo_2023.csv")

# ---------- home ----------
home = src.copy()
home.to_csv(OUT / "reef_home.csv", index=False)

# ---------- renamed: synonyms + -999 sentinel ----------
ren = src.rename(columns={
    "Year": "yr", "Month": "mo", "Day": "dy", "Region": "region",
    "Reef": "site_code", "Habitat": "zone", "MPA": "protection",
    "Transect": "replicate", "Area": "area_m2", "IDSpecies": "taxon_id",
    "Species": "taxon", "Quantity": "n_individuals", "Size": "length_cm",
    "Biomass": "biomass_g",
}).copy()
ren["biomass_g"] = ren["biomass_g"].fillna(-999)
ren.to_csv(OUT / "reef_renamed.csv", index=False)

# ---------- long: tidy, one row per measurement ----------
keep = src[["Reef", "Habitat", "Transect", "Species", "Quantity", "Size", "Biomass"]].copy()
keep.insert(0, "record_id", range(1, len(keep) + 1))
long = keep.melt(
    id_vars=["record_id", "Reef", "Habitat", "Transect", "Species"],
    value_vars=["Quantity", "Size", "Biomass"],
    var_name="metric", value_name="value",
).dropna(subset=["value"])          # missing measurements simply absent
long["metric"] = long["metric"].map({"Quantity": "abundance", "Size": "length_cm",
                                     "Biomass": "biomass_g"})
long = long.rename(columns={"Reef": "site", "Habitat": "zone",
                            "Transect": "replicate", "Species": "taxon"})
long = long.sort_values(["record_id", "metric"]).reset_index(drop=True)
long.to_csv(OUT / "reef_long.csv", index=False)

# ---------- verify the correct answer is invariant ----------
a = pd.read_csv(OUT / "reef_home.csv").groupby(["Reef", "Transect"])["Biomass"].sum().mean()
b = pd.read_csv(OUT / "reef_renamed.csv")
b = b[b["biomass_g"] != -999].groupby(["site_code", "replicate"])["biomass_g"].sum().mean()
c = pd.read_csv(OUT / "reef_long.csv")
c = c[c["metric"] == "biomass_g"].groupby(["site", "replicate"])["value"].sum().mean()

print(f"{'variant':10}{'answer':>22}  matches reference")
for name, val in [("home", a), ("renamed", b), ("long", c)]:
    print(f"{name:10}{val:>22.13f}  {abs(val - REF) < 1e-9}")
assert all(abs(v - REF) < 1e-9 for v in (a, b, c)), "variant changed the correct answer"
print("\nAll three variants preserve the reference exactly.")
for f in ["reef_home.csv", "reef_renamed.csv", "reef_long.csv"]:
    d = pd.read_csv(OUT / f)
    print(f"  {f:20} {d.shape[0]:>6} rows  cols: {list(d.columns)}")
