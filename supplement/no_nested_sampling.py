import lxml.etree as ET


def replace_clock(root):
    """

    >>> root = ET.XML("<beast><branchRateModel id="Clock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" /></beast>")
    >>> ET.dump(replace_clock(root))
    <beast>
      <branchRateModel id="Clock" spec="beast.evolution.branchratemodel.BurstClock" perSplit="@perSplit" >
        <branchonlyClock id="innerClock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" />
      </branchRateModel>
    </beast>
    """

    for logger in root.findall(".//logger"):
        logger.set("spec", "Logger")
        logger.set("logEvery", "10000")

    mcmc = root.find(".//run")
    del mcmc.attrib["epsilon"]
    del mcmc.attrib["subChainLength"]
    del mcmc.attrib["particleCount"]
    mcmc.set("storeEvery", "10000")
    mcmc.set("spec", "MCMC")

    return root


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
    root = replace_clock(root)

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
