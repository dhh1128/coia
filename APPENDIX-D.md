# Appendix D — Flag definitions

Normative for §6.3. Written to be usable in an application design session: each entry
states what a reader may conclude, who sets and clears it, and what the application must
decide for itself.

## 0. The alias assertion

Every COIA alias asserts one proposition. All flags are qualifications of it.

> *The alias assertion.* The aliased identifier is controlled by the party the creator
> calls `{who}`; that party acts in the capacity `{role}`; and it does so within the
> context `{scope}`.

Three components — subject, capacity, context. A flag that qualifies the assertion
qualifies *all three*, not just the subject. `0-cecilia-as-ceo-at-acme` does not mean
"this might not be Cecilia." It means any of: this might not be Cecilia; this might be
Cecilia but not acting as a CEO; Cecilia might not be the CEO at Acme.

An alias is *reflexive* when `{who}` is the creator. Reflexive aliases are marked in the
generator by the caller requesting the "me" sentinel, not by string inspection.

## 1. Cross-cutting rules

*Absence is never a guarantee.* For every flag, absence means only that the flag was not
set. It never asserts the negation. Absent `0` does not mean "verified." Absent `1` does
not mean "safe to share." Absent `9` does not mean "not compromised." An application MUST
NOT render absence as a positive assurance.

*Two classes of flag.* *Creator-indexed* flags record a state of the creator's own
knowledge or decision; two creators may legitimately differ about the same identifier.
*Referent-indexed* flags record a property of the identifier itself; all creators who
know the fact should agree.

*Derivability.* Some underlying facts are readable from the identifier's own record — a
KEL, a testnet address prefix, a registry. The registry excludes derivable *facts*, on the
grounds that software should read them fresh rather than cache them in a string. It
includes the *acceptance state* attached to a derivable fact, because a decision is never
derivable.

*Setting and clearing are decisions, not observations.* No flag's absence records that
evidence exists. It records that a person, or software acting under that person's policy,
decided the risk was no longer worth tracking.

## 2. The registry

---

### `0` — unverified

*Asserts.* The creator has not decided that the evidence for the alias assertion is
sufficient. Doubt remains outstanding about at least one of subject, capacity or context.

*Reading it.* A reader MUST treat the whole assertion as unconfirmed. Partial
confirmation does not clear the flag: a creator who has confirmed the subject's identity
but not their capacity still carries `0`.

*Class.* Creator-indexed. Two parties may hold aliases for the same identifier where one
carries `0` and the other does not, and both are correct.

*Derivable.* No.

*Set by.* The generator, by default, on every non-reflexive alias. This is a MUST: a
generator that cannot establish the assertion at creation MUST set `0`.

*Cleared by.* A creator decision, which MAY be automated by application policy.

*Re-set by.* A creator decision, or policy — for example when the evidence that
justified clearing is withdrawn (a backing credential revoked, a challenge-response that
no longer holds). Never automatically by re-derivation, because nothing about `0` is
derivable.

*Reflexive aliases.* MUST NOT carry `0`.

*The application must decide:*
- Which evidence types suffice to clear it — interactive challenge-response over a
  trusted backchannel, presentation of a high-assurance credential, out-of-band
  confirmation, prior transaction history.
- Whether the assertion's three components are evaluated separately, and if so, that
  partial confirmation still leaves `0` set.
- Whether clearing is automatic on receipt of qualifying evidence, or requires explicit
  user confirmation.
- What events re-set it, and whether re-setting notifies the user.
- What it renders when `0` is present, and — critically — what it renders when absent,
  given that absence is not an assurance.

---

### `1` — pairwise

*Asserts.* The identifier is intended for use in exactly one relationship. Using or
disclosing it in any other context defeats the correlation resistance it was minted for.

*Reading it.* A reader MUST treat sharing, export, publication and reuse as prohibited
by intent.

*Class.* Referent-indexed — a property of how the identifier was minted.

