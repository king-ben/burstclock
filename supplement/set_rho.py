import lxml.etree as ET
import pyglottolog
from cldfcatalog import Catalog


def replace_rho(root, rho):
    """

    >>> root = ET.XML("<beast><branchRateModel id="Clock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" /></beast>")
    >>> ET.dump(replace_clock(root))
    <beast>
      <branchRateModel id="Clock" spec="beast.evolution.branchratemodel.BurstClock" perSplit="@perSplit" >
        <branchonlyClock id="innerClock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" />
      </branchRateModel>
    </beast>
    """

    rho = root.find(".//parameter[@name='rho']")
    assert rho is not None
    rho.text = str(rho)

    return root


def count_languages(root) -> int:
    tip_dates = root.find(".//trait[@traitname='date-backward']")
    ancient = 0
    for date in tip_dates.text.split(","):
        tip, date = date.split("=")
        if int(date.strip()) != 0:
            ancient += 1
    n_sequences = len(root.findall(".//sequence"))
    return n_sequences - ancient


def glottolog_count_languages(languoid) -> int:
    if languoid.level.id == "language" and (
        languoid.endangerment is None or languoid.endangerment.status.id != "extinct"
    ):
        return 1 + sum(glottolog_count_languages(sub) for sub in languoid.children)
    return sum(glottolog_count_languages(sub) for sub in languoid.children)


if __name__ == "__main__":
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(
        description="Wrap the Clock beast object inside a burst clock"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="""Input beast XML, with a clock with id="Clock".""",
    )
    parser.add_argument(
        "clade", nargs="?", help="The glottolog clade to count as reference"
    )
    parser.add_argument(
        "-n", type=int, help="The total number of languages this is sampled from"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="""File to write output to. (default: Write to stdout)""",
    )
    args = parser.parse_args()

    if args.clade:
        with Catalog.from_config("glottolog", tag="v4.3") as glottolog_repo:
            glottolog = pyglottolog.Glottolog(glottolog_repo.dir)
        languoid = glottolog.languoid(args.clade)
        n = glottolog_count_languages(languoid)

    elif args.n:
        n = args.n
    else:
        raise argparse.ArgumentError(None, "You must specify either CLADE or N.")

    xmlparser = ET.XMLParser(remove_blank_text=True, resolve_entities=False)
    for line in args.input.open("rb"):
        xmlparser.feed(line)
    root = xmlparser.close()

    sampled = count_languages(root)
    root = replace_rho(root, rho=sampled / n)

    et = root.getroottree()
    if args.output:
        et.write(
            args.output.open("wb"),
            pretty_print=True,
            xml_declaration=True,
            encoding=et.docinfo.encoding,
        )
    else:
        print(
            ET.tostring(
                root,
                pretty_print=True,
                xml_declaration=True,
            ).decode("utf-8")
        )
