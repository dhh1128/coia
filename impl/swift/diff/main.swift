import Foundation

let data = try! String(contentsOfFile: "difftest-input.txt", encoding: .utf8)
for line in data.split(separator: "\n", omittingEmptySubsequences: true) {
    var s = String.UnicodeScalarView()
    for h in line.split(separator: " ") {
        if let v = UInt32(h, radix: 16), let u = Unicode.Scalar(v) { s.append(u) }
    }
    let r = Coia.normalize(String(s))
    print(r.unicodeScalars.map { String(format: "%X", $0.value) }.joined(separator: " "))
}
