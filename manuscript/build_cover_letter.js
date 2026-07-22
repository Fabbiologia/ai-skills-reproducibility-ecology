const T = require("./theme.js");
const { P, HR, GAP, buildDoc, write, rt, setSpacing } = T;
setSpacing(240); // cover letter is single-spaced
const path = require("path");
const docx = require("docx");
const { Paragraph, TextRun } = docx;

const c = [];
const small = (s, opts = {}) => P(s, { size: 20, ...opts });
const body = (s, opts = {}) => P(s, { size: 22, spacing: { after: 80, ...((opts || {}).spacing || {}) }, ...opts });

// letterhead
c.push(P("**Fabio Favoretto**", { size: 24, spacing: { after: 20 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { spacing: { after: 20 } }));
c.push(small("fabio.favoretto@plymouth.ac.uk", { spacing: { after: 40 } }));
c.push(HR());
c.push(small("15 July 2026", { spacing: { after: 160 } }));

c.push(small("The Editors", { spacing: { after: 0 } }));
c.push(small("*Methods in Ecology and Evolution*", { spacing: { after: 0 } }));
c.push(small("British Ecological Society", { spacing: { after: 160 } }));

c.push(body("**Re: Submission of an original Research Article, “Reusable instructions make AI ecological analyses reproducible when they remove analytical choices.”**", { spacing: { after: 120 } }));

c.push(body("Dear Editors,"));

c.push(body("We submit a controlled study of when a reusable set of instructions for an AI analysis tool, which we call a skill, makes an ecological analysis give the same answer from one run to the next, and whether a stable answer is also a correct one. Rather than asking whether longer instructions help, we take a skill apart one part at a time and measure the effect of each part, and we keep apart two things that are easily confused: whether repeated runs agree with one another, and whether they agree with an independently produced correct value."));

c.push(body("We ran four ecological analyses many times over, under instructions ranging from none to a complete recipe, in both Python and R, and then again as whole written reports graded for method by a separate tool. The clearest results are conditional. Where a task involved randomness, the answer became stable only once the instruction fixed it. Where a common analytical choice was left open, the repeated runs agreed with one another and were still all wrong, until the instruction fixed the choice. Adding words without fixing a choice did not help. We then repeated the main comparisons on five models from three different companies, and the pattern held: without a skill the models disagreed and were often wrong, and with the full skill they reached the correct answer at little added cost."));

c.push(body("The contribution is both a finding and a piece of infrastructure. We separate what the experiments support from what a shared, reviewed collection of skills should further require, and we provide a machine-readable manifest, a checker, a worked example, and an archive audit. A candidate skill faces three separate checks: that repeated runs agree, that they match a known answer, and that the analysis follows the method it claims to use."));

c.push(body("The study suits Methods in Ecology and Evolution because it turns a fast-spreading practice into something that can be stated, tested, and checked. We are also clear about its limits. The statistical tests are descriptive rather than confirmatory, each main finding rests on a small number of tasks, and the report grading is only partly auditable. The paper sets out what a confirmatory study across more tasks and providers would need to test, which we see as the natural next step."));

c.push(body("We confirm that this manuscript is original, has not been published before, and is not under consideration elsewhere, that all authors have approved the submission, and that we have no competing interests. The code, open data, structured outputs, and documents will be archived with a DOI, and the restricted reef-fish data are available on request."));

c.push(body("Thank you for considering our submission."));

c.push(GAP(120));
c.push(body("Yours sincerely,", { spacing: { after: 120 } }));
c.push(body("Fabio Favoretto, on behalf of all authors", { spacing: { after: 0 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { spacing: { after: 0 } }));
c.push(small("fabio.favoretto@plymouth.ac.uk"));

const doc = buildDoc(c, { title: "Cover letter for MEE submission", footerLeft: "Cover letter", lineNumbers: false });
write(doc, path.join(__dirname, "Cover_Letter_MEE.docx"));
