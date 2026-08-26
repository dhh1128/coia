// COIA v2 reference implementation (Go).
// Tables and vectors are generated; see ../../gencode.py.
package coia

import (
	"fmt"
	"sort"
	"strings"
	"unicode"

	"golang.org/x/text/unicode/norm"
)

const (
	tatweel = 0x0640
	zwj     = 0x200D
	zwnj    = 0x200C
)

// ME is the reflexive sentinel, distinct from the empty string (§4.1).
const ME = "\x00COIA-ME"

var fold = map[rune]rune{0x02BC: 0x02BB}

func inRanges(r rune, rs [][2]rune) bool {
	for _, p := range rs {
		if r >= p[0] && r <= p[1] {
			return true
		}
	}
	return false
}

// Default Case Folding from the normative table (Appendix B.6). Deliberately does
// NOT use strings.ToLower, which applies SIMPLE case mapping: it turns U+0130 into
// "i" where full folding gives "i" followed by U+0307.
func casefold(s string) string {
	var b strings.Builder
	for _, r := range s {
		if f, ok := Foldgap[r]; ok {
			b.WriteString(f)
		} else {
			b.WriteRune(r)
		}
	}
	return b.String()
}

func joinerOk(rs []rune, i int) bool {
	switch rs[i] {
	case zwj:
		return i > 0 && inRanges(rs[i-1], Virama)
	case zwnj:
		if i > 0 && inRanges(rs[i-1], Virama) {
			return true
		}
		return i > 0 && i < len(rs)-1 && inRanges(rs[i-1], Arabic) && inRanges(rs[i+1], Arabic)
	}
	return false
}

