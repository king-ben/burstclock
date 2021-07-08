import csv
import argparse
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("logfile")
args = parser.parse_args()

rows = [
    (float(row["perSplit"]), float(row["clockrate"]))
    for row in csv.DictReader(filter(lambda x: not x.startswith("#"), open(args.logfile),), delimiter="\t")   
]

array = numpy.array(rows)
years =array[:, 0]/array[:, 1]
print(numpy.quantile(years, [0.05, 0.5, 0.95]), years.mean(), years.std())
