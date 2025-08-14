# Conventions for Opaque Identifier Aliases (COIA)
## Overview
This spec explains [how to generate](#conventions) consistent, human-friendly aliases (labels) for opaque identifiers that refer to actors with complex identities (people, organizations, AI-based agents, and so forth). COIA aliases look like this:

* me-as-ceo-at-acme
* me-as-patient-at-mayo-clinic
* ?bob-as-business-executive

COIA benefits users of digital wallets, password managers, verifiable credentials, cryptographic keys, and similar technologies.

Implementing COIA is easy. Adopting COIA imposes no learning curve. Following COIA will improve clarity, confidence, utility, and safety. Since the conventions help software help its own users, they deliver value as soon as they're adopted in one app, regardless of when they spread throughout an ecosystem.

For more about the theory behind these conventions, see [Opaque Identifier Aliases](https://dhh1128.github.io/papers/oia.html).

This is version 1 of COIA. If a future spec is released, the version number will change per [semver](https://semver.org) guidelines.

## Goals
COIA aims for aliases that have the following properties:
  
1. Given a handful of examples and no explicit instruction, a user naturally develops accurate intuition about how the conventions work, and about best practices for managing identity.
2. When a user encounters an alias that they created, they immediately and effortlessly understand who is identified by the aliased identifier, and the context in which that identifier is relevant. 
3. Given a context and an identified actor, a user can correctly predict what a relevant alias created by them might look like.
4. The alias is a single token that naturally processes well in existing environments such as email, chat, and word processors.

Note that this spec aims to improve UX *unilaterally*, NOT to make aliases *interoperable*. Aliases are like private pet names; they aren't meant to be shared. When Cecilia transacts with Bob on Bitcoin, she doesn't use local aliases to identify her address or Bob's; she uses raw addresses. Therefore, how Cecilia locally labels her address or Bob's address is nobody's business but hers.

An aliases delivers the [human-friendliness in Zooko's triangle](https://dhh1128.github.io/papers/zh.html), but *only for the person who creates it*. For anyone else, an alias is not a commitment to meaning, let alone uniqueness. An alias can evolve without warning to suit its creator's fancy. It must be treated as a lookup convenience, not as an identifier in its own right, and it must be considered unresolvable outside the creator's context. Parsing someone else's aliases for strong meaning is a dangerous antipattern.

## Focus
Some identifiers naturally map from human-friendly names to their subjects, and therefore don't need aliases: email addresses &rarr; inboxes, social medial handles &rarr; accounts... Other identifiers have more abstract mappings and are hard for humans to remember, write, speak, compare, and search: SSH or PGP keys, bank account numbers, W3C [DIDs](https://www.w3.org/TR/did-1.0/), KERI [AIDs](https://trustoverip.github.io/tswg-keri-specification/#autonomic-identifier-aid), cryptocurrency payment addresses, smart contract addresses, [UUIDs](https://www.rfc-editor.org/rfc/rfc9562.html), passkeys, and so forth. Management tools (e.g., wallets, password managers, config files, X509 issuance or renewal wizards...) typically patch this human friendliness gap by letting users apply a comment or an arbitrary text label. However, they offer no guidance about how to choose the label. Users invent ad hoc conventions or use no conventions at all. They end up with inconsistent data and a mental model that's confusing, unstable, and hard to remember and use.

Opaque identifiers like this can benefit from COIA aliases. Suppose that in a given context, Cecilia is acting as the CEO of her company rather than as a patient at her doctor's office. It is much easier for her to select which DID she needs by looking up `me-as-ceo-at-acme`, not `did:xyz:EMyYnLzlJDJskqojipIMivAKHWeZofhWiYjB79uszynS`.

COIA produces good aliases for identifiers that reference *parties in a variety of  role-based interactions*. We call such parties *actors*: humans, organizations, and relatively autonomous things. If an opaque identifier references something that's *passive and stuck in a single, static role* &mdash; chunks of bytes (hashes), network interfaces (MAC addresses), books (ISBNs), or products (SKUs), for example &mdash; the conventions in this spec make less sense. (However, it may still be useful to use COIA aliases for passive object identifiers, if the objects associate so strongly to actors that identifying one amounts to identifying the other.)

## Terms

An *alias* is a human-friendly label for an opaque identifier that refers to an actor.

An *aliased identifier* is an opaque identifier that's labeled by an alias.

The *subject* of an aliased identifier is the actor identified or referenced by that identifier.

A *reflexive alias* has an aliased identifier that points to the creator of the alias.

## Conventions

### 1. Choose a template

Using the language preferences of the user, choose a template that builds the alias from substitutable variables. Recommended templates in various languages are given in [Appendix A](#appendix-a-templates-and-translations). For reference in our explanation, the English template is: `{flags}{who} as {role}{scope}`. The `{scope}` substitution variable is a prepositional phrase builder that is also defined in the appendix (" at {org}" in English).

### 2. Answer three questions
Three questions must be answered to generate a COIA alias for an identifier:

1. **who** — Which subject is referenced by the identifier? This is enough of a name to be meaningful in the user's context &mdash; perhaps a full name, or perhaps just a first name.
2. **role** — What responsibility, posture, or behavior pattern distinguishes this facet of the subject's identity from other facets? This is often a job title like "Board Member" or "Director of Marketing".
3. **scope** — In what context are the previous two properties relevant?

Many other questions could be asked, but these three are far and away the most helpful for discriminating among [multifaceted identities](https://dhh1128.github.io/papers/if.html). Answering them well maximizes cybersecurity benefits, privacy options, and searchability.

A crucial insight of COIA is that software often knows the answers to all three of these questions when it helps its user create an identifier, or when it presents its user with an identifier created elsewhere. And what it doesn't know, a user probably does.

* If Cecilia accepts an employee credential, she may want an alias for the identifier that points to herself as the holder of the credential. For all reflexive aliases like this, `who` is <var>me</var>. The answer to `role` is Cecilia's job title, and since such credentials will be presented to arbitrary verifiers, `scope` is any counterparty.

* If Cecilia meets a gamer named Bob in the AlienWrldz game universe, and Bob later sends her his PGP key, she may want an alias for it. For such an alias, `who` is "Bob", `role` might be "noob gamer", and `scope` is "AlienWrldz".

* If Cecilia wants to alias the public key that Beta Corp publishes on its public web site, `who` is "Beta Corp", `role` might be "domain owner", and `scope` is the general digital landscape in all its incarnations. We represent such a default scope with the empty string.

### 3. Convert scope to a phrase

If scope is not the empty string, convert it to a phrase like "at Acme" using the appropriate scope string and localized template.

### 4. Choose flags

Flags are things that are known about an alias, that should be signaled consistently to the user. Each flag is a single character; multiple flags are possible and should be combined such that the flags sort left-to-right in byte order. The following flags have predefined meaning:

flag | meaning
--- | ---
? | The subject of the identifier has not been proved in a way that eliminates MITM risk (e.g., interactive challenge-response with a backchannel; requesting high-assurance identity credentials). Any theory about the actor behind the identifier is therefore suspect. (Users never face MITM risk with reflexive aliases, but aliases that refer to remote parties always carry this flag until it is explicitly removed.)
\# | The aliased identifier is associated with an experimental/test/demo environment having no real-world consequences to reputation, governance, or cost. It must not be used if consequential production side effects are intended.
. | The aliased identifier is intended to be used in private (e.g., pairwise) contexts only; it should never be shared.

### 5. Expand the template

Substitute values into string.

### 6. Append a number if desired

If Alice already has an alias `bob-as-ceo-at-beta-corp`, and is creating a second alias that results in the same template expansion, one or more digits can be added to keep the alias unique (similar to how repeated downloads of a file yield `file.txt`, `file.txt (1)`, `file.txt (2)`, etc. -- except that no parens are used.) 

### 6. Normalize

Convert the string to lower case. Convert to Unicode NFKC form. Delete punctuation characters. Replace all spaces with the hyphen character.

### 7. Comparing

Although the canonical form of an alias is lower-case and contains no spaces or punctuation other than a hyphen, users that attempt to look up an alias by typing or pasting text containing capital letters, punctuation, or spaces should have their query matched as if it has undergone alias normalization.

## Examples

alias | notes
--- | ---
`me-as-ceo-at-acme` | Reflexive identifier used by Cecilia when she's signing a loan on behalf of the company. No flags.
`?cecilia-as-ceo-at-acme ` | A reasonable alias for the same identifier as previous, but created by the bank giving Acme a loan. Note the ? flag &mdash; the company should not accept this signature until it is has proved rather than assumed Cecilia's identity -- at which point, it should remove the flag.
`#?bob-as-payee-at-bitcoin` | An alias for a bitcoin address or DID &mdash; but one on testnet, not valid as a target of real payments. Bob's real-world identity is unproven, so there could be a man in the middle -- but it may not matter given the test context. 
`fred-perkins-as-business-exec` | A verified alias for Fred Perkins as he uses it with his general public reputation (e.g., on social media).
`.fred-as-business-partners-at-acme` | A verified but private alias for Fred Perkins, held by his co-founder for use in business rather than personal contexts.
`acme-as-manufacturer-at-supply-chain` | An alias used by stakeholders in a supply chain, to reference Acme's proven identity in supply chain interactions.
acme-as-domain-owner | An alias 


## Appendix A: Templates and Translations
Pull requests gladly accepted to improve language coverage.

| ISO 639-2 | Template translation | Notes |
|-----------|----------------------|-------|
| ara | `{flags}{who}` بصفته `{role}{scope}` | Arabic is RTL; role before context; sorting of `{flags}` may require testing. |
| chi | `{flags}{who}` 身为`{role}{scope}` | Chinese SVO; role before context; idiomatic placement with 身为. |
| eng | `{flags}{who}` as `{role}{scope}` | Standard English; role before context. |
| fra | `{flags}{who}` en tant que `{role}{scope}` | French: role before organization; gender forms may apply. |
| ger | `{flags}{who}` als `{role}{scope}` | German: role before organization; “bei” for context. |
| heb | `{flags}{who}` בתפקיד `{role}{scope}` | Hebrew RTL; role precedes context. |
| ita | `{flags}{who}` come `{role}{scope}` | Italian: role before organization. |
| jpn | `{flags}{who}` として`{role}{scope}` | Japanese: role before context particle; natural order. |
| kor | `{flags}{who}` `{role}`로서`{scope}` | Korean: role before context particle. |
| por | `{flags}{who}` como `{role}{scope}` | Portuguese: role before organization; article contraction applies. |
| rus | `{flags}{who}` в роли `{role}{scope}` | Russian: role before context; case agreement may apply. |
| spa | `{flags}{who}` como `{role}{scope}` | Spanish: role before organization; gender agreement may apply. |

| ISO 639-2 | scope template | Example expansion |
|-----------|--------------------|-----------------|
| ara | في `{org}` | في Acme |
| chi | 在`{org}` | 在Acme |
| eng | at `{org}` | at Acme |
| fra | chez `{org}` | chez Acme |
| ger | bei `{org}` | bei Acme |
| heb | ב`{org}` | בAcme |
| ita | presso `{org}` | presso Acme |
| jpn | （`{org}`で） | （Acmeで） |
| kor | `{org}`에서 | Acme에서 |
| por | na/ no `{org}` | na Acme / no Acme |
| rus | в `{org}` | в Acme |
| spa | en `{org}` | en Acme |

| ISO 639-2 | Example expansion | Notes |
|-----------|------------------|-------|
| ara | ?Alice بصفته CEO في Acme | Arabic RTL; role precedes context prepositional phrase. |
| chi | ?Alice 身为CEO在Acme | Chinese SVO; role before context particle; natural ordering with 身为…在. |
| eng | ?Alice as CEO at Acme | Standard English SVO order. |
| fra | ?Alice en tant que CEO chez Acme | French: role before “chez {org}”; gender-aware for roles if needed. |
| ger | ?Alice als CEO bei Acme | German: role before context; “bei” is natural. |
| heb | ?Alice בתפקיד CEO בAcme | Hebrew RTL; role precedes context prepositional phrase. |
| ita | ?Alice come CEO presso Acme | Italian: role before context; “presso” idiomatic. |
| jpn | ?Alice CEO（Acmeで）として | Japanese: context particle attached to org; role before particle; idiomatic. |
| kor | ?Alice CEO로서 Acme에서 | Korean: role before particle; context particle “에서” placed naturally. |
| por | ?Alice como CEO na Acme | Portuguese: role before context; article contraction applied if necessary. |
| rus | ?Alice в роли CEO в Acme | Russian: role before context preposition; case agreement may apply. |
| spa | ?Alice como CEO en Acme | Spanish: role before context preposition; gender agreement applies. |
