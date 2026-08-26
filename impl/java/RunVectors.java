import java.util.*;
import java.util.stream.Collectors;

public final class RunVectors {
    static final String SEP = String.valueOf((char) 1);
    static final String ME_MARK = new String(new char[]{0}) + "ME";
    static List<String[]> fails = new ArrayList<>();

    static void rec(String sec, String label, String got, String want) {
        if (!got.equals(want)) fails.add(new String[]{sec, label, got, want});
    }

    public static void main(String[] a) {
        for (String[] v : Data.VECTORS) {
            String sec = v[0], label = v[1], x = v[2], b = v[3], c = v[4];
            try {
                switch (sec) {
                    case "normalize" -> rec(sec, label, Coia.normalize(x), b);
                    case "generate" -> {
                        String[] p = split6(x);
                        String got;
                        try { got = Coia.createAlias(p[0], p[1], p[2], p[3], p[4], p[5]); }
                        catch (RuntimeException e) { got = "<" + e.getMessage() + ">"; }
                        rec(sec, label, got, b);
                    }
                    case "reject" -> {
                        String[] p = split6(x);
                        try {
                            String got = Coia.createAlias(p[0], p[1], p[2], p[3], p[4], p[5]);
                            rec(sec, label, "produced " + got, "<rejected>");
                        } catch (RuntimeException e) { /* expected */ }
                    }
                    case "parse" -> rec(sec, label, String.join(SEP, Coia.parseAlias(x)), b);
                    case "match" -> rec(sec, label, String.valueOf(Coia.matches(b, x)), c);
                    case "search" -> {
                        List<String> corpus = Arrays.asList(x.split(SEP, -1));
                        rec(sec, label, String.join(SEP, Coia.search(b, corpus)), c);
                    }
                }
            } catch (RuntimeException e) {
                rec(sec, label, "<" + e + ">", b);
            }
        }
        System.out.printf("%d/%d vectors pass%n%n", Data.VECTORS.length - fails.size(), Data.VECTORS.length);
        for (String[] f : fails)
            System.out.printf("  FAIL [%s] %s%n        got  %s%n        want %s%n", f[0], f[1], f[2], f[3]);
        if (!fails.isEmpty()) System.exit(1);
    }

    static String[] split6(String s) {
        String[] p = s.split(SEP, -1);
        if (ME_MARK.equals(p[1])) p[1] = Coia.ME;
        return p;
    }
}
