import csv
import sys
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("tsv", type=argparse.FileType("r"))
args = parser.parse_args()

languages = set()

reader = csv.DictReader(args.tsv, dialect='excel-tab')
writer = csv.DictWriter(sys.stdout, reader.fieldnames + ["id", "concept"], dialect="excel-tab")
writer.writeheader()
i = 0
for n, line in enumerate(reader):
    line["id"] = str(n + 1)
    line["concept"] = line["cc_alias"].split("-")[0]
    if not line["cc_id"]:
        line["cc_id"] = str(100000 + i)
        i += 1
    writer.writerow(line)
    languages.add(line["language"])

lwriter = csv.DictWriter(Path("raw_cldf/languages.tsv").open('w'), ["Name", "ID", "Glottocode"], dialect="excel-tab")
lwriter.writeheader()
lwriter.writerows({"Name": language, "ID": language, "Glottocode": "indo1319"} for language in languages)
