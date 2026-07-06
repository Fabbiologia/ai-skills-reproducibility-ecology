const T = require("./theme.js");
const { P, TITLE, H1, H2, H3, CAP, BULLET, NUM, REFP, HR, GAP, PB, img, table, buildDoc, write, rt } = T;
const path = require("path");
const RES = path.resolve(__dirname, "..", "results");

const c = [];

// ---------------- TITLE / AUTHORS ----------------
c.push(TITLE("Do AI skills improve the output reproducibility of ecological analyses? A controlled experiment"));
c.push(P("Fabio Favoretto¹*, Alberto Rivera², Eduardo León Solorzano³", { spacing: { after: 40 } }));
c.push(P("¹ School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { size: 20, spacing: { after: 20 } }));
c.push(P("² Scripps Institution of Oceanography, University of California San Diego, La Jolla, CA, USA", { size: 20, spacing: { after: 20 } }));
c.push(P("³ Centro para la Biodiversidad Marina y la Conservación, A.C., La Paz, BCS, Mexico", { size: 20, spacing: { after: 20 } }));
c.push(P("* Corresponding author: fabio.favoretto@plymouth.ac.uk", { size: 20, spacing: { after: 40 } }));
c.push(P("Article type: Research Article. Target journal: Methods in Ecology and Evolution.", { size: 20 }));
c.push(HR());

// ---------------- ABSTRACT ----------------
c.push(H1("Abstract"));
c.push(P("1. Ecology and evolutionary biology have a reproducibility problem. It comes less from weak science than from analysis code that is missing, does not run, or is poorly documented. Large language models (LLMs) and agent tools are now used for ecological analysis. One way proposed to make this help reliable is to give the tools reusable, structured instructions, which we call skills. We do not yet know whether skills improve reproducibility, or which of their parts matter."));
c.push(P("2. We ran a controlled experiment to test this, and we summarised the current literature to set the context. The experiment crossed four analysis tasks with five levels of skill detail, in two languages (Python and R), and repeated each combination ten times, for 400 runs in total. Each level adds one kind of instruction to the one before it, so we can see which part of a skill does the work, and the two languages let us check whether different code reaches the same answer."));
c.push(P("3. Reproducibility was already high when a task had one obvious way to do it. Where a task involved randomness, run to run variation disappeared only when the skill fixed the random seed and the data handling (agreement rose from 16 of 30 runs to 20 of 20; Fisher P = 2×10⁻⁴). On real reef fish data, plain runs were perfectly consistent but gave the wrong value, and the answer became correct only when the skill fixed how the survey unit was defined (from 0 of 20 correct to 30 of 30; P = 2×10⁻¹⁴). A long but vague skill did not help, and sometimes made things worse."));
c.push(P("4. Skills improve reproducibility by removing choices, not by adding words, and the part that matters depends on the task. Fix the random settings when a task involves randomness, and fix the data and method definitions when a convention is unclear. Python and R gave the same answer for the three deterministic tasks, but not for the classifier, because the two languages use different random number generators, so a tolerance is needed when comparing across languages. We give a short, ordered set of rules for writing reproducible skills for ecology, together with an open experimental design that others can reuse."));
c.push(P("Keywords: reproducibility; large language models; agent skills; open science; FAIR; prompt engineering; workflow; conservation; marine ecology.", { spacing: { before: 120 } }));
c.push(PB());

// ---------------- 1 INTRODUCTION ----------------
c.push(H1("1  Introduction"));
c.push(P("Reproducibility is the basis of cumulative science, yet across fields a large share of published computational results cannot be regenerated. In a survey of 1,576 researchers, more than 70% had failed to reproduce another group's results and more than half had failed to reproduce their own (Baker, 2016). In ecology and evolutionary biology the problem sits in the analysis. Data are shared more and more often, but the analysis code is frequently missing, broken, or undocumented (Culina et al., 2020; Kellner et al., 2025). Even when the code is available, results reproduce only some of the time (Kambouris et al., 2024)."));
c.push(P("At the same time, LLMs and agent tools are being used for ecological work, from pulling data out of text to reading quantitative datasets (Gallois et al., 2025). These tools bring a new problem. They are stochastic, so the same request can give different outputs on repeated runs, and their behaviour changes with the wording and layout of the prompt (He et al., 2024). One proposed fix is to package expert procedure into reusable, structured skills, that is, clear instructions, contracts, check lists, examples, and tool directions that guide a model toward a repeatable result. Whether skills actually make results reproducible, and which of their parts matter, is still an open question."));
c.push(P("One distinction frames this study. Following Goodman et al. (2016), we separate methods reproducibility (re-running the same code gives the same result), results reproducibility (an independent analysis gives the same result), and inferential reproducibility (the same conclusion is drawn). Most ecological work measures code reproducibility, but for someone using the result the useful target is output reproducibility, meaning whether the analysis gives the same answer even if the code differs. We use this output-based definition throughout, in line with Gundersen (2021). We treat two analyses as output-reproducible when they agree within a set tolerance, for example the same effect direction and significance, or the same number within a stated margin, whatever the code."));
c.push(P("We first summarise what earlier work shows (Section 2). We then report the experiment (Sections 3 and 4) and turn the results into practical guidance (Section 5). The experiment is the main contribution, and the literature review sets the context and is not a formal systematic review."));

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
c.push(H1("3  Materials and methods"));
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
c.push(P("The high-skill cells often had exactly zero variance (all 10 runs identical), so variance-equality tests are not meaningful here. We therefore tested the key contrasts as proportions. We compared run to run agreement and validity between the pooled low-skill and high-skill levels with Fisher's exact test, and checked the low-skill dispersion with a 5,000-sample bootstrap 95% confidence interval on the pooled SD. Analyses used scikit-learn 1.9.0, scipy 1.16.3, and numpy 2.4.6, and all code is provided (Section 6)."));
c.push(H2("3.7  Openness"));
c.push(P("The experiment is self-contained and can be re-run. The three data files, all 40 prompts (20 for Python and 20 for R), the two orchestration scripts that launched the 400 runs, every run's structured output, and the analysis scripts that regenerate all tables and figures are archived (Section 6; Supporting Information S5 to S8)."));
c.push(PB());

// ---------------- 4 RESULTS ----------------
c.push(H1("4  Results"));
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

// ---------------- 5 DISCUSSION ----------------
c.push(H1("5  Discussion"));
c.push(H2("5.1  Skills work by removing choices, and the part that matters depends on the task"));
c.push(P("The experiment gives direct evidence that AI skills can deliver output reproducibility for ecological analyses, with three qualifications. First, the benefit is not universal, because capable agents already settle on a correct default when a task has one obvious approach, so a skill has nothing to fix there. Second, where a skill does matter, the deciding part depends on the task. It is the random settings for a task with randomness (T2), and the input and method contract for a task where a convention is unclear (T4). Third, more words are not more reproducibility. The long but vague skill (C1) was the weakest of the skilled levels. A good skill finds the specific free choice that makes a task diverge and removes it."));
c.push(H2("5.2  What a skill should contain to improve output reproducibility"));
c.push(P("Bringing the experiment together with the literature, we rank skill parts by what they contributed here. The order depends on the task's main source of variation, which the author should identify first."));
c.push(NUM("Fix the random settings, meaning the random seed, the split ratio, and any scaling. This matters whenever the task involves randomness. Without it results vary by design, and with it they are identical (T2)."));
c.push(NUM("Fix the input and method contract, meaning the dataset, the columns, the missing-data rule, the unit of aggregation, and the exact test, model, or metric. This matters whenever a convention is unclear, and it turns a consistent but biased result into a correct one (T4)."));
c.push(NUM("State a reference value and a tolerance, so reproducible can be checked against correct, and not only against other runs."));
c.push(NUM("Add do-not rules and a validation check list. These are cheap guards that close known traps, such as a within-species correlation, a row-level biomass mean, or a dropped seed."));
c.push(P("Parts that did not help on their own were length, generic step lists, and encouragement without fixed choices. As a rule, a skill improves reproducibility in proportion to the number of free choices it removes, not the number of words it adds. Write skills as contracts, with fixed parameters, exact calls, named unit definitions, and clear do-not rules, rather than as tutorials."));
c.push(H2("5.3  Implications for practice"));
c.push(P("For AI-assisted ecological analysis we suggest a few practices. State and report the output-equivalence tolerances up front. Version and archive the skill with the analysis, and record the decoding parameters and the seeds. Give agents structured tool contracts rather than open access. Use self-consistency, meaning several runs combined, as a default where a single fixed answer is not possible (Wang et al., 2023). Register skills and datasets with a record of their origin, so a reproducible result stays reproducible. These practices put the FAIR (Wilkinson et al., 2016) and FAIR4RS (Barker et al., 2022) principles to work for AI skills. Because reproducibility and validity are separate (Section 4.3), a skill and an analysis should be judged on both, not on run to run consistency alone."));
c.push(H2("5.4  How this fits earlier work"));
c.push(P("The experiment supports the points from the literature and fills the missing case. It shows the extra run to run variation that LLM help brings (T2). It supports the idea that structure helps, with a refinement, because only constraining structure helped. It supports measuring the output rather than the code (T4), where identical outputs were consistently wrong until a contract fixed the target quantity. No earlier study had tested AI skills against output reproducibility in ecology, and this experiment gives a first direct estimate."));
c.push(P("The two languages sharpen the point about what to measure. For a fixed deterministic method, Python and R gave the same answer, so this kind of result is reproducible across languages and does not depend on the tool. For a method with randomness, the two languages could not be made equal, even with a full skill, because their random number generators and models differ, so across languages the right target is agreement within a stated tolerance, not an identical number. The biomass task adds a caution. Both languages agreed on the same wrong value before the contract, so agreement across languages shows that a result is stable, but not that it is correct. Reproducibility and validity still need to be checked separately, even when independent implementations agree."));
c.push(H2("5.5  Limitations"));
c.push(P("The experiment used four tasks, three datasets, two languages (Python and R), one agent and model provider, and ten replicates per cell. Three tasks had a strong correct default, so the random-settings effect rests on T2 and the contract effect rests on T4, each carried by one task. A single provider means the run to run variation reflects one system, and variation across providers is likely larger. The tasks give single-number outputs, and multi-step pipelines with choices that build on each other may behave differently. The literature review was an informal background search by one reviewer, not a formal systematic review, so it is meant to set context rather than to give a complete count."));
c.push(H2("5.6  A larger study"));
c.push(P("The design extends directly. A larger study should add at least two tasks per type of divergence, at least 20 replicates per cell, a contract-without-seed level on more stochastic tasks, multi-step ecological workflows (for example a full species-distribution-model or a biomass time series), and at least two model providers to estimate variation across systems. It should also set the output-equivalence tolerances for each outcome in advance. All materials here can be reused for this."));

// ---------------- 6 CONCLUSIONS ----------------
c.push(H1("6  Conclusions"));
c.push(P("Output reproducibility in ecological analysis is low and code-limited, AI help adds a new source of run to run variation, and structured guidance is the most likely way to counter it. Before this study, no work had directly measured whether AI skills give that benefit for ecological analyses. In a controlled experiment we show that they can, but by removing choices rather than by adding words, and that the deciding skill part depends on the task. Fix the random settings when a task involves randomness, and fix the input and method contract when a convention is unclear. Because reproducibility and validity are separate, a skill can make an analysis consistent without making it correct, so both should be measured. The practical output is a short, ordered set of rules for writing reproducible AI skills for ecology, and an open experimental design for testing them."));

// ---------------- BACK MATTER ----------------
c.push(HR("E5E7EB", 4));
c.push(H2("Author contributions"));
c.push(P("[To be completed.]", { size: 20 }));
c.push(H2("Data availability and reproducibility"));
c.push(P("All code and materials are publicly available in a Git repository at https://github.com/Fabbiologia/ai-skills-reproducibility-ecology, and will be archived on Zenodo with a DOI on acceptance. This includes the two open data files (iris and Palmer Penguins), the 40 prompts (Python and R), the two orchestration scripts that launched the 400 runs, every run's structured output for both languages, and the analysis scripts that regenerate all tables and figures. The LTEM Cabo Pulmo 2023 reef fish data used for Task T4 is restricted and is available on request from the Aburto Lab; Tasks T1 to T3 are fully reproducible from the repository as it stands. The list of studies read for the background, and the search terms, are given in S1 to S4.", { size: 21 }));
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
