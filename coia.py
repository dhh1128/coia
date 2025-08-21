import unicodedata
import regex as re

# Constant for the “me” placeholder
ME = ""

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
    if who == ME:
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
    result = unicodedata.normalize("NFKC", result)
    # Strip all leading/trailing Unicode whitespace
    result = re.sub(r"^\p{White_Space}+|\p{White_Space}+$", "", result)
    # Convert to lowercase
    result = result.lower()
    # Remove all punctuation
    result = re.sub(r"\p{P}+", "", result)
    # Replace all whitespace sequences with a single hyphen
    result = re.sub(r"\p{White_Space}+", "-", result)
    
    return result


# Example usage
if __name__ == "__main__":
    alias = create_alias(
        lang="fr",
        flags="02",
        who=ME,
        role="Directeur général",
        scope="Crédit Agricole"
    )
    print(alias)
    # Expected output: "02-moi-comme-directeur-général-à-crédit-agricole"
