// MEE title page (separate 'not for review' file). NOT anonymised: carries author
// names, affiliations, running headline, and all statements. Single-spaced.
const T = require("./theme.js");
const { P, TITLE, H2, HR, buildDoc, write, setSpacing } = T;
setSpacing(240);
const path = require("path");

const c = [];
c.push(TITLE("Skills as the new packages: an evidence-based standard for good AI analysis skills and a curated repository for ecology"));
c.push(P("Article type: Research Article. Target journal: Methods in Ecology and Evolution.", { size: 20, spacing: { after: 40 } }));
c.push(P("Running headline: AI analysis skills and reproducible ecology (43 characters).", { size: 20 }));
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
c.push(P("[Author 1] and [Author 2] conceived the ideas and designed the study; [Author 1] ran the experiments and analysed the data; [Author 1] led the writing of the manuscript. All authors contributed critically to the drafts and gave final approval for publication. (Please edit to reflect the actual contributions, and use the CRediT taxonomy if preferred.)"));

c.push(H2("Statement on inclusion"));
c.push(P("Our study brings together authors from several countries, including a researcher based in the region where the reef fish monitoring data were collected (Baja California Sur, Mexico). All authors were engaged early with the research and study design. Whenever relevant, work by scientists from the region was cited. (Please edit to reflect the actual collaboration.)"));

c.push(H2("Data availability statement"));
c.push(P("All code and materials are available in a Git repository at https://github.com/Fabbiologia/ai-skills-reproducibility-ecology, and will be archived on Zenodo with a citable DOI on acceptance. This includes the two open datasets (iris; Palmer Penguins, Horst et al. 2020), the 40 prompts (Python and R), the two orchestration scripts that launched the 400 runs, every run's structured output for both languages, the report experiment's prompts, workflows, and gradings, and the analysis scripts that regenerate all tables and figures. The LTEM Cabo Pulmo 2023 reef fish data used for Task T4 are restricted and are available on request from the Aburto Lab; Tasks T1 to T3 are fully reproducible from the repository as it stands."));

c.push(H2("Conflict of interest"));
c.push(P("The authors declare no conflict of interest."));

c.push(H2("Funding"));
c.push(P("[To be completed.]"));

const doc = buildDoc(c, { title: "Title page - MEE submission", footerLeft: "Title page (not for review)", lineNumbers: false });
write(doc, path.join(__dirname, "Title_Page_MEE.docx"));
