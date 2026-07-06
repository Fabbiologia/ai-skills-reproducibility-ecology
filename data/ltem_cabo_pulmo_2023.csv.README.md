# ltem_cabo_pulmo_2023.csv — available on request

The real reef-fish visual-transect data used for Task T4 (Cabo Pulmo National
Park, Gulf of California, 2023 surveys) is **not distributed in this repository**.
It comes from the Long-Term Ecological Monitoring (LTEM) programme and is
restricted. It is **available on request from the Aburto Lab**
(Scripps Institution of Oceanography, UC San Diego) and collaborators.

Everything else needed to reproduce the study is included, and the aggregate T4
results (in `results_v2.json`, `results_v2_R.json`, and the manuscript) are derived
from this file. Tasks T1, T2, and T3 (iris and Palmer Penguins) are fully
reproducible from the repository as-is.

## To reproduce Task T4 once you have the file

Place the file at this exact path:

    data/ltem_cabo_pulmo_2023.csv

It must contain one row per species record on one transect, with at least these
columns (this is what the T4 prompts and the reference recipe expect):

| Column   | Meaning                                             |
|----------|-----------------------------------------------------|
| Reef     | reef name                                           |
| Habitat  | depth stratum / habitat (BLOQUES, RISCO, PARED)     |
| Transect | transect id within a reef                           |
| Species  | species name                                        |
| Quantity | count                                               |
| Size     | size (cm)                                            |
| Area     | transect area (m²; 250 for fish transects)          |
| Biomass  | biomass of that record (blank/NA for non-biomass)   |

Reference value (canonical recipe): mean per-transect fish biomass, with a
transect survey unit defined as (Reef, Transect), summing `Biomass` within a unit
(NA treated as no biomass) and then averaging across units = **3.4642**.
The dataset used here has 2,798 rows across 10 Cabo Pulmo reefs.
