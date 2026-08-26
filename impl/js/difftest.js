import {readFileSync} from "fs";
import {normalize} from "./coia.js";
const enc = s => [...s].map(c => c.codePointAt(0).toString(16).toUpperCase()).join(" ");
const dec = l => l.trim() === "" ? "" : l.trim().split(/ +/).map(x => String.fromCodePoint(parseInt(x,16))).join("");
const lines = readFileSync("difftest-input.txt","utf8").split("\n");
for (const l of lines) { if (l === "") continue; console.log(enc(normalize(dec(l)))); }
