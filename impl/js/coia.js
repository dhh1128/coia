// COIA v2 reference implementation (JavaScript).
// Tables and vectors are generated; see ../../gencode.py.
import { SPLIT, VIRAMA, ARABIC, FOLDGAP, DIGITS } from "./data.js";

const TATWEEL = 0x0640, ZWJ = 0x200d, ZWNJ = 0x200c;
const FOLD = new Map([[0x02bc, 0x02bb]]);
export const ME = Symbol("me");

const inRanges = (cp, rs) => rs.some(([lo, hi]) => cp >= lo && cp <= hi);

const RE_MNMC = /\p{Mn}|\p{Mc}/u, RE_ME = /\p{Me}/u, RE_CF = /\p{Cf}/u,
      RE_LN = /\p{L}|\p{N}/u, RE_DIGIT = /\p{Nd}/u;

// Default Case Folding from the normative table (Appendix B.6). Deliberately does
// NOT use toLowerCase(): case mapping and case folding are different operations.
function casefold(s) {
  let out = "";
  for (const ch of s) out += FOLDGAP.get(ch.codePointAt(0)) ?? ch;
  return out;
}

function joinerOk(cps, i) {
  const cp = cps[i];
  if (cp === ZWJ) return i > 0 && inRanges(cps[i - 1], VIRAMA);
  if (cp === ZWNJ) {
    if (i > 0 && inRanges(cps[i - 1], VIRAMA)) return true;
    return i > 0 && i < cps.length - 1 &&
           inRanges(cps[i - 1], ARABIC) && inRanges(cps[i + 1], ARABIC);
  }
  return false;
}

export function normalize(s) {
  const cps = [...casefold(s.normalize("NFKC"))].map(c => c.codePointAt(0));
  let out = "", onBase = false;
  for (let i = 0; i < cps.length; i++) {
    const cp = cps[i], ch = String.fromCodePoint(cp);
    if (inRanges(cp, SPLIT)) { out += " "; onBase = false; }
    else if (cp === TATWEEL) { /* decorative */ }
    else if (RE_CF.test(ch)) { if (joinerOk(cps, i)) out += ch; }
    else if (RE_ME.test(ch)) { /* enclosing marks are decorative */ }
    else if (RE_MNMC.test(ch)) { if (onBase) out += ch; }
    else if (RE_LN.test(ch)) { out += String.fromCodePoint(FOLD.get(cp) ?? cp); onBase = true; }
    else onBase = false;
  }
  return out.split(/ +/).filter(Boolean).join("-");
}

// ------------------------------------------------------------- localization
// koJosa lived here: the -(으)로서 allomorphy. Native-speaker review
// 2026-08-25 confirmed the RULE was correct and the PARTICLE was the mistake.
// Removed with the particle it served.

// One template, every language: who, role, scope joined by spaces, scope
// omitted when empty. Native-speaker review 2026-08-25 (47 reviews, 11 languages,
// 7 models, 5 labs): bare apposition was proposed independently in every language,
// and who-role-scope was unanimous in 8 of 11 and 35 of all 47. See coia.py for the
// full rationale and for the connectors and allomorphy rules this replaced.
export function template(w, r, s) {
  return `${w} ${r}` + (s ? ` ${s}` : "");
}

export const PRONOUNS = {
  en: "me", es: "yo", de: "ich", fr: "moi", pt: "eu", it: "io",
  ru: "я", ja: "私", zh: "我", ko: "나", ar: "أنا", he: "אני",
};

// -------------------------------------------------------------------- flags
const ASSIGNED = new Set([..."0145678 9".replace(" ", "")]);

function flagGroup(digits, name) {
  if (!digits) return "";
  const seen = new Set();
  for (const ch of digits) {
    const d = DIGITS.get(ch.codePointAt(0));
    if (d === undefined) throw new Error(`${name} must contain only decimal digits, got ${ch}`);
    seen.add(d);
  }
  return [...seen].sort().reverse().join("");
}


export function createAlias(lang, who, role, scope = "", flags = "", privateFlags = "") {
  if (!(lang in PRONOUNS)) throw new Error(`unsupported language ${lang}`);
  const reflexive = who === ME;
  if (reflexive) who = PRONOUNS[lang];
  flags = flagGroup(flags, "flags");
  privateFlags = flagGroup(privateFlags, "private_flags");
  for (const d of flags) if (!ASSIGNED.has(d)) throw new Error(`digit ${d} is reserved`);
  if (reflexive && flags.includes("0")) throw new Error("reflexive aliases must not carry flag 0");

  const body = normalize(template(who, role, scope));
  if (!normalize(role)) throw new Error("role must be non-empty after normalization");
  if (!reflexive && !normalize(who)) throw new Error("who must be non-empty after normalization");
  if (!body) throw new Error("alias is empty after normalization");

  let out = body;
  if (flags || privateFlags) out += "," + flags;
  if (privateFlags) out += "," + privateFlags;
  return out;
}

const COMMA_VARIANTS = /[、،，]/g;

export function parseAlias(s) {
  const parts = s.replace(COMMA_VARIANTS, ",").split(",");
  if (parts.length > 3) throw new Error("an alias has at most two flag groups");
  return [normalize(parts[0]),
          flagGroup(parts[1] ?? "", "flags"),
          flagGroup(parts[2] ?? "", "private_flags")];
}

// ----------------------------------------------------------------- matching
const terms = q => q.split("-").filter(Boolean);

export function matches(query, alias) {
  const [body] = parseAlias(alias);
  const [qbody] = parseAlias(query);
  const ts = terms(qbody);
  return ts.length > 0 && ts.every(t => body.includes(t));
}

export function search(query, aliases) {
  const [qbody] = parseAlias(query);
  const ts = terms(qbody);
  const scored = [];
  for (const a of aliases) {
    const [body] = parseAlias(a);
    if (!ts.length || !ts.every(t => body.includes(t))) continue;
    const segs = body.split("-");
    const whole = ts.filter(t => segs.includes(t)).length;
    const first = Math.min(...ts.map(t => body.indexOf(t)));
    const cover = ts.reduce((n, t) => n + [...t].length, 0) / [...body].length;
    scored.push([-whole, first, -cover, a]);
  }
  scored.sort((x, y) => x[0] - y[0] || x[1] - y[1] || x[2] - y[2] || (x[3] < y[3] ? -1 : x[3] > y[3] ? 1 : 0));
  return scored.map(r => r[3]);
}