*Derivable.* Sometimes. A `did:peer` or a per-relationship AID is structurally pairwise.
The creator's *intent* to keep it so is not derivable.

*Set by.* The generator at creation, from knowledge of how the identifier was obtained
or minted.

*Cleared by.* Nothing in normal operation. Pairwise-ness is a property of intent at
minting and does not lapse. An identifier that has been disclosed more widely has not
stopped being pairwise; it has become unfit (`4`) or compromised (`9`).

*Reflexive aliases.* Valid.

*The application must decide:*
- Which identifier types it treats as pairwise by construction.
- Which UI actions it blocks or warns on — share, export, copy, publish to a directory,
  include in a backup that leaves the device.
- Whether it warns when a pairwise identifier appears in a second relationship's context.

---

### `2`, `3` — reserved

Unassigned. A generator MUST NOT emit them. A reader encountering one MUST surface it as
an unrecognized flag (see §3).

`2` carried "pairwise" in COIA v1. The v1 syntax used a prefix and this version uses a
comma-delimited suffix, so no v1 alias can be misread by a v2 reader, and v1 saw no
adoption. It is therefore available for reassignment rather than retired.

---

### `4` — unfit

*Asserts.* The identifier's technical construction is weaker than the creator's policy
requires for consequential use, and that weakness has not been accepted.

*Reading it.* A reader MUST treat the identifier as unsuitable for high-stakes use until
a person has accepted the specific weakness. The alias assertion may be perfectly true;
this flag is about fragility, not truth.

*Class.* Hybrid. The underlying weaknesses are referent-indexed and derivable; the
acceptance decision is creator-indexed and is what the flag actually records.

*This flag does not travel.* `4` is the only flag whose presence depends on application
policy rather than on facts about the world. The same identifier is `4` in an application
with strict thresholds and unflagged in a lax one, and both are correct. A reader MUST NOT
infer from an absent `4` that another application would have judged the identifier fit,
and an application receiving an alias from elsewhere SHOULD re-evaluate against its own
policy rather than trusting the flag's absence.

*Derivable.* The facts, yes — witness count, signature threshold, key type, whether
control is single-signature. The acceptance, no.

*Set by.* Software, by inspecting the identifier's record against application policy.

*Cleared by.* A deliberate decision to accept the identified weakness. Clearing MUST be
an explicit act, never a side effect.

*Re-set by.* Software, when a weakness appears that was not covered by the existing
acceptance. *An implementation MUST have a re-set policy. This specification does not
define one*, because the right policy depends on what an application inspects and how
often. A non-normative example: record which specific weaknesses were accepted in
application storage; do not re-set for an accepted weakness; re-set when a new one appears.

*Reflexive aliases.* Valid. A creator's own identifier can use a deprecated scheme.

*The application must decide:*
- Which properties it inspects and what thresholds count as weak — minimum witness count,
  acceptable signature schemes, whether single-signature control is acceptable, whether a
  delegation chain is acceptable.
- Whether thresholds vary by transaction stakes, and if so whether the flag is per-alias
  or evaluated per-use.
- What the acceptance record contains, where it is stored, and how long it survives.
- Its re-set policy — required by the spec, defined by the application.
- Whether acceptance is per-weakness or blanket.

---

### `5` — second-hand

*Asserts.* This alias did not originate from the creator's own act of aliasing in the
present context. It was imported from another application, restored from a backup, synced
from another device, or accepted from another party's record.

*Reading it.* A reader MUST NOT treat the alias's own history as evidence for the alias
assertion. Whatever verification the original creator performed is not transferable.

*Class.* Creator-indexed.

*Derivable.* No.

*Set by.* Software, at the moment of import, restore, sync or acceptance.

*Cleared by.* The creator establishing the assertion locally — the same class of act
that clears `0`.

*Re-set by.* A subsequent import of the same alias.

