import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

function findRepoRoot() {
  for (const seed of [process.cwd(), path.dirname(fileURLToPath(import.meta.url))]) {
    let cur = path.resolve(seed);
    for (let i = 0; i < 8; i++) {
      if (fs.existsSync(path.join(cur, "facts", "edu-order.csv")) && fs.existsSync(path.join(cur, "content", "book"))) {
        return cur;
      }
      const parent = path.dirname(cur);
      if (parent === cur) break;
      cur = parent;
    }
  }
  return path.resolve(process.cwd(), "..");
}

const REPO_ROOT = findRepoRoot();

function parseCsvSimple(rawText) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < rawText.length; i++) {
    const ch = rawText[i];
    if (inQuotes) {
      if (ch === '"' && rawText[i + 1] === '"') {
        field += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      if (row.some((c) => c.trim() !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field.replace(/\r$/, ""));
    if (row.some((c) => c.trim() !== "")) rows.push(row);
  }
  return rows;
}

let cachedGlossary = null;
function loadGlossary() {
  if (cachedGlossary) return cachedGlossary;
  const gPath = path.join(REPO_ROOT, "facts", "glossary.csv");
  if (!fs.existsSync(gPath)) {
    cachedGlossary = { map: new Map(), firstWords: new Set() };
    return cachedGlossary;
  }
  const lines = fs
    .readFileSync(gPath, "utf8")
    .split(/\r?\n/)
    .filter((l) => l.trim() && !l.trimStart().startsWith("#"))
    .join("\n");
  const rows = parseCsvSimple(lines);
  const map = new Map();
  const firstWords = new Set();
  if (rows.length >= 2) {
    const hdr = rows[0];
    const iTerm = hdr.indexOf("term");
    const iVi = hdr.indexOf("vi_gloss");
    const iEn = hdr.indexOf("en_gloss");
    for (const r of rows.slice(1)) {
      const term = (r[iTerm] || "").trim();
      const vi = (r[iVi] || "").trim();
      const en = (r[iEn] || "").trim();
      if (!term || !vi || term.includes("/") || term.length > 42) continue;
      const isShortAcronym = /^[A-Z0-9][A-Za-z0-9]{1,5}$/.test(term) && term !== term.toLowerCase();
      if (!isShortAcronym && term.length < 5) continue;
      const parts = term.split(/\s+/);
      if (parts.length > 3) continue;
      const lowerKey = parts.join(" ").toLowerCase();
      if (!map.has(lowerKey)) {
        map.set(lowerKey, { term, vi, en, exactCase: isShortAcronym });
        firstWords.add(parts[0].toLowerCase());
      }
    }
  }
  cachedGlossary = { map, firstWords };
  return cachedGlossary;
}

let cachedDiagrams = null;
function loadDiagramsForBook() {
  const dPath = path.join(REPO_ROOT, "facts", "diagrams.csv");
  if (!fs.existsSync(dPath)) return new Map();
  if (cachedDiagrams) return cachedDiagrams;
  const lines = fs
    .readFileSync(dPath, "utf8")
    .split(/\r?\n/)
    .filter((l) => l.trim() && !l.trimStart().startsWith("#"))
    .join("\n");
  const rows = parseCsvSimple(lines);
  const byChap = new Map();
  if (rows.length >= 2) {
    const hdr = rows[0];
    const iCh = hdr.indexOf("chapter");
    const iFile = hdr.indexOf("svg_file");
    const iCap = hdr.indexOf("caption_vi");
    const iSec = hdr.indexOf("anchor_section");
    for (const r of rows.slice(1)) {
      const chap = (r[iCh] || "").trim();
      const svgFile = (r[iFile] || "").trim();
      const cap = (r[iCap] || "").trim();
      const sec = (r[iSec] || "2").trim();
      const fullSvgPath = path.join(REPO_ROOT, "content", "diagrams", svgFile);
      if (!chap || !svgFile || !fs.existsSync(fullSvgPath)) continue;
      const svgRaw = fs.readFileSync(fullSvgPath, "utf8").trim();
      if (!byChap.has(chap)) byChap.set(chap, []);
      byChap.get(chap).push({ svgFile, cap, sec, svgRaw });
    }
  }
  cachedDiagrams = byChap;
  return byChap;
}

function textContent(node) {
  if (!node) return "";
  if (node.type === "text") return node.value || "";
  if (Array.isArray(node.children)) return node.children.map(textContent).join("");
  return "";
}

function fnameToChap(fname) {
  const base = path.basename(fname || "");
  let m = base.match(/^P0-00-(\d)-/);
  if (m) return `0.${m[1]}`;
  m = base.match(/^P14-([0-9.]+?)(?:-|$)/);
  if (m) return m[1];
  m = base.match(/^P(\d+)-(\d+)/);
  if (m) return `${parseInt(m[1], 10)}.${parseInt(m[2], 10)}`;
  return "";
}

const SKIP_TAGS = new Set(["a", "code", "pre", "h1", "h2", "h3", "h4", "svg", "abbr", "figcaption", "script", "style"]);
const TOKEN_RE = /[\p{L}\p{N}][\p{L}\p{N}._-]{1,}/gu;

function findGlossaryMatches(text, gloss, state) {
  const tokens = [];
  TOKEN_RE.lastIndex = 0;
  let m;
  while ((m = TOKEN_RE.exec(text)) !== null) {
    tokens.push({ word: m[0], lower: m[0].toLowerCase(), start: m.index, end: m.index + m[0].length });
  }
  if (!tokens.length) return null;

  const hits = [];
  let i = 0;
  while (i < tokens.length && state.count < 16) {
    if (!gloss.firstWords.has(tokens[i].lower)) {
      i++;
      continue;
    }
    let matchedSpan = null;
    for (let span = 3; span >= 1; span--) {
      if (i + span > tokens.length) continue;
      let contiguous = true;
      for (let k = 0; k < span - 1; k++) {
        if (text.slice(tokens[i + k].end, tokens[i + k + 1].start) !== " ") {
          contiguous = false;
          break;
        }
      }
      if (!contiguous) continue;
      const candKey = tokens.slice(i, i + span).map((t) => t.lower).join(" ");
      const entry = gloss.map.get(candKey);
      if (entry && !state.seen.has(candKey)) {
        if (entry.exactCase) {
          const rawSpan = tokens.slice(i, i + span).map((t) => t.word).join(" ");
          if (rawSpan !== entry.term) continue;
        }
        matchedSpan = { span, candKey, entry, start: tokens[i].start, end: tokens[i + span - 1].end };
        break;
      }
    }
    if (matchedSpan) {
      state.seen.add(matchedSpan.candKey);
      state.count++;
      hits.push(matchedSpan);
      i += matchedSpan.span;
    } else {
      i++;
    }
  }
  return hits.length ? hits : null;
}

const INLINE_TEXT_PARENTS = new Set(["p", "li", "td", "th", "strong", "em", "b", "i", "span"]);

function annotateGlossary(node, parentTag, state, gloss) {
  if (!gloss.firstWords.size || state.count >= 16) return;
  if (node.type === "element" && SKIP_TAGS.has(node.tagName)) return;
  if (node.type === "raw") return;

  if (node.type === "text" && INLINE_TEXT_PARENTS.has(parentTag)) {
    const val = node.value;
    if (!val || val.length < 4) return;
    const hits = findGlossaryMatches(val, gloss, state);
    if (!hits) return;
    const parts = [];
    let last = 0;
    for (const h of hits) {
      if (h.start > last) parts.push({ type: "text", value: val.slice(last, h.start) });
      parts.push({
        type: "element",
        tagName: "abbr",
        properties: {
          className: ["gloss"],
          tabIndex: 0,
          "data-term": h.entry.term,
          "data-vi": h.entry.vi,
          "data-en": h.entry.en,
          title: `${h.entry.term}: ${h.entry.vi}`,
        },
        children: [{ type: "text", value: val.slice(h.start, h.end) }],
      });
      last = h.end;
    }
    if (last < val.length) parts.push({ type: "text", value: val.slice(last) });
    return parts;
  }

  if (Array.isArray(node.children)) {
    const nextTag = node.type === "element" ? node.tagName : parentTag;
    const updated = [];
    for (const child of node.children) {
      const res = annotateGlossary(child, nextTag, state, gloss);
      if (Array.isArray(res)) updated.push(...res);
      else updated.push(child);
    }
    node.children = updated;
  }
}

export default function rehypeSystemCraft() {
  return (tree, file) => {
    const filePath = (file?.history && file.history[0]) || "";
    const normPath = filePath.replace(/\\/g, "/");
    const isBookChapter = normPath.includes("/content/book/") && !path.basename(normPath).startsWith("P15");
    const isCasePost = normPath.includes("/content/cases/");

    if (isBookChapter && Array.isArray(tree.children)) {
      const newChildren = [];
      let currentSec = null;
      for (const node of tree.children) {
        if (node.type === "element" && node.tagName === "h2") {
          const txt = textContent(node).trim();
          const m = txt.match(/^([0-8])\.\s/);
          if (m) {
            if (currentSec) newChildren.push(currentSec);
            currentSec = {
              type: "element",
              tagName: "section",
              properties: { className: ["sec"], "data-sec": m[1] },
              children: [node],
            };
            continue;
          }
        }
        if (currentSec) {
          currentSec.children.push(node);
        } else {
          newChildren.push(node);
        }
      }
      if (currentSec) newChildren.push(currentSec);
      tree.children = newChildren;

      const chap = fnameToChap(normPath);
      const diagrams = loadDiagramsForBook().get(chap) || [];
      for (const diag of diagrams) {
        const figNode = {
          type: "raw",
          value: `<figure class="diagram" data-diag="${diag.svgFile}">${diag.svgRaw}<figcaption>${diag.cap}</figcaption></figure>`,
        };
        const targetSec = tree.children.find(
          (n) => n.type === "element" && n.tagName === "section" && n.properties?.["data-sec"] === String(diag.sec)
        );
        if (targetSec && Array.isArray(targetSec.children)) {
          const insertIdx = Math.min(2, targetSec.children.length);
          targetSec.children.splice(insertIdx, 0, figNode);
        }
      }
    }

    if (isBookChapter || isCasePost) {
      const gloss = loadGlossary();
      annotateGlossary(tree, "", { seen: new Set(), count: 0 }, gloss);
    }
  };
}
