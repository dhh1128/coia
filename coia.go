// Public domain code ported from python by AI; use as you'd
// like but at your own risk. If anyone uses the code and
// confirms that it's working well, please raise a
// PR so I can remove the caveat.

// add to go.mod
// require golang.org/x/text v0.10.1

package coia

import (
	"fmt"
	"regexp"
	"sort"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// ME placeholder
const ME_AS_ARG = ""

// Pronoun translations
var pronounTranslations = map[string]string{
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

// Templates per language
var templates = map[string]string{
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

// Scope templates per language
var scopeTemplates = map[string]string{
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

// Precompile regexes
var (
	punctToSpacePattern = regexp.MustCompile(`[\p{Pd}\p{Pi}\p{Pf}\p{Ps}\p{Pe}&﹠＆.,‚،․。﹒．｡'’‘‚‛＇]`)
	whitespacePattern   = regexp.MustCompile(`\s+`)
	stripWSEdges        = regexp.MustCompile(`^\s+|\s+$`)
	disallowedPattern   = regexp.MustCompile(`[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{So}\p{Sm}\p{Sc}\p{Sk}\p{P}\p{M}]`)
)

// normalizeUnicode normalizes a string similarly to Python version
func normalizeUnicode(s string) string {
	// 1. NFKC normalization
	s = norm.NFKC.String(s)
	// 2. lowercase
	s = strings.ToLower(s)
	// 3. replace selected punctuators with space
	s = punctToSpacePattern.ReplaceAllString(s, " ")
	// 4. strip leading/trailing whitespace
	s = stripWSEdges.ReplaceAllString(s, "")
	// 5. delete disallowed characters
	s = disallowedPattern.ReplaceAllString(s, "")
	// 6. collapse whitespace into single ASCII hyphen
	s = whitespacePattern.ReplaceAllString(s, "-")
	return s
}

// CreateAlias generates a normalized alias
func CreateAlias(lang, flags, who, role, scope string) (string, error) {
	flags = strings.TrimSpace(flags)
	who = strings.TrimSpace(who)
	role = strings.TrimSpace(role)
	scope = strings.TrimSpace(scope)

	if role == "" {
		return "", fmt.Errorf("role cannot be empty")
	}

	if flags != "" && !regexp.MustCompile(`^\d+$`).MatchString(flags) {
		return "", fmt.Errorf("flags must be all digits or empty")
	}

	if len(flags) > 10 {
		return "", fmt.Errorf("flags must be at most 10 characters")
	}

	// Substitute ME with language-specific pronoun
	if who == ME_AS_ARG {
		pronoun, ok := pronounTranslations[lang]
		if !ok {
			return "", fmt.Errorf("no translation for 'me' in language %s", lang)
		}
		who = pronoun
	}

	// Process flags: sort digits
	if flags != "" {
		digits := strings.Split(flags, "")
		sort.Strings(digits)
		flags = strings.Join(digits, "") + " "
	}

	// Process scope
	if scope != "" {
		scopeTemplate, ok := scopeTemplates[lang]
		if !ok {
			return "", fmt.Errorf("no scope template for language %s", lang)
		}
		scope = " " + strings.ReplaceAll(scopeTemplate, "{org}", scope)
	}

	// Select template
	template, ok := templates[lang]
	if !ok {
		return "", fmt.Errorf("no template for language %s", lang)
	}

	// Interpolate template
	result := strings.ReplaceAll(template, "{flags}", flags)
	result = strings.ReplaceAll(result, "{who}", who)
	result = strings.ReplaceAll(result, "{role}", role)
	result = strings.ReplaceAll(result, "{scope}", scope)

	// Normalize
	return normalizeUnicode(result), nil
}
