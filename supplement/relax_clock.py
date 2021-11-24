import lxml.etree as ET


def count_languages(root) -> int:
    n_sequences = len(root.findall(".//sequence"))
    return n_sequences

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

    clock_model = root.find(
        ".//*[@spec='beast.evolution.branchratemodel.StrictClockModel']"
    )
    assert clock_model is not None
    id = clock_model.get("id")
    clock_model.set("spec", "beast.evolution.branchratemodel.UCRelaxedClockModel")
    clock_model.set("rates", "@RelaxedClockBranchRates")
    clock_model.set("tree", "@tree")
    ET.SubElement(
        clock_model,
        "distr",
        id="ClockRatesPrior",
        spec="beast.math.distributions.LogNormalDistributionModel",
        S="@RelaxedClockSigma",
        # TODO: This does not give a mean clock rate of 1. It should be changed
        # to M=1.0, meanInRealSpace="true"
        M="1.0",
        meanInRealSpace="true",
    )

    state = root.find(".//state[@id='state']")
    clock_sigma = ET.SubElement(
        state,
        "parameter",
        id="RelaxedClockSigma",
        spec="parameter.RealParameter",
        lower="0.0",
        name="stateNode",
    )
    clock_sigma.text = "0.2"
    clock_rates = ET.SubElement(
        state,
        "parameter",
        id="RelaxedClockBranchRates",
        spec="parameter.RealParameter",
        lower="0.0",
        name="stateNode",
    )
    clock_rates.text = " 1.0" * (count_languages(root) * 2)

    prior = root.find(".//distribution[@id='prior']")
    # TODO: This seems to be redundant with the ClockRatesPrior??? We don't
    # know why it needs to be in there twice, with potentially different specs,
    # and have contacted Jordan Douglas to find out.
    ratesprior = ET.SubElement(
        prior,
        "prior",
        spec="Prior",
        id="RelaxedClockBranchRatesPrior",
        name="distribution",
        x="@RelaxedClockBranchRates",
    )
    ET.SubElement(
        ratesprior,
        "distr",
        id="LogNormal.RelaxedClockBranchRates",
        spec="beast.math.distributions.LogNormalDistributionModel",
        S="@RelaxedClockSigma",
        M="1.0",
        meanInRealSpace="true",
    )
    sigmaprior = ET.SubElement(
        prior,
        "prior",
        spec="Prior",
        id="RelaxedClockSigmaPrior",
        name="distribution",
        x="@RelaxedClockSigma",
    )
    ET.SubElement(
        sigmaprior,
        "distr",
        id="Gamma.RelaxedClockSigma",
        spec="beast.math.distributions.Gamma",
        # Where did these numbers come from? I copied them from the TAP analysis.
        alpha="0.5396",
        beta="0.3819",
    )

    logger = root.find(".//logger[@id='tracelog']")
    ET.SubElement(
        logger,
        "log",
        idref="RelaxedClockSigma",
    )
    ET.SubElement(
        logger,
        "log",
        id="RatesStat",
        spec="beast.evolution.branchratemodel.RateStatistic",
        branchratemodel=f"@{id}",
        tree="@tree",
    )

    ET.SubElement(
        root, "kernel", id="BactrianKernel", spec="KernelDistribution$Bactrian"
    )
    ET.SubElement(
        root,
        "metric",
        id="RobinsonsFould",
        spec="beast.evolution.tree.RobinsonsFouldMetric",
        taxonset="@taxa",
    )

    operators = root.find(".//operator").getparent()
    operator = ET.SubElement(
        operators,
        "operator",
        id="ORCAdaptableOperatorSampler_sigma",
        spec="orc.operators.AdaptableOperatorSampler",
        weight="3.0",
        parameter="@RelaxedClockSigma",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCucldStdevScaler",
        spec="consoperators.UcldScalerOperator",
        distr="@ClockRatesPrior",
        rates="@RelaxedClockBranchRates",
        scaleFactor="0.5",
        stdev="@RelaxedClockSigma",
        weight="1.0",
        kernel="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCUcldStdevRandomWalk",
        spec="BactrianRandomWalkOperator",
        parameter="@RelaxedClockSigma",
        scaleFactor="0.1",
        weight="1.0",
        kernelDistribution="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCUcldStdevScale",
        spec="BactrianScaleOperator",
        parameter="@RelaxedClockSigma",
        scaleFactor="0.5",
        upper="10.0",
        weight="1.0",
        kernelDistribution="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCSampleFromPriorOperator_sigma",
        spec="orc.operators.SampleFromPriorOperator",
        parameter="@RelaxedClockSigma",
        prior2="@RelaxedClockSigmaPrior",
        weight="1.0",
    )

    operator = ET.SubElement(
        operators,
        "operator",
        id="ORCAdaptableOperatorSampler_rates_root",
        spec="orc.operators.AdaptableOperatorSampler",
        tree="@tree",
        weight="0.1",
        parameter="@RelaxedClockBranchRates",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCRootOperator1",
        spec="consoperators.SimpleDistance",
        clockModel=f"@{id}",
        rates="@RelaxedClockBranchRates",
        tree="@tree",
        twindowSize="0.005",
        weight="1.0",
        kernel="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCRootOperator2",
        spec="consoperators.SmallPulley",
        clockModel=f"@{id}",
        dwindowSize="0.005",
        rates="@RelaxedClockBranchRates",
        tree="@tree",
        weight="1.0",
        kernel="@BactrianKernel",
    )

    operator = ET.SubElement(
        operators,
        "operator",
        id="ORCAdaptableOperatorSampler",
        spec="orc.operators.AdaptableOperatorSampler",
        tree="@tree",
        weight="20.0",
        parameter="@RelaxedClockBranchRates",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCInternalnodesOperator",
        spec="consoperators.InConstantDistanceOperator",
        clockModel=f"@{id}",
        rates="@RelaxedClockBranchRates",
        tree="@tree",
        twindowSize="0.005",
        weight="1.0",
        kernel="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCRatesRandomWalk",
        spec="BactrianRandomWalkOperator",
        parameter="@RelaxedClockBranchRates",
        scaleFactor="0.1",
        weight="1.0",
        kernelDistribution="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCRatesScale",
        spec="BactrianScaleOperator",
        parameter="@RelaxedClockBranchRates",
        scaleFactor="0.5",
        upper="10.0",
        weight="1.0",
        kernelDistribution="@BactrianKernel",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCSampleFromPriorOperator",
        spec="orc.operators.SampleFromPriorOperator",
        parameter="@RelaxedClockBranchRates",
        prior2="@RelaxedClockBranchRatesPrior",
        weight="1.0",
    )

    operator = ET.SubElement(
        operators,
        "operator",
        id="ORCAdaptableOperatorSampler_NER.c:clock",
        spec="orc.operators.AdaptableOperatorSampler",
        tree="@tree",
        weight="15.0",
        metric="@RobinsonsFould",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCNER_Exchange",
        spec="SAExchange",
        tree="@tree",
        weight="0.0",
    )
    ET.SubElement(
        operator,
        "operator",
        id="ORCNER_dAE_dBE_dCE",
        spec="orc.ner.NEROperator_dAE_dBE_dCE",
        rates="@RelaxedClockBranchRates",
        tree="@tree",
        weight="1.0",
    )

    logger = root.find(".//log[@spec='beast.evolution.tree.TreeWithMetaDataLogger']")
    logger.set("branchratemodel", f"@{id}")

    return root


if __name__ == "__main__":
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(
        description="Replace a strict clock with an optimized relaxed clock"
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
