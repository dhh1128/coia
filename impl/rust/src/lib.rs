//! COIA v2 reference implementation (Rust).
//! Tables and vectors are generated; see ../../gencode.py.
pub mod data;

use std::collections::BTreeSet;
use unicode_normalization::UnicodeNormalization;
use unicode_properties::{GeneralCategory, UnicodeGeneralCategory};

const TATWEEL: u32 = 0x0640;
const ZWJ: u32 = 0x200D;
const ZWNJ: u32 = 0x200C;

/// The reflexive sentinel, distinct from the empty string (§4.1).
pub const ME: &str = "\u{0}COIA-ME";

fn in_ranges(cp: u32, rs: &[(u32, u32)]) -> bool {
    rs.iter().any(|&(lo, hi)| cp >= lo && cp <= hi)
}

fn fold_char(c: char) -> char {
    if c as u32 == 0x02BC { '\u{02BB}' } else { c }
}

// Default Case Folding from the normative table (Appendix B.6). Deliberately does
// NOT use to_lowercase(): case mapping and case folding are different operations.
fn casefold(s: &str) -> String {
    let mut out = String::new();
    for c in s.chars() {
        match data::FOLDGAP.binary_search_by_key(&(c as u32), |&(k, _)| k) {
            Ok(i) => out.push_str(data::FOLDGAP[i].1),
            Err(_) => out.push(c),
        }
    }
    out
}

fn joiner_ok(cps: &[char], i: usize) -> bool {
    let cp = cps[i] as u32;
    if cp == ZWJ {
        return i > 0 && in_ranges(cps[i - 1] as u32, data::VIRAMA);
    }
    if cp == ZWNJ {
        if i > 0 && in_ranges(cps[i - 1] as u32, data::VIRAMA) {
            return true;
        }
        return i > 0
            && i + 1 < cps.len()
            && in_ranges(cps[i - 1] as u32, data::ARABIC)
            && in_ranges(cps[i + 1] as u32, data::ARABIC);
    }
    false
}

/// Reduce a string to COIA canonical form (§5).
pub fn normalize(s: &str) -> String {
    let folded = casefold(&s.nfkc().collect::<String>());
    let cps: Vec<char> = folded.chars().collect();
    let mut out = String::new();
    let mut on_base = false;
    for (i, &c) in cps.iter().enumerate() {
        let cp = c as u32;
        let gc = c.general_category();
        if in_ranges(cp, data::SPLIT) {
            out.push(' ');
            on_base = false;
        } else if cp == TATWEEL {
            // decorative
        } else if gc == GeneralCategory::Format {
            if joiner_ok(&cps, i) {
                out.push(c);
            }
        } else if gc == GeneralCategory::EnclosingMark {
            // enclosing marks are decorative
        } else if matches!(gc, GeneralCategory::NonspacingMark | GeneralCategory::SpacingMark) {
            if on_base {
                out.push(c);
            }
        } else if c.is_alphabetic() || c.is_numeric() {
            out.push(fold_char(c));
            on_base = true;
        } else {
            on_base = false;
        }
    }
    out.split(' ').filter(|p| !p.is_empty()).collect::<Vec<_>>().join("-")
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
fn template(w: &str, r: &str, s: &str) -> String {
    format!("{w} {r}{}", if s.is_empty() { String::new() } else { format!(" {s}") })
}

fn pronoun(lang: &str) -> &'static str {
    match lang {
        "en" => "me", "es" => "yo", "de" => "ich", "fr" => "moi", "pt" => "eu",
        "it" => "io", "ru" => "я", "ja" => "私", "zh" => "我", "ko" => "나",
        "ar" => "أنا", "he" => "אני", _ => "",
    }
}

// -------------------------------------------------------------------- flags

const ASSIGNED: &[char] = &['0', '1', '4', '5', '6', '7', '8', '9'];

fn flag_group(digits: &str, name: &str) -> Result<String, String> {
    if digits.is_empty() {
        return Ok(String::new());
    }
    let mut seen = BTreeSet::new();
    for c in digits.chars() {
        match data::DIGITS.binary_search_by_key(&(c as u32), |&(k, _)| k) {
            Ok(i) => { seen.insert(data::DIGITS[i].1); }
            Err(_) => return Err(format!("{name} must contain only decimal digits, got {c:?}")),
        }
    }
    Ok(seen.iter().rev().collect())
}