// Normalize reduces a string to COIA canonical form (§5).
func Normalize(s string) string {
	rs := []rune(casefold(norm.NFKC.String(s)))
	var b strings.Builder
	onBase := false
	for i, r := range rs {
		switch {
		case inRanges(r, Split):
			b.WriteRune(' ')
			onBase = false
		case r == tatweel:
			// decorative
		case unicode.Is(unicode.Cf, r):
			if joinerOk(rs, i) {
				b.WriteRune(r)
			}
		case unicode.Is(unicode.Me, r):
			// enclosing marks are decorative
		case unicode.Is(unicode.Mn, r) || unicode.Is(unicode.Mc, r):
			if onBase {
				b.WriteRune(r)
			}
		case unicode.IsLetter(r) || unicode.IsNumber(r):
			if f, ok := fold[r]; ok {
				r = f
			}
			b.WriteRune(r)
			onBase = true
		default:
			onBase = false
		}
	}
	return strings.Join(strings.Fields(b.String()), "-")
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
func template(w, r, s string) string {
	return w + " " + r + opt(s, " "+s)
}

func opt(cond, val string) string {
	if cond == "" {
		return ""
	}
	return val
}

var pronouns = map[string]string{
	"en": "me", "es": "yo", "de": "ich", "fr": "moi", "pt": "eu", "it": "io",
	"ru": "я", "ja": "私", "zh": "我", "ko": "나", "ar": "أنا", "he": "אני",
}

// -------------------------------------------------------------------- flags

var assigned = map[rune]bool{'0': true, '1': true, '4': true, '5': true,
	'6': true, '7': true, '8': true, '9': true}

func flagGroup(digits, name string) (string, error) {
	if digits == "" {
		return "", nil
	}
	seen := map[rune]bool{}
	for _, r := range digits {
		d, ok := Digits[r]
		if !ok {
			return "", fmt.Errorf("%s must contain only decimal digits, got %q", name, r)
		}
		seen[d] = true
	}
	out := make([]rune, 0, len(seen))
	for d := range seen {
		out = append(out, d)
	}
	sort.Slice(out, func(i, j int) bool { return out[i] > out[j] })
	return string(out), nil
}

// CreateAlias mints an alias (§4, §6).
func CreateAlias(lang, who, role, scope, flags, privateFlags string) (string, error) {
	if _, ok := pronouns[lang]; !ok {
		return "", fmt.Errorf("unsupported language %q", lang)
	}
	reflexive := who == ME
	if reflexive {
		who = pronouns[lang]
	}
	f, err := flagGroup(flags, "flags")
	if err != nil {
		return "", err
	}
	pf, err := flagGroup(privateFlags, "private_flags")
	if err != nil {
		return "", err
	}
	for _, d := range f {
		if !assigned[d] {
			return "", fmt.Errorf("digit %q is reserved", d)
		}
	}
	if reflexive && strings.ContainsRune(f, '0') {
		return "", fmt.Errorf("reflexive aliases must not carry flag 0")
	}

	body := Normalize(template(who, role, scope))
	if Normalize(role) == "" {
		return "", fmt.Errorf("role must be non-empty after normalization")
	}
	if !reflexive && Normalize(who) == "" {
		return "", fmt.Errorf("who must be non-empty after normalization")
	}
	if body == "" {
		return "", fmt.Errorf("alias is empty after normalization")
	}

	out := body
	if f != "" || pf != "" {
		out += "," + f
	}
	if pf != "" {
		out += "," + pf
	}
	return out, nil
}

var commaVariants = strings.NewReplacer("、", ",", "،", ",", "，", ",")

// ParseAlias splits a raw alias into body and flag groups (§6.1, §6.2).
func ParseAlias(s string) (string, string, string, error) {
	parts := strings.Split(commaVariants.Replace(s), ",")
	if len(parts) > 3 {
		return "", "", "", fmt.Errorf("an alias has at most two flag groups")
	}
	get := func(i int) string {
		if i < len(parts) {
			return parts[i]
		}
		return ""
	}
	g1, err := flagGroup(get(1), "flags")
	if err != nil {
		return "", "", "", err
	}
	g2, err := flagGroup(get(2), "private_flags")
	if err != nil {
		return "", "", "", err
	}
	return Normalize(parts[0]), g1, g2, nil
}

// ----------------------------------------------------------------- matching

func terms(q string) []string {
	var out []string
	for _, t := range strings.Split(q, "-") {
		if t != "" {
			out = append(out, t)
		}
	}
	return out
}

// Matches reports whether a query finds an alias (§7).
func Matches(query, alias string) bool {
	body, _, _, err := ParseAlias(alias)
	if err != nil {
		return false
	}
	qbody, _, _, err := ParseAlias(query)
	if err != nil {
		return false
	}
	ts := terms(qbody)
	if len(ts) == 0 {
		return false
	}
	for _, t := range ts {
		if !strings.Contains(body, t) {
			return false
		}
	}
	return true
}

// Search returns matching aliases in the normative order (§7).
func Search(query string, aliases []string) []string {
	qbody, _, _, err := ParseAlias(query)
	if err != nil {
		return nil
	}
	ts := terms(qbody)
	type row struct {
		whole int
		first int
		cover float64
		alias string
	}
	var rows []row
	for _, a := range aliases {
		body, _, _, err := ParseAlias(a)
		if err != nil || len(ts) == 0 {
			continue
		}
		ok := true
		for _, t := range ts {
			if !strings.Contains(body, t) {
				ok = false
				break
			}
		}
		if !ok {
			continue
		}
		segs := strings.Split(body, "-")
		whole, first, matched := 0, 1<<30, 0
		for _, t := range ts {
			for _, s := range segs {
				if s == t {
					whole++
					break
				}
			}
			if i := strings.Index(body, t); i < first {
				first = i
			}
			matched += len([]rune(t))
		}
		rows = append(rows, row{whole, first, float64(matched) / float64(len([]rune(body))), a})
	}
	sort.Slice(rows, func(i, j int) bool {
		a, b := rows[i], rows[j]
		if a.whole != b.whole {
			return a.whole > b.whole
		}
		if a.first != b.first {
			return a.first < b.first
		}
		if a.cover != b.cover {
			return a.cover > b.cover
		}
		return a.alias < b.alias
	})
	out := make([]string, len(rows))
	for i, r := range rows {
		out[i] = r.alias
	}
	return out
}
