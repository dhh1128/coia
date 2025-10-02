// Public domain code ported from python by AI; light testing confirms
// basic functionality is working with believable input from several
// languages (Portuguese, Russian). But use at your own risk. If anyone
// uses the code heavily and confirms that it's working well, please raise
// a PR to remove this caveat.

// IMPORTANT NOTE: THIS CODE CONTAINS MANY UNICODE STRING CONSTANTS AND CAN 
// BE MANGLED SUBTLY IF YOU COPY/PASTE IT IN A BROWSER. DOWNLOADING THE FILE
// DIRECTLY SHOULD BE LOSSLESS. TO TEST WHETHER MANGLING HAS HAPPENED, CHECK
// THE punctPattern REGEX AS AN EXAMPLE ABOUT 60 LINES BELOW. YOUR IDE SHOULD
// SHOW THAT IT ENDS WITH SOME SMART QUOTE CHARACTERS; IT SHOULD *NOT*
// DISPLAY ACCENTED LATIN CHARACTERS INSIDE IT.

import Foundation

public enum CoiaError: Error, LocalizedError {
    case emptyRole
    case invalidFlags
    case flagsTooLong
    case noPronounTranslation(lang: String)
    case noScopeTemplate(lang: String)
    case noTemplate(lang: String)

    public var errorDescription: String? {
        switch self {
        case .emptyRole: return "Role cannot be empty"
        case .invalidFlags: return "Flags must be all digits or empty"
        case .flagsTooLong: return "Flags must be at most 10 characters"
        case .noPronounTranslation(let lang): return "No translation for 'me' in language \(lang)"
        case .noScopeTemplate(let lang): return "No scope template for language \(lang)"
        case .noTemplate(let lang): return "No template for language \(lang)"
        }
    }
}

public struct Coia {
    public static let meAsArg = ""

    public static let pronounTranslations: [String: String] = [
        "en": "me", "fr": "moi", "es": "yo", "de": "ich",
        "pt": "eu", "ja": "私", "zh": "我", "ko": "나",
        "ar": "أنا", "he": "אני", "ru": "я"
    ]

    public static let templates: [String: String] = [
        "en": "{flags}{who} as {role}{scope}",
        "fr": "{flags}{who} comme {role}{scope}",
        "es": "{flags}{who} como {role}{scope}",
        "de": "{flags}{who} als {role}{scope}",
        "pt": "{flags}{who} como {role}{scope}",
        "ja": "{flags}{who}として{role}{scope}",
        "zh": "{flags}{who}作为{role}{scope}",
        "ko": "{flags}{who}로서{role}{scope}",
        "ar": "{flags}{who} بصفتي {role}{scope}",
        "he": "{flags}{who} בתור {role}{scope}",
        "ru": "{flags}{who} как {role}{scope}"
    ]

    public static let scopeTemplates: [String: String] = [
        "en": " at {org}", "fr": " à {org}", "es": " en {org}",
        "de": " bei {org}", "pt": " na {org}", "ja": "に-{org}",
        "zh": "在-{org}", "ko": "-{org}", "ar": " في {org}",
        "he": " ב{org}", "ru": " в {org}"
    ]

    // MARK: - Unicode normalization

    public static func normalizeUnicode(_ s: String) -> String {
        // 1. NFKC normalization
        var result = s.precomposedStringWithCompatibilityMapping
        // 2. lowercase
        result = result.lowercased()
        // 3. replace selected punctuators with space
        let punctPattern = #"[\p{Pd}\p{Pi}\p{Pf}\p{Ps}\p{Pe}&﹠＆.,‚،․。﹒．｡'’‘‚‛＇]"#
        result = result.replacingOccurrences(of: punctPattern, with: " ", options: .regularExpression)
        // 4. strip leading/trailing whitespace
        result = result.trimmingCharacters(in: .whitespacesAndNewlines)
        // 5. delete disallowed characters
        let disallowedPattern = #"[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{So}\p{Sm}\p{Sc}\p{Sk}\p{P}\p{M}]"#
        result = result.replacingOccurrences(of: disallowedPattern, with: "", options: .regularExpression)
        // 6. collapse whitespace into single ASCII hyphen
        let whitespacePattern = #"\s+"#
        result = result.replacingOccurrences(of: whitespacePattern, with: "-", options: .regularExpression)
        return result
    }

    // MARK: - Alias creation

    public static func createAlias(
        lang: String,
        flags: String? = nil,
        who: String? = nil,
        role: String,
        scope: String? = nil
    ) throws -> String {
        let flagsTrimmed = flags?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        var whoTrimmed = who?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let roleTrimmed = role.trimmingCharacters(in: .whitespacesAndNewlines)
        var scopeTrimmed = scope?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""

        guard !roleTrimmed.isEmpty else { throw CoiaError.emptyRole }

        if !flagsTrimmed.isEmpty && !flagsTrimmed.allSatisfy({ $0.isNumber }) {
            throw CoiaError.invalidFlags
        }
        if flagsTrimmed.count > 10 {
            throw CoiaError.flagsTooLong
        }

        // Substitute ME with language-specific pronoun
        if whoTrimmed == meAsArg {
            guard let pronoun = pronounTranslations[lang] else {
                throw CoiaError.noPronounTranslation(lang: lang)
            }
            whoTrimmed = pronoun
        }

        // Process flags: sort digits
        var flagsSorted = flagsTrimmed
        if !flagsTrimmed.isEmpty {
            flagsSorted = String(flagsTrimmed.sorted()) + " "
        }

        // Process scope
        if !scopeTrimmed.isEmpty {
            guard let scopeTemplate = scopeTemplates[lang] else {
                throw CoiaError.noScopeTemplate(lang: lang)
            }
            scopeTrimmed = " " + scopeTemplate.replacingOccurrences(of: "{org}", with: scopeTrimmed)
        }

        // Select template
        guard let template = templates[lang] else {
            throw CoiaError.noTemplate(lang: lang)
        }

        // Interpolate
        var result = template
        result = result.replacingOccurrences(of: "{flags}", with: flagsSorted)
        result = result.replacingOccurrences(of: "{who}", with: whoTrimmed)
        result = result.replacingOccurrences(of: "{role}", with: roleTrimmed)
        result = result.replacingOccurrences(of: "{scope}", with: scopeTrimmed)

        // Normalize
        return normalizeUnicode(result)
    }
}
