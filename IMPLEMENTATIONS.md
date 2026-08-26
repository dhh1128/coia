# Implementations

Six, all held to the same normative vectors (Appendix C).

    ./conformance.sh          run the 132 vectors against all six
    python3 difftest.py N     feed N generated inputs to all six, compare byte-for-byte

| language | location | NFKC from | notes |
|---|---|---|---|
| Python | `coia.py` | `unicodedata` | folds with `str.casefold()`, which is definitionally Default Case Folding; serves as the check on the generated table |
| JavaScript | `impl/js/` | `String.normalize` | ESM |
| Go | `impl/go/` | `golang.org/x/text/unicode/norm` | the only dependency; stdlib has no NFKC |
| Java | `impl/java/` | `java.text.Normalizer` | no external dependency |
| Rust | `impl/rust/` | `unicode-normalization` | plus `unicode-properties`; std has neither NFKC nor General_Category |
| Swift | `impl/swift/` | `Foundation` | `precomposedStringWithCompatibilityMapping` |

## Generated files

`gentables.py` builds `tables.json` from the rules in §5. `gencode.py` emits the tables,
the case-folding table and the vectors as source for each language, so no implementation
needs a JSON parser. Regenerate rather than hand-edit anything named `data.*` or `Data.*`.

## Why the differential test exists

Vectors are fixed and were written by someone who already knew what the answers should be.
The differential test feeds the same generated inputs to all six and compares byte-for-byte;
it found a divergence at 3,000 inputs that 132 vectors and 300 differential inputs both
missed — Go's `strings.ToLower` applies simple case mapping, so `İ` folded to `i` there and
to `i` + U+0307 everywhere else. That is what moved case folding from "lowercase, then patch
the differences" to a complete normative table.

Current status: 132/132 vectors in all six, and 25,000 differential inputs with no divergence.

## Known gaps

- `coia.rs` in the repository root is the COIA 1.x implementation and **cannot run** —
  the Rust `regex` crate rejects `\p{Cs}`, which its committed pattern contains. The v2
  Rust implementation here is a rewrite, not a port.
- Language templates other than English are provisional pending native review; see
  Appendix A.
