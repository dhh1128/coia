# What changed from COIA 1.x, and why

Every change here is MAJOR under §10. A COIA 1.x alias and a COIA 2.0 alias for the same
inputs generally differ.

## Migration is safe in one specific sense

A 1.x reader cannot parse a 2.0 flag block (it looks for a leading digit run before the
first hyphen; 2.0 puts flags after a comma). A 2.0 reader cannot parse a 1.x flag block
(it looks for a comma). Each therefore reads the other's flagged aliases as **unflagged**.

Warnings are lost across the boundary. They are never inverted — which matters, because
`9` meant "test environment" in 1.x and means "compromised" in 2.0.

## Localization

**One template, in every language, with no connectors.** `{who} {role} {scope}`, joined by
spaces, scope omitted when empty. `cecilia-as-ceo-at-acme` becomes `cecilia-ceo-acme`;
`hans-als-direktor-deutsche-bank` becomes `hans-direktor-deutsche-bank`. English changed
along with everything else — it is not privileged here.

Eleven languages went to a panel of native-speaker model reviewers: 47 independent reviews,
seven models, five labs. Bare apposition was proposed independently in all eleven, and the
order `who role scope` was unanimous in 8 of them across 33 reviews with no dissent. The
three that dissented did not agree with each other. Appendix A.2 carries the evidence and
A.3 lists everything this deleted.

The practical effect is that COIA 1.x's per-language appendix — connectors, prepositions,
particles, the Korean `-(으)로서` allomorphy, the Russian `в`/`во` list — is gone. A
connector is the part of a template that has to know an organization's gender, or the case
its preposition governs, or which allomorph a particle takes; none of that is derivable
from an open class of names. Removing the connector dissolves the whole category.

**The language code now selects only the reflexive pronoun.** Two `create_alias` calls
differing only in language produce identical output unless `who` is the "me" sentinel.

## Flags

**Moved from prefix to comma-delimited suffix.** `0-cecilia-as-ceo-at-acme` becomes
`cecilia-ceo-acme,0`. (The body changed too, for an unrelated reason — see Localization
below. Holding the body fixed, the flag move alone is `0-x` to `x,0`.)

The prefix collided with organization names beginning with a digit: `0-3m-as-supplier`
could not be distinguished from a `3M` alias carrying no flag, so the "strip the flag once
verified" step was string surgery on an ambiguous string. Plan 9, Studio 54, 7-Eleven,
Level 3 and 23andMe are all in the failing set.

The prefix was also unstable under bidirectional rendering: a flagged Hebrew alias put the
warning at the visual left in an LTR paragraph and the visual right in an RTL one. As a
suffix with digit values it renders identically in both.

**Renumbered.** `9` was test/demo and is now compromised; test/demo moved to `6`. `2` was
pairwise; pairwise moved to `1`, and `2` is reserved.

**Sorted descending**, so the most serious flag appears first. 1.x said "numerical order",
which every implementation read as ascending.

**Second group added.** `body,spec-flags,private-flags`. All ten registry digits are
reserved to the specification; private conventions go in the second group, where a reader
must not interpret them. This is what makes an unrecognized digit in the first group
unambiguously a warning from a later version rather than possibly somebody's private note.

**New digits** — `4` unfit, `5` second-hand, `7` do-not-use, `8` retired. See Appendix D.

**Duplicates collapse.** 1.x accepted `00` and `0` as different strings, therefore
different aliases for the same state.

**Reserved digits are rejected at generation.** 1.x left 1 and 3–8 undefined and every
implementation accepted them.

## Normalization

**Combining marks are no longer deleted.** The 1.x rule destroyed Yoruba and Igbo tone
marking, every Indic and Southeast Asian script, and 94 letters that NFKC decomposes into
base plus mark — Thai `สำนักงาน` became `สานกงาน`, a different syllable. It protected
nothing: NFKC recomposes European diacritics before the deletion step runs. Enclosing
marks (`Me`) are still elided; they are decorative.

**Modifier letters are no longer deleted.** The rule turned `Hawaiʻi` into `hawaii`,
`Oʻzbekiston` into `ozbekiston` and `サプライチェーン` into `サプライチェン`. NFKC already folds
the phonetic modifiers it was aimed at.

