# Proposed AI Skill Evidence Standard (version 0.1)

This folder makes the manuscript's repository proposal executable. It does not claim to be a universal or final standard. It is a falsifiable minimum submission contract derived from the study: a skill entry must declare what it computes, which choices it fixes, the environment it assumes, how closely repeated outputs must agree, what reference output it must match, how method coherence is checked, and where it is known not to generalise.

Each candidate entry contains the instruction artifact (`SKILL.md`) and `skill-evidence.json`, validated against `skill-evidence.schema.json`. The manifest separates three acceptance gates that the experiments showed should not be collapsed:

1. **Self-consistency:** repeated executions agree within a declared tolerance.
2. **Reference validity:** outputs match independently stored fixtures within that tolerance.
3. **Method coherence:** the delivered output actually follows the declared analytical contract.

The manifest also requires versioning, provenance, environment constraints, fixed stochastic controls, and known limitations. These fields are repository requirements proposed by the authors; only the effects of contracts and controls were experimentally ablated in the present study.

Validate every example with:

```bash
python repository_standard/validate_skills.py
```

The `penguins-sex-classifier` entry is a worked example built from Task T2. A production repository should additionally run the declared fixtures across multiple model providers, retain full agent rollouts, record failure and retry counts, and publish signed result summaries for every skill version.
