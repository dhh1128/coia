// COIA v2 reference implementation (Swift).
// Tables and vectors are generated; see ../../gencode.py.
import Foundation

enum Coia {
    static let TATWEEL: UInt32 = 0x0640
    static let ZWJ: UInt32 = 0x200D
    static let ZWNJ: UInt32 = 0x200C

    /// The reflexive sentinel, distinct from the empty string (§4.1).
    static let ME = "\u{0}COIA-ME"

    static func inRanges(_ cp: UInt32, _ rs: [(UInt32, UInt32)]) -> Bool {
        rs.contains { cp >= $0.0 && cp <= $0.1 }
    }

    // Default Case Folding from the normative table (Appendix B.6). Deliberately does
    // NOT use lowercased(): case mapping and case folding are different operations.
    static func casefold(_ s: String) -> String {
        var out = ""
        for u in s.unicodeScalars {
            if let f = FOLDGAP[u.value] { out += f } else { out.unicodeScalars.append(u) }
        }
        return out
    }

    static func joinerOk(_ cps: [Unicode.Scalar], _ i: Int) -> Bool {
        let cp = cps[i].value
        if cp == ZWJ { return i > 0 && inRanges(cps[i - 1].value, VIRAMA) }
        if cp == ZWNJ {
            if i > 0 && inRanges(cps[i - 1].value, VIRAMA) { return true }
            return i > 0 && i + 1 < cps.count
                && inRanges(cps[i - 1].value, ARABIC) && inRanges(cps[i + 1].value, ARABIC)
        }
        return false
    }

    static func isLetterOrNumber(_ gc: Unicode.GeneralCategory) -> Bool {
        switch gc {
        case .uppercaseLetter, .lowercaseLetter, .titlecaseLetter, .modifierLetter,
             .otherLetter, .decimalNumber, .letterNumber, .otherNumber: return true
        default: return false
        }
    }

    /// Reduce a string to COIA canonical form (§5).
    static func normalize(_ s: String) -> String {
        let nfkc = s.precomposedStringWithCompatibilityMapping
        let cps = Array(casefold(nfkc).unicodeScalars)
        var out = String.UnicodeScalarView()
        var onBase = false
        for (i, u) in cps.enumerated() {
            let cp = u.value
            let gc = u.properties.generalCategory
            if inRanges(cp, SPLIT) {
                out.append(" ")
                onBase = false
            } else if cp == TATWEEL {
                // decorative
            } else if gc == .format {
                if joinerOk(cps, i) { out.append(u) }
            } else if gc == .enclosingMark {
                // enclosing marks are decorative
            } else if gc == .nonspacingMark || gc == .spacingMark {
                if onBase { out.append(u) }
            } else if isLetterOrNumber(gc) {
                out.append(cp == 0x02BC ? Unicode.Scalar(0x02BB)! : u)
                onBase = true
            } else {
                onBase = false
            }
        }
        return String(out).split(separator: " ").joined(separator: "-")
    }

    // --------------------------------------------------------- localization

    /* koJosa lived here: the -(으)로서 allomorphy. Native-speaker review
    2026-08-25 confirmed the RULE was correct and the PARTICLE was the mistake.
    Removed with the particle it served. */

    // One template, every language: who, role, scope joined by spaces, scope
    // omitted when empty. Native-speaker review 2026-08-25 (47 reviews, 11 languages,
    // 7 models, 5 labs): bare apposition was proposed independently in every language,
    // and who-role-scope was unanimous in 8 of 11 and 35 of all 47. See coia.py for the
    // full rationale and for the connectors and allomorphy rules this replaced.
    static func template(_ w: String, _ r: String, _ s: String) -> String {
        return "\(w) \(r)" + (s.isEmpty ? "" : " \(s)")
    }

    static func pronoun(_ lang: String) -> String {
        ["en": "me", "es": "yo", "de": "ich", "fr": "moi", "pt": "eu", "it": "io",
         "ru": "я", "ja": "私", "zh": "我", "ko": "나", "ar": "أنا", "he": "אני"][lang] ?? ""
    }

    // ----------------------------------------------------------------- flags

    static let ASSIGNED: Set<Character> = ["0", "1", "4", "5", "6", "7", "8", "9"]

