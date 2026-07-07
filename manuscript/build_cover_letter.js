const T = require("./theme.js");
const { P, HR, GAP, buildDoc, write, rt, setSpacing } = T;
setSpacing(240); // cover letter is single-spaced
const path = require("path");
const docx = require("docx");
const { Paragraph, TextRun } = docx;

const c = [];
const small = (s, opts = {}) => P(s, { size: 20, ...opts });

// letterhead
c.push(P("**Fabio Favoretto**", { size: 24, spacing: { after: 20 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { spacing: { after: 20 } }));
c.push(small("fabio.favoretto@plymouth.ac.uk", { spacing: { after: 40 } }));
c.push(HR());
c.push(small("2 July 2026", { spacing: { after: 160 } }));

c.push(small("The Editors", { spacing: { after: 0 } }));
c.push(small("*Methods in Ecology and Evolution*", { spacing: { after: 0 } }));
c.push(small("British Ecological Society", { spacing: { after: 160 } }));

c.push(P("**Re: Submission of an original Research Article, “Skills as the new packages: an evidence-based standard for good AI analysis skills and a curated repository for ecology.”**", { spacing: { after: 160 } }));

c.push(P("Dear Editors,"));

c.push(P("We are pleased to submit our manuscript for consideration as a Research Article in *Methods in Ecology and Evolution*. Software packages, shared through curated repositories such as CRAN, made data analysis reusable and easier to reproduce. Large language models and agent tools are now used for ecological analysis, and the structured instructions that drive them, which we call skills, are becoming a reusable unit of the same kind, but they are shared informally, without versions, tests, or review. We argue that skills should be treated like packages and distributed through a curated repository, and we use controlled experiments to work out what such a repository should require of a skill."));

c.push(P("The paper reports two controlled experiments and turns their results into a proposal. The first crossed four analysis tasks with five levels of skill detail, in Python and R, for 400 runs. The second raised the output from a single number to a whole data report and used an independent judge to check whether each report used the statistics the skill specifies. The tasks use the iris and Palmer Penguins datasets and real reef fish monitoring data from Cabo Pulmo National Park, Gulf of California. From the results we set out a short standard for a good skill, three automated checks it should pass before publication, and the design of a curated repository for Model Context Protocol servers and skills. A short review of the literature sets the context, but the paper is a primary study, not a formal systematic review."));

c.push(P("The main findings are about method, and we think they will interest a broad readership. First, skills improve reproducibility by removing choices, not by adding words, and a long but vague skill did not help and sometimes made things worse. Second, the part that matters depends on the task. Fixing the random settings (seed, split, scaling) matters where a task involves randomness, and fixing the input and method (for example how a survey unit is defined) matters where a convention is unclear. Third, reproducibility and validity are separate. On the real marine data, plain runs were perfectly consistent but gave the wrong value until a contract fixed the target quantity. We turn these results into a short, ordered set of rules for writing reproducible skills for ecology."));

c.push(P("We believe the work fits *Methods in Ecology and Evolution* well. It is about method rather than one system, and it proposes concrete infrastructure for reproducible AI-assisted analysis, a standard and a curated repository for skills, in the spirit of CRAN and of reporting standards such as ODMAP and PRISMA-EcoEvo. It uses standard ecological datasets together with real monitoring data, and it comes with a reusable, fully open experimental design and complete materials (data, prompts, orchestration, analysis code, and document scripts) that others can build on."));

c.push(P("We confirm that this manuscript is original, has not been published before, and is not under consideration elsewhere, that all authors have approved the submission, and that we have no competing interests. All data and code are provided as Supporting Information and will be archived on OSF and Zenodo with a citable DOI on acceptance. The literature review in this draft is an informal background search, and a larger pre-registered search could be added later if the editors prefer."));

c.push(P("We would be glad to suggest reviewers with expertise in computational reproducibility, species distribution modelling, and AI for ecology. Thank you for considering our submission. We look forward to your response."));

c.push(GAP(120));
c.push(P("Yours sincerely,", { spacing: { after: 200 } }));
c.push(P("Fabio Favoretto, on behalf of all authors", { spacing: { after: 0 } }));
c.push(small("School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { spacing: { after: 0 } }));
c.push(small("fabio.favoretto@plymouth.ac.uk"));

const doc = buildDoc(c, { title: "Cover letter for MEE submission", footerLeft: "Cover letter", lineNumbers: false });
write(doc, path.join(__dirname, "Cover_Letter_MEE.docx"));
