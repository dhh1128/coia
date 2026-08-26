import { VECTORS } from "./data.js";
import * as coia from "./coia.js";

const SEP = "\u0001", MEMARK = "\u0000ME";
const fails = [];
const rec = (sec, label, got, want) => {
  if (JSON.stringify(got) !== JSON.stringify(want)) fails.push([sec, label, got, want]);
};
const mkArgs = a => {
  const [lang, who, role, scope, flags, priv] = a.split(SEP);
  return [lang, who === MEMARK ? coia.ME : who, role, scope, flags, priv];
};

for (const [sec, label, a, b, c] of VECTORS) {
  try {
    if (sec === "normalize") rec(sec, label, coia.normalize(a), b);
    else if (sec === "generate") rec(sec, label, coia.createAlias(...mkArgs(a)), b);
    else if (sec === "reject") {
      let got = null;
      try { got = "produced " + coia.createAlias(...mkArgs(a)); } catch (e) { /* expected */ }
      if (got !== null) rec(sec, label, got, "<rejected>");
    }
    else if (sec === "parse") rec(sec, label, coia.parseAlias(a), b.split(SEP));
    else if (sec === "match") rec(sec, label, String(coia.matches(b, a)), c);
    else if (sec === "search") rec(sec, label, coia.search(b, a.split(SEP)), c ? c.split(SEP) : []);
  } catch (e) {
    rec(sec, label, "<" + e.message + ">", b);
  }
}
console.log(`${VECTORS.length - fails.length}/${VECTORS.length} vectors pass\n`);
for (const [sec, label, got, want] of fails)
  console.log(`  FAIL [${sec}] ${label}\n        got  ${JSON.stringify(got)}\n        want ${JSON.stringify(want)}`);
process.exit(fails.length ? 1 : 0);