**Case folding replaces lowercasing.** 1.x said "convert to lower case" and pinned neither
algorithm nor locale. Go's `strings.ToLower` produced `οδοσ` where every other
implementation produced `οδος`; Java's locale-default `toLowerCase()` produced `ıstanbul`
under a Turkish locale. `Straße` and `STRASSE` now match.

**Whitespace is no longer deleted before it can split.** Tab, newline and U+0085 are both
`White_Space` and `Cc`; the 1.x deletion step ran first, so `Beta\tCorp` joined into
`betacorp` while `Beta Corp` split correctly. Anything pasted from a spreadsheet collapsed.

**Unassigned codepoints are no longer deleted.** `\p{Cn}` made the alias a function of the
runtime's Unicode version — Go reports 15.0 where Node reports 17.0 — so a name in a
newly-encoded script was preserved on one stack and annihilated on another.

**Step order is normative, and reordered.** Edge-stripping ran before deletion in 1.x, so
anything deleted next to a space left whitespace at an edge that became a hyphen:
`create_alias('en','','🙂 Bob','ceo','')` produced `-bob-as-ceo`, which normalized again to
`bob-as-ceo`. Normalization was not idempotent, so pasting a stored alias into a search box
could fail to find it. Fifty spacing-accent codepoints reached this through ordinary
input — `Acme´` is a dead-key artifact on French, Spanish and Portuguese layouts.

**Defined by explicit tables, not Unicode property names.** The 1.x pattern used `\p{Cs}`,
which the Rust `regex` crate rejects outright — `coia.rs` could not run at all. Go and Java
cannot express `\p{Dash}`; Java's `\s` is ASCII-only by default, so U+1680 and U+2028
survived into aliases that then failed the specification's own regular expression.

**Joiners are kept where orthography requires them.** 1.x deleted all `Cf`, so Sinhala
`ශ්‍රී` — the first word of Sri Lanka's name for itself — lost the ZWJ its orthography
requires.

**U+2044 FRACTION SLASH now splits.** In 1.x, `Version ½` and `Version 12` produced the
same alias, because NFKC expands `½` to `1⁄2` and the fraction slash was deleted.

## Substitution

**A single simultaneous pass, no rescanning, no replacement patterns.** 1.x said only
"substitute the values into string". Python used `str.format` (simultaneous), JavaScript
used `String.replace` with a string needle (first occurrence only), and the others used
sequential replace-all, so a value substituted early was rescanned: `who='{role}'` gave
three different answers across five implementations. `coia.js` additionally inherited
`String.prototype.replace`'s replacement patterns, so a `who` of `A$&B` produced
`awhob-as-ceo-at-acme` — and `coia.js` is what the specification's own demo page runs.

## Matching

**Specified as a testable predicate.** 1.x had one sentence, and it implied equality:
against a stored `0-cecilia-as-ceo-at-acme`, the queries `Cecilia`, `Acme` and
`CEO at Acme` all missed, and the only thing that hit was retyping the software-supplied
flag digit and the whole string.

**Flags are stripped from both sides.** **Order is defined.** **Normalization is an
exported operation** — `coia.go` and `coia.rs` kept it private, so a consumer could not
implement the matching rule without vendoring a private function.

## Localization

**Appendix A is normative for generators.** As "recommended", two conforming
implementations could be required to disagree, and no generation vector was well-formed.

**Four languages moved to apposition**; **Korean, Japanese and Arabic gained rules**;
**Italian's pronoun resolved to `io`**; **language codes moved to ISO 639-1**.

## Removed

**The uniqueness suffix.** 1.x specified an optional numeric suffix appended to
disambiguate identical aliases. No implementation ever had it — no parameter, no code
path. It also could not work as described: "uniqueness is not a requirement, only an
option" leaves an implementation that declines the option minting two identical labels for
two different identifiers with no rule for what happens next. Under §7 two identical
aliases are not a lookup failure; the user searches, receives both, and chooses.

**Eight examples.** Of eighteen published aliases, ten reproduced and eight did not, and
every failure was non-English. The specific lesson the failing examples taught — that CJK
constituents are hyphen-separated — is the one the algorithm does not implement.

## Added

Conformance classes (§3). Error behaviour and preconditions on normalized values (§4.3).
Post-conditions (§4.4). Privacy considerations (§9). Versioning and stability (§10).
Normative golden vectors (Appendix C). Normative character tables (Appendix B).
