# COIA 2.0 — Conventions for Opaque Identifier Aliases

*Draft. Supersedes COIA 1.x. See [CHANGES](CHANGES.md) for what moved and why.*

Opaque identifiers — DIDs, KERI AIDs, SSH and PGP keys, payment addresses, UUIDs,
passkeys, account numbers — are hard for people to remember, speak, compare and search.
Management tools paper over this with a free-text label field and offer no guidance about
what to put in it. Users invent ad hoc conventions or none at all.

COIA is a convention for that label. It is not an identifier, not a namespace, and not a
protocol.

COIA aliases look like this:

- `cecilia-second-violin-vienna-symphony`
- `moi-directeur-général-l-oréal` — reflexive: *me, as CEO at L'Oréal*
- `hans-müller-buchhalter` — no scope, because none is interesting here
- `トヨタ-購買者-サプライチェーン,0` — *Toyota, purchaser, supply chain*, flagged unverified
- `علي-شريك-تجاري,1` — *Ali, business partner*, flagged as intended for one relationship
- `bob-payee-bitcoin,9` — flagged compromised, so it is shown but not used

Every one of those is real output from the reference implementation, not an illustration.
You can [generate your own](form.html) in the browser, or run any of the six ports — the
oracle in [python](coia.py), plus [javascript](impl/js/coia.js), [go](impl/go/coia.go),
[java](impl/java/Coia.java), [rust](impl/rust/src/lib.rs) and [swift](impl/swift/Coia.swift).
All six are held byte-for-byte to the same vectors; see [IMPLEMENTATIONS](IMPLEMENTATIONS.md).

The three fields are always the same three, in the same order, in every language: *who*,
*role*, *scope* (§4.1). Anything after a comma is a flag (§6) — a safety-relevant warning
about the identifier, not part of the label.

Flag placement and the template both changed in 2.0:

    0-cecilia-as-ceo-at-acme      <- COIA 1.x
    cecilia-ceo-acme,0            <- COIA 2.0

## 1. Scope and non-goals

An alias improves UX *for the person who creates it*. It is not a commitment to meaning
for anyone else. An alias may change at its creator's whim, is unresolvable outside the
creator's context, and parsing someone else's alias for strong meaning is a dangerous
antipattern.

This specification defines:

- how an alias is generated from three answers and a language;
- a normalization algorithm that maps any string to a canonical form;
- a flag syntax and registry for safety-relevant qualifications;
- a matching rule for lookup.

It does not define: how aliases are stored, whether generation inputs are retained, how
collisions between identical aliases are resolved, or how an application ranks results
beyond the default order in §7.

## 2. Goals

*G1 — intuitable.* Given a handful of examples and no explicit instruction, a user
develops accurate intuition about how the conventions work.

*G2 — memorable.* Encountering an alias they created, a user immediately remembers who
is identified and in what context.

*G3 — predictable.* Given a context and an actor, a user correctly predicts what a
relevant alias might look like, and can therefore search with confidence.

*G4 — resident.* An alias is usable as-is in the places aliases live: the label or
comment field of a wallet, password manager, config file, or certificate wizard; and the
search box that finds it again.

*G5 — durable in transit.* If an alias is copied elsewhere — an email, a chat message, a
word processor, a log file, a shell, a spreadsheet, a Markdown document — it survives as a
single token, and it can be read aloud with high confidence.

G5 is a robustness claim, not an endorsement. §1 says aliases are not made to be reshared.
G5 says that when one is copied anyway, it should not be mangled.

