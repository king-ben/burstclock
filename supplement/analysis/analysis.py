import argparse
import csv
import itertools
from collections import defaultdict
from pathlib import Path

import numpy
from arviz import ess
from matplotlib import pyplot as plt

FAMILIES = [
    "Austronesian",
    "Bantu",
    "Indo-European",
    "Sino-Tibetan",
]

# Harmonic Mean Estimator?


class BeastLogDialect(csv.Dialect):
    """The CSV dialect for BEAST2 log files."""

    delimiter = "\t"
    quoting = csv.QUOTE_MINIMAL
    quotechar = '"'
    lineterminator = "\n"


class Unconverged(ValueError):
    """Raised when an MCMC run has not converged, so analyses are invalid."""


def family_to_path(family: str) -> str:
    """Apply our naming convention for file paths.

    >>> family_to_path('Sino-Tibetan')
    'sinotibetan'

    """
    return family.replace("-", "").lower()


def read_logfile(vocabulary: Path, r: bool, b: bool, threshold: float = 200):
    log: dict[str, list[float]] = defaultdict(list)
    csvfile = csv.DictReader(
        (r for r in vocabulary.open() if not r.startswith("#") if "\0" not in r),
        dialect=BeastLogDialect,
    )
    fieldnames = csvfile.fieldnames[:]
    if b:
        fieldnames.append("Years")
    if r:
        fieldnames.append("clock_std")
    fieldnames.append("clockrate_est")
    fieldnames.append("yearloss")

    step = None
    previous = None
    deviation = 0
    write_back_fixed = csv.DictWriter(
        vocabulary.with_suffix(".log2").open("w"), fieldnames, dialect=BeastLogDialect
    )
    write_back_fixed.writeheader()
    for n_row, row in enumerate(csvfile):
        row["Sample"] = int(row["Sample"])
        if step is None and previous is None:
            previous = row["Sample"]
        elif step is None and previous is not None:
            step = int(row["Sample"]) - previous
            previous = row["Sample"]
        elif row["Sample"] - previous - step != deviation:
            if args.print_expected:
                print(
                    "Expected", previous + step + deviation, "but found", row["Sample"]
                )
            previous = previous + step
            deviation = row["Sample"] - previous
            row["Sample"] = previous
        else:
            previous = previous + step
            row["Sample"] = previous

        if b:
            row["perSplit"] = max(float(row["perSplit"]), 0)
            row["Years"] = row["perSplit"] / float(row["clockrate"])
        if r:
            row["clockrate_est"] = row["RatesStat.mean"]
            row["clock_std"] = float(row["RatesStat.variance"]) ** 0.5
        else:
            row["clockrate_est"] = row["clockrate"]

        row["yearloss"] = (1 - (1 - float(row["lossrate"])) ** 1000) * 100

        for key, value in row.items():
            try:
                log[key].append(float(value))
            except ValueError:
                pass

        write_back_fixed.writerow(row)
    unconverged = False
    perSplit_ess = None
    for key, value in log.items():
        if key == "perSplit_ess":
            continue
        log[key] = value[int(round(len(value) * BURNIN)) :]
        neff = ess(numpy.array(log[key]), method="bulk")
        if key != "Sample" and neff < threshold:
            print(f"Effective sample size of {key:} in {vocabulary:} was {neff:}")
            unconverged = True
        if key == "perSplit":
            perSplit_ess = neff
    if unconverged:
        print(
            vocabulary.relative_to(Path("/home/gereon/BigData/burstclock-runs/")).parent
        )
        return {"n_samples_unconverged": [int(row["Sample"])]}
        raise Unconverged()
    if perSplit_ess:
        log["perSplit_ess"] = [perSplit_ess]
    log["n_samples"] = [int(row["Sample"])]
    return log


