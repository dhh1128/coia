// COIA v2 reference implementation (Java).
// Tables and vectors are generated; see ../../gencode.py.
import java.text.Normalizer;
import java.util.*;
import java.util.stream.Collectors;

public final class Coia {
    private static final int TATWEEL = 0x0640, ZWJ = 0x200D, ZWNJ = 0x200C;

    /** The reflexive sentinel, distinct from the empty string (§4.1). */
    public static final String ME = new String(new char[]{0}) + "COIA-ME";

    private static final Map<Integer, Integer> FOLD = Map.of(0x02BC, 0x02BB);
    private static final Map<Integer, String> FOLDGAP_MAP = new HashMap<>();
    private static final Map<Integer, Integer> DIGIT_MAP = new HashMap<>();
    static {
        for (String[] p : Data.FOLDGAP) FOLDGAP_MAP.put(p[0].codePointAt(0), p[1]);
        for (int[] p : Data.DIGITS) DIGIT_MAP.put(p[0], p[1]);
    }

    private static boolean inRanges(int cp, int[][] rs) {
        for (int[] r : rs) if (cp >= r[0] && cp <= r[1]) return true;
        return false;
    }

    // Default Case Folding from the normative table (Appendix B.6). Deliberately does
    // NOT use toLowerCase(): that is case mapping, it is locale-sensitive, and under
    // tr_TR it turns I into a dotless i.
    private static String casefold(String s) {
        StringBuilder b = new StringBuilder();
        s.codePoints().forEach(cp -> {
            String f = FOLDGAP_MAP.get(cp);
            if (f != null) b.append(f); else b.appendCodePoint(cp);
        });
        return b.toString();
    }

    private static boolean joinerOk(int[] cps, int i) {
        if (cps[i] == ZWJ) return i > 0 && inRanges(cps[i - 1], Data.VIRAMA);
        if (cps[i] == ZWNJ) {
            if (i > 0 && inRanges(cps[i - 1], Data.VIRAMA)) return true;
            return i > 0 && i < cps.length - 1
                && inRanges(cps[i - 1], Data.ARABIC) && inRanges(cps[i + 1], Data.ARABIC);
        }
        return false;
    }

    private static boolean isLetterOrNumber(int cp) {
        int t = Character.getType(cp);
        return t == Character.UPPERCASE_LETTER || t == Character.LOWERCASE_LETTER
            || t == Character.TITLECASE_LETTER || t == Character.MODIFIER_LETTER
            || t == Character.OTHER_LETTER || t == Character.DECIMAL_DIGIT_NUMBER
            || t == Character.LETTER_NUMBER || t == Character.OTHER_NUMBER;
    }

    /** Reduce a string to COIA canonical form. */
    public static String normalize(String s) {
        int[] cps = casefold(Normalizer.normalize(s, Normalizer.Form.NFKC)).codePoints().toArray();
        StringBuilder b = new StringBuilder();
        boolean onBase = false;
        for (int i = 0; i < cps.length; i++) {
            int cp = cps[i], t = Character.getType(cp);
            if (inRanges(cp, Data.SPLIT)) { b.append(' '); onBase = false; }
            else if (cp == TATWEEL) { /* decorative */ }
            else if (t == Character.FORMAT) { if (joinerOk(cps, i)) b.appendCodePoint(cp); }
            else if (t == Character.ENCLOSING_MARK) { /* decorative */ }
            else if (t == Character.NON_SPACING_MARK || t == Character.COMBINING_SPACING_MARK) {
                if (onBase) b.appendCodePoint(cp);
            }
            else if (isLetterOrNumber(cp)) { b.appendCodePoint(FOLD.getOrDefault(cp, cp)); onBase = true; }
            else onBase = false;
        }
        return Arrays.stream(b.toString().trim().split(" +"))
                     .filter(x -> !x.isEmpty()).collect(Collectors.joining("-"));
    }

    // --------------------------------------------------------- localization

    /* koJosa lived here: the -(으)로서 allomorphy. Native-speaker review
    2026-08-25 confirmed the RULE was correct and the PARTICLE was the mistake.
    Removed with the particle it served. */

    private static String opt(String cond, String val) { return cond.isEmpty() ? "" : val; }

    // One template, every language: who, role, scope joined by spaces, scope
    // omitted when empty. Native-speaker review 2026-08-25 (47 reviews, 11 languages,
    // 7 models, 5 labs): bare apposition was proposed independently in every language,
    // and who-role-scope was unanimous in 8 of 11 and 35 of all 47. See coia.py for the
    // full rationale and for the connectors and allomorphy rules this replaced.
    private static String template(String w, String r, String s) {
        return w + " " + r + opt(s, " " + s);
    }

