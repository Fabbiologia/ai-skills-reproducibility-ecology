const T = require("./theme.js");
const { P, TITLE, H1, H2, H3, CAP, BULLET, NUM, REFP, HR, GAP, PB, img, table, buildDoc, write, rt } = T;
const path = require("path");
const RES = path.resolve(__dirname, "..", "results");

const c = [];

// ---------------- TITLE / AUTHORS ----------------
c.push(TITLE("Skills as the new packages: an evidence-based standard for good AI analysis skills and a curated repository for ecology"));
c.push(P("Fabio Favoretto¹*, Alberto Rivera², Eduardo León Solorzano³", { spacing: { after: 40 } }));
c.push(P("¹ School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { size: 20, spacing: { after: 20 } }));
c.push(P("² Scripps Institution of Oceanography, University of California San Diego, La Jolla, CA, USA", { size: 20, spacing: { after: 20 } }));
c.push(P("³ Centro para la Biodiversidad Marina y la Conservación, A.C., La Paz, BCS, Mexico", { size: 20, spacing: { after: 20 } }));
c.push(P("* Corresponding author: fabio.favoretto@plymouth.ac.uk", { size: 20, spacing: { after: 40 } }));
c.push(P("Article type: Research Article. Target journal: Methods in Ecology and Evolution.", { size: 20 }));
c.push(HR());

// ---------------- ABSTRACT ----------------
c.push(H1("Abstract"));
c.push(P("1. Software packages, shared through curated repositories such as CRAN for R, made data analysis reusable and easier to reproduce. Large language models (LLMs) and agent tools are now used for ecological analysis, and the structured instructions that drive them, which we call skills, are becoming a reusable unit of the same kind. Today skills are shared informally, without versions, tests, or review. We argue that skills should be treated like packages and distributed through a curated repository, and we use controlled experiments to work out what such a repository should require of a skill."));
c.push(P("2. We ran two controlled experiments, and we summarised the current literature to set the context. The first crossed four analysis tasks with five levels of skill detail, in two languages (Python and R), and repeated each combination ten times, for 400 runs in total. Each level adds one kind of instruction to the one before it, so we can see which part of a skill does the work, and the two languages let us check whether different code reaches the same answer. The second experiment raised the output from a single number to a whole data report and used an independent judge to check whether each report used the statistics the skill specifies."));
c.push(P("3. Reproducibility was already high when a task had one obvious way to do it. Where a task involved randomness, run to run variation disappeared only when the skill fixed the random seed and the data handling (agreement rose from 16 of 30 runs to 20 of 20; Fisher P = 2×10⁻⁴). On real reef fish data, plain runs were perfectly consistent but gave the wrong value, and the answer became correct only when the skill fixed how the survey unit was defined (from 0 of 20 correct to 30 of 30; P = 2×10⁻¹⁴). A long but vague skill did not help, and sometimes made things worse. In the report experiment, a full methods skill made reports use the specified statistics (coherence rose to 100%), and for a report whose analyses each had a real method fork it also restored agreement between independent reports from half to all."));
c.push(P("4. Skills improve reproducibility by removing choices, not by adding words, and the part that matters depends on the task. From the results we set out a short standard for a good skill (fix the random settings, fix the input and method contract, declare a reference value and a tolerance, and add do-not rules and a check list), three automated checks a skill should pass before it is published (self-consistency, reference, and coherence), and the design of a curated repository for Model Context Protocol servers and skills. Treating skills as versioned, tested, reviewed packages would give ecology a dependable and citable body of analysis skills, and we provide an open experimental design for testing them."));
c.push(P("Keywords: reproducibility; large language models; agent skills; Model Context Protocol; research software; package repository; open science; FAIR; conservation; marine ecology.", { spacing: { before: 120 } }));
c.push(PB());

// ---------------- 1 INTRODUCTION ----------------
c.push(H1("1  Introduction"));
c.push(P("Reproducibility is the basis of cumulative science, yet across fields a large share of published computational results cannot be regenerated. In a survey of 1,576 researchers, more than 70% had failed to reproduce another group's results and more than half had failed to reproduce their own (Baker, 2016). In ecology and evolutionary biology the problem sits in the analysis. Data are shared more and more often, but the analysis code is frequently missing, broken, or undocumented (Culina et al., 2020; Kellner et al., 2025). Even when the code is available, results reproduce only some of the time (Kambouris et al., 2024)."));
c.push(P("At the same time, LLMs and agent tools are being used for ecological work, from pulling data out of text to reading quantitative datasets (Gallois et al., 2025). These tools bring a new problem. They are stochastic, so the same request can give different outputs on repeated runs, and their behaviour changes with the wording and layout of the prompt (He et al., 2024). One proposed fix is to package expert procedure into reusable, structured skills, that is, clear instructions, contracts, check lists, examples, and tool directions that guide a model toward a repeatable result. Whether skills actually make results reproducible, and which of their parts matter, is still an open question."));
c.push(P("There is a precedent for making a new kind of analysis dependable. Software packages, distributed through curated repositories such as CRAN for R and Bioconductor for bioinformatics, turned analysis code into versioned, documented, tested, and reviewed units, and the analyses built on them became easier to reproduce. Skills play the same role for LLMs and their tools, especially now that tools are reached through a shared interface such as the Model Context Protocol (MCP), so a skill can package an expert procedure together with the tools and data it calls. Yet skills today are shared informally, without versions, tests, or review, much as analysis code was before package repositories existed. We argue that skills should be treated like packages and distributed through a curated repository, and that the repository should admit a skill only when the skill is shown to produce reproducible and correct results. This raises a concrete question. What must a skill contain, and what must it be tested for, to deserve a place in such a repository? We answer both with controlled experiments and turn the answer into a standard and a repository design."));
c.push(P("One distinction frames this study. Following Goodman et al. (2016), we separate methods reproducibility (re-running the same code gives the same result), results reproducibility (an independent analysis gives the same result), and inferential reproducibility (the same conclusion is drawn). Most ecological work measures code reproducibility, but for someone using the result the useful target is output reproducibility, meaning whether the analysis gives the same answer even if the code differs. We use this output-based definition throughout, in line with Gundersen (2021). We treat two analyses as output-reproducible when they agree within a set tolerance, for example the same effect direction and significance, or the same number within a stated margin, whatever the code."));
c.push(P("We first summarise what earlier work shows (Section 2). We then report two experiments, one on a single analytical output (Sections 3 and 4) and one on a whole report (Section 5). From their results we set out a standard for a good skill, the checks it should pass, and the design of a curated repository for MCP and skills (Section 6), and we discuss the implications (Section 7). The experiments are the evidence, and the standard and the repository are the contribution. The literature review sets the context and is not a formal systematic review."));

// ---------------- 2 BACKGROUND ----------------
c.push(H1("2  Background from earlier work"));
c.push(P("We searched the literature (Google Scholar, general web search, and targeted journal and preprint searching, July 2026) for evidence on AI skills and the output reproducibility of ecological and computational analyses. We read 19 studies closely. The list of studies, the search terms, and what we recorded from each study are in the Supporting Information (S1 to S4). Four points stand out."));
c.push(P("First, baseline reproducibility in ecology is low, and code is the main limit. Code is shared for a minority of studies and often does not run (Culina et al., 2020; Kellner et al., 2025). Even when both data and code are shared, only 27% to 73% of targeted meta-analytic results could be reproduced, depending on how strict the check was (Kambouris et al., 2024). General computing shows the same pattern. Only 26% of R files ran, rising to 44% after automated cleaning (Trisovic et al., 2022), and just 4.0% of 1.4 million notebooks reproduced their stated results (Pimentel et al., 2019)."));
c.push(P("Second, LLM and agent help adds a new source of variation that fixed code does not have. Prompt layout alone changed task performance by up to 40% (He et al., 2024). Repeated agent runs drift in the tools, the order, and the arguments they choose (How Consistent Are LLM Agents?, 2026), and even greedy decoding is not deterministic in practice, although determinism can be recovered at a cost in speed (Nondeterminism in LLM inference, 2025). In ecology, general LLM outputs were accurate for taxonomy (94.9%) but weak for conservation status (27.2%), so reliability depends on the task (LLM ecological knowledge benchmark, 2026)."));
c.push(P("Third, structure helps. Standardising the software environment gave the largest single gain in re-execution success (Trisovic et al., 2022). Structured reporting protocols such as ODMAP for species distribution models (Zurell et al., 2020) and PRISMA-EcoEvo (O'Dea et al., 2021) improve documentation and reporting. In the LLM setting, running a task several times and combining the answers (self-consistency) makes the output more stable (Wang et al., 2023). These map onto the parts of a skill, such as explicit steps, an input and output contract, an environment specification, a validation check list, a tool-use contract, and worked examples."));
c.push(P("Fourth, the useful thing to measure is the output, not the code. Most work measures code reproducibility, yet what matters in practice is whether the analysis gives the same answer (Goodman et al., 2016; Gundersen, 2021). A skill that writes different but equivalent code, and reaches the same answer within tolerance, should count as reproducing the result. We did not find a study that set output-equivalence tolerances for AI-assisted ecological analysis."));
c.push(P("Taken together, no study we read had directly tested whether AI skills improve the output reproducibility of ecological analyses. The direct evidence is about general LLM and agent consistency, and the ecological evidence is about code reproducibility without AI. The experiment below tests the missing case directly."));
c.push(PB());

// ---------------- 3 METHODS ----------------
c.push(H1("3  Study 1: materials and methods"));
c.push(P("Study 1 tests reproducibility at the level of a single analytical output (one number per task). Study 2 (Section 5) raises this to a whole report."));
c.push(H2("3.1  Rationale and hypotheses"));
c.push(P("We expected that (H1) richer, more structured skills reduce run to run variation; (H2) the reduction comes from parts that fix the analysis (input and output contracts, fixed parameters and seeds, an explicit method, and warnings about mistakes) rather than from length; and (H3) reproducibility and validity are different, so a skill can make an analysis consistent without making it correct, and the reverse. To tell these apart we added one skill feature at a time, rather than comparing a single skill against no skill."));
c.push(H2("3.2  Design"));
c.push(P("We ran a fully crossed design of 4 tasks by 5 skill levels by 2 languages (Python and R) with 10 independent replicate runs per cell, giving 400 runs. Each run was a fresh autonomous LLM agent, a general-purpose coding agent built on the same underlying model, given the same prompt, told to run the analysis (Python or R) against a fixed local data file and return a structured result. Within a cell all 10 prompts were identical, so the only source of variation was the agent's own run to run stochasticity, which is the variation the literature describes. Runs were orchestrated independently, and no run could see another run's output. The two languages let us test a stronger form of reproducibility, namely whether independent implementations in different languages reach the same answer, which is results reproducibility in the sense of Goodman et al. (2016)."));
c.push(H2("3.3  Tasks and datasets"));
c.push(P("We chose four tasks to cover different analysis types and different ways an analysis can diverge, and because each has a reference answer that depends on the method chosen (Table 1). Data were given as fixed local files, so the only thing that varied was the method, not the data. The iris and Palmer Penguins datasets are standard open teaching datasets. Task T4 uses real reef fish visual-census data from the Long-Term Ecological Monitoring programme in Cabo Pulmo National Park, Gulf of California (2023 surveys, 2,798 species records across 10 reefs)."));
c.push(table(
  ["Task", "Dataset (domain)", "Question", "Main source of divergence", "Reference"],
  [
    ["T1", "iris (classic)", "Correlation of sepal length and width, and its sign", "Scope of the correlation (pooled vs within species), which can flip the sign (Simpson's paradox)", "r = −0.1176"],
    ["T2", "Palmer penguins (ecology)", "Predict sex from body measurements, test accuracy", "Model choice, data split, random seed, and scaling", "0.8806"],
    ["T3", "Palmer penguins (ecology)", "Does body mass differ among species, effect size", "Which effect size or test is used", "η² = 0.6697"],
    ["T4", "LTEM reef fish (marine ecology)", "Mean fish biomass per transect in the reserve", "How records are combined per transect. Averaging rows directly is about 30 times too low", "3.4642"],
  ],
  [700, 1750, 2150, 3160, 1360]
));
c.push(CAP("Table 1. The four analysis tasks. Each reference is the value from the fully specified recipe, computed independently. The T4 reference equals the value that the operational LTEM database tool reports for the same region and year."));
c.push(P("The same four tasks were run in Python and in R. In R the agents used the built-in iris data, read the same penguins and LTEM files, and used R functions (cor, glm with family binomial, aov, and dplyr for the aggregation). Three of the four references are the same value in both languages, because a correlation, an ANOVA effect size, and a sum then mean are the same number whatever the language. The classifier is the exception. Its fully specified R value is 0.8657 (a binomial glm with the same seed and split rule), which is close to but not the same as the Python value of 0.8806, because scikit-learn and R use different models and different random number generators. We recorded a Python reference and an R reference for that task and scored each language against its own reference."));
c.push(H2("3.4  Skill levels"));
c.push(P("The variable we changed was the content of an instruction block placed before the same task. Each level adds structure to the one before it, so the step between two levels shows what one skill feature contributes (Table 2). The full text of all 20 prompts (4 tasks by 5 levels) is in the Supporting Information (S5)."));
c.push(table(
  ["Level", "What it adds", "What it isolates"],
  [
    ["C0 none", "Bare task, no skill", "Default behaviour"],
    ["C1 basic", "Generic steps such as load the data, run the analysis, and report the result. Longer, but fixes nothing", "Length without constraint"],
    ["C2 contract", "Fixes the input (dataset, columns, missing-data rule, unit or scope) and the method (the exact test, model, or metric)", "Fixing what to compute"],
    ["C3 controls", "Fixes the random settings (seed, split ratio, scaling)", "Fixing the random settings"],
    ["C4 full", "Adds a validation check list and clear do-not rules", "Warnings about mistakes"],
  ],
  [1500, 5060, 2800]
));
c.push(CAP("Table 2. The five skill levels, each adding to the one before it. This is the variable we changed."));
c.push(H2("3.5  Outcome measures"));
c.push(P("For each cell we scored two things across the 10 runs. For run to run reproducibility we used the standard deviation (SD) and the coefficient of variation of the main output, the number of distinct answers within a set tolerance, and the exact-match rate, meaning the share of runs equal to the most common answer. For validity we used the share of runs whose output matched the independent reference within tolerance. We also recorded the most common method, test, or model, and for T1 the reported sign. Tolerances were 10⁻³ for correlation, accuracy, and η², and 10⁻² (biomass units) for T4."));
c.push(H2("3.6  Statistical analysis"));
c.push(P("The high-skill cells often had exactly zero variance (all 10 runs identical), so variance-equality tests are not meaningful here. We therefore tested the key contrasts as proportions. We compared run to run agreement and validity between the pooled low-skill and high-skill levels with Fisher's exact test, and checked the low-skill dispersion with a 5,000-sample bootstrap 95% confidence interval on the pooled SD. Analyses used scikit-learn 1.9.0, scipy 1.16.3, and numpy 2.4.6, and all code is provided in the Data availability section."));
c.push(H2("3.7  Openness"));
c.push(P("The experiment is self-contained and can be re-run. The three data files, all 40 prompts (20 for Python and 20 for R), the two orchestration scripts that launched the 400 runs, every run's structured output, and the analysis scripts that regenerate all tables and figures are archived (see Data availability and Supporting Information S5 to S8)."));
c.push(PB());

// ---------------- 4 RESULTS ----------------
c.push(H1("4  Study 1: results"));
c.push(P("All 200 runs finished (10 per cell). Table 3 gives reproducibility and validity by task and level."));
c.push(table(
  ["Task", "Level", "SD", "Distinct", "Exact-match", "Validity", "Diff. from ref."],
  [
    ["T1 iris corr", "C0 to C4", "0.000", "1", "100%", "100%", "0.000"],
    ["T2 penguin clf", "C0 none", "0.0061", "2", "50%", "50%", "0.006"],
    ["", "C1 basic", "0.0090", "3", "60%", "30%", "0.012"],
    ["", "C2 contract", "0.0086", "3", "50%", "40%", "0.005"],
    ["", "C3 controls", "0.000", "1", "100%", "100%", "0.000"],
    ["", "C4 full", "0.000", "1", "100%", "100%", "0.000"],
    ["T3 penguin ANOVA", "C0 to C4", "0.000", "1", "100%", "100%", "0.000"],
    ["T4 LTEM biomass", "C0 none", "0.000", "1", "100%", "0%", "0.169"],
    ["", "C1 basic", "0.000", "1", "100%", "0%", "0.169"],
    ["", "C2 contract", "0.000", "1", "100%", "100%", "0.000"],
    ["", "C3 controls", "0.000", "1", "100%", "100%", "0.000"],
    ["", "C4 full", "0.000", "1", "100%", "100%", "0.000"],
  ],
  [1900, 1500, 1000, 1260, 1400, 1200, 1100]
));
c.push(CAP("Table 3. Output reproducibility and validity by task and level (10 runs per cell). SD and the difference from the reference are in the units of each task."));

c.push(img(path.join(RES, "fig3_heatmaps.png"), 600, 210, "Reproducibility and validity heatmaps"));
c.push(CAP("Figure 1. Run to run agreement (left) and validity against the reference (right), as a percentage of the 10 runs per cell. Agreement falls below 100% only for the stochastic task T2, and returns to 100% at C3. Validity shows two different fixes. T2 is corrected at C3, while T4 is consistent but wrong (0%) until the contract at C2 (100%)."));

c.push(H2("4.1  Reproducibility was high by default, except where a task involved randomness"));
c.push(P("Three of the four tasks (T1, T3, T4) were 100% reproducible at every level, including no skill. Agents settled on one common approach (pooled Pearson correlation, one-way ANOVA with η², and summing biomass within a transect). The mistake of averaging biomass across rows, which is about 30 times too low, was never made, even at C0. The only task with leftover run to run variation was the stochastic classifier T2 (Figure 2)."));
c.push(img(path.join(RES, "fig2_reproducibility_gradient.png"), 600, 230, "Reproducibility gradient by condition"));
c.push(CAP("Figure 2. Run to run standard deviation (left) and coefficient of variation (right) by level, one line per task. Only T2 (orange) shows variation. It rises slightly at C1, where a basic skill is no better than none, and drops to zero at C3. T1, T3, and T4 sit on the zero line."));

c.push(H2("4.2  Fixing the random settings removed the variation (T2)"));
c.push(P("For T2, fixing the method (C2) was not enough. With the model fixed but the seed, split, and scaling still free, runs gave three distinct accuracies and only 50% agreement. Adding the random settings at C3 brought the variation to zero, and all 20 runs at C3 and C4 were identical and equal to the reference. Pooled run to run agreement rose from 16 of 30 at the low-skill levels (C0 to C2) to 20 of 20 at the high-skill levels (C3 and C4) (Fisher's exact P = 2.2×10⁻⁴). The pooled low-skill SD was 0.0086, with a bootstrap 95% confidence interval of [0.0063, 0.0109] that excludes zero, against exactly 0.0000 at high skill. Validity rose in step, from 12 of 30 to 20 of 20 (P = 8.4×10⁻⁶). The random seed and the related data handling are therefore the most useful skill parts for a task that involves randomness, and no lower level replaces them."));
c.push(H2("4.3  Reproducible is not the same as correct (T4)"));
c.push(P("The reef fish biomass task separated the two outcomes clearly. It was fully reproducible at every level, with all 10 runs identical in each cell, yet wrong under no skill or a basic skill. All 20 low-skill runs agreed on 3.2952, because they defined the survey unit as reef by habitat by transect, while the reference is 3.4642 (reef by transect). The fix came from the input and method contract at C2, which set the survey unit, and not from the seed (not relevant here) or the do-not rules. Validity rose from 0 of 20 before the contract (C0 and C1) to 30 of 30 with the contract and above (C2 to C4) (Fisher's exact P = 2.1×10⁻¹⁴), while reproducibility stayed at 100% throughout. A consistent pipeline can consistently give the wrong number, and only a clear contract points it at the intended quantity."));
c.push(H2("4.4  A long but vague skill did not help, and could hurt (T2)"));
c.push(P("Adding a long but vague skill (C1) did not improve T2 and, on balance, made it worse. Run to run SD rose from 0.006 (C0) to 0.009 (C1), and validity fell from 50% to 30%, because the instruction to train a classifier invited a free choice of model. Agents drifted to a random forest with varied splits, which moved results away from the reference. Length was not the active part; constraint was. A separate iris classifier task showed the same pattern more strongly, with a basic-skill SD of 0.044 against 0.000 for the fully specified skill."));
c.push(H2("4.5  Richer skills did not harm the fully specified results"));
c.push(P("The two richest levels (C3 and C4) reached 100% reproducibility and 100% validity on every task. The check list and the do-not rules added at C4 caused no measurable harm where they were not the deciding factor, and they act as low-cost insurance against the traps in each task (a within-species correlation, a row-level biomass mean, and a dropped seed)."));
c.push(H2("4.6  The same pattern holds in R, and the deterministic tasks agree across languages"));
c.push(P("The R runs repeated the Python pattern (Figure 3). In R, T1 and T3 were reproducible and correct at every level, T4 was reproducible but wrong until the contract at C2, and the classifier T2 varied at the low levels and then dropped to zero variation at C3. So the main results do not depend on the language."));
c.push(P("Comparing the two languages directly is the stronger test (Table 4). For the three deterministic tasks, Python and R gave the same value at every level, to the tolerance used. This held even where the value was wrong. On the biomass task, both languages agreed on 3.2952 at the low levels, so the two independent implementations reproduced the same wrong number, and both moved to 3.4642 once the contract set the survey unit. The classifier was the only task where Python and R did not match. Their fully specified values (0.8806 and 0.8657) differ by about 0.015, because scikit-learn and R use different models and different random number generators. Each language was still perfectly reproducible within itself once the seed was fixed, but they cannot be made bit-for-bit equal across languages, so a cross-language comparison of a random method has to use a tolerance rather than exact equality."));
c.push(table(
  ["Task", "Python (full skill)", "R (full skill)", "Same across languages?"],
  [
    ["T1 iris correlation", "−0.1176", "−0.1176", "Yes"],
    ["T2 penguin classifier", "0.8806", "0.8657", "No (differ by ~0.015)"],
    ["T3 penguin ANOVA (η²)", "0.6697", "0.6697", "Yes"],
    ["T4 LTEM biomass", "3.4642", "3.4642", "Yes"],
  ],
  [2600, 2200, 2100, 2460]
));
c.push(CAP("Table 4. Cross-language comparison at the full skill level (C4). The three deterministic tasks agree exactly. The classifier does not, because the two languages use different models and random number generators."));
c.push(img(path.join(RES, "fig4_python_vs_r.png"), 600, 400, "Python versus R output by skill level"));
c.push(CAP("Figure 3. Output by skill level in Python (blue) and R (red), 10 runs per cell per language. Dashed lines show the reference for each language. T1, T3, and T4 sit on one shared line in both languages, including the wrong value (3.2952) for T4 at C0 and C1. T2 sits on two different lines, because the Python and R classifiers do not give the same accuracy."));
c.push(PB());

// ---------------- 5 STUDY 2 ----------------
c.push(H1("5  Study 2: reproducibility of a whole report"));
c.push(P("Study 1 measured a single number. A real deliverable is usually a report with several analyses and written conclusions. Study 2 asks the same two questions for a whole report. Does the report use the statistics the skill specifies, which we call coherence, and do independent reports agree with each other, which is report reproducibility."));
c.push(H2("5.1  Design"));
c.push(P("Agents wrote a short data report on the Palmer Penguins dataset that answered several questions and ended with a conclusion. We used two versions. A standard report asked four common questions (a correlation, a group difference with an effect size, a sex-prediction accuracy, and per-species means). A hard report asked six questions that each have a real method fork, namely how many clusters to use, cross-validation or a single split for the accuracy, which predictors to put in a body-mass model, a t interval or a bootstrap for a confidence interval, a pooled or a within-species correlation, and whether to standardise before a principal component analysis. Each version had three conditions, which were no skill, a structure-only skill that fixes the sections but not the statistics, and a full skill that fixes the exact method, parameters, and missing-data rule for every question, with 8 reports per condition. A second judge agent then graded each report against one fixed rubric, the same rubric for every condition, and scored how many of the specified methods the report actually used. Reference values were computed independently. Full materials are in the Supporting Information and the repository."));
c.push(H2("5.2  Results"));
c.push(P("For the standard report, the reports were fully reproducible in every condition. Eight independent agents produced the same numbers and the same conclusions even with no skill, so reproducibility was already high and the skill did not need to fix it. What the skill fixed was coherence and validity. Coherence rose from 79% with no skill to 100% with the full skill, and validity from 75% to 100%. Without the full skill, every report used the machine-learning library's default 75/25 split for the classifier instead of the specified 80/20 split, so the reports were reproducible but wrong. The structure-only skill fixed the layout but not the statistics."));
c.push(P("The hard report, where each analysis has a real fork, tells the fuller story (Table 5, Figure 4). Now reproducibility broke as well. Without the skill, independent reports agreed on all of their numbers only half of the time (whole-report agreement 50%), coherence was 58%, and validity 56%. The full skill returned all three to 100%. Two kinds of failure appeared. Some analyses diverged from run to run, for example the species-accuracy question, where different reports used random forests, discriminant analysis, or logistic regression with different validation. Other analyses were reproducible but wrong, for example the clustering, where every no-skill report chose two clusters (the value that maximises the silhouette score) instead of the three species the skill specifies, and the body-mass model, where most reports added species and reached a higher R-squared. As in Study 1, the skill changed the outcome only where the default differed. Three of the six analyses did not diverge, because the agents' own default already matched the specified method."));
c.push(table(
  ["Metric", "No skill", "Structure skill", "Full skill"],
  [
    ["Skill coherence (uses the specified statistics)", "58%", "69%", "100%"],
    ["Report reproducibility (all numbers agree)", "50%", "50%", "100%"],
    ["Validity (numbers match the reference)", "56%", "61%", "100%"],
  ],
  [3560, 1900, 2000, 1900]
));
c.push(CAP("Table 5. Hard report with six forky analyses, 8 reports per condition. Only the full methods skill made the report coherent, reproducible, and valid at the same time."));
c.push(img(path.resolve(__dirname, "..", "report_reproducibility", "results", "fig_hard_report.png"), 640, 256, "Hard report results"));
c.push(CAP("Figure 4. Hard report results. Left: skill coherence, whole-report agreement, and validity by condition. Right: agreement across runs for each of the six analyses. The species-accuracy and body-mass questions diverge without the skill, while the other four do not, because their default already matched the specified method."));
c.push(PB());

// ---------------- 6 DISCUSSION ----------------
// ---------------- 6 STANDARD + REPOSITORY ----------------
c.push(H1("6  A standard for good skills and a repository for MCP and skills"));
c.push(P("Software packages changed analysis. Curated repositories such as CRAN for R and Bioconductor for bioinformatics gave the community versioned, documented, and tested reusable units, and the analyses built on them became easier to reproduce. Skills are becoming a reusable unit of the same kind for LLMs and their tools, now that tools are reached through a shared interface such as the Model Context Protocol (MCP). Today skills are shared informally, without versions, tests, or review, much as analysis code was before package repositories. The two experiments say what such a repository should require of a skill, both in what the skill contains and in what it is tested for."));
c.push(H2("6.1  What a good skill must contain"));
c.push(P("The two experiments give an ordered list of what a skill needs. The order depends on the task's main source of variation, which the author should identify first."));
c.push(NUM("Fix the random settings, meaning the random seed, the split ratio, and any scaling. This matters whenever the task involves randomness. Without it results vary by design, and with it they are identical (T2)."));
c.push(NUM("Fix the input and method contract, meaning the dataset, the columns, the missing-data rule, the unit of aggregation, and the exact test, model, or metric. This matters whenever a convention is unclear, and it turns a consistent but biased result into a correct one (T4)."));
c.push(NUM("Declare a reference value and a tolerance, so the skill can be checked for being correct, and not only for agreeing with itself."));
c.push(NUM("Add do-not rules and a validation check list. These are cheap guards that close known traps, such as a within-species correlation, a row-level biomass mean, or a dropped seed."));
c.push(P("Length, generic step lists, and encouragement without fixed choices did not help on their own. A skill improves the output in proportion to the number of free choices it removes, not the number of words it adds, so a good skill reads as a contract with fixed parameters, exact calls, named unit definitions, and clear do-not rules, not as a tutorial. Fixing only the report structure, without fixing the statistics, did not make the analysis reproducible or correct (Study 2), so a skill must fix the methods, not just the layout."));
c.push(H2("6.2  Checks a skill must pass before it is published"));
c.push(P("The measures we used to score the experiments can be run automatically, so a repository can screen a skill the way R CMD check screens an R package before it reaches CRAN. We propose three checks. A self-consistency check runs the skill several times on fixed data and confirms the outputs agree within the stated tolerance (Wang et al., 2023); a skill whose outputs do not converge is not ready. A reference check compares the output against a stored reference value within the tolerance the skill declares, so the skill is tested for being correct, not only for agreeing with itself, because reproducibility and validity are separate (Section 4.3). A coherence check has an independent grader read the finished output and confirm it used the methods the skill specifies, which a short judge rubric did reliably in Study 2. A skill passes when it is reproducible, valid, and coherent with its own stated methods."));
c.push(H2("6.3  A curated repository for MCP and skills"));
c.push(P("We are building such a repository for MCP servers and skills, modelled on CRAN and Bioconductor. Each skill is a versioned package with metadata (author, version, licence, and the reproducibility tolerances it guarantees), a declared list of the tools and data sources it depends on, worked examples, and the three checks above run when it is submitted and when it changes. Provenance is recorded, so a result stays traceable to the exact skill version, tool versions, and settings that produced it, which puts the FAIR (Wilkinson et al., 2016) and FAIR4RS (Barker et al., 2022) principles to work for AI skills. Curation and review, the same practices that let package repositories raise the reproducibility of ordinary analysis code, are what would turn a loose collection of prompts into a dependable, shared, and citable body of analysis skills for ecology."));

// ---------------- 7 DISCUSSION ----------------
c.push(H1("7  Discussion"));
c.push(H2("7.1  Skills work by removing choices, and the part that matters depends on the task"));
c.push(P("The experiments give direct evidence that AI skills can deliver output reproducibility for ecological analyses, with three qualifications. First, the benefit is not universal, because capable agents already settle on a correct default when a task has one obvious approach, so a skill has nothing to fix there. Second, where a skill does matter, the deciding part depends on the task. It is the random settings for a task with randomness (T2), and the input and method contract for a task where a convention is unclear (T4). Third, more words are not more reproducibility. The long but vague skill (C1) was the weakest of the skilled levels. A good skill finds the specific free choice that makes a task diverge and removes it."));
c.push(H2("7.2  How this fits earlier work"));
c.push(P("The experiment supports the points from the literature and fills the missing case. It shows the extra run to run variation that LLM help brings (T2). It supports the idea that structure helps, with a refinement, because only constraining structure helped. It supports measuring the output rather than the code (T4), where identical outputs were consistently wrong until a contract fixed the target quantity. No earlier study had tested AI skills against output reproducibility in ecology, and this experiment gives a first direct estimate."));
c.push(P("The two languages sharpen the point about what to measure. For a fixed deterministic method, Python and R gave the same answer, so this kind of result is reproducible across languages and does not depend on the tool. For a method with randomness, the two languages could not be made equal, even with a full skill, because their random number generators and models differ, so across languages the right target is agreement within a stated tolerance, not an identical number. The biomass task adds a caution. Both languages agreed on the same wrong value before the contract, so agreement across languages shows that a result is stable, but not that it is correct. Reproducibility and validity still need to be checked separately, even when independent implementations agree."));
c.push(H2("7.3  From single numbers to whole reports"));
c.push(P("Study 2 extends the finding from a single number to a whole report, and shows the effect grows with difficulty. For a standard report the reports were already reproducible without a skill, so the skill mainly improved coherence and validity. For a report whose analyses each had a real method fork, independent reports no longer agreed, and only the full skill made the report reproducible, coherent, and valid at the same time. The same two failure modes appeared as in Study 1, where some analyses diverged from run to run and others were reproducible but wrong. A short judge rubric, run over the finished report, was enough to measure whether the report used the specified statistics. This gives authors, reviewers, and editors a simple check for whether an AI-assisted report is coherent with its stated methods."));
c.push(H2("7.4  Limitations"));
c.push(P("The experiment used four tasks, three datasets, two languages (Python and R), one agent and model provider, and ten replicates per cell. Three tasks had a strong correct default, so the random-settings effect rests on T2 and the contract effect rests on T4, each carried by one task. A single provider means the run to run variation reflects one system, and variation across providers is likely larger. The tasks give single-number outputs, and multi-step pipelines with choices that build on each other may behave differently. The literature review was an informal background search by one reviewer, not a formal systematic review, so it is meant to set context rather than to give a complete count. Study 2 used one dataset, two report templates, one language, eight reports per condition, and a single judge to grade each report; a larger version should add more datasets and templates and a multi-judge grader."));
c.push(H2("7.5  A larger study and building the repository"));
c.push(P("The design extends directly. A larger study should add at least two tasks per type of divergence, at least 20 replicates per cell, a contract-without-seed level on more stochastic tasks, multi-step ecological workflows (for example a full species-distribution-model or a biomass time series), and at least two model providers to estimate variation across systems. It should also set the output-equivalence tolerances for each outcome in advance. All materials here can be reused for this."));

// ---------------- 6 CONCLUSIONS ----------------
c.push(H1("8  Conclusions"));
c.push(P("Software packages, shared through curated repositories, made analysis reusable and easier to reproduce, and AI skills are becoming a reusable unit of the same kind for large language models and their tools. In two controlled experiments we found that a skill improves an output by removing free choices, not by adding words, and that the deciding part depends on the task, namely the random settings where a task involves randomness and the input and method contract where a convention is unclear. Reproducibility and validity are separate, so a skill can make an analysis consistent without making it correct, and both must be checked; the same held for a whole report. From these results we set out what a good skill must contain, three checks it should pass (self-consistency, a reference, and coherence with its stated methods), and the design of a curated repository for Model Context Protocol servers and skills. Treating skills as versioned, tested, and reviewed packages, as CRAN and Bioconductor did for code, would give ecology a dependable and citable body of analysis skills, and the open experimental design here is a way to test each one before it is shared. Building and launching this repository, with automated validation on submission and a citable DOI for each skill version, is work we are now beginning."));

// ---------------- BACK MATTER ----------------
c.push(HR("E5E7EB", 4));
c.push(H2("Author contributions"));
c.push(P("[To be completed.]", { size: 20 }));
c.push(H2("Data availability and reproducibility"));
c.push(P("All code and materials are publicly available in a Git repository at https://github.com/Fabbiologia/ai-skills-reproducibility-ecology, and will be archived on Zenodo with a DOI on acceptance. This includes the two open data files (iris and Palmer Penguins), the 40 prompts (Python and R), the two orchestration scripts that launched the 400 runs, every run's structured output for both languages, and the analysis scripts that regenerate all tables and figures. The LTEM Cabo Pulmo 2023 reef fish data used for Task T4 is restricted and is available on request from the Aburto Lab; Tasks T1 to T3 are fully reproducible from the repository as it stands. The report-level study (Study 2) adds its own prompts, the generation and judge workflows, the report outputs with judge grades, and its analysis scripts, in the report_reproducibility folder of the repository. The list of studies read for the background, and the search terms, are given in S1 to S4.", { size: 21 }));
c.push(H2("Conflicts of interest"));
c.push(P("None declared.", { size: 20 }));
c.push(H2("Funding"));
c.push(P("[To be completed.]", { size: 20 }));

// ---------------- REFERENCES ----------------
c.push(H1("References"));
const refs = [
  "Baker, M. (2016). 1,500 scientists lift the lid on reproducibility. Nature, 533, 452–454.",
  "Barker, M., Chue Hong, N. P., Katz, D. S., et al. (2022). Introducing the FAIR Principles for research software. Scientific Data, 9, 622.",
  "Culina, A., van den Berg, I., Evans, S., & Sánchez-Tójar, A. (2020). Low availability of code in ecology: a call for urgent action. PLOS Biology, 18(7), e3000763.",
  "Gallois, E. C., Salili-James, A., Poon, S. T. S., Trebski, A., & Redding, D. W. (2025). Fast-tracking ecological interpretation using bespoke quantitative large language models. Methods in Ecology and Evolution, 16(12), 2730–2740.",
  "Goodman, S. N., Fanelli, D., & Ioannidis, J. P. A. (2016). What does research reproducibility mean? Science Translational Medicine, 8(341), 341ps12.",
  "Gundersen, O. E. (2021). The fundamental principles of reproducibility. Philosophical Transactions of the Royal Society A, 379, 20200210.",
  "Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. Nature, 585, 357–362.",
  "He, J., Rungta, M., Koleczek, D., Sekhon, A., Wang, F. X., & Hasan, S. (2024). Does prompt formatting have any impact on LLM performance? arXiv:2411.10541.",
  "Horst, A. M., Hill, A. P., & Gorman, K. B. (2020). palmerpenguins: Palmer Archipelago (Antarctica) penguin data. R package; data from Gorman, Williams & Fraser (2014), PLOS ONE 9(3), e90081.",
  "Kambouris, S., Wilkinson, D. P., Smith, E. T., & Fidler, F. (2024). Computationally reproducing results from meta-analyses in ecology and evolutionary biology using shared code and data. PLOS ONE, 19(3), e0300333.",
  "Kellner, K. F., et al. (2025). Functional R code is rare in species distribution and abundance papers. Ecology, e4475.",
  "O'Dea, R. E., Lagisz, M., Jennions, M. D., et al. (2021). Preferred reporting items for systematic reviews and meta-analyses in ecology and evolutionary biology: a PRISMA extension (PRISMA-EcoEvo). Biological Reviews, 96, 1695–1722.",
  "Pedregosa, F., Varoquaux, G., Gramfort, A., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
  "Pimentel, J. F., Murta, L., Braganholo, V., & Freire, J. (2019). A large-scale study about quality and reproducibility of Jupyter notebooks. MSR 2019.",
  "R Core Team (2026). R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria. Version 4.6.0.",
  "Trisovic, A., Lau, M. K., Pasquier, T., & Crosas, M. (2022). A large-scale study on research code quality and execution. Scientific Data, 9, 60.",
  "Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods, 17, 261–272.",
  "Wang, X., Wei, J., Schuurmans, D., et al. (2023). Self-consistency improves chain-of-thought reasoning in language models. ICLR 2023. arXiv:2203.11171.",
  "Wilkinson, M. D., Dumontier, M., Aalbersberg, Ij. J., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data, 3, 160018.",
  "Zurell, D., Franklin, J., König, C., et al. (2020). A standard protocol for reporting species distribution models (ODMAP). Ecography, 43(9), 1261–1277.",
  "How consistent are LLM agents? Measuring behavioral reproducibility in multi-step tool-calling pipelines (2026, preprint). arXiv:2605.28840.",
  "Large language models possess some ecological knowledge, but how much? (2026). Journal for Nature Conservation.",
  "Understanding and mitigating numerical sources of nondeterminism in LLM inference (2025, preprint). arXiv:2506.09501.",
];
refs.forEach(r => c.push(REFP(r)));

const doc = buildDoc(c, { title: "AI skills and output reproducibility in ecology (MEE manuscript)", footerLeft: "AI skills and output reproducibility of ecological analyses" });
write(doc, path.join(__dirname, "Manuscript_AI_Skills_Reproducibility_MEE.docx"));
