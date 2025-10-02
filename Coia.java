// Public domain code ported from python by AI. Light testing confirms
// basic functionality is working with believable input from several
// languages (Portuguese, Russian). But use at your own risk. If anyone
// uses the code heavily and confirms that it's working well, please raise
// a PR to remove this caveat.

// IMPORTANT NOTE: THIS CODE CONTAINS MANY UNICODE STRING CONSTANTS AND CAN 
// BE MANGLED SUBTLY IF YOU COPY/PASTE IT IN A BROWSER. DOWNLOADING THE FILE
// DIRECTLY SHOULD BE LOSSLESS. TO TEST WHETHER MANGLING HAS HAPPENED, CHECK
// PUNCT_TO_SPACE_PATTERN AS AN EXAMPLE ABOUT 50 LINES BELOW. YOUR IDE SHOULD
// SHOW THAT IT ENDS WITH SOME SMART QUOTE CHARACTERS; IT SHOULD *NOT*
// DISPLAY ACCENTED LATIN CHARACTERS INSIDE IT.

import java.text.Normalizer;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.Arrays;

public class Coia {

    private static final String ME_AS_ARG = "";

    private static final Map<String, String> PRONOUN_TRANSLATIONS = new HashMap<>() {{
        put("en", "me");
        put("fr", "moi");
        put("es", "yo");
        put("de", "ich");
        put("pt", "eu");
        put("ja", "私");
        put("zh", "我");
        put("ko", "나");
        put("ar", "أنا");
        put("he", "אני");
        put("ru", "я");
    }};

    private static final Map<String, String> TEMPLATES = new HashMap<>() {{
        put("en", "{flags}{who} as {role}{scope}");
        put("fr", "{flags}{who} comme {role}{scope}");
        put("es", "{flags}{who} como {role}{scope}");
        put("de", "{flags}{who} als {role}{scope}");
        put("pt", "{flags}{who} como {role}{scope}");
        put("ja", "{flags}{who}として{role}{scope}");
        put("zh", "{flags}{who}作为{role}{scope}");
        put("ko", "{flags}{who}로서{role}{scope}");
        put("ar", "{flags}{who} بصفتي {role}{scope}");
        put("he", "{flags}{who} בתור {role}{scope}");
        put("ru", "{flags}{who} как {role}{scope}");
    }};

    private static final Map<String, String> SCOPE_TEMPLATES = new HashMap<>() {{
        put("en", " at {org}");
        put("fr", " à {org}");
        put("es", " en {org}");
        put("de", " bei {org}");
        put("pt", " na {org}");
        put("ja", "に-{org}");
        put("zh", "在-{org}");
        put("ko", "-{org}");
        put("ar", " في {org}");
        put("he", " ב{org}");
        put("ru", " в {org}");
    }};

    // Regex patterns
    private static final Pattern PUNCT_TO_SPACE_PATTERN = Pattern.compile(
        "[\\p{Pd}\\p{Ps}\\p{Pe}\\p{Pi}\\p{Pf}\\p{Pc}&﹠＆.,‚،․。﹒．｡'’‘‚‛＇]",
        Pattern.UNICODE_CHARACTER_CLASS
    );
    private static final Pattern WHITESPACE_PATTERN = Pattern.compile("\\s+");
    private static final Pattern STRIP_WS_EDGES = Pattern.compile("^\\s+|\\s+$");
    private static final Pattern DISALLOWED_PATTERN = Pattern.compile(
        "[\\p{Cc}\\p{Cf}\\p{Cs}\\p{Co}\\p{Cn}\\p{So}\\p{Sm}\\p{Sc}\\p{Sk}\\p{P}\\p{M}]",
        Pattern.UNICODE_CHARACTER_CLASS
    );

    public static String normalizeUnicode(String s) {
        // 1. NFKC normalization
        s = Normalizer.normalize(s, Normalizer.Form.NFKC);

        // 2. lowercase
        s = s.toLowerCase();

        // 3. replace selected punctuators with space
        s = PUNCT_TO_SPACE_PATTERN.matcher(s).replaceAll(" ");

        // 4. strip leading/trailing whitespace
        s = STRIP_WS_EDGES.matcher(s).replaceAll("");

        // 5. delete disallowed characters
        s = DISALLOWED_PATTERN.matcher(s).replaceAll("");

        // 6. collapse whitespace into single ASCII hyphen
        s = WHITESPACE_PATTERN.matcher(s).replaceAll("-");

        return s;
    }

    public static String createAlias(String lang, String flags, String who, String role, String scope) {
        flags = flags != null ? flags.trim() : "";
        who = who != null ? who.trim() : "";
        role = role != null ? role.trim() : "";
        scope = scope != null ? scope.trim() : "";

        if (role.isEmpty()) throw new IllegalArgumentException("Role cannot be empty");
        if (!flags.isEmpty() && !flags.matches("\\d+")) throw new IllegalArgumentException("Flags must be all digits or empty");
        if (flags.length() > 10) throw new IllegalArgumentException("Flags must be at most 10 characters");

        // Substitute ME with language-specific pronoun
        if (who.equals(ME_AS_ARG)) {
            if (!PRONOUN_TRANSLATIONS.containsKey(lang)) {
                throw new IllegalArgumentException("No translation for 'me' in language " + lang);
            }
            who = PRONOUN_TRANSLATIONS.get(lang);
        }

        // Process flags
        if (!flags.isEmpty()) {
            char[] arr = flags.toCharArray();
            Arrays.sort(arr);
            flags = new String(arr) + " ";
        }

        // Process scope
        if (!scope.isEmpty()) {
            if (!SCOPE_TEMPLATES.containsKey(lang)) {
                throw new IllegalArgumentException("No scope template for language " + lang);
            }
            String scopeTemplate = SCOPE_TEMPLATES.get(lang);
            scope = " " + scopeTemplate.replace("{org}", scope);
        }

        // Select template
        if (!TEMPLATES.containsKey(lang)) {
            throw new IllegalArgumentException("No template for language " + lang);
        }
        String template = TEMPLATES.get(lang);

        // Interpolate
        String result = template
                .replace("{flags}", flags)
                .replace("{who}", who)
                .replace("{role}", role)
                .replace("{scope}", scope);

        // Normalize
        result = normalizeUnicode(result);

        return result;
    }
}