def get_runtime(path):
    """Extract the mean time per Msample from all screenlogs.

    The estimated run time per Megasample is logged in the screenlog by beast,
    which gets turned into a .out file in the run directory by Slurm. This
    function returns the mean run time in hours per megasample for a particular
    run directory, aggregating from all available estimates in all available
    .out files in the directory.

    """
    times = []
    for slurm in path.glob("*.out"):
        with slurm.open() as run_log:
            for line in run_log:
                if "Msample" in line:
                    time = line.split()[-1][:-10]
                    m, s = time.split("m")
                    if "h" in m:
                        h, m = m.split("h")
                        m = int(h) * 60 + int(m)
                    else:
                        m = int(m)
                    times.append(m + int(s) / 60)
    return sum(times) / len(times) / 60


def extract_statistics(path: Path, threshold: float = 200) -> dict[str, list[float]]:
    basename = path.stem
    summaries = defaultdict(list)
    for r in [False, True]:
        r_string = ["", "-relaxed"][r]
        for b in [False, True]:
            b_string = ["", "-burstclock"][b]
            log: dict[str, list[float]] = defaultdict(list)
            for i in range(1, 10):
                file = path / f"{basename:}{r_string}{b_string}-{i}"
                if not file.exists():
                    continue
                runtime = get_runtime(file)
                vocabulary = file / "vocabulary.log"
                log_one_run = read_logfile(vocabulary, r, b, threshold)
                for key, value in log_one_run.items():
                    log[key].extend(value)
                # print(
                #     runtime,
                #     log["n_samples"][-1] / 1_000_000,
                #     runtime * log["n_samples"][-1] / 1_000_000,
                # )
                try:
                    summaries[
                        "Runtime "
                        + ("(relaxed" if r else "(strict")
                        + (" with bursts)" if b else ", no bursts)")
                    ].append(runtime * log["n_samples"][-1] / 1_000_000)
                except IndexError:
                    summaries[
                        "Runtime, incomplete "
                        + ("(relaxed" if r else "(strict")
                        + (" with bursts)" if b else ", no bursts)")
                    ].append(runtime * log["n_samples_unconverged"][-1] / 1_000_000)
                summaries[
                    "Tree height "
                    + ("(relaxed" if r else "(strict")
                    + (" with bursts)" if b else ", no bursts)")
                ] = log["TreeHeight"]
            if not log["yearloss"]:
                continue
            if b:
                summaries[
                    "Years per split " + ("(relaxed)" if r else "(strict)")
                ] = log["Years"]
                summaries[
                    "Changes per split " + ("(relaxed)" if r else "(strict)")
                ] = numpy.quantile(
                    [x for x in log["perSplit"] if x > 0], [0.05, 0.5, 0.95]
                )
                summaries[
                    "ESS of burst parameter " + ("(relaxed)" if r else "(strict)")
                ] = numpy.min(log["perSplit_ess"])
                summaries["Bursts " + ("(relaxed)" if r else "(strict)")] = [
                    numpy.mean(numpy.array(log["perSplit"]) > 0)
                ]
            if r:
                summaries[
                    "Standard deviation of the clock relaxation "
                    + ("(with bursts)" if b else "(no bursts)")
                ] = log["RelaxedClockSigma"]
            summaries[
                "Loss per 1000 years "
                + ("(relaxed" if r else "(strict")
                + (" with bursts)" if b else ", no bursts)")
            ] = log["yearloss"]
            summaries[
                "Clock rate "
                + ("(relaxed" if r else "(strict")
                + (" with bursts)" if b else ", no bursts)")
            ] = log["clockrate_est"]
    plt.figure(figsize=(4, 6))
    plt.boxplot(
        [
            summaries["Years per split (strict)"],
            summaries["Years per split (relaxed)"],
        ],
        showfliers=False,
        widths=0.7,
    )
    plt.xticks([1, 2], ["strict", "relaxed"])
    plt.ylim(bottom=0)
    plt.savefig(
        Path(__file__).parent / f"{basename}_years_per_split.png", bbox_inches="tight"
    )
    if args.show:
        plt.show()
    else:
        plt.close()

    plt.figure(figsize=(6, 4))
    plt.title("Tree height")
    plt.boxplot(
        [
            summaries["Tree height (strict, no bursts)"],
            summaries["Tree height (relaxed, no bursts)"],
            summaries["Tree height (strict with bursts)"],
            summaries["Tree height (relaxed with bursts)"],
        ],
        showfliers=False,
        widths=0.7,
    )
    plt.xticks(
        [1, 2, 3, 4],
        [
            "strict,\nno bursts",
            "relaxed,\nno bursts",
            "strict\nwith bursts",
            "relaxed\nwith bursts",
        ],
    )
    plt.ylim(bottom=0)
    plt.savefig(
        Path(__file__).parent / f"{basename}_treeheight.png", bbox_inches="tight"
    )

    plt.figure(figsize=(6, 4))
    plt.boxplot(
        [
            summaries["Clock rate (strict, no bursts)"],
            summaries["Clock rate (relaxed, no bursts)"],
            summaries["Clock rate (strict with bursts)"],
            summaries["Clock rate (relaxed with bursts)"],
        ],
        showfliers=False,
        widths=0.7,
    )
    plt.xticks(
        [1, 2, 3, 4],
        [
            "strict,\nno bursts",
            "relaxed,\nno bursts",
            "strict\nwith bursts",
            "relaxed\nwith bursts",
        ],
    )
    plt.ylim(bottom=0)
    plt.savefig(
        Path(__file__).parent / f"{basename}_clockrates.png", bbox_inches="tight"
    )

    plt.figure(figsize=(6, 4))
    plt.title("Standard deviation of the clock relaxation")
    plt.boxplot(
        [
            summaries["Standard deviation of the clock relaxation (with bursts)"],
            summaries["Standard deviation of the clock relaxation (no bursts)"],
        ],
        showfliers=False,
        widths=0.7,
    )
    plt.xticks(
        [1, 2],
        [
            "relaxed,\nno bursts",
            "relaxed\nwith bursts",
        ],
    )
    plt.ylim(bottom=0)
    plt.savefig(
        Path(__file__).parent / f"{basename}_clockrates.png", bbox_inches="tight"
    )

    plt.figure(figsize=(6, 4))
    plt.boxplot(
        [
            summaries["Loss per 1000 years (strict, no bursts)"],
            summaries["Loss per 1000 years (relaxed, no bursts)"],
            summaries["Loss per 1000 years (strict with bursts)"],
            summaries["Loss per 1000 years (relaxed with bursts)"],
        ],
        showfliers=False,
        widths=0.7,
    )
    plt.xticks(
        [1, 2, 3, 4],
        [
            "strict,\nno bursts",
            "relaxed,\nno bursts",
            "strict\nwith bursts",
            "relaxed\nwith bursts",
        ],
    )
    plt.ylim(bottom=0, top=38)
    plt.savefig(
        Path(__file__).parent / f"{basename}_replacement.png", bbox_inches="tight"
    )
    if args.show:
        plt.show()
    else:
        plt.close()
    return dict(summaries)


