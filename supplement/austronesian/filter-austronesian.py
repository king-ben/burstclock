import sys
import pycldf

ds = pycldf.Wordlist.from_metadata("raw_cldf/cldf-metadata.json")

austronesian = {
    l["ID"] for l in ds["LanguageTable"]
    if l["Family"] == "Austronesian"
}

countlects = 0
for i in sys.stdin:
    i = i.strip()
    if i in austronesian:
        print(i)
        countlects += 1

with open("stats.tex", "w") as s:
    print(f"""
    \\newcommand{{countlects}}{{{countlects}}}
        """, file=s)
