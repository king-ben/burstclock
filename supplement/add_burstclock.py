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

    clock_model = root.find(".//*[@id='Clock']")
    assert clock_model is not None
    id = clock_model.attrib.get("id")
    name = clock_model.get("name") or clock_model.tag
    parent = clock_model.getparent()
    burst_clock = ET.SubElement(
        parent,
        name,
        id="Clock",
        spec="ch.uzh.beast.evolution.branchratemodel.BurstClock",
        perSplit="@perSplit",
    )
    clock_model.addnext(burst_clock)
    clock_model.set("id", "innerClock")
    clock_model.set("name", "branchonlyClock")
    burst_clock.append(clock_model)

    state = root.find(".//state[@id='state']")
    persplit = ET.SubElement(
        state,
        "parameter",
        id="perSplit",
        spec="parameter.RealParameter",
        name="stateNode",
    )
    persplit.text = "2e-4"
    state.append(persplit)

    logger = root.find(".//logger[@id='tracelog']")
    operator = ET.SubElement(
        logger,
        "log",
        idref="perSplit",
    )

    operators = root.find(".//operator").getparent()
    operator = ET.SubElement(
        operators,
        "operator",
        spec="beast.evolution.operators.RealRandomWalkOperator",
        id="BurstClockShift",
        windowSize="1e-4",
        parameter="@perSplit",
        useGaussian="true",
        weight="3.",
    )
    operators.append(operator)

    prior = root.find(".//distribution[@id='prior']")
    persplitprior = ET.SubElement(
        prior,
        "prior",
        spec="Prior",
        id="PerSplitPrior",
        name="distribution",
        x="@perSplit",
    )
    ET.SubElement(
        persplitprior,
        "distr",
        id="Normal.PerSplit",
        spec="beast.math.distributions.Normal",
        mean="0.0",
        sigma="3.6e-3",
    )

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
