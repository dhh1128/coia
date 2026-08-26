package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"

	"coia"
)

func main() {
	f, _ := os.Open("difftest-input.txt")
	defer f.Close()
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1<<20), 1<<20)
	for sc.Scan() {
		line := sc.Text()
		if line == "" {
			continue
		}
		var sb strings.Builder
		for _, h := range strings.Fields(line) {
			v, _ := strconv.ParseInt(h, 16, 32)
			sb.WriteRune(rune(v))
		}
		var out []string
		for _, r := range coia.Normalize(sb.String()) {
			out = append(out, strings.ToUpper(strconv.FormatInt(int64(r), 16)))
		}
		fmt.Println(strings.Join(out, " "))
	}
}
