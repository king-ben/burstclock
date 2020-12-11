import sys
import pycldf

ds = pycldf.Wordlist.from_metadata("raw_cldf/cldf-metadata.json")

austronesian = {
    l["ID"] for l in ds["LanguageTable"]
    if l["Family"] == "Austronesian"
}