*Known limitations of G5.* U+002D HYPHEN-MINUS has line-break class HY (UAX #14), so a
renderer may break an alias at any hyphen, and double-click word selection does not select
the whole token. Aliases MUST NOT be used as DNS labels when flagged (§6.6), nor as
unescaped CSS or XML identifiers. In scriptio-continua languages (Chinese, Japanese, Thai)
an alias is a single unsegmented token and the read-aloud clause of G5 does not apply.

## 3. Conformance classes

An implementation MAY conform as any subset of:

- *Normalizer* — implements §5. MUST export normalization as a callable operation;
  matching is defined in terms of it, and a consumer cannot implement §7 without it.
- *Generator* — implements §4 and §6, and normalizes via a conforming Normalizer.
- *Matcher* — implements §7, and normalizes via a conforming Normalizer.

Every MUST in this specification binds one of these three classes. A requirement that
constrains a human's judgment, a user interface, or third-party software is written as
guidance, not as a normative keyword.

The golden vectors in [Appendix C](APPENDIX-C.md) are normative. Where prose and vectors
disagree, that is a defect in this specification; report it.

## 4. Creating an alias

### 4.1 Answer three questions

- *who* — which subject the identifier refers to. Enough of a name to be meaningful in
  the creator's context.
- *role* — what responsibility, posture or behaviour distinguishes this facet of the
  subject's identity from other facets.
- *scope* — which environment, context or relationship defines the role. MAY be empty
  when the context is unconstrained or uninteresting.

Software often knows all three when it helps a user create or accept an identifier.

For a *reflexive* alias — one whose subject is the creator — the caller supplies a
distinguished sentinel rather than a name, and the generator substitutes the pronoun for the
chosen language ([Appendix A.2](APPENDIX-A.md)). A generator MUST NOT use the empty string as
this sentinel: a caller that omits `who` by accident would otherwise mint a reflexive alias for
a third party's identifier.

### 4.2 Expand the template

A generator MUST reject a language it does not support rather than falling back to
another. Templates and their per-language rules are in [Appendix A](APPENDIX-A.md), which is
*normative for the Generator class*.

Substitution MUST be a single simultaneous pass. Substituted values MUST NOT be rescanned,
and MUST NOT be interpreted as replacement patterns. A `who` of `{role}` produces the
literal text; a `who` containing `$&` produces those characters.

### 4.3 Preconditions

A generator MUST evaluate preconditions on *normalized* values, not raw input:

- `role` MUST be non-empty after normalization. (A raw `role` of `.` normalizes to the
  empty string and MUST be rejected, even though the raw value is non-empty.)
- `who` MUST be non-empty after normalization, unless the alias is reflexive.
- The complete alias MUST be non-empty after normalization.

### 4.4 Post-conditions

A generator's output MUST satisfy all of:

- `normalize(alias) == alias` — normalization is idempotent on a generated alias.
- The body matches the grammar in §8.
- No leading or trailing hyphen, and no doubled hyphen.

## 5. Normalization

Normalization maps any string to canonical form. *Step order is normative.*

1. Apply Unicode Normalization Form KC (NFKC).
2. Apply Unicode Default Case Folding — full, non-Turkic, no locale tailoring — using
   the CASEFOLD table in [Appendix B.6](APPENDIX-B.md). An implementation MUST NOT substitute
   its runtime's lowercase operation. Case mapping and case folding are different
   operations, and every runtime tested diverges somewhere: Go's `strings.ToLower`
   applies simple mapping (`İ` → `i` rather than `i` + U+0307) and omits the
   Final_Sigma rule; Java's `toLowerCase()` is locale-sensitive and yields `ıstanbul`
   under `tr_TR`; and no lowercase operation expands `ß` to `ss`.
3. Process the result one character at a time, in order, and for each character:
   - if it is in the *SPLIT* table ([Appendix B.1](APPENDIX-B.md)), emit U+0020 SPACE;
   - else if it is U+0640 ARABIC TATWEEL, emit nothing;
   - else if its General_Category is `Cf`, emit it only if §5.1 licenses it, else nothing;
   - else if its General_Category is `Me`, emit nothing;
   - else if its General_Category is `Mn` or `Mc`, emit it only if the previous emitted
     character was a letter, number or mark, else nothing;
   - else if its General_Category is `L*` or `N*`, emit it, applying the folds in
     [Appendix B.4](APPENDIX-B.md);
   - else emit nothing.
4. Split the result on runs of U+0020 and join the parts with U+002D HYPHEN-MINUS,
   discarding empty parts.

The character policy is therefore an allowlist: letters, numbers and orthographic marks
are kept,
a listed set becomes separators, and everything else is discarded. This is deliberate.
Naming Unicode properties directly is not portable — the Rust `regex` crate rejects
`\p{Cs}`, and neither Go nor Java can express `\p{Dash}` — and a property-based
definition makes the alias a function of each runtime's Unicode version.

Modifier letters (`Lm`) are kept. NFKC already folds the phonetic and superscript
modifiers; what survives is orthography — the katakana prolonged sound mark, kana and
ideographic iteration marks, the okina, and tone and length marks in Miao, Lisu, Ol Chiki,
N'Ko and others.

Combining marks are kept, except enclosing marks (`Me`). The thirteen `Me` characters are
enclosing circles, keycaps and Cyrillic liturgical number signs — decorative or symbolic,
not part of any orthography, and the keycap is an emoji component that would otherwise
survive where every other emoji is discarded. Deleting the other marks destroys Yoruba and Igbo
tone marking and every Indic and Southeast Asian script, while protecting nothing: NFKC
recomposes European
diacritics into single codepoints before this step runs, so `José` and `João` are
unaffected either way.

*Compatibility decompositions are accepted as-is.* NFKC turns 94 letters into base plus
mark. All 94 are Unicode composition exclusions, so no recomposition pass restores them,
and this specification does not attempt one. Both spellings converge, so a user typing
either finds the alias.

### 5.1 Joiners

U+200D ZERO WIDTH JOINER and U+200C ZERO WIDTH NON-JOINER are `Cf`, and are discarded
except where orthography requires them. Modelled on IDNA2008 CONTEXTJ (RFC 5892 A.1, A.2):

- *ZWJ* is kept if and only if the preceding character is in the *VIRAMA* table
  ([Appendix B.2](APPENDIX-B.md)).
- *ZWNJ* is kept if and only if the preceding character is in the VIRAMA table, or both
  neighbouring characters are in the *ARABIC* ranges ([Appendix B.3](APPENDIX-B.md)).

This preserves Sinhala `ශ්‍රී`, Devanagari conjuncts, Malayalam chillus, and Persian and
Urdu word-internal breaks, while discarding a bare joiner between Latin letters, which
would otherwise produce two aliases that render identically.

The Arabic clause is an approximation. RFC 5892 tests Joining_Type, which is unreachable
from Go and JavaScript regular expressions and would add several hundred table entries. It
over-permits slightly, within Arabic-script text only.

## 6. Flags

A flag qualifies *the alias assertion*: that the identifier is controlled by the party
the creator calls `who`; that this party acts in the capacity `role`; and that it does so
within the context `scope`. A flag qualifies all three components, not only the subject.

### 6.1 Syntax

    alias := body [ "," group1 [ "," group2 ] ]

`group1` holds registry digits (§6.3). `group2` is private use. Each group is a run of
ASCII decimal digits. A generator MUST emit at most two groups.

Both groups MUST have duplicates collapsed and MUST be sorted in *descending* numeric
order, so that the most serious flag appears first. (COIA 1.x sorted ascending. See
CHANGES.)

An empty `group1` with a populated `group2` is written `body,,digits`. Canonical form
omits trailing empty groups: `body,,` is not canonical and normalizes to `body`.

Because normalization (§5) discards all punctuation, a comma in a generated alias is
always a delimiter and never content.

### 6.2 Ordering of operations

A matcher or reader MUST split flag groups off *before* normalizing the body. The
reverse order destroys the delimiter.

On input, a reader MUST accept U+3001, U+060C and U+FF0C as group delimiters in addition
to U+002C, so a user retyping an alias on a CJK or Arabic keyboard is understood. (U+FF0C
folds to U+002C under NFKC in any case.) A generator MUST emit U+002C.

Similarly, a generator MUST emit ASCII digits, folding any Unicode decimal digit to its
ASCII equivalent; a reader MUST accept any Unicode decimal digit.

### 6.3 The registry

    0  unverified     doubt about the alias assertion is unresolved
    1  pairwise       for one relationship only; do not share
    2  —              reserved
    3  —              reserved
    4  unfit          technical posture weak for high-stakes use, and not yet accepted
    5  second-hand    imported, restored, synced, or accepted from another party
    6  test           throwaway, test, demo; no real-world consequence
    7  do-not-use     the creator has decided not to transact
    8  retired        no longer in service; historical references still resolve
    9  compromised    positive evidence that the wrong party controls it

Full definitions, including what sets and clears each flag and what an application must
decide for itself, are in [Appendix D](APPENDIX-D.md).

Digits are ordered by seriousness, ascending. This ordering carries meaning: a reader
encountering an unrecognized digit MAY use its position as a severity hint.

*Absence is never a guarantee.* For every flag, absence means only that the flag was not
set; it never asserts the negation. An application MUST NOT render an absent flag as a
positive assurance.

A generator MUST NOT emit a reserved digit. A reader encountering an unrecognized digit in
`group1` MUST surface it rather than ignore it — it is a warning from a later version of
this specification. A reader MUST NOT interpret `group2`.

Reflexive aliases MUST NOT carry `0`.

### 6.4 Clearing flags

Setting and clearing are decisions, not observations. Clearing `0` does not assert that
evidence exists; it records that a person, or software acting under that person's policy,
judged the remaining risk not worth tracking.

`4` is set by software from facts it can derive, and cleared by a deliberate acceptance of
the identified weakness. Because those facts remain true after acceptance, software
re-checking them will observe them again. *An implementation MUST have a policy governing
when `4` is re-set. This specification does not define one*; see [Appendix D.4](APPENDIX-D.md)
for a non-normative example.

`4` does not travel between applications: it is the only flag whose presence depends on
local policy rather than on facts about the world.

### 6.5 What flags are not

Facts an application can derive from an identifier's own record — witness count, signature
threshold, delegation, key type, whether control is multi-signature — are not flags.
Software should read them fresh rather than cache them in a string that can go stale. What
the registry records is the *acceptance state* attached to such a fact, which is a
decision, and decisions are never derivable.

### 6.6 Flags and DNS

An unflagged alias is a valid IDNA label in every language this specification supports,
subject to length. A flagged alias is not: the comma is not permitted in a label, and a
flag digit at the start of a right-to-left label violates the Bidi Rule (RFC 5893). Since
the delimiter appears only on flagged aliases, this is self-enforcing.

## 7. Comparing and matching

A query is normalized (§5) and its flag groups discarded before comparison.

*Predicate.* A matcher MUST report a match if and only if every term of the normalized
query is a substring of the normalized, flag-stripped alias, where a term is a
hyphen-delimited part of the normalized query. Term order does not matter.

Substring rather than segment comparison, because in scriptio-continua languages the whole
alias is a single segment and segment comparison could not find it by any word inside it.

*Order.* A matcher MUST return matches ordered by, in priority order:

1. the number of query terms matching a whole segment, descending;
2. the position of the earliest matching term, ascending;
3. coverage — the sum of matched term lengths divided by alias length — descending;
4. the alias itself, in codepoint order.

Key 4 leaves no ties, so the order is total and testable. This order is a default that is
correct with no information beyond the strings. An application holding its own signals —
recency, frequency, favourites — MAY re-rank.

Key 3 divides by length in characters, which favours short aliases. CJK aliases are
shorter in characters than Latin aliases carrying the same content, so a mixed-language
corpus will float them upward. This is a known bias, accepted in preference to normalizing
by segment count, which is biased the other way.

There is no minimum query length. A single-character query matching most of a corpus is
correct behaviour for incremental search, and CJK names are routinely one character.

*Uniqueness is out of scope.* Two identical aliases for different identifiers are not a
lookup failure: the user searches, receives both, and chooses. COIA 1.x described an
optional numeric suffix; it was never implemented and is removed. See CHANGES.

## 8. Grammar

    alias   := body [ "," group [ "," group ] ]
    body    := segment ( "-" segment )*
    segment := ( L | N | Mn | Mc )+
    group   := DIGIT*

where `L`, `N`, `M` are Unicode General_Category letter, number and mark, plus the
joiners licensed by §5.1.

As a regular expression, for the body:

    ^[\p{L}\p{N}\p{M}]+(-[\p{L}\p{N}\p{M}]+)*$

A permissive variant for user input, tolerating hyphen alternatives a keyboard may
produce:

    ^[\p{L}\p{N}\p{M}]+([-‐‑‒–−][\p{L}\p{N}\p{M}]+)*$

## 9. Privacy considerations

An alias is plaintext, and its structure is regular. `who`, `role` and `scope` always
appear in the same positions, so a backup, a sync service, a crash report, a screenshot or
a subpoena yields structured relationship data rather than idiosyncratic notes.

This is worse than an arbitrary label, not neutral, and the trade is deliberate: the
structure is what makes an alias memorable and searchable. An alias such as
`alice-smith-hiv-patient-mercy-clinic,1` is a plausible one to create and a
damaging one to leak.

Applications should consider: whether alias text is included in crash reports and
telemetry; whether it appears in logs that leave the device; whether it is visible on a
lock screen; and whether sensitive aliases warrant a separate store.

This specification does not require or forbid retaining generation inputs. Storage is
outside the conformance classes.

## 10. Versioning and stability

This specification uses semantic versioning, with these meanings.

*MAJOR* — any change to normalization, to the grammar, or to the meaning of an existing
flag digit. A stored alias may stop matching a freshly normalized query.

*MINOR* — adding a language, assigning a reserved flag digit, or clarifying prose. A
MINOR change MUST NOT change the alias produced for any previously valid input.

Implementations MUST record the COIA version and the Unicode version used to produce an
alias. A matcher MUST compare against the stored alias as it stands, and MUST NOT assume
it was produced by the current version.

Normalization is deliberately defined by explicit tables rather than by Unicode
properties, so a Unicode upgrade does not silently change an alias: new characters are
preserved by default because they are letters, and the SPLIT and VIRAMA tables change only
when this specification changes.

## Appendices

- [Appendix A](APPENDIX-A.md) — Localization: the template, the reflexive pronouns, and why
  there are no per-language rules. Normative for generators.
- [Appendix B](APPENDIX-B.md) — Character tables: SPLIT, VIRAMA, ARABIC, folds, CASEFOLD.
  Normative.
- [Appendix C](APPENDIX-C.md) — Golden vectors. Normative.
- [Appendix D](APPENDIX-D.md) — Flag definitions and application guidance.

And, non-normative:

- [CHANGES](CHANGES.md) — what moved from COIA 1.x, and why.
- [IMPLEMENTATIONS](IMPLEMENTATIONS.md) — the six reference ports and how to run them
  against the vectors.
- [NATIVE-LANGUAGE-REVIEW](NATIVE-LANGUAGE-REVIEW.md) — the review that produced
  [Appendix A](APPENDIX-A.md), including the limitations that argue against it.
- [`v1/`](v1/README.md) — COIA 1.x, preserved.
