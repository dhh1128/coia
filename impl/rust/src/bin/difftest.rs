use std::fs;

fn main() {
    let data = fs::read_to_string("difftest-input.txt").unwrap();
    for line in data.lines() {
        if line.is_empty() { continue; }
        let s: String = line.split_whitespace()
            .map(|h| char::from_u32(u32::from_str_radix(h, 16).unwrap()).unwrap())
            .collect();
        let out: Vec<String> = coia::normalize(&s).chars()
            .map(|c| format!("{:X}", c as u32)).collect();
        println!("{}", out.join(" "));
    }
}
