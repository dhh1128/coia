# Native-language review of the COIA templates

*2026-08-25. The evidence behind [Appendix A.2](APPENDIX-A.md).*

[Appendix A](APPENDIX-A.md) used to define a template per language plus a page of per-language rules. It now
defines one template used everywhere and a table of reflexive pronouns. This document is
what changed the appendix, including the parts that argue against the conclusion.

## Method

Eleven languages — `ar de es fr he it ja ko pt ru zh` — were each sent to independent
reviewers with a self-contained prompt: the register an alias needs, the constraints a
template cannot escape, the aliases the reference implementation actually produced for that
language, and a required output structure (verdict, findings, proposal, confidence).
English was excluded as settled, which turned out to be a mistake — see Limitations.

Seven models, one flagship from each of seven labs: DeepSeek, Moonshot, Z.ai, Alibaba,
OpenAI, Google, Mistral. Two to four seats per language, chosen so that at least two
independent training lineages saw each one. *No seat was shown another seat's answer.*
34 reviews in round one, 13 in a second round for the four languages that had not
converged, 47 total.

Reviewers cannot execute code, so every "I tested this" claim in them is hand-simulation.
The aliases quoted in the prompts were real output from the reference implementation, which
makes a reviewer contradicting them about *what the algorithm produces* wrong, and a
reviewer contradicting them about *whether that output is good language* the entire point.

## What came back

*Round one: no language passed clean.* 25 FLAWED, 5 ACCEPTABLE, 4 WRONG across 34
reviews. All three Japanese seats returned WRONG, agreeing on the defect: the trailing
`{org}での` left a particle attached to nothing.

*Bare apposition — dropping the connectors entirely — was proposed independently in all
eleven languages.* Not as a hedge. The argument was the same each time: an alias is a
business card, and a bare noun sequence is the business-card register in every one of these
languages. The strongest single result was Italian, where three seats from three labs
proposed the identical template and produced byte-identical aliases, agreeing at the level
of the output string rather than merely its shape.

*Round two* put the four unconverged languages — `es he ar zh` — a narrower question: is
apposition right for your language, and if not, what does it require that the others do not?
Hebrew and Arabic came back unanimous for bare apposition with byte-identical aliases.
Spanish split 2–1 on each of two independent axes, landing on the same place. Chinese
produced four different templates across eight reviews and never converged.

### Word order

With the connectors gone, the only remaining per-language question was order. Classifying
every proposed template across all 47 reviews:

| order | reviews |
|---|---|
| `who role scope` | 35 |
| `who scope role` | 5 |
| `scope role who` | 4 |
| `scope who role` | 3 |

`who role scope` was *unanimous in 8 of the 11 languages* — Spanish, German, French,
Portuguese, Italian, Russian, Arabic, Hebrew — across 33 reviews with no dissent. Only
Japanese, Korean and Chinese proposed anything else, and they did not agree with each
other: Japanese `scope role who` at 2 of 3, Korean `scope who role` at 2 of 3, Chinese with
no majority at all while still putting `who` first in 5 of 8. There is no coherent
alternative order, only three mutually inconsistent ones.

## What was adopted

One template, `{who} {role} {scope}`, in every language, with the reflexive pronoun as the
only per-language datum. [Appendix A.3](APPENDIX-A.md) lists everything that deleted.

Findings adopted that no one had been looking for:

- *Arabic `في` asserted containment.* A reviewer showed that `أليس بصفة أم في بوب` reads
  as "Alice as mother *inside* Bob" whenever scope is not an organization. Reported as an
  Arabic bug; it is in fact general — English `at` fails the same way, and the whole class
  disappears with the connectors.
- *Hebrew `ב` is a prefix that fuses to the following word.* Two seats raised
  independently that a leading `ה` in an organization name may be the definite article or a
  root consonant, which neither the template nor a reader can disambiguate.
- *The Korean `-(으)로서` allomorphy rule was correct.* A reviewer confirmed it against the
  examples. It was removed because the particle was the mistake, not the rule. Recorded
  verbatim in A.3 so it is not rediscovered as a defect.

## Limitations, stated because they are load-bearing

*The prompts asserted the conclusion they then confirmed.* Every prompt contained the line
*"An alias is a label, not a sentence,"* and named the business card, name badge and
org-chart entry as its cousins. Reviewers were therefore asked to judge against a premise,
not to discover one. Of 47 reviews, three mention speech at all, and all three use "reads
like a spoken sentence" as the *charge*. What the panel established is: *given that an
alias is a business card, apposition is right in every language.* It never tested the
antecedent. Anyone who thinks aliases should be sayable should read this document as
evidence about the wrong question.

*Round two was not independent.* It told reviewers that apposition had won elsewhere, which
is exactly the contamination round one was designed to avoid. The question was posed
adversarially and the candidate templates were listed without attribution, but round-two
agreement is weaker evidence than round one's and should be discounted accordingly. It is
strongest where seats supplied mechanisms rather than assent — the Hebrew `ה` ambiguity and
the Arabic register argument are not things a model produces by going along.

*The reviewers are models, not people.* They are the wrong instrument for a question about
what a speaker finds natural, and the right one only because they are cheap enough to run
eleven languages by seven lineages twice. Treat unanimity across independent lineages as
worth something and any single seat's opinion as worth little.

*The original templates were written by an AI, and the consolidation was done by the same
model family.* Where a dissent was judged weak below, that judgement came from the party
being reviewed.

*One seat was systematically unreliable.* Mistral produced the lone dissent on three
pronouns, two of the three proposals that were not computable from the inputs, and an Arabic
template built on parentheses — which the prompt states plainly are erased by normalization.
Several 2–1 splits in the raw data are really 2–0 with a bad seat attached. Discounting it
is itself a judgement call, and it happens to favour the outcome.

*English was excluded and then changed anyway.* The brief declared English settled and out
of scope, so no reviewer ever assessed it. When the panel's finding generalized to a single
universal template, English had to change with everything else or remain the sole surviving
special case, defeating the simplification. `cecilia-as-ceo-at-acme` became
`cecilia-ceo-acme` on an argument from consistency, with no review behind it.

*Japanese and Korean use an order their own reviewers ranked second.* A 2-of-3 split
contradicted by its nearest typological neighbour is weak evidence against 33 unanimous
reviews, and the simplification is large. But it is an override.

## Raw data

The 47 individual reviews are not in this repository — they are several hundred kilobytes of
model output whose value is almost entirely captured above. The prompts were generated from
the reference implementation and are reproducible; the per-seat responses are retained
outside the repo and can be published if anyone wants to audit a specific claim.
