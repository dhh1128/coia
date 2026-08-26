# Appendix A — Localization

*Normative for the Generator class.* In COIA 1.x this appendix was "recommended", which
meant two implementations could both fully conform and be required to disagree, and no
generation vector was well-formed. It is normative now.

A generator MUST reject a language it does not support rather than falling back to
another. Language codes are ISO 639-1. (COIA 1.x used ISO 639-2/B — `ger`, `chi` — which
are bibliographic codes; every implementation used 639-1 anyway.)

## A.0 The template

There is one, and it is the same in every language:

    {who} {role} {scope}

joined by single spaces, with `{scope}` and its space omitted when scope is empty.
Normalization (§5) does the rest, so an alias body is three hyphen-separated fields.

    en  Cecilia / CEO / Acme              ->  cecilia-ceo-acme
    de  Hans / Direktor / Deutsche Bank   ->  hans-direktor-deutsche-bank
    ja  田中太郎 / 経理担当者 / 三菱銀行       ->  田中太郎-経理担当者-三菱銀行
    ar  علي / شريك / أرامكو                ->  علي-شريك-أرامكو
    he  אלי כהן / מנהל כספים / בנק הפועלים  ->  אלי-כהן-מנהל-כספים-בנק-הפועלים

*No language contributes a connector, preposition, particle, article or case ending.* A
generator that emits one does not conform.

## A.1 The reflexive pronoun

The only per-language datum in COIA. It is consulted only when the caller supplies the
reflexive sentinel in place of `who`; for every other alias the language code selects
nothing, and two calls differing only in language MUST produce identical output.

| lang | pronoun | lang | pronoun |
|---|---|---|---|
| en | me  | ru | я    |
| es | yo  | ja | 私   |
| de | ich | zh | 我   |
| fr | moi | ko | 나   |
| pt | eu  | ar | أنا  |
| it | io  | he | אני  |

Two were contested and are recorded so they are not reopened casually. Italian is `io`:
COIA 1.x offered `me stesso / io` unresolved, and `me stesso` is masculine, so a female
creator's reflexive alias was ungrammatical with no way for a generator to know. Arabic is
`أنا` rather than `نفسي`, because `نفسي` is also the adjective "psychological" — a
psychiatrist's own alias would read `نفسي-طبيب-نفسي` and look like a duplication bug —
because `أنا` is what a speaker actually types when hunting for their own entry, and
because `أ` sorts first in the Arabic alphabet, pinning a user's own aliases to the top of
a list where `ن` buries them.

## A.2 Why there is nothing else to localize

Eleven languages were put to a panel of native-speaker model reviewers on 2026-08-25: 47
independent reviews, seven models from seven labs — DeepSeek, Moonshot, Z.ai, Alibaba,
OpenAI, Google and Mistral — no reviewer shown another's answer. The full report,
including the limitations that argue against this conclusion, is in
[NATIVE-LANGUAGE-REVIEW.md](NATIVE-LANGUAGE-REVIEW.md). Two
findings collapsed what had been a page of per-language rules.

*Bare apposition was proposed independently in every language.* Not as a least-bad hedge
but as the register the artifact wants — an alias is a business card, a name badge, an
org-chart entry, and a bare noun sequence is what all three use in all eleven.

The deeper reason it works is that *a connector is precisely the part of a template that
must know what a template cannot know.* A preposition governs case (Russian `в` takes the
prepositional), demands an article and a gender (German `bei der`, Portuguese `na`/`no`),
contracts (French `à` + `le`), or selects an allomorph from the preceding sound (Korean
`-(으)로서`). Every one of those is agreement with an organization name, and organization
names are an open class — new ones appear daily — so any rule is silently wrong for names
it did not anticipate, and differently wrong across rule versions. Dropping the connector
does not solve those problems. It dissolves them.

Apposition also asserts no relation, which is a real limitation and not only a virtue:
`alice-parent-bob` does not say which of the two is the parent. That is accepted. The label
is private, §7 matching is order-independent, and its only reader already knows.

*The order is `who role scope`, and it is not a per-language question.* Unanimous in 8 of
11 languages — Spanish, German, French, Portuguese, Italian, Russian, Arabic, Hebrew —
across 33 reviews with no dissent, and the majority in 35 of all 47. Only Japanese, Korean
and Chinese proposed anything else, and *they did not agree with each other*: Japanese
proposed `scope role who`, Korean `scope who role`, and Chinese produced four different
orders across eight reviews with no majority at all, while still putting `who` first in
five of them. There is no coherent alternative to adopt, only three mutually inconsistent
ones, each carried by 2-of-3 or less.

The cost is stated plainly rather than buried: *Japanese and Korean use an order their own
reviewers ranked second.* A 2-of-3 split contradicted by its nearest typological neighbour
is weak evidence against 33 unanimous reviews, and the gain is large — one template, no
per-language rules, nothing to get wrong across eleven languages and six implementations.
But it is an override, and if it is ever revisited, this paragraph is why.

## A.3 What used to be here

Recorded so none of it is rediscovered as a missing feature.

- *Korean `-(으)로서` allomorphy.* `로서` when `(codepoint - 0xAC00) mod 28` is 0 (no
  batchim) or 8 (ㄹ), else `으로서`. *The rule was correct* — a reviewer confirmed it
  against the examples — and it is gone because the particle it served is gone. All three
  Korean reviewers read `김철수 사장으로서 삼성에서` as a clause missing its predicate
  rather than as a label.
- *Russian `в`/`во`* before certain consonant clusters. Already dead before this round:
  apposition had removed its only call site.
- *The connectors.* en `as`/`at`, es `como`/`en`, de `als`, fr `comme`, pt `como`, it
  `come`/`presso`, ru `как`, ja `の`/`として`/`での`, ko `-(으)로서`/`에서`, ar `بصفة`/`في`,
  he `בתפקיד`/`ב`, zh `作为`/`在`.
- *The Arabic capacity marker `بصفة`* was the uninflected construct form, chosen because
  the possessive forms (`بصفتي`, `بصفته`, `بصفتها`) inflect for the subject and COIA 1.x
  shipped inconsistent ones in its template and its examples. It was the best of the marked
  options, and reviewers rejected all of them as formal filler (حشو) in a label.
- *The Arabic preposition `في`* went a round earlier, for a different reason: it means
  "inside", right for an organization and wrong for everything else. `أليس بصفة أم في بوب`
  reads as "Alice as mother inside Bob", and §4.1 scope is any environment, context or
  relationship.

Reintroducing any of these means first reintroducing a reason for a connector.

## A.4 Word segmentation

The algorithm inserts no word boundary *within* a field. Chinese, Japanese and Thai fields
are therefore single unsegmented tokens: segmenting them would require a dictionary, and
that puts a CLDR-scale dependency inside a specification whose selling point is that it is
easy to implement.

The three fields are still separated from one another, because A.0 joins them with spaces
and §5 turns a space into a hyphen. So `田中太郎-経理担当者-三菱銀行` carries exactly two
hyphens — one per field boundary, none inside a field. Under COIA 1.x's Japanese template
the entire alias was one unbroken run with no hyphens at all, which made it the least
searchable alias the algorithm produced. A.0 fixes that as a side effect.

COIA 1.x's examples showed hyphen-separated CJK *constituents* that the algorithm never
produced, teaching a convention that did not exist. Those examples are removed.

The read-aloud clause of G5 does not apply to these languages. §7's matching predicate is
substring rather than segment comparison specifically so that an alias in these languages
can still be found by a word inside it.
