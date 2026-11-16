import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

function findRepoRoot(): string {
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
  throw new Error("Could not locate repository root containing facts/edu-order.csv");
}

export const REPO_ROOT = findRepoRoot();

function parseCsvRows(relPath) {
  const full = path.join(REPO_ROOT, relPath);
  if (!fs.existsSync(full)) return [];
  const raw = fs.readFileSync(full, "utf8").replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    if (inQuotes) {
      if (ch === '"' && raw[i + 1] === '"') {
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
      const trimmed = field.replace(/\r$/, "");
      row.push(trimmed);
      const first = (row[0] || "").trim();
      if (row.some((c) => c.trim() !== "") && !first.startsWith("#")) {
        rows.push(row.map((c) => c.trim()));
      }
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field.replace(/\r$/, ""));
    const first = (row[0] || "").trim();
    if (row.some((c) => c.trim() !== "") && !first.startsWith("#")) {
      rows.push(row.map((c) => c.trim()));
    }
  }
  return rows;
}

function parseCsvDicts(relPath) {
  const rows = parseCsvRows(relPath);
  if (rows.length < 2) return [];
  const hdr = rows[0];
  return rows.slice(1).map((r) => {
    const obj = {};
    hdr.forEach((h, i) => {
      obj[h] = r[i] ?? "";
    });
    return obj;
  });
}

export function fnameToChap(fname) {
  const base = path.basename(fname, ".md");
  let m = base.match(/^P0-00-(\d)-/);
  if (m) return `0.${m[1]}`;
  m = base.match(/^P14-([0-9.]+?)(?:-|$)/);
  if (m) return m[1];
  m = base.match(/^P(\d+)-(\d+)/);
  if (m) return `${parseInt(m[1], 10)}.${parseInt(m[2], 10)}`;
  return base;
}

export const PART_NAMES = {
  "1": "Học 1 — Máy & Mã",
  "2": "Học 2 — Dữ liệu & Giao tiếp",
  "3": "Học 3 — Phân tán, Cloud, An ninh, Vận hành",
  "4": "Học 4 — AI & Biên giới",
  "9": "Phụ lục — Đọc khi cần",
};

export interface ChapterMeta {
  slug: string;
  file: string;
  title: string;
  cluster: number;
  phan: string;
  isP15: boolean;
  entryId: string;
  star: boolean;
}

const STAR_CHAPTERS = new Set([
  // SYS101 (11)
  "0.2", "1.1", "1.2", "1.4", "1.7", "2.1", "2.3", "2.4", "3.1", "3.10", "4.1",
  // SYS102 (10)
  "5.2", "5.7", "5.12", "5.14", "6.5", "8.2", "8.3", "9.1", "9.7", "10.3",
  // SYS103 (9)
  "8.4", "8.5", "8.7", "11.1", "11.5", "12.2", "12.5", "13.1", "14.10.2",
]);

export function loadBookIndex(): ChapterMeta[] {
  const eduOrder = parseCsvRows("facts/edu-order.csv");
  const bookDir = path.join(REPO_ROOT, "content", "book");
  const list: ChapterMeta[] = [];

  for (const [fn, phan] of eduOrder) {
    const full = path.join(bookDir, fn);
    if (!fs.existsSync(full)) continue;
    const raw = fs.readFileSync(full, "utf8");
    const h1 = raw.match(/^#\s+(.+)$/m)?.[1]?.trim() || fn;
    const slug = fnameToChap(fn);
    const mCluster = fn.match(/^P(\d+)-/);
    list.push({
      slug,
      file: fn,
      title: h1,
      cluster: mCluster ? parseInt(mCluster[1], 10) : 0,
      phan: phan || "1",
      isP15: false,
      entryId: fn.replace(/\.md$/, ""),
      star: STAR_CHAPTERS.has(slug),
    });
  }

  const p15Files = fs
    .readdirSync(bookDir)
    .filter((f) => f.startsWith("P15") && f.endsWith(".md"))
    .sort();
  for (const fn of p15Files) {
    const raw = fs.readFileSync(path.join(bookDir, fn), "utf8");
    const h1 = raw.match(/^#\s+(.+)$/m)?.[1]?.trim() || fn;
    const slug = fn.replace(/\.md$/, "");
    list.push({
      slug,
      file: fn,
      title: h1,
      cluster: 15,
      phan: "15",
      isP15: true,
      entryId: slug,
      star: false,
    });
  }

  return list;
}

export function loadEduBridges(): Map<string, string> {
  const rows = parseCsvDicts("facts/red-thread-edu-bridges.csv");
  const m = new Map<string, string>();
  for (const r of rows) {
    if (r.den_chuong && r.van_ban_noi) {
      m.set(r.den_chuong, r.van_ban_noi);
    }
  }
  return m;
}

export function loadLearningPaths() {
  const rows = parseCsvRows("facts/learning-paths.csv");
  const personas: Record<string, Record<number, { chap: string; kind: string }[]>> = {
    a: {},
    b: {},
    c: {},
  };
  for (const [p, wStr, ch, kind] of rows) {
    if (!personas[p]) continue;
    const w = parseInt(wStr, 10);
    if (!personas[p][w]) personas[p][w] = [];
    personas[p][w].push({ chap: ch, kind });
  }
  return personas;
}

export function loadChapterCaseLinks() {
  const rows = parseCsvDicts("facts/chapter-case-links.csv");
  const byChap = new Map<string, { case_slug: string; vi_relation: string; en_relation: string }[]>();
  const byCase = new Map<string, { chapter: string; vi_relation: string; en_relation: string }[]>();
  for (const r of rows) {
    if (!byChap.has(r.chapter)) byChap.set(r.chapter, []);
    byChap.get(r.chapter)!.push({
      case_slug: r.case_slug,
      vi_relation: r.vi_relation,
      en_relation: r.en_relation,
    });
    if (!byCase.has(r.case_slug)) byCase.set(r.case_slug, []);
    byCase.get(r.case_slug)!.push({
      chapter: r.chapter,
      vi_relation: r.vi_relation,
      en_relation: r.en_relation,
    });
  }
  return { byChap, byCase };
}

export function loadStatusSnapshot() {
  const versions = parseCsvDicts("facts/versions.csv");
  const watchlist = parseCsvDicts("facts/watchlist.csv");
  const decisions = parseCsvDicts("facts/coverage-decisions.csv");
  const incidents = parseCsvDicts("facts/coverage-incidents.csv");
  const glossary = parseCsvDicts("facts/glossary.csv");
  const errataPath = path.join(REPO_ROOT, "facts", "ERRATA.md");
  const errata = fs.existsSync(errataPath) ? fs.readFileSync(errataPath, "utf8") : "";
  const unverified = versions.filter((r) => r.audit_verdict === "UNVERIFIED").length;
  const dates = versions.map((r) => r.last_verified).filter(Boolean).sort();
  return {
    versionCount: versions.length,
    unverified,
    watchlistCount: watchlist.length,
    decisionsCount: decisions.length,
    incidentsCount: incidents.length,
    glossaryCount: glossary.length,
    latestVerified: dates[dates.length - 1] || "2026-11-16",
    versions,
    watchlist,
    errata,
  };
}
