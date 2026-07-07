// Shared Modern-Corporate theme + rich-text helpers for the MEE manuscript & SI.
const docx = require("docx");
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, Header, Footer, PageBreak, TabStopType, TabStopPosition,
} = docx;

const FONT = "Times New Roman";
const BODY = "1F2937", HEAD = "111827", TEAL = "0F766E", GRAY = "6B7280", LINE = "E5E7EB", FILL = "F3F4F6";

// rich text: **bold**, *italic*, ~sub~ handled minimally; splits a string into TextRuns
function rt(s, base = {}) {
  const runs = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_)/g;
  let last = 0, m;
  const push = (text, extra) => { if (text) runs.push(new TextRun({ text, font: FONT, size: base.size || 24, color: base.color || BODY, bold: base.bold, italics: base.italics, ...extra })); };
  while ((m = re.exec(s))) {
    push(s.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**")) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith("*")) push(tok.slice(1, -1), { italics: true });
    else if (tok.startsWith("_")) push(tok.slice(1, -1), { italics: true });
    last = m.index + tok.length;
  }
  push(s.slice(last));
  return runs;
}

const P = (s, opts = {}) => new Paragraph({ spacing: { line: 336, after: 120, ...(opts.spacing || {}) }, alignment: opts.align, children: typeof s === "string" ? rt(s, opts) : s, ...(opts.p || {}) });
const TITLE = (s) => new Paragraph({ style: "Title", children: rt(s, { size: 24, bold: true, color: HEAD }) });
const H1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: rt(s, { size: 24, bold: true, color: HEAD }) });
const H2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: rt(s, { size: 24, bold: true, color: HEAD }) });
const H3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: rt(s, { size: 24, bold: true, color: HEAD }) });
const CAP = (s) => new Paragraph({ spacing: { after: 160, line: 300 }, children: rt(s, { size: 22, color: GRAY, italics: true }) });
const TCAP = (s) => new Paragraph({ spacing: { before: 200, after: 60, line: 300 }, children: rt(s, { size: 22, color: GRAY, italics: true }) });
const BULLET = (s) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60, line: 320 }, children: rt(s) });
const NUM = (s, ref = "nums") => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 320 }, children: rt(s) });
const REFP = (s) => new Paragraph({ spacing: { after: 100, line: 300 }, indent: { left: 360, hanging: 360 }, children: rt(s, { size: 24 }) });
const HR = (color = TEAL, size = 6) => new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size, color, space: 1 } }, spacing: { before: 160, after: 160 } });
const GAP = (after = 120) => new Paragraph({ spacing: { after }, children: [] });
const PB = () => new Paragraph({ children: [new PageBreak()] });

function img(path, w, h, alt = "figure") {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 80 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width: w, height: h }, altText: { title: alt, description: alt, name: alt } })] });
}

function table(headers, rows, colWidths) {
  const accent = { style: BorderStyle.SINGLE, size: 6, color: TEAL };
  const sub = { style: BorderStyle.SINGLE, size: 4, color: LINE };
  const hcell = (t, w) => new TableCell({ borders: { bottom: accent }, width: { size: w, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 120, right: 120 }, shading: { fill: FILL, type: ShadingType.CLEAR }, children: [new Paragraph({ spacing: { line: 300 }, children: rt(t, { size: 20, bold: true, color: HEAD }) })] });
  const bcell = (t, w) => new TableCell({ borders: { bottom: sub }, width: { size: w, type: WidthType.DXA }, margins: { top: 90, bottom: 90, left: 120, right: 120 }, children: [new Paragraph({ spacing: { line: 300 }, children: rt(String(t), { size: 19 }) })] });
  const trs = [new TableRow({ tableHeader: true, children: headers.map((h, i) => hcell(h, colWidths[i])) })];
  rows.forEach(r => trs.push(new TableRow({ children: r.map((c, i) => bcell(c, colWidths[i])) })));
  return new Table({ width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: colWidths, rows: trs });
}

function buildDoc(children, { title = "Document", footerLeft = "", lineNumbers = true } = {}) {
  return new Document({
    creator: "Aburto Lab", title,
    styles: {
      default: { document: { run: { font: FONT, size: 24, color: BODY }, paragraph: { spacing: { line: 336, after: 120 } } } },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: HEAD }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: HEAD }, paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: HEAD }, paragraph: { spacing: { before: 260, after: 80 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: HEAD }, paragraph: { spacing: { before: 200, after: 40 }, outlineLevel: 2 } },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] },
        { reference: "nums", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 300 } } } }] },
        { reference: "nums2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 300 } } } }] },
      ],
    },
    sections: [{
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
        ...(lineNumbers ? { lineNumbers: { countBy: 1, restart: "continuous", distance: 360 } } : {}),
      },
      footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }], children: [new TextRun({ text: footerLeft, font: FONT, size: 16, color: GRAY }), new TextRun({ text: "\t", font: FONT, size: 16 }), new TextRun({ children: ["Page ", PageNumber.CURRENT], font: FONT, size: 16, color: GRAY })] })] }) },
      children,
    }],
  });
}

async function write(doc, path) { const buf = await Packer.toBuffer(doc); fs.writeFileSync(path, buf); console.log("wrote", path, fs.statSync(path).size, "bytes"); }

module.exports = { rt, P, TITLE, H1, H2, H3, CAP, TCAP, BULLET, NUM, REFP, HR, GAP, PB, img, table, buildDoc, write, COLORS: { BODY, HEAD, TEAL, GRAY, LINE, FILL } };
