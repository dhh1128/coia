package main

import (
	"fmt"
	"os"
	"strings"

	"coia"
)

const sep = "\u0001"
const meMark = "\u0000ME"

type fail struct{ sec, label, got, want string }

func main() {
	var fails []fail
	rec := func(sec, label, got, want string) {
		if got != want {
			fails = append(fails, fail{sec, label, got, want})
		}
	}
	args := func(a string) (string, string, string, string, string, string) {
		p := strings.Split(a, sep)
		who := p[1]
		if who == meMark {
			who = coia.ME
		}
		return p[0], who, p[2], p[3], p[4], p[5]
	}
	for _, v := range coia.Vectors {
		sec, label, a, b, c := v[0], v[1], v[2], v[3], v[4]
		switch sec {
		case "normalize":
			rec(sec, label, coia.Normalize(a), b)
		case "generate":
			l, w, r, s, f, pf := args(a)
			got, err := coia.CreateAlias(l, w, r, s, f, pf)
			if err != nil {
				got = "<" + err.Error() + ">"
			}
			rec(sec, label, got, b)
		case "reject":
			l, w, r, s, f, pf := args(a)
			if got, err := coia.CreateAlias(l, w, r, s, f, pf); err == nil {
				rec(sec, label, "produced "+got, "<rejected>")
			}
		case "parse":
			body, g1, g2, err := coia.ParseAlias(a)
			got := strings.Join([]string{body, g1, g2}, sep)
			if err != nil {
				got = "<" + err.Error() + ">"
			}
			rec(sec, label, got, b)
		case "match":
			rec(sec, label, fmt.Sprintf("%t", coia.Matches(b, a)), c)
		case "search":
			var want []string
			if c != "" {
				want = strings.Split(c, sep)
			}
			got := coia.Search(b, strings.Split(a, sep))
			rec(sec, label, strings.Join(got, sep), strings.Join(want, sep))
		}
	}
	fmt.Printf("%d/%d vectors pass\n\n", len(coia.Vectors)-len(fails), len(coia.Vectors))
	for _, f := range fails {
		fmt.Printf("  FAIL [%s] %s\n        got  %q\n        want %q\n", f.sec, f.label, f.got, f.want)
	}
	if len(fails) > 0 {
		os.Exit(1)
	}
}
