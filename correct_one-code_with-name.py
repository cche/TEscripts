#!/usr/bin/env python3

import argparse
from typing import NamedTuple

parser = argparse.ArgumentParser(
    description="Parse one-code output and eliminate lines that are contained in previously identified loci"
)
parser.add_argument("-i", help="One code output file")
parser.add_argument("-o", help="Output file name")
options = parser.parse_args()


class Element:
    def __init__(self, line, support):
        F = line.strip().split("\t")
        self.line = line
        self.chrom = F[4]
        self.parts = F[0]
        self.start = int(F[5])
        self.stop = int(F[6])
        self.fam = F[9]
        self.support = support

    def containedIn(self, previous):
        if self.chrom == previous.chrom:
            return (previous.start <= self.start) and (previous.stop >= self.stop)
        else:
            return False


chroms = {}
outlines = []
header = ""

# Parse data
with open(options.i) as fi:
    for line in fi:
        if line.startswith("Score"):
            header = line
            continue
        supportlines = []
        if not line.startswith("###"):
            continue

        numparts = len(line.split("\t")[0].split("/"))
        if numparts > 1:
            supportlines.extend(fi.readline() for _ in range(numparts))
        newelem = Element(line, supportlines)
        if newelem.chrom not in chroms:
            chroms[newelem.chrom] = [newelem]
        elif not newelem.containedIn(chroms[newelem.chrom][-1]):
            chroms[newelem.chrom].append(newelem)

# Produce output
with open(options.o, "w") as fo:
    fo.write(header)
    for ch in chroms:
        # write all elements to output
        for elem in chroms[ch]:
            # Get internal part to name the LTR element
            if elem.fam.endswith("_LTR") or elem.fam.endswith("_I"):
                if elem.fam.endswith("_LTR"):
                    newfam = elem.fam[:-4]
                if elem.fam.endswith("_I"):
                    newfam = elem.fam[:-2]
                tmpline = elem.line.split("\t")
                tmpline[9] = newfam
                elem.line = "\t".join(tmpline)
            fo.write(elem.line)
            # Write all supporting lines
            for sl in elem.support:
                fo.write(sl)
            fo.write("\n")
