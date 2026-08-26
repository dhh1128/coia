#!/usr/bin/env bash
# Run the normative vectors against every implementation.
set -u
cd "$(dirname "$0")"
PY=${PY:-python3}
export PATH="$HOME/opt/jdk-21.0.12+8/bin:$PATH"
rc=0
run() {
  printf "%-10s " "$1"
  out=$(cd "$2" && eval "$3" 2>&1)
  if [ $? -eq 0 ]; then echo "$out" | head -1
  else echo "FAIL"; echo "$out" | head -20; rc=1; fi
}
run python .    "$PY run_vectors.py"
run javascript  impl/js    "node run_vectors.mjs"
run go          impl/go    "go run ./cmd"
run java        impl/java  "javac -encoding UTF-8 -d . Coia.java Data.java RunVectors.java && java -cp . RunVectors"
run rust        impl/rust  "cargo run -q --bin coia"
run swift       impl/swift "swiftc -o runvectors Coia.swift Data.swift main.swift && ./runvectors"
exit $rc