    struct CoiaError: Error { let message: String }

    static func flagGroup(_ digits: String, _ name: String) throws -> String {
        if digits.isEmpty { return "" }
        var seen = Set<Character>()
        for u in digits.unicodeScalars {
            guard let d = DIGITS[u.value] else {
                throw CoiaError(message: "\(name) must contain only decimal digits")
            }
            seen.insert(d)
        }
        return String(seen.sorted(by: >))
    }

    /// Mint an alias (§4, §6).
    static func createAlias(_ lang: String, _ who: String, _ role: String,
                            _ scope: String = "", _ flags: String = "",
                            _ privateFlags: String = "") throws -> String {
        let reflexive = (who == ME)
        let subject = reflexive ? pronoun(lang) : who
        let f = try flagGroup(flags, "flags")
        let pf = try flagGroup(privateFlags, "private_flags")
        for d in f where !ASSIGNED.contains(d) {
            throw CoiaError(message: "digit \(d) is reserved")
        }
        if reflexive && f.contains("0") {
            throw CoiaError(message: "reflexive aliases must not carry flag 0")
        }
        if pronoun(lang).isEmpty {
            throw CoiaError(message: "unsupported language \(lang)")
        }
        let expanded = template(subject, role, scope)
        let body = normalize(expanded)
        if normalize(role).isEmpty {
            throw CoiaError(message: "role must be non-empty after normalization")
        }
        if !reflexive && normalize(subject).isEmpty {
            throw CoiaError(message: "who must be non-empty after normalization")
        }
        if body.isEmpty {
            throw CoiaError(message: "alias is empty after normalization")
        }
        var out = body
        if !f.isEmpty || !pf.isEmpty { out += "," + f }
        if !pf.isEmpty { out += "," + pf }
        return out
    }

    /// Split a raw alias into body and flag groups (§6.1, §6.2).
    static func parseAlias(_ s: String) throws -> [String] {
        let unified = String(s.map { c -> Character in
            (c == "、" || c == "،" || c == "，") ? "," : c
        })
        let parts = unified.components(separatedBy: ",")
        if parts.count > 3 {
            throw CoiaError(message: "an alias has at most two flag groups")
        }
        return [normalize(parts[0]),
                try flagGroup(parts.count > 1 ? parts[1] : "", "flags"),
                try flagGroup(parts.count > 2 ? parts[2] : "", "private_flags")]
    }

    // -------------------------------------------------------------- matching

    static func terms(_ q: String) -> [String] {
        q.split(separator: "-").map(String.init)
    }

    /// Does a query find an alias? (§7)
    static func matches(_ query: String, _ alias: String) -> Bool {
        guard let body = try? parseAlias(alias)[0],
              let qbody = try? parseAlias(query)[0] else { return false }
        let ts = terms(qbody)
        return !ts.isEmpty && ts.allSatisfy { body.contains($0) }
    }

    /// Matching aliases in the normative order (§7).
    static func search(_ query: String, _ aliases: [String]) -> [String] {
        guard let qbody = try? parseAlias(query)[0] else { return [] }
        let ts = terms(qbody)
        var rows: [(Int, Int, Double, String)] = []
        for a in aliases {
            guard let body = try? parseAlias(a)[0] else { continue }
            if ts.isEmpty || !ts.allSatisfy({ body.contains($0) }) { continue }
            let segs = body.split(separator: "-").map(String.init)
            let whole = ts.filter { segs.contains($0) }.count
            let first = ts.compactMap { t -> Int? in
                guard let r = body.range(of: t) else { return nil }
                return body.distance(from: body.startIndex, to: r.lowerBound)
            }.min() ?? 0
            let matched = ts.reduce(0) { $0 + $1.unicodeScalars.count }
            let cover = Double(matched) / Double(body.unicodeScalars.count)
            rows.append((-whole, first, -cover, a))
        }
        rows.sort {
            if $0.0 != $1.0 { return $0.0 < $1.0 }
            if $0.1 != $1.1 { return $0.1 < $1.1 }
            if $0.2 != $1.2 { return $0.2 < $1.2 }
            return $0.3 < $1.3
        }
        return rows.map { $0.3 }
    }
}
