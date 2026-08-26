"""Every locked decision, and every verified defect from the adversarial review."""
import coia
from coia import create_alias as mk, normalize as N, ME

FAILED = []
def check(label, got, want):
    ok = got == want
    if not ok: FAILED.append((label, got, want))
    print(f"  {'ok  ' if ok else 'FAIL'} {label:44} {got!r}" + ("" if ok else f"  want {want!r}"))

def raises(label, fn):
    try:
        fn(); FAILED.append((label,"no error","error")); print(f"  FAIL {label:44} no error raised")
    except ValueError as e:
        print(f"  ok   {label:44} rejected: {str(e)[:40]}")

print("\n--- D-A idempotence and post-conditions ---")
check("emoji who leaves no leading hyphen", mk('en','🙂 Bob','ceo'), 'bob-ceo')
check("normalize is idempotent", N(mk('en','🙂 Bob','ceo')), mk('en','🙂 Bob','ceo'))
check("dead-key artifact leaves no trailing hyphen", mk('en','Bob','ceo','Acme´'), 'bob-ceo-acme')

print("\n--- D-B split vs elide ---")
check("tab splits, does not join", mk('en','Beta\tCorp','vendor'), 'beta-corp-vendor')
check("space splits", mk('en','Beta Corp','vendor'), 'beta-corp-vendor')
check("ideographic comma splits", N('東京、大阪'), '東京-大阪')
check("ideographic period splits", N('東京。大阪'), '東京-大阪')
check("fraction slash splits", N('Version ½'), 'version-1-2')
check("minus sign splits", N('a−b'), 'a-b')

print("\n--- D-B marks preserved ---")
check("Khmer intact", N('ព្រះរាជាណាចក្រកម្ពុជា'), 'ព្រះរាជាណាចក្រកម្ពុជា')
check("Dhivehi intact", N('ބިޒްނަސް'), 'ބިޒްނަސް')
check("Burmese intact", N('ကုမ္ပဏီ'), 'ကုမ္ပဏီ')
check("Yoruba tone marks intact", N('Ọbáfẹ́mi'), 'ọbáfẹ́mi')
check("Yoruba minimal pairs stay distinct", N('ọkọ́') != N('ọkọ̀'), True)
check("Portuguese accents intact", N('João Conceição'), 'joão-conceição')

print("\n--- D-C case folding ---")
check("Greek final sigma folds", N('ΟΔΟΣ'), N('οδος'))
check("German sharp s folds", N('Straße'), N('STRASSE'))

print("\n--- Lm and joiners ---")
check("katakana prolonged sound mark kept", N('サプライチェーン'), 'サプライチェーン')
check("ideographic iteration mark kept", N('人々'), '人々')
check("okina kept", N('Hawaiʻi'), 'hawaiʻi')
check("U+02BC folds to okina", N('Oʼzbekiston'), N('Oʻzbekiston'))
check("tatweel elided", N('مـــرحبا'), N('مرحبا'))
check("Sinhala ZWJ kept", N('ශ්‍රී ලංකා'), 'ශ්‍රී-ලංකා')
check("Persian ZWNJ kept", N('می‌روم'), 'می‌روم')
check("bare ZWJ elided (spoof)", N('bo‍b'), 'bob')
check("emoji ZWJ sequence elided", N('👨‍👩'), '')

print("\n--- D-F substitution ---")
check("brace in who is literal", mk('en','{role}','ceo','Acme'), 'role-ceo-acme')
check("dollar-ampersand not a replacement pattern", mk('en',"A$&B",'ceo','Acme'), 'a-b-ceo-acme')
check("dollar-quote is literal", mk('en',"A$'B",'ceo','Acme'), 'a-b-ceo-acme')

print("\n--- D-J error behaviour ---")
raises("role='.' rejected on normalized value", lambda: mk('en','Bob','.'))
raises("empty role rejected", lambda: mk('en','Bob',''))
raises("NBSP-only role rejected", lambda: mk('en','Bob',' '))
raises("unsupported language rejected", lambda: mk('xx','Bob','ceo'))
raises("reserved digit 3 rejected", lambda: mk('en','Bob','ceo',flags='3'))
raises("reflexive with flag 0 rejected", lambda: mk('en',ME,'ceo',flags='0'))
raises("empty who rejected (ME sentinel required)", lambda: mk('en','','ceo'))

