"""Differential test: same inputs through all six implementations, compared
byte-for-byte. The vectors are fixed; this covers inputs nobody chose.

Interchange is one input per line, as space-separated hex codepoints, so no
implementation needs a JSON parser. Output is the same format.
"""
import os, random, subprocess, sys, unicodedata as ud

random.seed(20260824)

POOL = []
for lo, hi in [(0x20,0x7E),(0xA0,0x2FF),(0x370,0x5FF),(0x600,0x6FF),(0x900,0x9FF),
               (0xE00,0xE7F),(0x1780,0x17FF),(0x3040,0x30FF),(0x4E00,0x4E80),
               (0xAC00,0xACFF),(0x2000,0x206F),(0x2190,0x21FF),(0xFF00,0xFF60),
               (0x1F600,0x1F64F),(0x10400,0x1044F)]:
    POOL += [cp for cp in range(lo, hi+1) if ud.category(chr(cp)) not in ('Cn','Cs')]
POOL += [0x200C,0x200D,0x0640,0x02BC,0x02BB,0x0E33,0x2044,0x3001,0x3002,0x060C,
         0x00DF,0x03C2,0x0DCA,0x094D,0x30FC,0x20E3,0x0345]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
cases = ["".join(chr(random.choice(POOL)) for _ in range(random.randint(1,12)))
         for _ in range(N)]
enc = lambda s: " ".join(f"{ord(c):X}" for c in s)
dec = lambda l: "".join(chr(int(x,16)) for x in l.split()) if l.strip() else ""
open("difftest-input.txt","w").write("\n".join(enc(c) for c in cases) + "\n")

PYBIN = os.environ.get("PYBIN", "python3")
JDK = os.path.expanduser("~/opt/jdk-21.0.12+8/bin")
env = dict(os.environ, PATH=f"{JDK}:{os.environ['PATH']}")

RUNNERS = [
 ("python", ".",           [PYBIN, "difftest_run.py"]),
 ("node",   "impl/js",     ["node", "difftest.mjs"]),
 ("go",     "impl/go",     ["go", "run", "./diffcmd"]),
 ("java",   "impl/java",   ["java", "-cp", ".", "DiffTest"]),
 ("rust",   "impl/rust",   ["cargo", "run", "-q", "--bin", "difftest"]),
 ("swift",  "impl/swift",  ["./diff/difftest"]),
]

out = {}
for name, cwd, cmd in RUNNERS:
    if cwd != ".":
        open(os.path.join(cwd, "difftest-input.txt"), "w").write(
            "\n".join(enc(c) for c in cases) + "\n")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"{name}: FAILED TO RUN\n{r.stderr[:400]}")
        sys.exit(1)
    lines = r.stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()                      # trailing newline only; interior blanks are
    out[name] = [dec(l) for l in lines]  # real results (normalization can be empty)
    if len(out[name]) != len(cases):
        print(f"{name}: produced {len(out[name])} lines, expected {len(cases)}")
        sys.exit(1)

names = list(out)
bad = 0
for i, s in enumerate(cases):
    vals = {n: out[n][i] for n in names}
    if len(set(vals.values())) > 1:
        bad += 1
        if bad <= 6:
            print(f"DIVERGENCE on input {s!r}  ({enc(s)})")
            for n, v in vals.items():
                print(f"   {n:8} {v!r}")
print(f"\n{len(cases)} inputs x {len(names)} implementations: {', '.join(names)}")
print("ALL AGREE" if bad == 0 else f"{bad} DIVERGENCES")
sys.exit(1 if bad else 0)
