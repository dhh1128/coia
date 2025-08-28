# Conventions for Opaque Identifier Aliases (COIA)
## Overview
This spec explains [how to generate](#conventions) consistent, human-friendly aliases (labels) for hard-to-remember identifiers (AIDs, DIDs, public keys...) that refer to actors with complex identities (people, organizations, AI-based agents, and so forth).

COIA aliases look like this:

* cecilia-as-second-violin-at-vienna-symphony
* moi-en-tant-que-directeur-général-chez-l-oréal ("Me as CEO at L'Oréal")
* 0-トヨタサプライチェーンでの購買者として ("unverified: Toyota as purchaser in supply chain")
* 2-علي-بصفته-شريك-تجاري ("pairwise: Ali as business partner")

### Reference implementation
You can use an [interactive form](https://dhh1128.github.io/coia/form.html) to see what aliases are produced by this spec in various situations. You may also want to see or use reference implementations in [python](coia.py) (treat as the oracle), [javascript](coia.js), [java](Coia.java), [rust](coia.rs), [go](coia.go), and [swift](Coia.swift).

### Why?
COIA aliases are a high-ROI UX enhancement for users of digital wallets, password managers, verifiable credentials, cryptographic keys, and similar technologies.

Implementing COIA is easy. Adopting COIA imposes no learning curve. Following COIA will improve clarity, confidence, utility, and safety. Since the conventions help software help its own users, they deliver value as soon as they're adopted in one app, regardless of when they spread throughout an ecosystem.

For more about the theory behind these conventions, see [Opaque Identifier Aliases](https://dhh1128.github.io/papers/oia.html).

### Version
This is version 1 of COIA. If a future spec is released, the version number will change per [semver](https://semver.org) guidelines.

## Goals
COIA aims for aliases that have the following properties:
  
1. Given a handful of examples and no explicit instruction, a user naturally develops accurate intuition about how the conventions work, and about best practices for managing identity.
2. When a user encounters an alias that they created, they immediately and effortlessly remember who is identified by the aliased identifier, and the context in which that identifier is relevant. 
3. Given a context and an identified actor, a user correctly predicts what a relevant alias created by them might look like, allowing them to search with confidence.
4. The alias is a single token that processes correctly, with no special handling, in environments such as email, chat, URLs, word processors, log files, and markup languages. It can also be read aloud with high confidence.

Note that this spec aims to improve UX *for the alias creator*, not to make aliases interoperable with *other* humans, *other* languages, or *other* software. Aliases are like private nicknames; a stranger might overhear one, but they aren't created to be reshared. When Cecilia transacts with Bob on Bitcoin, she doesn't use local aliases to publicly identify her address or Bob's; she uses raw addresses. Therefore, how Cecilia locally labels her address or Bob's address is only interesting to her.

An aliases delivers the [human-friendliness in Zooko's triangle](https://dhh1128.github.io/papers/zh.html), but *only for the person who creates it*. For anyone else, an alias might be suggestive, but it is not a commitment to meaning. An alias can evolve without warning to suit its creator's fancy. It must be treated as a lookup convenience, not as an identifier in its own right, and it must be considered unresolvable outside the creator's context. Parsing someone else's aliases for strong meaning is a dangerous antipattern.

## Focus
Some identifiers naturally map from human-friendly names to their subjects, and therefore don't need aliases: email addresses &rarr; inboxes, social medial handles &rarr; accounts... Other identifiers have more abstract mappings and are hard for humans to remember, write, speak, compare, and search: SSH or PGP keys, bank account numbers, W3C [DIDs](https://www.w3.org/TR/did-1.0/), KERI [AIDs](https://trustoverip.github.io/tswg-keri-specification/#autonomic-identifier-aid), cryptocurrency payment addresses, smart contract addresses, [UUIDs](https://www.rfc-editor.org/rfc/rfc9562.html), passkeys, and so forth. Management tools (e.g., wallets, password managers, config files, X509 issuance or renewal wizards...) typically patch this human friendliness gap by letting users apply a comment or an arbitrary text label. However, they offer no guidance about how to choose the label. Users invent ad hoc conventions or use no conventions at all. They end up with inconsistent data and a mental model that's confusing, unstable, and hard to remember and use.

Opaque identifiers like this can benefit from COIA aliases. Suppose that in a given context, Cecilia is acting as the CEO of her company rather than as a patient at her doctor's office. It is much easier for her to select which DID she needs by looking up `me-as-ceo-at-acme`, not `did:xyz:EMyYnLzlJDJskqojipIMivAKHWeZofhWiYjB79uszynS`.

COIA produces good aliases for identifiers that reference *parties engaging in a variety of role-based interactions*. We call such parties *actors*: humans, organizations, and relatively autonomous things. If an opaque identifier instead references something that's *passive and stuck in a single, static role* &mdash; chunks of bytes (hashes), network interfaces (MAC addresses), books (ISBNs), or products (SKUs), for example &mdash; the conventions in this spec make less sense. (However, it may still be useful to use COIA aliases for passive object identifiers, if the objects associate so strongly to actors that identifying one amounts to identifying the other.)

## Terms

An *alias* is a human-friendly label for an opaque identifier that refers to an actor.

An *aliased identifier* is an opaque identifier that's labeled by an alias.

The *subject* of an aliased identifier is the actor identified or referenced by that identifier.

A *reflexive alias* is associated with an aliased identifier that has a subject who is the creator of the alias: <var>me</var>.

## Conventions
### Creating
#### 1. Choose a template

Using the natural language preferences of the user, choose a [main template](#main-template) from [Appendix A](#appendix-a-localization). For reference in our explanation, the English template is: `{flags}{who} as {role}{scope}`.

#### 2. Answer three questions
Three questions must be answered to generate a COIA alias for an identifier:

1. **who** — Which subject is referenced by the identifier? The value that answers this question should be enough of a name to be meaningful in the user's context &mdash; perhaps a full name, or perhaps just a first name.
2. **role** — What responsibility, posture, or behavior pattern distinguishes this facet of the subject's identity from other facets? This might be a job title like "Board Member" or "Director of Marketing" &mdash; or it might be a role played by an organization, such as "Vendor", "Payee", or "Licensor". If the identifier is used in conjunction with credentials, the type of credential and the role the subject plays vis-a-vis that credential is often the best answer: "Driver" (for holders of driver's licenses), "Citizen" (for holders of passports), "Accredited University" (for issuers of PhDs), etc.
3. **scope** — Which environment, context, or relationship defines the role?

Many other questions could be asked, but these three are far and away the most helpful for discriminating among [multifaceted identities](https://dhh1128.github.io/papers/if.html). Answering them well maximizes cybersecurity benefits, privacy options, and searchability.

A crucial insight of COIA is that software often knows the answers to all three of these questions when it helps its user create an identifier, or when it presents its user with an identifier created elsewhere. And what it doesn't know, a user probably does.

* If Cecilia accepts an employee credential, she may want an alias for the identifier that points to herself as the holder of the credential. For reflexive aliases like this, `who` is the word for "me" in Cecilia's preferred language (see [translations](#appendix-a-templates-and-translations) below). The answer to `role` is Cecilia's job title, and since such a credential is strongly associated with her employer, `scope` is the name of the issuing company.

* If Cecilia meets a gamer named BobRocks in the AlienWrldz game universe, and BobRocks later sends her their PGP key, she may want an alias for it. For such an alias, `who` is "BobRocks", `role` might be "noob gamer", and `scope` is "AlienWrldz".

* If Cecilia wants to alias the public key that Beta Corp publishes on its web site, `who` is "Beta Corp", `role` might be "domain owner", and `scope` is the internet writ large, or the general digital landscape, or just *anywhere*. When scope is vague or uninteresting like this, we use the empty string as a concise default. (We could also say that the appropriate scope for a public domain in DNS is "ICANN", but most users probably won't have such a precise mental model.)

#### 3. Convert scope to a phrase

If `scope` is interesting enough to require a value other than the empty string (meaning, "no particularly constrained context"), transform it to a phrase like "at Acme" using the appropriate localized [scope template](#scope-template).

#### 4. Choose flags

Flags are signals that remind a user about important semantics for the identifier they're aliasing. Each semantic possibility is represented as a single ASCII digit. If no special semantics apply, `flags` becomes an empty string &mdash; the identifier is verified, public, and usable in production. Otherwise, it expands to one or more digits (with the digits in numerical order), followed by a space: `02 `. The following semantic meanings have predefined flag characters:

char | meaning
--- | ---
0 | The subject of the identifier has not (yet) been verified in a way that eliminates MITM risk. Any theory about the actor behind the identifier is therefore suspect. (Users never face MITM risk with reflexive aliases, but aliases that refer to remote parties should always carry this flag as a warning until it is explicitly removed. This can be done by interactive challenge-response confirmed over a trusted backchannel, by requesting high-assurance identity credentials, etc.)
2 | The aliased identifier is intended to be used in pairwise or private contexts only; it should not be shared.
9 | The aliased identifier is associated with an experimental/test/demo environment having no real-world consequences to reputation, governance, or cost. It must not be used where consequential production side effects are intended.

#### 5. Expand the template

Substitute the values for `flags`, `who`, `role`, and `scope` into string.

#### 6. Append a numeric suffix if desired

If Alice already has an alias `bob-as-ceo-at-beta-corp`, and is creating another alias that results in the same template expansion, a suffix consisting of a space followed by ASCII digits can be added to make the new alias unique. (Uniqueness is not a requirement, though, only an option.) This is similar to how browsers deal with repeated downloads of the same filename: `file` &rarr; `file (1)` &rarr; `file (2)`, etc. &mdash; except that no parens are used. 

#### 7. Normalize

1. Convert the string to [Unicode's Normalization Form KC](https://www.unicode.org/reports/tr15/) (NFKC).
2. Convert to lower case.
3. Replace all hyphens, dashes, ampersands, periods, commas, apostrophes, and quotes with spaces.
4. Strip leading and trailing whitespace characters. (Unicode `Z*` character class plus a few orphans, `\p{White_Space}` covers all of them in regex.)
5. Delete all disallowed characters. These are characters that are lossy, ambiguous, or problematic in various processing contexts, including verbal communication. They include control characters, emoji, mathematical symbols, dingbats, and punctuation (other than the characters previously converted to spaces).
6. Replace all remaining sequences of 1 or more whitespace characters with a single ASCII hyphen.

### Comparing

Although the canonical form of an alias is lower-case and contains no spaces or punctuation other than a hyphen, users that attempt to look up an alias by typing or pasting text containing capital letters, punctuation, or spaces should have their query matched as if it has undergone alias normalization.

A regex that matches COIA aliases exactly as described here is:

>^[\p{L}\p{N}]+(-[\p{L}\p{N}]+)*$

A slightly more permissive version that tolerates alternatives to the ASCII hyphen (which a user might type, depending on their natural language and keyboard), is:

>^[\p{L}\p{N}]+([-\u2010\u2011\u2012\u2013\u2212][\p{L}\p{N}]+)*$

## Implementation
See reference code in [python](coia.py).

## Examples

alias | notes
--- | ---
`me-as-ceo-at-acme` | Reflexive identifier used by Cecilia when she's signing a loan on behalf of the company. Reflexive identifiers never have the `0` flag, and this one doesn't have the other flags, either.
`0-cecilia-as-ceo-at-acme ` | A reasonable alias for the same identifier as previous, but created by the bank giving Acme a loan. Note the `0-` flag prefix. The bank should not accept a signature from this identifier until it is has proved rather than assumed Cecilia's identity &mdash; at which point, it should remove the flag.
`09-bob-as-payee-at-bitcoin` | An alias for a bitcoin address or DID &mdash; but one on a testnet or similar, not valid as a target of real payments. Bob's real-world identity is unproven, so there could be a man in the middle &mdash; but it may not matter given the test context.
`fred-perkins-as-business-exec` | A verified alias for Fred Perkins as he uses it with his general public reputation (e.g., on LinkedIn or other social media).
`2-fred-as-cofounder` | A verified alias that associates with Fred Perkins, created by his co-founder for use in business rather than personal contexts. The `2` flag tells us that this identifier is a private, pairwise one between Fred and his co-founder, not the same identifier that Fred uses in public business contexts.
`acme-as-manufacturer-at-supply-chain` | An alias used by stakeholders in a supply chain, to reference Acme's proven identity in supply chain interactions
`joão-silva-como-diretor-financeiro-na-caixa-geral-de-depósitos` | A verified alias for João as CFO at a Portuguese bank.
`9-腾讯-作为-供应商-向-工信部` | demo alias for Tencent as supplier to Ministry of Industry and Information Technology
`02-juan-como-gerente-financiero-en-bbva` | unverified pairwise alias for Juan as financial manager at BBVA 
`0-иван-петров-kak-glavnyj-buhgalter-v-gazprom` | unverified alias for Ivan Petrov as chief accountant at Gazprom
`佐藤-として-経理担当者-に-三菱東京UFJ銀行` | verified alias for Sato as Accounting Officer at Mitsubishi Tokyo UFJ Bank
`أنا-بصفتي-محاسب`| "me as accountant" &mdash; perhaps used with a general career profile on places such as LinkedIn
`02-阿里巴巴-作为-支付方-向-人民银行` | AliBaba as payee to People's Bank of China. A pairwise alias held by the bank, not yet verified.
`나-회사에서-재무담당자-로-삼성전자` | me as finance officer at Samsung
`ich-als-vertriebsleiter-bei-münchener-rück` | me as Sales Manager at Münchener Rück
`09-דוד-כמנהל-כספים-בבנק-הפועלים` | unverified test alias for David as Finance Manager at Bank Hapoalim



## Appendix A: Localization
The following translations are recommended. Pull requests are gladly accepted to improve language coverage.

### Main template
Used in [Step 1](#1-choose-a-template).

| Lang | Template translation | Notes |
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

### Scope template
Used in [Step 3](#3-convert-scope-to-a-phrase).

| Lang | Template | Example expansion |
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

### Pronoun translations
Used if `who` is <var>me</var> [Step 2](#2-answer-three-questions).

| Lang | Translation of "me" | Notes |
|-----------|-------------------|-------|
| ara | أنا | Standard first-person singular pronoun; works naturally in “أنا بصفتي &lt;role&gt;\{scope\}”. |
| chi | 我 | Standard first-person pronoun; works for “我身为&lt;role&gt;\{scope\}”. |
| eng | me | Standard English; “me as &lt;role&gt; at &lt;org&gt;”. |
| fra | moi | Stressed pronoun; idiomatic for “moi en tant que &lt;role&gt;\{scope\}”. |
| ger | ich | “Ich als &lt;role&gt;\{scope\}”; nominative first person. |
| heb | אני | Standard first-person singular; “אני בתפקיד &lt;role&gt;\{scope\}”. |
| ita | me stesso / io | “me stesso” works in reflexive/idiomatic sense if needed; “io” is nominative. |
| jpn | 私 (わたし) | Standard first-person pronoun; polite/formal. |
| kor | 나 | Standard first-person pronoun; “나 &lt;role&gt;\{scope\}로서”. |
| por | eu | Standard first-person; “eu como &lt;role&gt;\{scope\}”. |
| rus | я | Standard nominative; “я в роли &lt;role&gt;\{scope\}”. |
| spa | yo | Standard first-person; “yo como &lt;role&gt;\{scope\}”. |
