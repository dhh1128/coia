# Public domain code written by Daniel Hardman (with a
# little help from an AI friend). Tested and appears to
# exactly match the intent of the spec.

import unicodedata
import regex as re

# Constant for the “me” placeholder
ME_AS_ARG = ""

# Example pronoun translation table
PRONOUN_TRANSLATIONS = {
    "en": "me",
    "fr": "moi",
    "es": "yo",
    "de": "ich",
    "pt": "eu",
    "ja": "私",
    "zh": "我",
    "ko": "나",
    "ar": "أنا",
    "he": "אני",
    "ru": "я",
}

# Example templates per language (template uses {flags}{who} as {role}{scope})
TEMPLATES = {
    "en": "{flags}{who} as {role}{scope}",
    "fr": "{flags}{who} comme {role}{scope}",
    "es": "{flags}{who} como {role}{scope}",
    "de": "{flags}{who} als {role}{scope}",
    "pt": "{flags}{who} como {role}{scope}",
    "ja": "{flags}{who}として{role}{scope}",
    "zh": "{flags}{who}作为{role}{scope}",
    "ko": "{flags}{who}로서{role}{scope}",
    "ar": "{flags}{who} بصفتي {role}{scope}",
    "he": "{flags}{who} בתור {role}{scope}",
    "ru": "{flags}{who} как {role}{scope}",
}

# Example scope templates per language, use "{org}" as placeholder
SCOPE_TEMPLATES = {
    "en": " at {org}",
    "fr": " à {org}",
    "es": " en {org}",
    "de": " bei {org}",
    "pt": " na {org}",
    "ja": "に-{org}",
    "zh": "在-{org}",
    "ko": "-{org}",
    "ar": " في {org}",
    "he": " ב{org}",
    "ru": " в {org}",
}

# normalize step 3: map selected punctuators to a space
PUNCT_TO_SPACE_PATTERN = re.compile(r"""(
      \p{Dash}                 # all hyphens/dashes
    | \p{Quotation_Mark}       # all quotes/apostrophes
    | [&﹠＆]                   # ampersand variants
    | [.,‚،․。﹒．｡]           # periods and commas
    | ['’‘‚‛＇]                # extra apostrophes/quotes
)""", re.VERBOSE)

# normalize step 4/6: whitespace handling
WHITESPACE_PATTERN = re.compile(r"\p{White_Space}+")
STRIP_WS_EDGES = re.compile(r"^\p{White_Space}+|\p{White_Space}+$")

# normalize step 5: disallowed characters (delete)
DISALLOWED_PATTERN = re.compile(r"""
    [\p{Cc}\p{Cf}]   # control/format
  | \p{Cs}           # surrogates
  | \p{Co}           # private-use
  | \p{Cn}           # unassigned
  | \p{So}           # symbols, other (emoji, dingbats, etc.)
  | \p{Sm}           # math symbols
  | \p{Sc}           # currency symbols
  | \p{Sk}           # modifier symbols
  | \p{P}            # punctuation (anything not mapped to space)
  | \p{M}            # combining marks (orphaned marks after NFKC)
""", re.VERBOSE)

def normalize_unicode(s: str) -> str:
    # 1. NFKC normalization
    s = unicodedata.normalize("NFKC", s)

    # 2. lowercase
    s = s.lower()

    # 3. replace selected punctuators with space
    s = PUNCT_TO_SPACE_PATTERN.sub(" ", s)

    # 4. strip leading/trailing whitespace
    s = STRIP_WS_EDGES.sub("", s)

    # 5. delete disallowed characters (incl. orphaned combining marks)
    s = DISALLOWED_PATTERN.sub("", s)

    # 6. collapse whitespace into single ASCII hyphen
    s = WHITESPACE_PATTERN.sub("-", s)

    return s


def create_alias(lang, flags, who, role, scope):
    # Trim all inputs
    flags = flags.strip() if flags else ""
    who = who.strip() if who else ""
    role = role.strip() if role else ""
    scope = scope.strip() if scope else ""
    
    # Precondition checks
    if not role:
        raise ValueError("Role cannot be empty")
    if not flags.isdigit() and flags != "":
        raise ValueError("Flags must be all digits or empty")
    if len(flags) > 10:
        raise ValueError("Flags must be at most 10 characters")
    
    # Substitute ME with language-specific pronoun
    if who == ME_AS_ARG:
        if lang not in PRONOUN_TRANSLATIONS:
            raise ValueError(f"No translation for 'me' in language {lang}")
        who = PRONOUN_TRANSLATIONS[lang]
    
    # Process flags
    if flags:
        sorted_flags = "".join(sorted(flags))
        flags = sorted_flags + " "
    
    # Process scope
    if scope:
        if lang not in SCOPE_TEMPLATES:
            raise ValueError(f"No scope template for language {lang}")
        scope_template = SCOPE_TEMPLATES[lang]
        scope = " " + scope_template.format(org=scope)
    
    # Select template
    if lang not in TEMPLATES:
        raise ValueError(f"No template for language {lang}")
    template = TEMPLATES[lang]
    
    # Interpolate
    result = template.format(flags=flags, who=who, role=role, scope=scope)
    
    # Normalize
    result = normalize_unicode(result)
    
    return result


# Example usage
if __name__ == "__main__":
    import argparse
    syntax = argparse.ArgumentParser(description="Generate a normalized alias.")
    syntax.add_argument("--lang", required=False, default="fr", help="Language code (e.g., en, fr)")
    syntax.add_argument("--flags", required=False, default="02", help="Flags (digits only)")
    syntax.add_argument("--who", required=False, default=ME_AS_ARG, help="Who (use empty for 'me')")
    syntax.add_argument("--role", required=False, default="Directeur général", help="Role description")
    syntax.add_argument("--scope", required=False, default="Crédit Agricole", help="Scope/organization")
    args = syntax.parse_args()
    alias = create_alias(
        lang=args.lang,
        flags=args.flags,
        who=args.who,
        role=args.role,
        scope=args.scope
    )
    print(f"{args.lang}: {args.flags} {args.who} {args.role} {args.scope} -> {alias}")
    # Expected output: "02-moi-comme-directeur-général-à-crédit-agricole"
