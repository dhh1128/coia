import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

public class DiffTest {
    public static void main(String[] a) throws Exception {
        for (String line : Files.readAllLines(Paths.get("difftest-input.txt"))) {
            if (line.isEmpty()) continue;
            StringBuilder in = new StringBuilder();
            for (String h : line.trim().split(" +"))
                in.appendCodePoint(Integer.parseInt(h, 16));
            String r = Coia.normalize(in.toString());
            System.out.println(r.codePoints()
                .mapToObj(cp -> Integer.toHexString(cp).toUpperCase())
                .collect(Collectors.joining(" ")));
        }
    }
}
