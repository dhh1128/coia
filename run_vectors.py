"""Run the normative vectors against the reference implementation."""
import json, sys
import coia

V = json.load(open("vectors.json"))
fails = []

def rec(section, label, got, want):
    if got != want:
        fails.append((section, label, got, want))

for label, src, want in V["normalize"]:
    rec("normalize", label, coia.normalize(src), want)

for label, args, want in V["generate"]:
    lang, who, role, scope, flags, priv = args
    who = coia.ME if who is None else who
    try:
        got = coia.create_alias(lang, who, role, scope, flags, priv)
    except Exception as e:
        got = f"<{type(e).__name__}: {e}>"
    rec("generate", label, got, want)

for label, args in V["reject"]:
    lang, who, role, scope, flags, priv = args
    who = coia.ME if who is None else who
    try:
        got = coia.create_alias(lang, who, role, scope, flags, priv)
        rec("reject", label, f"produced {got!r}", "<rejected>")
    except ValueError:
        pass
    except Exception as e:
        rec("reject", label, f"wrong exception {type(e).__name__}", "ValueError")

for label, src, want in V["parse"]:
    try:
        got = list(coia.parse_alias(src))
    except Exception as e:
        got = f"<{type(e).__name__}: {e}>"
    rec("parse", label, got, want)

for label, alias, query, want in V["match"]:
    try:
        got = coia.matches(query, alias)
    except Exception as e:
        got = f"<{type(e).__name__}: {e}>"
    rec("match", label, got, want)

for label, corpus, query, want in V["search"]:
    try:
        got = coia.search(query, corpus)
    except Exception as e:
        got = f"<{type(e).__name__}: {e}>"
    rec("search", label, got, want)

total = sum(len(V[k]) for k in V if not k.startswith("_"))
print(f"{total - len(fails)}/{total} vectors pass\n")
for section, label, got, want in fails:
    print(f"  FAIL [{section}] {label}")
    print(f"        got  {got!r}")
    print(f"        want {want!r}")
sys.exit(1 if fails else 0)
