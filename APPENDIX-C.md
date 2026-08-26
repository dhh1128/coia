# Appendix C — Golden vectors

*Normative.* Where this specification's prose and these vectors disagree, that is a
defect; report it.

The machine-readable set is `vectors.json`. Each entry carries the section it tests, so a
failing vector points at the rule it came from.

Total: 136 — 69 normalize, 26 generate, 11 parse, 17 match, 10 reject, 3 search.

Vectors are authored *from the prose*, not captured from an implementation's output. An
implementation is not the oracle — that is how COIA 1.x's specification and its
[Appendix A](APPENDIX-A.md) drifted apart without either being anyone's bug.

## Sections

| section | count | tests |
|---|---|---|
| `normalize` | 69 | §5, input → canonical form |
| `generate` | 22 | §4, §6.1, (lang, who, role, scope, flags, private) → alias |
| `reject` | 10 | §4.3, §6.3, inputs a generator MUST refuse |
| `parse` | 11 | §6.1, §6.2, alias → (body, group1, group2) |
| `match` | 17 | §7, (alias, query) → boolean |
| `search` | 3 | §7, (corpus, query) → ordered list |

`null` in a `generate` vector's `who` position means the reflexive sentinel (§4.1), not an
empty string — the two are required to behave differently.

## Running them

    python run_vectors.py

Exits non-zero on any failure, printing the section, the vector's label, and both values.

## Coverage intent

Every MUST in §4 through §7 has at least one vector. The `normalize` section additionally
covers, by name: each SPLIT subclass (whitespace, dashes, quotes, script terminators,
fraction slash); marks in Yoruba, Khmer, Dhivehi, Devanagari, Tamil and Hebrew; modifier
letters in Japanese, Hawaiian, N'Ko and Lisu; all four joiner contexts in §5.1; NFKC
folding of fullwidth, circled, ligature, superscript, Roman-numeral and halfwidth forms;
and the degenerate inputs (empty, wholly elided, wholly separators).
