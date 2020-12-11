import sys
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

from tqdm import tqdm
import pycldf
import pyglottolog
from cldfcatalog import Catalog

parser = argparse.ArgumentParser(
    description="Export a CLDF dataset (or similar) to bioinformatics alignments"
)
parser.add_argument(
    "--output-file",
    "-o",
    type=Path,
    help="""File to write output to. (If output file exists, add tags in there.) Default: Write to stdout""",
)
args = parser.parse_args(["-o", "austronesian.xml"])

ds = pycldf.Wordlist.from_metadata("raw_cldf/cldf-metadata.json")

langs = {l.strip() for l in sys.stdin}

with Catalog.from_config('glottolog', tag='v4.3') as glottolog_repo:
    glottolog = pyglottolog.Glottolog(glottolog_repo.dir)
    languages = {}
    for language in tqdm(ds["LanguageTable"], total=ds["LanguageTable"].common_props['dc:extent']):
        id = language["ID"]
        if id not in langs:
            continue
        family = language["Family"]
        if family != "Austronesian":
            continue
        languoid = glottolog.languoid(language["Glottocode"])
        ancestors = languoid.ancestors
        languages[id] = [languoid.id] + [a.id for a in ancestors]

for lang in languages:
    print(lang)


if args.output_file is None:
    root = ET.fromstring('''
    <beast><tree /><run><distribution id="posterior" spec="util.CompoundDistribution"><distribution id="prior" spec="util.CompoundDistribution" /></distribution></run></beast>
    ''')
    et = ET.ElementTree(root)
elif args.output_file.exists():
    et = ET.parse(args.output_file)
    root = et.getroot()
else:
    root = ET.fromstring('''
    <beast><tree /><run><distribution id="posterior" spec="util.CompoundDistribution"><distribution id="prior" spec="util.CompoundDistribution" /></distribution></run></beast>
    ''')
    et = ET.ElementTree(root)

prior = list(root.iter("distribution"))[1]
assert prior.attrib["id"] == "prior"

run = list(root.iter("run"))[0]

traits = list(root.iter("trait"))
if not traits:
    tree = list(root.iter("tree"))[0]
    trait = ET.SubElement(tree, "trait", id="datetrait", spec="beast.evolution.tree.TraitSet", taxa="@taxa", traitname="date-backward")
else:
    trait = traits[0]
    assert trait.attrib["traitname"] == "date-backward"


def calibration(mean, std, languages=languages, glottolog_clade=None):
    if glottolog_clade is not None:
        languages = {l for l, lineage in languages.items() if glottolog_clade in lineage}
    if len(languages) == 0:
        return
    elif len(languages) == 1:
        language = list(languages)[0]
        if glottolog_clade:
            mrcaprior = ET.SubElement(prior, "distribution", id=f"{language:}_originateMRCA", monophyletic="true", spec="beast.math.distributions.MRCAPrior", tree="@Tree.t:beastlingTree", useOriginate="true")
            taxonset = ET.SubElement(mrcaprior, "taxonset", id=f"tx_{language:}", spec="TaxonSet")
            ET.SubElement(taxonset, "taxon", id=f"{language:}", spec="Taxon")
            ET.SubElement(mrcaprior, "Normal", name="distr", offset="0.0", mean=f"{mean:}", sigma=f"{std:}")
        else:
            if not trait.text:
                trait.text = ''
            trait.text += f"\n{language:} = {mean:}"

            op = ET.SubElement(run, "operator", id=f"TipDatesandomWalker:{language:}", spec="TipDatesRandomWalker", windowSize="1", tree="@Tree.t:beastlingTree", weight="3.0")
            ET.SubElement(op, "taxonset", idref=f"{language:}_tip")

            mrcaprior = ET.SubElement(prior, "distribution", id=f"{language:}_tipMRCA", monophyletic="true", spec="beast.math.distributions.MRCAPrior", tree="@Tree.t:beastlingTree", tipsonly="true")
            taxonset = ET.SubElement(mrcaprior, "taxonset", id=f"{language:}_tip", spec="TaxonSet")
            ET.SubElement(taxonset, "taxon", id=f"{language:}", spec="Taxon")
            ET.SubElement(mrcaprior, "Normal", name="distr", offset="0.0", mean=f"{mean:}", sigma=f"{std:}")
    else:
        mrcaprior = ET.SubElement(prior, "distribution", id=f"{glottolog_clade:}_tipMRCA", monophyletic="true", spec="beast.math.distributions.MRCAPrior", tree="@Tree.t:beastlingTree")
        taxonset = ET.SubElement(mrcaprior, "taxonset", id=f"{glottolog_clade}", spec="TaxonSet")
        plate = ET.SubElement(taxonset, "plate", range=",".join(languages), var="language")
        ET.SubElement(taxonset, "taxon", id="$(language)", spec="Taxon")
        ET.SubElement(mrcaprior, "Normal", name="distr", offset="0.0", mean=f"{mean:}", sigma=f"{std:}")
    mrcaprior.tail="\n"

