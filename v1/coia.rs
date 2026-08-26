// Public domain code ported from python by AI; light testing confirms
// basic functionality is working with believable input from several
// languages (Portuguese, Russian). But use at your own risk. If anyone
// uses the code heavily and confirms that it's working well, please raise
// a PR to remove this caveat.

// IMPORTANT NOTE: THIS CODE CONTAINS MANY UNICODE STRING CONSTANTS AND CAN 
// BE MANGLED SUBTLY IF YOU COPY/PASTE IT IN A BROWSER. DOWNLOADING THE FILE
// DIRECTLY SHOULD BE LOSSLESS. TO TEST WHETHER MANGLING HAS HAPPENED, CHECK
// THE punct_to_space REGEX AS AN EXAMPLE ABOUT 50 LINES BELOW. YOUR IDE SHOULD
// SHOW THAT IT ENDS WITH SOME SMART QUOTE CHARACTERS; IT SHOULD *NOT*
// DISPLAY ACCENTED LATIN CHARACTERS INSIDE IT.

// add to Cargo.toml
// [dependencies]
// regex = "1.10"
// unicode-normalization = "0.1"

use regex::Regex;
use unicode_normalization::UnicodeNormalization;
use std::collections::HashMap;

const ME_AS_ARG: &str = "";

fn pronoun_translations() -> HashMap<&'static str, &'static str> {
    let mut map = HashMap::new();
    map.insert("en", "me");
    map.insert("fr", "moi");
    map.insert("es", "yo");
    map.insert("de", "ich");
    map.insert("pt", "eu");
    map.insert("ja", "私");
    map.insert("zh", "我");
    map.insert("ko", "나");
    map.insert("ar", "أنا");
    map.insert("he", "אני");
    map.insert("ru", "я");
    map
}

fn templates() -> HashMap<&'static str, &'static str> {
    let mut map = HashMap::new();
    map.insert("en", "{flags}{who} as {role}{scope}");
    map.insert("fr", "{flags}{who} comme {role}{scope}");
    map.insert("es", "{flags}{who} como {role}{scope}");
    map.insert("de", "{flags}{who} als {role}{scope}");
    map.insert("pt", "{flags}{who} como {role}{scope}");
    map.insert("ja", "{flags}{who}として{role}{scope}");
    map.insert("zh", "{flags}{who}作为{role}{scope}");
    map.insert("ko", "{flags}{who}로서{role}{scope}");
    map.insert("ar", "{flags}{who} بصفتي {role}{scope}");
    map.insert("he", "{flags}{who} בתור {role}{scope}");
    map.insert("ru", "{flags}{who} как {role}{scope}");
    map
}

fn scope_templates() -> HashMap<&'static str, &'static str> {
    let mut map = HashMap::new();
    map.insert("en", " at {org}");
    map.insert("fr", " à {org}");
    map.insert("es", " en {org}");
    map.insert("de", " bei {org}");
    map.insert("pt", " na {org}");
    map.insert("ja", "に-{org}");
    map.insert("zh", "在-{org}");
    map.insert("ko", "-{org}");
    map.insert("ar", " في {org}");
    map.insert("he", " ב{org}");
    map.insert("ru", " в {org}");
    map
}

/// Normalize a string similarly to the Python version
fn normalize_unicode(s: &str) -> String {
    // 1. NFKC normalization
    let s = s.nfkc().collect::<String>();
    // 2. lowercase
    let s = s.to_lowercase();

    // 3. Replace selected punctuators with space
    let punct_to_space = Regex::new(
        r#"[\p{Pd}\p{Pi}\p{Pf}\p{Ps}\p{Pe}&﹠＆.,‚،․。﹒．｡'’‘‚‛＇]"#
    ).unwrap();
    let s = punct_to_space.replace_all(&s, " ");

    // 4. Strip leading/trailing whitespace
    let strip_ws = Regex::new(r#"^\s+|\s+$"#).unwrap();
    let s = strip_ws.replace_all(&s, "");

    // 5. Delete disallowed characters
    let disallowed = Regex::new(
        r#"[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{So}\p{Sm}\p{Sc}\p{Sk}\p{P}\p{M}\p{Lm}]"#
    ).unwrap();
    let s = disallowed.replace_all(&s, "");

    // 6. Collapse whitespace into single ASCII hyphen
    let whitespace = Regex::new(r#"\s+"#).unwrap();
    let s = whitespace.replace_all(&s, "-");

    s.into_owned()
}

/// Create an alias given language, flags, who, role, scope
pub fn create_alias(
    lang: &str,
    flags: Option<&str>,
    who: Option<&str>,
    role: &str,
    scope: Option<&str>
) -> Result<String, String> {
    if role.trim().is_empty() {
        return Err("Role cannot be empty".to_string());
    }

    let mut flags = flags.unwrap_or("").trim().to_string();
    let mut who = who.unwrap_or("").trim().to_string();
    let role = role.trim();
    let mut scope = scope.unwrap_or("").trim().to_string();

    if !flags.is_empty() && !flags.chars().all(|c| c.is_ascii_digit()) {
        return Err("Flags must be all digits or empty".to_string());
    }
    if flags.len() > 10 {
        return Err("Flags must be at most 10 characters".to_string());
    }

    let pronouns = pronoun_translations();
    let templates_map = templates();
    let scope_map = scope_templates();

    if who == ME_AS_ARG {
        who = pronouns.get(lang)
            .ok_or_else(|| format!("No translation for 'me' in language {}", lang))?
            .to_string();
    }

    // Process flags
    if !flags.is_empty() {
        let mut chars: Vec<char> = flags.chars().collect();
        chars.sort();
        flags = chars.into_iter().collect::<String>() + " ";
    }

    // Process scope
    if !scope.is_empty() {
        let scope_template = scope_map.get(lang)
            .ok_or_else(|| format!("No scope template for language {}", lang))?;
        scope = format!(" {}", scope_template.replace("{org}", &scope));
    }

    // Select template
    let template = templates_map.get(lang)
        .ok_or_else(|| format!("No template for language {}", lang))?;

    let result = template
        .replace("{flags}", &flags)
        .replace("{who}", &who)
        .replace("{role}", role)
        .replace("{scope}", &scope);

    Ok(normalize_unicode(&result))
}
