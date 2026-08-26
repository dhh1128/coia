use coia::data::VECTORS;

const SEP: char = '\u{1}';
const ME_MARK: &str = "\u{0}ME";

fn main() {
    let mut fails: Vec<(String, String, String, String)> = vec![];
    let mut rec = |sec: &str, label: &str, got: String, want: &str| {
        if got != want {
            fails.push((sec.into(), label.into(), got, want.into()));
        }
    };
    let split6 = |a: &str| -> Vec<String> {
        let mut p: Vec<String> = a.split(SEP).map(|x| x.to_string()).collect();
        if p[1] == ME_MARK { p[1] = coia::ME.to_string(); }
        p
    };
    for v in VECTORS {
        let (sec, label, a, b, c) = (v[0], v[1], v[2], v[3], v[4]);
        match sec {
            "normalize" => rec(sec, label, coia::normalize(a), b),
            "generate" => {
                let p = split6(a);
                let got = match coia::create_alias(&p[0], &p[1], &p[2], &p[3], &p[4], &p[5]) {
                    Ok(s) => s,
                    Err(e) => format!("<{e}>"),
                };
                rec(sec, label, got, b);
            }
            "reject" => {
                let p = split6(a);
                if let Ok(s) = coia::create_alias(&p[0], &p[1], &p[2], &p[3], &p[4], &p[5]) {
                    rec(sec, label, format!("produced {s}"), "<rejected>");
                }
            }
            "parse" => {
                let got = match coia::parse_alias(a) {
                    Ok((x, y, z)) => format!("{x}{SEP}{y}{SEP}{z}"),
                    Err(e) => format!("<{e}>"),
                };
                rec(sec, label, got, b);
            }
            "match" => rec(sec, label, format!("{}", coia::matches(b, a)), c),
            "search" => {
                let corpus: Vec<String> = a.split(SEP).map(|x| x.to_string()).collect();
                let got = coia::search(b, &corpus).join(&SEP.to_string());
                rec(sec, label, got, c);
            }
            _ => {}
        }
    }
    println!("{}/{} vectors pass\n", VECTORS.len() - fails.len(), VECTORS.len());
    for (sec, label, got, want) in &fails {
        println!("  FAIL [{sec}] {label}\n        got  {got:?}\n        want {want:?}");
    }
    if !fails.is_empty() { std::process::exit(1); }
}
