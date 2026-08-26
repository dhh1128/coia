import sys, coia
enc = lambda s: " ".join(f"{ord(c):X}" for c in s)
dec = lambda l: "".join(chr(int(x, 16)) for x in l.split()) if l.strip() else ""
for line in open("difftest-input.txt").read().split("\n"):
    if line == "":
        continue
    print(enc(coia.normalize(dec(line))))
