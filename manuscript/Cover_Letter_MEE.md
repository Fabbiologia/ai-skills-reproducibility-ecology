# Cover letter for *Methods in Ecology and Evolution*

**Fabio Favoretto**
School of Biological and Marine Science, University of Plymouth, Plymouth, UK
fabio.favoretto@plymouth.ac.uk

---

2 July 2026

The Editors
*Methods in Ecology and Evolution*
British Ecological Society

**Re: Submission of an original Research Article, "Do AI skills improve the output reproducibility of ecological analyses? A controlled experiment."**

Dear Editors,

We are pleased to submit our manuscript for consideration as a Research Article in *Methods in Ecology and Evolution*. Large language models and agent tools are now widely used for ecological data analysis, and people are starting to package expert procedure into reusable, structured instructions, which we call skills, to make this help reliable. Whether skills actually improve reproducibility, and which of their parts matter, has not been tested, as far as we know. Our paper tests this directly.

The paper reports a controlled experiment. We crossed four analysis tasks with five levels of skill detail and repeated each combination ten times, for 200 runs. The tasks use the iris and Palmer Penguins datasets and real reef fish monitoring data from Cabo Pulmo National Park, Gulf of California. The five levels add one kind of instruction at a time, so we can see which part of a skill does the work. A short review of the literature sets the context, but the paper is a primary study, not a formal systematic review.

The main findings are about method, and we think they will interest a broad readership. First, skills improve reproducibility by removing choices, not by adding words, and a long but vague skill did not help and sometimes made things worse. Second, the part that matters depends on the task. Fixing the random settings (seed, split, scaling) matters where a task involves randomness, and fixing the input and method (for example how a survey unit is defined) matters where a convention is unclear. Third, reproducibility and validity are separate. On the real marine data, plain runs were perfectly consistent but gave the wrong value until a contract fixed the target quantity. We turn these results into a short, ordered set of rules for writing reproducible skills for ecology.

We believe the work fits *Methods in Ecology and Evolution* well. It is about method rather than one system, it supports open and reproducible practice in the age of AI-assisted analysis, it uses standard ecological datasets together with real monitoring data, and it comes with a reusable, fully open experimental design and complete materials (data, prompts, orchestration, analysis code, and document scripts) that others can build on. The study also uses an output-based definition of reproducibility that fits well with existing reporting standards such as ODMAP and PRISMA-EcoEvo.

We confirm that this manuscript is original, has not been published before, and is not under consideration elsewhere, that all authors have approved the submission, and that we have no competing interests. All data and code are provided as Supporting Information and will be archived on OSF and Zenodo with a citable DOI on acceptance. The literature review in this draft is an informal background search, and a larger pre-registered search could be added later if the editors prefer.

We would be glad to suggest reviewers with expertise in computational reproducibility, species distribution modelling, and AI for ecology. Thank you for considering our submission. We look forward to your response.

Yours sincerely,

Fabio Favoretto, on behalf of all authors
School of Biological and Marine Science, University of Plymouth, Plymouth, UK
fabio.favoretto@plymouth.ac.uk
