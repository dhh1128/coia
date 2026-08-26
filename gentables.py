"""Generate COIA v2 normative character tables from the locked rules."""
import unicodedata as ud, regex, json

def ranges(cps):
    cps = sorted(cps); out=[]; a=p=cps[0]
    for cp in cps[1:]:
        if cp == p+1: p = cp; continue
        out.append((a,p)); a=p=cp
    out.append((a,p)); return out

def fmt(rs):
    return [f"{a:04X}" if a==b else f"{a:04X}-{b:04X}" for a,b in rs]

# SPLIT: characters that become word separators.
SPLIT = set()
for cp in range(0x110000):
    c = chr(cp)
    if regex.match(r'\p{Dash}|\p{Quotation_Mark}|\p{White_Space}', c):
        SPLIT.add(cp)
SPLIT |= {ord(c) for c in "&.,'"}
SPLIT |= {0x2044,   # FRACTION SLASH  (Version ½ -> version-1-2, not version-12)
          0x3001,   # IDEOGRAPHIC COMMA
          0x3002,   # IDEOGRAPHIC FULL STOP
          0x060C,   # ARABIC COMMA
          0x061B,   # ARABIC SEMICOLON
          0x06D4,   # ARABIC FULL STOP
          0x0964, 0x0965,  # DEVANAGARI DANDA, DOUBLE DANDA
          0x104A, 0x104B,  # MYANMAR SIGN LITTLE SECTION, SECTION
          0x17D4, 0x17D5,  # KHMER SIGN KHAN, BARIYOOSAN
          0x1362,          # ETHIOPIC FULL STOP
          0x0E5A, 0x0E5B}  # THAI ANGKHANKHU, KHOMUT

# VIRAMA: ccc == 9. Used by the ZWJ/ZWNJ context rules.
VIRAMA = {cp for cp in range(0x110000) if ud.combining(chr(cp)) == 9}

# ARABIC-SCRIPT blocks, for the ZWNJ context rule.
ARABIC = [(0x0600,0x06FF),(0x0750,0x077F),(0x0870,0x089F),(0x08A0,0x08FF)]

tables = {
  "split":  fmt(ranges(SPLIT)),
  "virama": fmt(ranges(VIRAMA)),
  "arabic": [f"{a:04X}-{b:04X}" for a,b in ARABIC],
  "elide_lm": ["0640"],                    # ARABIC TATWEEL
  "fold": {"02BC": "02BB"},                # MODIFIER APOSTROPHE -> OKINA
}
json.dump(tables, open("tables.json","w"), indent=1)
for k in ("split","virama","arabic"):
    n = sum(1 for r in tables[k] for _ in range(1))
    total = sum((int(r.split('-')[1],16)-int(r.split('-')[0],16)+1) if '-' in r else 1
                for r in tables[k])
    print(f"{k:8} {total:>6} codepoints in {len(tables[k]):>3} ranges")