*Reflexive aliases.* Valid. A reflexive alias restored from a backup or synced from
another device is second-hand: local software has not established that the identifier is
really the creator's. This is the case that makes the "reflexive aliases face no MITM
risk" claim too strong, and `5` is what expresses it.

*The application must decide:*
- Which ingestion paths set it — first-run restore, ongoing sync between the user's own
  devices, import from a third-party app, an alias received in a credential exchange.
- Whether sync between the user's own devices counts as second-hand.
- What local act clears it, and whether that act is the same one that clears `0`.

---

### `6` — test or demo

*Asserts.* The identifier belongs to an experimental, test or demonstration environment
and has no real-world consequence to reputation, governance or cost.

*Reading it.* A reader MUST NOT use the identifier where consequential production side
effects are intended.

*Class.* Referent-indexed.

*Derivable.* Often — testnet address prefixes, known test networks, development
registries.

*Set by.* Software from the identifier's own form, or by the creator.

*Cleared by.* Nothing. A test identifier does not become a production identifier.

*Reflexive aliases.* Valid.

*The application must decide:*
- Which environments it recognizes as test.
- Whether it blocks or merely warns on consequential actions.
- Whether test and production aliases are visually separated or interleaved.

*(This flag was `9` in COIA v1.)*

---

### `7` — do not use

*Asserts.* The creator has decided not to transact with this party. Nothing is asserted
about the identifier's soundness or the truth of the alias assertion.

*Reading it.* A reader MUST treat new interactions as against the creator's intent, and
MUST NOT infer that anything is wrong with the identifier itself.

*Class.* Creator-indexed. This is a relationship decision, not a fact about the world.

*Derivable.* No.

*Set by.* The creator.

*Cleared by.* The creator.

*Reflexive aliases.* Valid.

*The application must decide:*
- Whether these aliases are hidden, greyed, or shown normally with a marker.
- Whether the flag blocks actions or only warns.
- Whether a reason is recorded alongside, and where.

---

### `8` — retired

*Asserts.* The identifier is no longer in service — its key state has been rotated to
null, or the creator has written it off. It remains defined and historical references to
it remain resolvable.

*Reading it.* A reader MUST NOT use the identifier for new interactions. It MAY still
resolve it for historical verification.

*Class.* Referent-indexed when the key state was rotated to null; creator-indexed when
it is the creator's own judgment.

*Derivable.* Partly. A null rotation is in the key event log. "Abandoned for other
reasons" is not.

*Set by.* Software on observing a null rotation, or the creator.

*Cleared by.* Nothing. Retirement is terminal.

*Reflexive aliases.* Valid.

*The application must decide:*
- Whether it distinguishes observed null rotation from creator judgment.
- Whether retired aliases remain searchable, and where they sort.
- What it does with a credential or signature that predates retirement.

---

### `9` — compromised

*Asserts.* There is positive evidence that a party other than the one named controls the
identifier, or that duplicity has been observed.

*Reading it.* A reader MUST NOT rely on the identifier for any purpose. Note the
difference from `0`: `0` is absence of evidence, `9` is evidence of absence.

*Class.* Referent-indexed.

*Derivable.* Partly. Duplicity is detectable from conflicting events. Compromise learned
by other means — a report, an out-of-band warning — is not.

*Set by.* Software on observing duplicity, or the creator on external information.

*Cleared by.* Nothing. The correct response to a compromised identifier is to abandon
it, not to re-verify it.

*Reflexive aliases.* Valid.

*The application must decide:*
- What sources it accepts as evidence of compromise.
- Whether it blocks outright or warns.
- What it does with credentials or signatures already accepted from this identifier.
- Whether it propagates the finding to related aliases.

## 3. Unrecognized digits

A reader encountering a digit not in this registry MUST surface it rather than ignore it.
Because digits are ordered by seriousness and sorted descending, a reader MAY use position
as a severity hint: an unrecognized `4` is roughly as serious as `6`.

Group 2 (after the second comma) is private use. A reader MUST NOT interpret or surface
it as a warning.
