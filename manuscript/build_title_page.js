// MEE title page (separate 'not for review' file). NOT anonymised: carries author
// names, affiliations, running headline, and all statements. Single-spaced.
const T = require("./theme.js");
const { P, TITLE, H2, HR, buildDoc, write, setSpacing } = T;
setSpacing(220);
const path = require("path");

const c = [];
c.push(TITLE("Reusable instructions make AI ecological analyses reproducible when they remove analytical choices"));
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
c.push(P("Code and materials are available at https://github.com/Fabbiologia/ai-skills-reproducibility-ecology and will be archived on Zenodo with a citable DOI. The companion Scientific AI Skills Registry (version 0.1.0), which implements the proposed community-submission workflow, is available at https://github.com/Fabbiologia/scientific-ai-skills-registry. The repository includes open iris and Palmer Penguins data, 40 scalar-task prompts, orchestration scripts, 400 scalar structured outputs, 48 report records and judge grades, analysis and document builders, an archive audit, and the proposed Skill Evidence Manifest. The restricted LTEM Cabo Pulmo 2023 reef-fish data are available on request from the Aburto Lab. Historical run records do not include exact model/provider/decoding metadata, and report records do not retain the full judged report text; these limitations are documented in PROVENANCE.md."));

c.push(H2("Use of AI tools"));
c.push(P("[Before submission, identify the exact applications and versions used for experimental generation and manuscript/code assistance, describe human verification, and align this statement with the Methods. Do not infer missing historical model metadata.]"));

c.push(H2("Conflict of interest and funding"));
c.push(P("Conflict of interest: The authors declare no conflict of interest. Funding: [To be completed.]"));

const doc = buildDoc(c, { title: "Title page - MEE submission", footerLeft: "Title page (not for review)", lineNumbers: false });
write(doc, path.join(__dirname, "Title_Page_MEE.docx"));