parser = argparse.ArgumentParser()
parser.add_argument("ess_threshold", type=float, nargs="?", default=200)
parser.add_argument("--burnin", type=float, default=0.1)
parser.add_argument("--print-expected", default=False, action="store_true")
parser.add_argument("--show", default=False, action="store_true")
args = parser.parse_args()
BURNIN = args.burnin

min_05 = 1
max_95 = 0
min_ess = numpy.inf
max_ess = 0
p_bursts = []

runtimes = []
incomplete_runtimes = []
for f, family in enumerate(FAMILIES):
    path = Path.home() / "BigData" / "burstclock-runs" / family_to_path(family)
    s = extract_statistics(path, threshold=args.ess_threshold)

    runtimes.extend(
        [
            s.get("Runtime (strict, no bursts)", numpy.nan),
            s.get("Runtime (relaxed, no bursts)", numpy.nan),
            s.get("Runtime (strict with bursts)", numpy.nan),
            s.get("Runtime (relaxed with bursts)", numpy.nan),
        ],
    )

    incomplete_runtimes.extend(
        [
            s.get("Runtime, incomplete (strict, no bursts)", [numpy.nan]),
            s.get("Runtime, incomplete (relaxed, no bursts)", [numpy.nan]),
            s.get("Runtime, incomplete (strict with bursts)", [numpy.nan]),
            s.get("Runtime, incomplete (relaxed with bursts)", [numpy.nan]),
        ],
    )

    try:
        if s["Changes per split (relaxed)"][0] < min_05:
            min_05 = s["Changes per split (relaxed)"][0]
            min_05_run = f"{family} (relaxed)"
        if s["Changes per split (strict)"][0] < min_05:
            min_05 = s["Changes per split (strict)"][0]
            min_05_run = f"{family} (strict)"
        if s["Changes per split (relaxed)"][2] > max_95:
            max_95 = s["Changes per split (relaxed)"][2]
            max_95_run = f"{family} (relaxed)"
        if s["Changes per split (strict)"][2] > max_95:
            max_95 = s["Changes per split (strict)"][2]
            max_95_run = f"{family} (strict)"
        if numpy.min(s["Bursts (relaxed)"]) == 1:
            if s["ESS of burst parameter (relaxed)"] > max_ess:
                max_ess = s["ESS of burst parameter (relaxed)"]
                max_ess_run = f"{family} (relaxed)"
            if s["ESS of burst parameter (relaxed)"] < min_ess:
                min_ess = s["ESS of burst parameter (relaxed)"]
                min_ess_run = f"{family} (relaxed)"
        else:
            for p in s["Bursts (relaxed)"]:
                p_bursts.append(p / (1 - p))
        if numpy.min(s["Bursts (strict)"]) == 1:
            if s["ESS of burst parameter (strict)"] > max_ess:
                max_ess = s["ESS of burst parameter (strict)"]
                max_ess_run = f"{family} (strict)"
            if s["ESS of burst parameter (strict)"] < min_ess:
                min_ess = s["ESS of burst parameter (strict)"]
                min_ess_run = f"{family} (strict)"
        else:
            for p in s["Bursts (strict)"]:
                p_bursts.append(p / (1 - p))

    except KeyError:
        print(f"Error: Family {family} does not have converged data.")