/// Mint an alias (§4, §6).
pub fn create_alias(lang: &str, who: &str, role: &str, scope: &str,
                    flags: &str, private_flags: &str) -> Result<String, String> {
    let reflexive = who == ME;
    let who = if reflexive { pronoun(lang) } else { who };
    let f = flag_group(flags, "flags")?;
    let pf = flag_group(private_flags, "private_flags")?;
    for d in f.chars() {
        if !ASSIGNED.contains(&d) {
            return Err(format!("digit {d:?} is reserved"));
        }
    }
    if reflexive && f.contains('0') {
        return Err("reflexive aliases must not carry flag 0".into());
    }
    if pronoun(lang).is_empty() {
        return Err(format!("unsupported language {lang:?}"));
    }
    let expanded = template(who, role, scope);
    let body = normalize(&expanded);
    if normalize(role).is_empty() {
        return Err("role must be non-empty after normalization".into());
    }
    if !reflexive && normalize(who).is_empty() {
        return Err("who must be non-empty after normalization".into());
    }
    if body.is_empty() {
        return Err("alias is empty after normalization".into());
    }
    let mut out = body;
    if !f.is_empty() || !pf.is_empty() {
        out.push(',');
        out.push_str(&f);
    }
    if !pf.is_empty() {
        out.push(',');
        out.push_str(&pf);
    }
    Ok(out)
}

/// Split a raw alias into body and flag groups (§6.1, §6.2).
pub fn parse_alias(s: &str) -> Result<(String, String, String), String> {
    let s: String = s.chars()
        .map(|c| if c == '、' || c == '،' || c == '，' { ',' } else { c })
        .collect();
    let parts: Vec<&str> = s.split(',').collect();
    if parts.len() > 3 {
        return Err("an alias has at most two flag groups".into());
    }
    Ok((normalize(parts[0]),
        flag_group(parts.get(1).copied().unwrap_or(""), "flags")?,
        flag_group(parts.get(2).copied().unwrap_or(""), "private_flags")?))
}

// ----------------------------------------------------------------- matching

fn terms(q: &str) -> Vec<&str> {
    q.split('-').filter(|t| !t.is_empty()).collect()
}

/// Does a query find an alias? (§7)
pub fn matches(query: &str, alias: &str) -> bool {
    let (body, _, _) = match parse_alias(alias) { Ok(v) => v, Err(_) => return false };
    let (qbody, _, _) = match parse_alias(query) { Ok(v) => v, Err(_) => return false };
    let ts = terms(&qbody);
    !ts.is_empty() && ts.iter().all(|t| body.contains(t))
}

/// Matching aliases in the normative order (§7).
pub fn search(query: &str, aliases: &[String]) -> Vec<String> {
    let (qbody, _, _) = match parse_alias(query) { Ok(v) => v, Err(_) => return vec![] };
    let ts = terms(&qbody);
    let mut rows: Vec<(i64, usize, f64, String)> = vec![];
    for a in aliases {
        let (body, _, _) = match parse_alias(a) { Ok(v) => v, Err(_) => continue };
        if ts.is_empty() || !ts.iter().all(|t| body.contains(t)) {
            continue;
        }
        let segs: Vec<&str> = body.split('-').collect();
        let whole = ts.iter().filter(|t| segs.contains(t)).count() as i64;
        let first = ts.iter().filter_map(|t| body.find(t)).min().unwrap_or(0);
        let matched: usize = ts.iter().map(|t| t.chars().count()).sum();
        let cover = matched as f64 / body.chars().count() as f64;
        rows.push((-whole, first, -cover, a.clone()));
    }
    rows.sort_by(|x, y| {
        x.0.cmp(&y.0)
            .then(x.1.cmp(&y.1))
            .then(x.2.partial_cmp(&y.2).unwrap())
            .then(x.3.cmp(&y.3))
    });
    rows.into_iter().map(|r| r.3).collect()
}