print("\n--- flag syntax ---")
check("descending sort", mk('en','Bob','ceo',flags='69'), 'bob-ceo,96')
check("duplicates collapse", mk('en','Bob','ceo',flags='000'), 'bob-ceo,0')
check("private group", mk('en','Bob','ceo',flags='9',private_flags='37'), 'bob-ceo,9,73')
check("private only uses empty group 1", mk('en','Bob','ceo',private_flags='7'), 'bob-ceo,,7')
check("Arabic-Indic digit folds to ASCII", mk('en','Bob','ceo',flags='٩'), 'bob-ceo,9')
check("leading-digit name is unambiguous", mk('en','Plan 9','vendor',flags='9'), 'plan-9-vendor,9')
check("parse round-trips", coia.parse_alias('bob-ceo,96,73'), ('bob-ceo','96','73'))
check("parse accepts Arabic comma", coia.parse_alias('bob-as-ceo،9'), ('bob-as-ceo','9',''))

print("\n--- matching ---")
stored = mk('en','Cecilia','CEO','Acme',flags='0')
check("stored form", stored, 'cecilia-ceo-acme,0')
for q in ['Cecilia','Acme','Acme CEO','ceci','cecilia acme']:
    check(f"query {q!r} hits", coia.matches(q, stored), True)
check("negative control misses", coia.matches('Bob', stored), False)
# A.0 removed the connectors, so they are no longer terms in the alias and a query
# that spells them out now misses. Every query term must be present (§7).
for q in ['CEO at Acme', 'Cecilia as CEO at Acme']:
    check(f"connector-bearing query {q!r} now MISSES", coia.matches(q, stored), False)
ja = mk('ja','トヨタ','購買者','サプライチェーン')
check("ja query by company name hits", coia.matches('トヨタ', ja), True)
check("ja hyphen substituted for ー hits", coia.matches('サプライチェ-ン', ja), True)

print("\n--- ordering ---")
corpus = ['cecilia-ceo-acme','acme-vendor','carol-notary-acmeville','dmitri-cfo-acme']
check("ordered by structural relevance", coia.search('acme', corpus),
      ['acme-vendor','dmitri-cfo-acme','cecilia-ceo-acme','carol-notary-acmeville'])
# dmitri precedes cecilia: equal whole-segment matches, and the ranking's second key
# is the earliest match index (11 vs 12), not alias length or alphabetical order.

print("\n--- localization ---")
check("Korean, no particle", mk('ko','김철수','사장','삼성'), '김철수-사장-삼성')
check("Korean, vowel-final role is no longer a special case",
      mk('ko','김철수','의사','삼성'), '김철수-의사-삼성')
check("German, no connector", mk('de','Hans','Direktor','Deutsche Bank'), 'hans-direktor-deutsche-bank')
check("Russian, no connector", mk('ru','Иван','директор','Газпром'), 'иван-директор-газпром')
check("Italian reflexive io", mk('it',ME,'amministratore','Acme'), 'io-amministratore-acme')
check("Arabic, no capacity marker", mk('ar','علي','شريك'), 'علي-شريك')

# A.0/A.1: language selects the pronoun and nothing else.
nonreflexive = {coia.create_alias(l,'Cecilia','CEO','Acme') for l in coia.LANGUAGES}
check("language does not affect a non-reflexive alias", len(nonreflexive), 1)
reflexive = {coia.create_alias(l,ME,'CEO','Acme') for l in coia.LANGUAGES}
check("language selects a distinct pronoun for every reflexive alias",
      len(reflexive), len(coia.LANGUAGES))

print("\n" + "="*70)
print(f"{len(FAILED)} failure(s)" if FAILED else "ALL PASS")
for l,g,w in FAILED: print(f"   {l}: got {g!r} want {w!r}")