plt.figure(figsize=(8, 4))
plt.scatter(
    [x for x, ys in enumerate(runtimes) for y in ys],
    [y for ys in runtimes for y in ys],
    edgecolors="k",
    facecolors="k",
)
plt.scatter(
    [x for x, ys in enumerate(incomplete_runtimes) for y in ys],
    [y for ys in incomplete_runtimes for y in ys],
    marker="o",
    edgecolors="k",
    facecolors="none",
)
plt.xticks(
    range(0, 4 * len(FAMILIES)),
    [
        "strict\nno bursts",
        "relaxed\nno bursts",
        "strict\nwith bursts",
        "relaxed\nwith bursts",
    ]
    * len(FAMILIES),
    rotation=90,
    fontdict={"multialignment": "right"},
)
plt.ylim(bottom=0)
plt.savefig(Path(__file__).parent / "runtimes.png", bbox_inches="tight")
if args.show:
    plt.show()
else:
    plt.close()

with (Path(__file__).parent / "stats.tex").open("w") as stats:
    print(r"\newcommand{\minx}{%f}" % min_05, file=stats)
    print(r"\newcommand{\minn}{%s}" % min_05_run, file=stats)
    print(r"\newcommand{\maxx}{%f}" % max_95, file=stats)
    print(r"\newcommand{\maxn}{%s}" % max_95_run, file=stats)
    print(r"\newcommand{\minessx}{%0.0f}" % min_ess, file=stats)
    print(r"\newcommand{\minessn}{%s}" % min_ess_run, file=stats)
    print(r"\newcommand{\maxessx}{%0.0f}" % max_ess, file=stats)
    print(r"\newcommand{\maxessn}{%s}" % max_ess_run, file=stats)
    print(r"\newcommand{\worstburst}{%0.1f}" % numpy.min(p_bursts), file=stats)