    private static final Map<String, String> PRONOUNS = new LinkedHashMap<>();
    static {
        PRONOUNS.put("en","me"); PRONOUNS.put("es","yo"); PRONOUNS.put("de","ich");
        PRONOUNS.put("fr","moi"); PRONOUNS.put("pt","eu"); PRONOUNS.put("it","io");
        PRONOUNS.put("ru","я"); PRONOUNS.put("ja","私"); PRONOUNS.put("zh","我");
        PRONOUNS.put("ko","나"); PRONOUNS.put("ar","أنا");
        PRONOUNS.put("he","אני");
    }

    // ----------------------------------------------------------------- flags

    private static final Set<Integer> ASSIGNED =
        Set.of((int)'0',(int)'1',(int)'4',(int)'5',(int)'6',(int)'7',(int)'8',(int)'9');

    private static String flagGroup(String digits, String name) {
        if (digits == null || digits.isEmpty()) return "";
        TreeSet<Integer> seen = new TreeSet<>(Comparator.reverseOrder());
        for (int cp : digits.codePoints().toArray()) {
            Integer d = DIGIT_MAP.get(cp);
            if (d == null)
                throw new IllegalArgumentException(name + " must contain only decimal digits");
            seen.add(d);
        }
        StringBuilder b = new StringBuilder();
        seen.forEach(b::appendCodePoint);
        return b.toString();
    }

    /** Mint an alias. */
    public static String createAlias(String lang, String who, String role,
                                     String scope, String flags, String privateFlags) {
        if (!PRONOUNS.containsKey(lang))
            throw new IllegalArgumentException("unsupported language " + lang);
        boolean reflexive = ME.equals(who);
        if (reflexive) who = PRONOUNS.get(lang);

        String f = flagGroup(flags, "flags");
        String pf = flagGroup(privateFlags, "private_flags");
        for (int cp : f.codePoints().toArray())
            if (!ASSIGNED.contains(cp))
                throw new IllegalArgumentException("digit is reserved");
        if (reflexive && f.indexOf('0') >= 0)
            throw new IllegalArgumentException("reflexive aliases must not carry flag 0");

        String body = normalize(template(who, role, scope));
        if (normalize(role).isEmpty())
            throw new IllegalArgumentException("role must be non-empty after normalization");
        if (!reflexive && normalize(who).isEmpty())
            throw new IllegalArgumentException("who must be non-empty after normalization");
        if (body.isEmpty())
            throw new IllegalArgumentException("alias is empty after normalization");

        String out = body;
        if (!f.isEmpty() || !pf.isEmpty()) out += "," + f;
        if (!pf.isEmpty()) out += "," + pf;
        return out;
    }

    /** Split a raw alias into body and flag groups. */
    public static String[] parseAlias(String s) {
        s = s.replace('、', ',').replace('،', ',').replace('，', ',');
        String[] parts = s.split(",", -1);
        if (parts.length > 3)
            throw new IllegalArgumentException("an alias has at most two flag groups");
        return new String[]{ normalize(parts[0]),
                             flagGroup(parts.length > 1 ? parts[1] : "", "flags"),
                             flagGroup(parts.length > 2 ? parts[2] : "", "private_flags") };
    }

    // -------------------------------------------------------------- matching

    private static List<String> terms(String q) {
        return Arrays.stream(q.split("-")).filter(x -> !x.isEmpty()).collect(Collectors.toList());
    }

    /** Does a query find an alias? */
    public static boolean matches(String query, String alias) {
        String body = parseAlias(alias)[0];
        List<String> ts = terms(parseAlias(query)[0]);
        return !ts.isEmpty() && ts.stream().allMatch(body::contains);
    }

    private record Row(int whole, int first, double cover, String alias) {}

    /** Matching aliases in the normative order. */
    public static List<String> search(String query, List<String> aliases) {
        List<String> ts = terms(parseAlias(query)[0]);
        List<Row> rows = new ArrayList<>();
        for (String a : aliases) {
            String body = parseAlias(a)[0];
            if (ts.isEmpty() || !ts.stream().allMatch(body::contains)) continue;
            List<String> segs = Arrays.asList(body.split("-"));
            int whole = (int) ts.stream().filter(segs::contains).count();
            int first = ts.stream().mapToInt(body::indexOf).min().orElse(0);
            double cover = ts.stream().mapToInt(x -> x.codePointCount(0, x.length())).sum()
                         / (double) body.codePointCount(0, body.length());
            rows.add(new Row(whole, first, cover, a));
        }
        rows.sort(Comparator.comparingInt(Row::whole).reversed()
                  .thenComparingInt(Row::first)
                  .thenComparing(Comparator.comparingDouble(Row::cover).reversed())
                  .thenComparing(Row::alias));
        return rows.stream().map(Row::alias).collect(Collectors.toList());
    }
}
