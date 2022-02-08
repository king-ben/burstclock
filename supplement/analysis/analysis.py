import csv
from pathlib import Path
from collections import defaultdict

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
    delimiter = "\t"
    quoting = csv.QUOTE_MINIMAL
    quotechar = '"'
    lineterminator = "\n"


def family_to_path(family: str) -> str:
    return family.replace("-", "").lower()


def read_logfile(vocabulary: Path, r: bool, b: bool, threshold: float = 200):
    log: dict[str, list[float]] = defaultdict(list)
    csvfile = csv.DictReader(
        (r for r in vocabulary.open() if not r.startswith("#") if '\0' not in r),
        dialect=BeastLogDialect,
    )
    fieldnames = csvfile.fieldnames[:]
    if b:
        fieldnames.append("Years")

    step = None
    previous = None
    deviation = 0
    write_back_fixed = csv.DictWriter(
        vocabulary.with_suffix(".log2").open("w"),
        fieldnames, dialect=BeastLogDialect)
    write_back_fixed.writeheader()
    for n_row, row in enumerate(csvfile):
        row["Sample"] = int(row["Sample"])
        if step is None and previous is None:
            previous = row["Sample"]
        elif step is None and previous is not None:
            step = int(row["Sample"]) - previous
            previous = row["Sample"]
        elif row["Sample"] - previous - step != deviation:
            print("Expected", previous + step + deviation, "but found", row["Sample"])
            previous = previous + step
            deviation = row["Sample"] - previous
            row["Sample"] = previous
        else:
            previous = previous + step
            row["Sample"] = previous
        
        for key, value in row.items():
            try:
                log[key].append(float(value))
            except ValueError:
                pass
        if b:
            row["perSplit"] = max(float(row["perSplit"]), 0)
            row["Years"] = row["perSplit"] / float(row["clockrate"])
            log["Years"].append(row["Years"])
        if r:
            log["clockrate_est"].append(float(row["RatesStat.mean"]))
            log["clock_std"].append(float(row["RatesStat.variance"]) ** 0.5)
        else:
            log["clockrate_est"].append(float(row["clockrate"]))

        write_back_fixed.writerow(row)
        log["lossrate"].append((1 - (1-float(row["lossrate"]))**1000) * 100)
    unconverged = False
    for key, value in log.items():
        log[key] = value[int(round(len(value)*BURNIN)):]
        neff = ess(numpy.array(log[key]), method="bulk")
        if key != "Sample" and neff < threshold:
            print(f"Effective sample size of {key:} in {vocabulary:} was {neff:}")
            unconverged = True
    if unconverged:
        print(
            vocabulary.relative_to(Path("/home/gereon/BigData/burstclock-runs/")).parent
        )
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
                vocabulary = file / "vocabulary.log"
                for key, value in read_logfile(vocabulary, r, b, threshold).items():
                    log[key].extend(value)
                runtime = get_runtime(file)
                print(
                    runtime,
                    log["n_samples"][-1] / 1_000_000,
                    runtime * log["n_samples"][-1] / 1_000_000,
                )
                summaries[
                    "Runtime "
                    + ("(relaxed" if r else "(strict")
                    + (" with bursts)" if b else ", no bursts)")
                ].append(runtime * log["n_samples"][-1] / 1_000_000)
            if b:
                summaries[
                    "Years per split " + ("(relaxed)" if r else "(strict)")
                ] = log["Years"]
            summaries[
                "Loss rate "
                + ("(relaxed" if r else "(strict")
                + (" with bursts)" if b else ", no bursts)")
            ] = log["lossrate"]
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
    plt.show()

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
    plt.boxplot(
        [
            summaries["Loss rate (strict, no bursts)"],
            summaries["Loss rate (relaxed, no bursts)"],
            summaries["Loss rate (strict with bursts)"],
            summaries["Loss rate (relaxed with bursts)"],
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
        Path(__file__).parent / f"{basename}_replacement.png", bbox_inches="tight"
    )
    plt.show()
    return summaries

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("ess_threshold",
        type=float, nargs="?", default=200)
parser.add_argument("--burnin", type=float, default=0.1)
args = parser.parse_args()
BURNIN = args.burnin

runtimes = []
for f, family in enumerate(FAMILIES):
    path = Path.home() / "BigData" / "burstclock-runs" / family_to_path(family)
    s = extract_statistics(path, threshold=args.ess_threshold)

    runtimes.extend(
        [
            s["Runtime (strict, no bursts)"],
            s["Runtime (relaxed, no bursts)"],
            s["Runtime (strict with bursts)"],
            s["Runtime (relaxed with bursts)"],
        ],
    )


plt.figure(figsize=(8, 4))
plt.scatter(
    [x for x, ys in enumerate(runtimes) for y in ys],
    [y for ys in runtimes for y in ys],
    # widths=0.7,
)
plt.xticks(
    range(1, 4 * len(FAMILIES) + 1),
    [
        "strict,\nno bursts",
        "relaxed,\nno bursts",
        "strict\nwith bursts",
        "relaxed\nwith bursts",
    ]
    * len(FAMILIES),
)
plt.ylim(bottom=0)
plt.savefig(Path(__file__).parent / f"runtimes.png", bbox_inches="tight")
plt.show()
