// Public domain code ported from python by AI; light testing confirms
// basic functionality is working with believable input from several
// languages (Portuguese, Russian). But use at your own risk. If anyone
// uses the code heavily and confirms that it's working well, please raise
// a PR to remove this caveat.

// IMPORTANT NOTE: THIS CODE CONTAINS MANY UNICODE STRING CONSTANTS AND CAN 
// BE MANGLED SUBTLY IF YOU COPY/PASTE IT IN A BROWSER. DOWNLOADING THE FILE
// DIRECTLY SHOULD BE LOSSLESS. TO TEST WHETHER MANGLING HAS HAPPENED, CHECK
// PUNCT_TO_SPACE_PATTERN AS AN EXAMPLE ABOUT 50 LINES BELOW. YOUR IDE SHOULD
// SHOW THAT IT ENDS WITH SOME SMART QUOTE CHARACTERS; IT SHOULD *NOT*
// DISPLAY ACCENTED LATIN CHARACTERS INSIDE IT.

const ME_AS_ARG = "";

const PRONOUN_TRANSLATIONS = {
    en: "me",
    fr: "moi",
    es: "yo",
    de: "ich",
    pt: "eu",
    ja: "私",
    zh: "我",
    ko: "나",
    ar: "أنا",
    he: "אני",
    ru: "я"
};

const TEMPLATES = {
    en: "{flags}{who} as {role}{scope}",
    fr: "{flags}{who} comme {role}{scope}",
    es: "{flags}{who} como {role}{scope}",
    de: "{flags}{who} als {role}{scope}",
    pt: "{flags}{who} como {role}{scope}",
    ja: "{flags}{who}として{role}{scope}",
    zh: "{flags}{who}作为{role}{scope}",
    ko: "{flags}{who}로서{role}{scope}",
    ar: "{flags}{who} بصفتي {role}{scope}",
    he: "{flags}{who} בתור {role}{scope}",
    ru: "{flags}{who} как {role}{scope}"
};

const SCOPE_TEMPLATES = {
    en: " at {org}",
    fr: " à {org}",
    es: " en {org}",
    de: " bei {org}",
    pt: " na {org}",
    ja: "に-{org}",
    zh: "在-{org}",
    ko: "-{org}",
    ar: " في {org}",
    he: " ב{org}",
    ru: " в {org}"
};

const PUNCT_TO_SPACE_PATTERN = /[\p{Dash}\p{Quotation_Mark}&﹠＆.,‚،․。﹒．｡'’‘‚‛＇]/gu;
const WHITESPACE_PATTERN = /\p{White_Space}+/gu;
const STRIP_WS_EDGES = /^\p{White_Space}+|\p{White_Space}+$/gu;
const DISALLOWED_PATTERN = /[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{So}\p{Sm}\p{Sc}\p{Sk}\p{P}\p{M}\p{Lm}]/gu;

function normalizeUnicode(str) {
    // 1. NFKC normalization
    str = str.normalize("NFKC");

    // 2. Lowercase
    str = str.toLowerCase();

    // 3. Replace selected punctuators with space
    str = str.replace(PUNCT_TO_SPACE_PATTERN, " ");

    // 4. Strip leading/trailing whitespace
    str = str.replace(STRIP_WS_EDGES, "");

    // 5. Delete disallowed characters
    str = str.replace(DISALLOWED_PATTERN, "");

    // 6. Collapse whitespace into single ASCII hyphen
    str = str.replace(WHITESPACE_PATTERN, "-");

    return str;
}

// Alias creation function
function createAlias(lang, flags, who, role, scope) {
    flags = flags ? flags.trim() : "";
    who = who ? who.trim() : "";
    role = role ? role.trim() : "";
    scope = scope ? scope.trim() : "";

    if (!role) throw new Error("Role cannot be empty");
    if (flags && !/^\d+$/.test(flags)) throw new Error("Flags must be all digits or empty");
    if (flags.length > 10) throw new Error("Flags must be at most 10 characters");

    // Substitute ME with language-specific pronoun
    if (who === ME_AS_ARG) {
        if (!(lang in PRONOUN_TRANSLATIONS)) throw new Error(`No translation for 'me' in language ${lang}`);
        who = PRONOUN_TRANSLATIONS[lang];
    }

    // Process flags
    if (flags) {
        flags = flags.split("").sort().join("") + " ";
    }

    // Process scope
    if (scope) {
        if (!(lang in SCOPE_TEMPLATES)) throw new Error(`No scope template for language ${lang}`);
        const scopeTemplate = SCOPE_TEMPLATES[lang];
        scope = " " + scopeTemplate.replace("{org}", scope);
    }

    // Select template
    if (!(lang in TEMPLATES)) throw new Error(`No template for language ${lang}`);
    const template = TEMPLATES[lang];

    // Interpolate
    let result = template
        .replace("{flags}", flags)
        .replace("{who}", who)
        .replace("{role}", role)
        .replace("{scope}", scope);

    // Normalize
    result = normalizeUnicode(result);

    return result;
}

// Example usage
//const example = createAlias("fr", "02", ME_AS_ARG, "Directeur général", "Crédit Agricole");
//console.log(example); // Expected: "02-moi-comme-directeur-général-à-crédit-agricole"
