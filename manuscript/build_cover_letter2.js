const T = require("./theme.js");
const { P, HR, GAP, buildDoc, write, setSpacing } = T;
setSpacing(240);
const path = require("path");

const c = [];
const small = (s, opts = {}) => P(s, { size: 20, ...opts });
const body = (s, opts = {}) => P(s, { size: 22, spacing: { after: 80, ...((opts || {}).spacing || {}) }, ...opts });

c.push(P("**Fabio Favoretto**", { size: 24, spacing: { after: 20 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { spacing: { after: 20 } }));
c.push(small("fabio.favoretto@plymouth.ac.uk", { spacing: { after: 40 } }));
c.push(HR());
c.push(small("22 July 2026", { spacing: { after: 160 } }));

c.push(small("The Editors", { spacing: { after: 0 } }));
c.push(small("*Methods in Ecology and Evolution*", { spacing: { after: 0 } }));
c.push(small("British Ecological Society", { spacing: { after: 160 } }));

c.push(body("**Re: Submission of an original Research Article, “Repeated AI analyses of ecological data agree on wrong answers until the method is written down.”**", { spacing: { after: 120 } }));

c.push(body("Dear Editors,"));

c.push(body("We submit a new study on how reliably an artificial-intelligence tool answers an ecological data question, and on what makes the answer correct. We should say at the outset that this work follows an earlier submission of ours, MEE-26-07-694, which you declined. That decision set out two specific problems, and rather than argue with them we designed and ran a new study to address both. We describe below what changed, so that you can judge quickly whether the design now carries its conclusions."));

c.push(body("The first problem you identified was that the inferential design did not support the claims, because each mechanism rested on a single task and the tests pooled repeated runs of one prompt on one model as though they were independent replicates. That criticism was correct. The present study uses twelve tasks across four ecological datasets, with three tasks for each of four kinds of analytical choice, so no claim rests on a single task and no kind of choice is confined to a single dataset. The unit of replication is now the task, so that each task contributes one figure per condition, namely the proportion of its runs that reached the reference, and conditions are compared across the twelve tasks with paired tests. Repeated runs of one task are treated as repeated measures of that task and never as independent observations."));

c.push(body("The second problem you identified was more fundamental. You observed that reproducibility and validity were reached only where the instruction specified the method, columns, seed and split in full, that such an instruction is close to the analysis code written out in prose, and that the reproducibility literature already recommends sharing versioned code in a fixed environment. We took this as a hypothesis to be tested rather than a matter of opinion, and built it into the design as a third condition. Alongside the question by itself and the question with a written specification, every task was also run with a working script that answers a question of the same kind on a different dataset, which the model was told it could adapt. That condition is the recommendation to share code, given a fair trial."));

c.push(body("The result is that the written specification outperformed the working script. Across the twelve tasks the specification reached the reference in 96 per cent of runs against 75 per cent for the script, a difference of 21 percentage points that holds in a paired test across the twelve tasks. The script was 16 points ahead of giving no instruction at all, but that difference was not supported by the paired test. The reason is visible in the runs: a script carries the column names and table shape of the dataset it was written against, and those particulars have to be undone before the method underneath can be reused, whereas a specification carries the method without them. We report this as evidence that the two are complements rather than substitutes, and we also report the limits we found, namely that a specification survives a change in what the columns are called but not a rearrangement of the table, and that it fixes the quantity but not the estimator."));

c.push(body("The finding we think most useful to readers of this journal is what happened to reproducibility. Measured across all twelve tasks, the script made runs agree with one another exactly as often as the specification did, on eleven tasks of twelve, while reaching the correct value far less often. On one task every one of the ten runs given a working script returned the same number and none of them was right, because the script counted only the plot-years present in the file and dropped the surveys that caught nothing. The number those ten runs agreed on is the part we would most like to draw to your attention. It is not noise but the reference value of a neighbouring task in the same study, the one that asks the same question without the instruction about empty plot-years, matched to seven decimal places. The runs given code computed a quantity correctly and in complete agreement with one another, and answered a question nobody had asked. That is reproducibility without validity, produced by the practice most often recommended for obtaining reproducibility, and we think it is worth putting in front of ecologists who are beginning to use these tools. The wrong values were plausible rather than absurd, differing from the reference by a few per cent, and repeating the analysis, rewriting it in a second language or moving to a model from another company would each have confirmed the error."));

c.push(body("We should draw your attention to one analytical choice, because it affects a reported comparison and we would rather state it than have it found. Runs can fail to return a number either because the model produced code that does not run, which is a property of the condition, or because the call failed at the provider on a network error, which is not. The primary analysis excludes the second and counts the first as a wrong answer. The advantage of the specification over the script holds under that convention and also when every run is counted, but among only those runs that returned a number the two are not distinguishable, because much of the script's disadvantage is that it produced code that did not run. All three conventions are given in the results and tabulated in the Supporting Information, and the discussion says plainly which part of the claim rests on which."));

c.push(body("The manuscript also carries three smaller sets of runs, on four tasks, which repeat one of these questions with the analysis written in R rather than Python, on five models from three companies, and with the request changed from a single number to a short written report. These are reported as description, without any statistical test, and we say so in the methods and again in the limitations. They are there because they answer the question a reader will ask about the main result, which is whether the same wrong number appears in another language and on other models, and because the report runs show something the single-number tasks cannot, namely that the conclusions a report states were identical across conditions while the numbers behind them were not. Every conclusion of the paper rests on the twelve tasks and would stand without these runs."));

c.push(body("On the standing of the reference values, which any study of this kind depends on, each quantity is stated in words and then computed by two implementations written independently of one another. A reference was accepted only where the two agreed. We also state plainly where an instruction was unnecessary: seven of the twelve tasks were answered correctly without one, and we report that as a result rather than setting it aside."));

c.push(body("We enclose the manuscript, a title page, and a Supporting Information document that gives the twelve tasks and their specifications in full, the complete per-task results referred to from the results section, the wrong values with the reading of the question that produces each, and the sensitivity table described above. The Supporting Information is generated from the archived run records when it is built, so it cannot fall out of step with the analysis. All tasks, reference values, prompts, run records, analysis scripts and figures are in an anonymised repository linked in the manuscript. We confirm that this manuscript is original, is not under consideration elsewhere, that all authors have approved the submission, and that we have no competing interests."));

c.push(body("We are grateful for the earlier assessment, which was specific enough to be acted on, and we hope the design now meets the standard you set out."));

c.push(GAP(120));
c.push(body("Yours sincerely,", { spacing: { after: 120 } }));
c.push(body("Fabio Favoretto, on behalf of all authors", { spacing: { after: 0 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK"));

const doc = buildDoc(c, { title: "Cover letter", footerLeft: "Cover letter", lineNumbers: false });
write(doc, path.join(__dirname, "Cover_Letter_Specifications.docx"));
