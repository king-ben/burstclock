import sys
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

from tqdm import tqdm
import pycldf
import pyglottolog
from cldfcatalog import Catalog


def normal(mean, std):
    return dict(
        tag="Normal", name="distr", offset="0.0", mean=f"{mean:}", sigma=f"{std:}"
    )


def until(lower, upper):
    # Assume lower to upper is the 2 σ interval of a normal distribution
    mean, std = (lower + upper) / 2, (upper - lower) / 4
    return normal(mean, std)


def calibration(
        run, prior, trait, all_languages, d, languages=[], glottolog_clade=None, mean=0.0, name=None
):
    if glottolog_clade is not None:
        languages = {
            l for l, lineage in all_languages.items() if glottolog_clade in lineage
        }
    if name is None:
        if glottolog_clade is None:
            name = '_'.join(languages)
        else:
            name = glottolog_clade

    if mean == 0.0:
        mean = d.get("mean", mean)

    tag = d.pop('tag')

    if len(languages) == 0:
        return
    elif len(languages) == 1:
        language = list(languages)[0]
        if glottolog_clade:
            mrcaprior = ET.SubElement(
                prior,
                "distribution",
                id=f"{language:}_originateMRCA",
                monophyletic="true",
                spec="beast.math.distributions.MRCAPrior",
                tree="@Tree.t:tree",
                useOriginate="true",
            )
            taxonset = ET.SubElement(
                mrcaprior, "taxonset", id=f"tx_{language:}", spec="TaxonSet"
            )
            ET.SubElement(taxonset, "taxon", idref=f"{language:}")
            ET.SubElement(mrcaprior, tag, **d)
        else:
            if not trait.text or not trait.text.strip():
                trait.text = f"\n{language:} = {mean:}"
            else:
                trait.text += f",\n{language:} = {mean:}"

            op = ET.SubElement(
                run,
                "operator",
                id=f"TipDatesandomWalker:{language:}",
                spec="TipDatesRandomWalker",
                windowSize="1",
                tree="@Tree.t:tree",
                weight="3.0",
            )
            ET.SubElement(op, "taxonset", idref=f"{language:}_tip")

            mrcaprior = ET.SubElement(
                prior,
                "distribution",
                id=f"{language:}_tipMRCA",
                monophyletic="true",
                spec="beast.math.distributions.MRCAPrior",
                tree="@Tree.t:tree",
                tipsonly="true",
            )
            taxonset = ET.SubElement(
                mrcaprior, "taxonset", id=f"{language:}_tip", spec="TaxonSet"
            )
            ET.SubElement(taxonset, "taxon", idref=f"{language:}")
            ET.SubElement(mrcaprior, tag, **d)
    else:
        mrcaprior = ET.SubElement(
            prior,
            "distribution",
            id=f"{name}_tipMRCA",
            monophyletic="false",  # Should these be true?
            spec="beast.math.distributions.MRCAPrior",
            tree="@Tree.t:tree",
        )
        taxonset = ET.SubElement(
            mrcaprior, "taxonset", id=f"{name}", spec="TaxonSet"
        )
        plate = ET.SubElement(
            taxonset, "plate", range=",".join(languages), var="language"
        )
        ET.SubElement(plate, "taxon", idref="$(language)")
        ET.SubElement(mrcaprior, tag, **d)
    mrcaprior.tail = "\n"


def main(calibrations):
    parser = argparse.ArgumentParser(
        description="Export a CLDF dataset (or similar) to bioinformatics alignments"
    )
    parser.add_argument(
        "--family",
        "-f",
        help="""Only include languages within this Glottolog clade""",
    )
    parser.add_argument(
        "--subset",
        type=argparse.FileType('r'),
        help="A file (or '-' for stdin) containing one language to be included per line"
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=Path,
        help="""File to write output to. (If output file exists, add tags in there.) Default: Write to stdout""",
    )
    args = parser.parse_args()

    ds = pycldf.Wordlist.from_metadata("raw_cldf/cldf-metadata.json")

    if args.subset:
        langs = {l.strip() for l in args.subset}

    with Catalog.from_config("glottolog", tag="v4.3") as glottolog_repo:
        glottolog = pyglottolog.Glottolog(glottolog_repo.dir)
        languages = {}
        for language in tqdm(
            ds["LanguageTable"], total=ds["LanguageTable"].common_props["dc:extent"]
        ):
            id = language["ID"]
            if args.subset and id not in langs:
                continue
            try:
                languoid = glottolog.languoid(language["Glottocode"])
            except TypeError:
                continue
            ancestors = [languoid.id] + [a.id for a in languoid.ancestors]
            if args.family and args.family not in ancestors:
                continue
            languages[id] = ancestors

    if args.output_file is None:
        root = ET.fromstring(
            """
        <beast><tree /><run><distribution id="posterior" spec="util.CompoundDistribution"><distribution id="prior" spec="util.CompoundDistribution" /></distribution></run></beast>
        """
        )
        et = ET.ElementTree(root)
    elif args.output_file.exists():
        et = ET.parse(args.output_file)
        root = et.getroot()
    else:
        root = ET.fromstring(
            """
        <beast><tree /><run><distribution id="posterior" spec="util.CompoundDistribution"><distribution id="prior" spec="util.CompoundDistribution" /></distribution></run></beast>
        """
        )
        et = ET.ElementTree(root)

    prior = list(root.iter("distribution"))[1]
    assert prior.attrib["id"] == "prior"

    run = list(root.iter("run"))[0]

    traits = list(root.iter("trait"))
    if not traits:
        tree = list(root.iter("tree"))[0]
        trait = ET.SubElement(
            tree,
            "trait",
            id="datetrait",
            spec="beast.evolution.tree.TraitSet",
            taxa="@taxa",
            traitname="date-backward",
        )
    else:
        trait = traits[0]
        assert trait.attrib["traitname"] == "date-backward"

    taxa = ET.SubElement(root, "taxonset", id="taxa", spec="TaxonSet")
    for lang in languages:
        print(lang)
        ET.SubElement(taxa, "taxon", id=lang, spec="Taxon")

    for c in calibrations:
        calibration(run, prior, trait, languages, **c)

    et.write(args.output_file, encoding="unicode")
    return et, root, run, prior, trait, languages
