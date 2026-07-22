// Title page for the specification study (separate 'not for review' file). NOT
// anonymised: carries author names, affiliations, running headline, statements.
const T = require("./theme.js");
const { P, TITLE, H2, HR, buildDoc, write, setSpacing } = T;
setSpacing(220);
const path = require("path");

const c = [];
c.push(TITLE("Repeated AI analyses of ecological data agree on wrong answers until the method is written down"));
c.push(P("Article type: Research Article. Target journal: Methods in Ecology and Evolution.", { size: 20, spacing: { after: 40 } }));
c.push(P("Running headline: Written specifications and AI analysis (44 characters).", { size: 20 }));
c.push(HR());

c.push(H2("Authors and affiliations"));
c.push(P("Fabio Favoretto¹*, Alberto Rivera², Eduardo León Solorzano³", { spacing: { after: 40 } }));
c.push(P("¹ School of Biological and Marine Science, University of Plymouth, Plymouth, UK", { size: 22, spacing: { after: 20 } }));
c.push(P("² Scripps Institution of Oceanography, University of California San Diego, La Jolla, CA, USA", { size: 22, spacing: { after: 20 } }));
c.push(P("³ Centro para la Biodiversidad Marina y la Conservación, A.C., La Paz, BCS, Mexico", { size: 22, spacing: { after: 20 } }));
c.push(P("* Corresponding author: Fabio Favoretto, School of Biological and Marine Science, University of Plymouth, Plymouth, UK. Email: fabio.favoretto@plymouth.ac.uk", { size: 22 }));

c.push(H2("Acknowledgements"));
c.push(P("[To be completed.]"));

c.push(H2("Author contributions"));
c.push(P("[Author 1] and [Author 2] conceived the ideas and designed the study; [Author 1] built the task set and the reference implementations, ran the experiments and analysed the data; [Author 1] led the writing of the manuscript. All authors contributed critically to the drafts and gave final approval for publication. (Please edit to reflect the actual contributions, and use the CRediT taxonomy if preferred.)"));

c.push(H2("Statement on inclusion"));
c.push(P("Our study brings together authors from several countries, including a researcher based in the region where the reef-fish monitoring data were collected in Baja California Sur, Mexico. All authors were engaged early with the research and the study design, and work by scientists from the region was cited where relevant. (Please edit to reflect the actual collaboration.)"));

c.push(H2("Data availability statement"));
c.push(P("All materials are available at https://github.com/Fabbiologia/ai-skills-reproducibility-ecology and will be archived on Zenodo with a citable DOI on acceptance. For peer review the same materials are available anonymously at https://anonymous.4open.science/r/ai-skills-reproducibility-ecology-B13E/README.md. The archive contains the twelve tasks with their questions, written specifications and tolerances; the two independent implementations of every reference value and the agreement check between them; the prompts as they were sent; the 360 run records with the returned value and the executed script for each; the analysis script that produces every number reported in the paper, including the sensitivity of one comparison to how failed runs are counted; and the scripts that draw both figures and build the Supporting Information, which is generated from the archived records so that it cannot fall out of step with the analysis. It also contains the materials for the three further sets of runs described in section 2.5, namely the runs written in R, the runs across five models from three companies, and the whole-report runs, together with the records of the transfer runs on renamed and rearranged data."));
c.push(P("The iris and Palmer Penguins data and the Portal rodent survey records are openly available and are included in the archive. The reef-fish transect data from the Cabo Pulmo monitoring programme are available on request from the Aburto Lab. Records from the three further sets of runs were collected before the main study and do not carry the exact model identifiers and decoding settings for every run; this is documented in PROVENANCE.md and is one reason those runs are reported as description rather than as evidence."));

c.push(H2("Use of AI tools"));
c.push(P("Artificial-intelligence models are the object of study in this work. The twelve-task study used two models, requested by the identifiers gpt-4.1 and gemini-pro-latest, called through their companies' programming interfaces in July 2026 with the sampling temperature left at its default value of one. The three further sets of runs used five models from three companies. Every script returned by a model was executed unchanged in a fixed environment, and the numbers reported are the numbers those scripts printed. [Before submission, state which tools were used in preparing the manuscript itself and the code around the experiment, and describe the human verification applied. Do not infer model metadata that the historical records do not contain.]"));

c.push(H2("Conflict of interest and funding"));
c.push(P("Conflict of interest: The authors declare no conflict of interest. Funding: [To be completed.]"));

const doc = buildDoc(c, { title: "Title page - MEE submission", footerLeft: "Title page (not for review)", lineNumbers: false });
write(doc, path.join(__dirname, "Title_Page_Specifications.docx"));
