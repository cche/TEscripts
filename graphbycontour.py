#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_file(filename):
    """Parse the onecode output and return all lines starting with ###"""
    lines = []
    with open(filename) as fi:
        header = fi.readline()
        lines.extend(line for line in fi if line.startswith("###"))
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse RepeatMasker .out file and graph percent similarity by repeat family"
    )
    parser.add_argument("-i", help="Onecode .elem_sorted.csv file")
    parser.add_argument("-b", help="Number of bins")
    parser.add_argument("-s", help="Size of image in WxH in inches")
    parser.add_argument("-f", default="", help="Class to filter")
    parser.add_argument("-o", help="Filename for graph")
    args = parser.parse_args()

    size = args.s.split("x")
    W = int(size[0])
    H = int(size[1])

    tdf = pd.read_csv(
        args.i,
        sep="\t",
        usecols=["ID", "%_Div", "Element", "Family", "%_of_Ref", "Score"],
        index_col="ID",
    )
    df = tdf[tdf.Score.str.startswith("###")]

    fig, ax = plt.subplots(1, 1)
    if args.f != "":
        dd = df[df["Element"] == args.f]
        # dd["%_Div"].hist(bins=int(args.b), by=dd["Element"])
        hist, xedges, yedges = np.histogram2d(
            dd["%_Div"],
            dd["%_of_Ref"] * 100,
            bins=[20, int(args.b)],
            range=[[0, 20], [0, 100]],
        )
        # Construct arrays for the anchor positions of the 16 bars.
        # xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
        xpos, ypos = np.meshgrid(xedges[:-1], yedges[:-1])
        # xpos = xpos.ravel()
        # ypos = ypos.ravel()
        zpos = 0
        print(xpos)
        print(ypos)
        # print(zpos)

        # Construct arrays with the dimensions for the 16 bars.
        dx = dy = 0.5 * np.ones_like(zpos)
        # dz = hist.ravel()
        dz = hist.transpose()
        # print(dx)
        # print(dy)
        print(dz)

        cp = ax.contourf(xpos, ypos, dz, levels=20)
        print(cp)
        fig.colorbar(cp)
        ax.set_title(f"Distance plot - {args.f}")
    else:
        dd = df
        # plt.figure()
        dd["%_Div"].hist(bins=int(args.b), by=dd["Family"])
    # plt.show()
    plt.savefig(args.o, dpi=300)
