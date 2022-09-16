#!/usr/bin/env python3

from Bio import AlignIO
import argparse


class ErodeAlignment(object):
    """Class representing an alignment"""

    def __init__(self, align):
        self.align = align
        self.numseqs = len(align)
        self.conservation = []
        self.confidence = []
        self.alignlen = len(align[0])
        self.erodestart = -1
        self.erodeend = 10000000000
        for i in range(self.alignlen):
            col = align[:, i]
            colstr = "".join(col).upper()
            Ds = colstr.count("-")
            ns = self.numseqs-Ds

            As = float(colstr.count("A"))/ns
            Cs = float(colstr.count("C"))/ns
            Gs = float(colstr.count("G"))/ns
            Us = float(colstr.count("U")+colstr.count("T"))/ns
            self.conservation.append(max(As, Cs, Gs, Us))
            self.confidence.append((1-(float(Ds)/self.numseqs)))

    def __repr__(self):
        "Generate a printable representation of a Alignment object"
        return f"Alignment: len={self.alignlen} numseq={self.numseqs}"

    def pretty(self):
        '''Generate a pretty printable representation of a alignment object
        suitable for output of the program. The output can be a tab-delimited
        string
        Arguments:
        Result:
           A string suitable for pretty printed output
        '''
        return "\n".join([" ".join([f"{x:.2f}" for x in self.conservation]), " ".join([f"{x:.2f}" for x in self.confidence])])

    def erode(self, win, cons_threshold, confidence_threshold):
        inregion = False
        for pos in range(self.alignlen-win):
            confids = self.confidence[pos:pos+win]
            if sum(confids)/len(confids) < confidence_threshold:
                continue

            conservs = self.conservation[pos:pos+win]
            if sum(conservs) / len(conservs) >= cons_threshold and not inregion:
                inregion = True
                self.erodestart = pos
                break

        inregion = False
        for pos in reversed(range(win, self.alignlen)):
            confids = self.confidence[pos-win:pos]
            if sum(confids)/len(confids) < confidence_threshold:
                continue

            conservs = self.conservation[pos-win:pos]
            if sum(conservs) / len(conservs) >= cons_threshold and not inregion:
                inregion = True
                self.erodeend = pos
                break

        if self.erodestart != -1:
            return self.align[:, self.erodestart:self.erodeend]
        else:
            return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", help="Input multialignment file in FASTA format")
    parser.add_argument(
        "-w", help="Window size to calculate confidence and conservation")
    parser.add_argument(
        "-c", help="Conservation threshold 0.0 - 1.0")
    parser.add_argument(
        "-f", help="Confidence threshold 0.0 - 1.0")
    parser.add_argument(
        "-o", help="New multi-alignment file")
    args = parser.parse_args()

    align = AlignIO.read(args.i, "fasta")
    myalign = ErodeAlignment(align)
    #  print(myalign)
    # print(myalign.pretty())
    eroded = myalign.erode(int(args.w), float(args.c), float(args.f))
    if eroded != None:
        AlignIO.write(eroded, args.o, "fasta")
    else:
        print("There was no erosion")
