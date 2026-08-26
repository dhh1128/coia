import Foundation

let SEP = "\u{1}"
let ME_MARK = "\u{0}ME"
var fails: [(String, String, String, String)] = []

func rec(_ sec: String, _ label: String, _ got: String, _ want: String) {
    if got != want { fails.append((sec, label, got, want)) }
}

func split6(_ a: String) -> [String] {
    var p = a.components(separatedBy: SEP)
    if p[1] == ME_MARK { p[1] = Coia.ME }
    return p
}

for v in VECTORS {
    let (sec, label, a, b, c) = (v[0], v[1], v[2], v[3], v[4])
    switch sec {
    case "normalize":
        rec(sec, label, Coia.normalize(a), b)
    case "generate":
        let p = split6(a)
        var got: String
        do { got = try Coia.createAlias(p[0], p[1], p[2], p[3], p[4], p[5]) }
        catch let e as Coia.CoiaError { got = "<\(e.message)>" }
        catch { got = "<error>" }
        rec(sec, label, got, b)
    case "reject":
        let p = split6(a)
        if let got = try? Coia.createAlias(p[0], p[1], p[2], p[3], p[4], p[5]) {
            rec(sec, label, "produced \(got)", "<rejected>")
        }
    case "parse":
        var got: String
        do { got = try Coia.parseAlias(a).joined(separator: SEP) }
        catch let e as Coia.CoiaError { got = "<\(e.message)>" }
        catch { got = "<error>" }
        rec(sec, label, got, b)
    case "match":
        rec(sec, label, String(Coia.matches(b, a)), c)
    case "search":
        let corpus = a.components(separatedBy: SEP)
        rec(sec, label, Coia.search(b, corpus).joined(separator: SEP), c)
    default:
        break
    }
}

print("\(VECTORS.count - fails.count)/\(VECTORS.count) vectors pass\n")
for (sec, label, got, want) in fails {
    print("  FAIL [\(sec)] \(label)")
    print("        got  \(got.debugDescription)")
    print("        want \(want.debugDescription)")
}
if !fails.isEmpty { exit(1) }
