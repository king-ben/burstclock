import logging
import lxml.etree as ET


def set_tips(root, tips):
    """

    >>> root = ET.XML("<beast><branchRateModel id="Clock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" /></beast>")
    >>> ET.dump(replace_clock(root))
    <beast>
      <branchRateModel id="Clock" spec="beast.evolution.branchratemodel.BurstClock" perSplit="@perSplit" >
        <branchonlyClock id="innerClock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" />
      </branchRateModel>
    </beast>
    """
    starting_tree = root.find(".//init[@spec='beast.evolution.tree.RandomTreeWithSA']")
    for tip in tips:
        ET.SubElement(starting_tree, "sampledAncestor", idref=tip)
    return root


def into_jump_operator(root, tips):
    """

    >>> root = ET.XML("<beast><branchRateModel id="Clock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" /></beast>")
    >>> ET.dump(replace_clock(root))
    <beast>
      <branchRateModel id="Clock" spec="beast.evolution.branchratemodel.BurstClock" perSplit="@perSplit" >
        <branchonlyClock id="innerClock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" />
      </branchRateModel>
    </beast>
    """
    operator = root.find(".//operator[@spec='LeafToSampledAncestorJump']")
    for tip in tips:
        ET.SubElement(operator, "sampledTaxa", idref=tip)
    return root


if __name__ == "__main__":
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(
        description="Start the supplied tips as Sampled Ancestors"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="""Input beast XML, with a beast.evolution.tree.RandomTreeWithSA initializer.""",
    )
    parser.add_argument(
        "jumping",
        nargs="*",
        help="The tips that jump between being sampled ancestors or not.",
    )
    parser.add_argument(
        "--sampled-ancestor",
        "-s",
        action="append",
        default=[],
        help="The tips to initialize as sampled ancestors.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="""File to write output to. (default: Write to stdout)""",
    )
    args = parser.parse_args()

    xmlparser = ET.XMLParser(remove_blank_text=True, resolve_entities=False)
    for line in args.input.open("rb"):
        xmlparser.feed(line)
    root = xmlparser.close()

    all_languages = {e.attrib.get("taxon") for e in root.findall(".//sequence")}
    if set(args.jumping) - all_languages:
        logging.warning(
            "“Jumping” languages %s were not in the XML file", set(args.jumping) - all_languages
        )
    if args.jumping:
        root = into_jump_operator(root, set(args.jumping) & all_languages)

    if set(args.sampled_ancestor) - all_languages:
        logging.warning(
            "Sampled ancestor languages %s were not in the XML file",
            set(args.sampled_ancestor) - all_languages,
        )
    if args.sampled_ancestor:
        root = into_jump_operator(root, set(args.sampled_ancestor) & all_languages)

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