def ms(lower, upper):
    # Assume lower to upper is the 2 σ interval of a normal distribution
    return (lower + upper) / 2, (upper - lower) / 4

# ‘(i) Proto-Oceanic (mean of 3,300 y, SD = 100 y)’
# Development of Proto-Oceanic 3,200 – 3,600 [Lynch et al. (2002)]
# Oceanic: https://glottolog.org/resource/languoid/id/ocea1241
calibration(glottolog_clade="ocea1241", mean=3300, std=100)

# ‘(ii) Proto-Central Pacific (mean of 3,000 y, SD = 100)’
# Central Pacific linkage: https://glottolog.org/resource/languoid/id/cent2060
calibration(glottolog_clade="cent2060", mean=3000, std=100)

# ‘(iii) Proto-Malayo-Polynesian (mean of 4,000 y, SD = 250)’
# Austronesian Entry into the Philippines (Proto-Malayo-Polynesian) 3,600 – 4,500 [Pawley (2002)]
# Malayo-Polynesian: https://glottolog.org/resource/languoid/id/mala1545
calibration(glottolog_clade="mala1545", mean=4000, std=250)

# ‘(iv) Proto-Micronesian (mean of 2,000 y, SD = 100)’
# Micronesian: https://glottolog.org/resource/languoid/id/micr1243
calibration(glottolog_clade='micr1243', mean=2000, std=100)

# ‘(v) Proto-Austronesian (mean of 5,200 y, SD = 300)’
# Austronesian: https://glottolog.org/resource/languoid/id/aust1307
calibration(glottolog_clade='aust1307', mean=5200, std=300)

# Favorlang 346 – 384 [Age of Source Data]
# https://abvd.shh.mpg.de/austronesian/language.php?id=831 “In Ogawa & Li (2003), Some data may have also been derived from Dutch sources (missionary tracts, etc.) dating from the mid-1600's.”
calibration(*ms(346, 384), {'831'})

# Siraya 346 – 384 [Age of Source Data]
# https://abvd.shh.mpg.de/austronesian/language.php?id=1517: “This is one of the two oldest and best documented sources (originally compiled in 17th century). The other is the Gospel dialect ( Gravius 1661)” (i.e. https://abvd.shh.mpg.de/austronesian/language.php?id=1519, which does not cite its source)
calibration(*ms(346, 384), {'1517'})
calibration(2000-1661, (384-346)/4, {'1519'})

# Old Javanese 700 – 1,200 [Zoetmulder (1982)]
# https://abvd.shh.mpg.de/austronesian/language.php?id=290
calibration(*ms(700, 1200), {'290'})

# Settlement of Madagascar 1,100 – 1,300 [Vérin & Wright (1999)]
# Malagasic: https://glottolog.org/resource/languoid/id/mala1537
calibration(*ms(1100, 1300), glottolog_clade='mala1537')

# Proto-Javanese 1,100 – 1,300 [Zoetmulder (1982), Anderson & Sinoto (2002)]
# Modern Javanese: https://glottolog.org/resource/languoid/id/mode1251
calibration(*ms(1100, 1300), glottolog_clade='mode1251')

# Initial Settlement of Eastern Polynesia 1,150 – 1,800 [Green (2003), Kirch & Green (2001), Pawley (2002)]
# East Polynesian: https://glottolog.org/resource/languoid/id/east2449
calibration(*ms(1150, 1800), glottolog_clade='east2449')

# Habitation of Tuvalu/Tokelau becomes possible 1,000 – 2,000 Dickinson (2003)
# Ellicean [clade with Tuvalu and Samoan-Tokelauan]: https://glottolog.org/resource/languoid/id/elli1239
calibration(*ms(1000, 2000), glottolog_clade='elli1239')

# Historical Attestation of Chamic Subgroup 1,800 – 2,500 Thurgood (1999)
# Chamic: https://glottolog.org/resource/languoid/id/cham1330
calibration(*ms(1800, 2500), glottolog_clade='cham1330')

# Settlement of Micronesia 1,900 – 2,200 Pawley (2002)
# Micronesian: https://glottolog.org/resource/languoid/id/micr1243
calibration(*ms(1900, 2200), glottolog_clade='micr1243')

# Existence of Malayo-Chamic Subgroup 2,000 – 3,000 Thurgood (1999)
# North and East Malayo-Sumbawan [clade with Malayic and Chamic]: https://glottolog.org/resource/languoid/id/nort3170
calibration(*ms(2000, 3000), glottolog_clade='nort3170')

# Human settlement of the Reefs and Santa Cruz 3,000 – 3,150 Green et al. (2008)
# Reefs-Santa Cruz: https://glottolog.org/resource/languoid/id/reef1242
calibration(*ms(3000, 3150), glottolog_clade='reef1242')


et.write(args.output_file, encoding="unicode")
