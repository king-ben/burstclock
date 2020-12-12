import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Insert alignments from Nexus into a BEAST template"
    )
    parser.add_argument(
        "nexus",
        type=Path
    )
    parser.add_argument(
        "beast",
        type=Path
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Beast output file (optional. If not given, edit BEAST in place.)"
    )
    args = parser.parse_args()

    if not args.beast.exists():
        raise ValueError("Input BEAST must exist")
    et = ET.parse(args.beast)
    root = et.getroot()

    data = list(root.iter("data"))[0]
    data.text = '\n'
    data.attrib["id"] = 'vocabulary'
    data.attrib["dataType"] = 'integer'
    data.attrib["spec"] = 'Alignment'

    in_matrix = False
    for line in args.nexus.open("r"):
        if line.strip() == "MATRIX":
            in_matrix = True
        elif not in_matrix:
            continue
        else:
            try:
                taxon, sequence = line.split()
                taxon = taxon.strip()
                sequence = sequence.strip()
                print(taxon)
                ET.SubElement(data, 'sequence', id=f"sequence_{taxon}", taxon=taxon, value=sequence).tail = '\n'
            except ValueError:
                continue

    et.write((args.output or args.beast).open('w'), encoding="unicode")
