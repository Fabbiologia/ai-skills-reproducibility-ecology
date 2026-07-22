---
name: penguins-sex-classifier
description: Run a reproducible holdout classifier for penguin sex from the four Palmer Penguins body measurements. Use when a compatible CSV contains bill length, bill depth, flipper length, body mass, and sex, and the requested output is test-set accuracy under the study's fixed reference protocol.
---

# Penguin sex classifier

Apply this contract exactly. If the requested estimand or available columns differ, stop and state that this skill is not applicable.

## Input contract

- Read `bill_length_mm`, `bill_depth_mm`, `flipper_length_mm`, `body_mass_g`, and `sex`.
- Drop rows missing any of those five values; do not impute.
- Use only the four measurements as predictors. Do not use species or island.

## Method contract

1. Split once with `train_test_split(test_size=0.2, random_state=42, stratify=y)`.
2. Fit `StandardScaler` on the training fold only, preferably in a pipeline.
3. Fit `LogisticRegression(max_iter=2000)` with otherwise default parameters.
4. Report `accuracy_score` on the held-out test fold.

## Validation contract

- Confirm 333 complete cases and 67 test cases for the archived Palmer Penguins file.
- Confirm the scaler never sees the test fold during fitting.
- Confirm the seed, split, predictor set, and model match this contract.
- For the archived fixture, require accuracy `0.8805970149` within absolute tolerance `0.001`.

Return the accuracy, sample sizes, method, seed, split, scaling rule, missing-data rule, and any contract failure.
