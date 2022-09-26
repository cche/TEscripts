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
    # print(df.head())

    fig = plt.figure(figsize=(W, H))
    plt.title("% similarity for " + args.f)
    ax = fig.add_subplot(111, projection="3d")
    if args.f != "":
        dd = df[df["Element"] == args.f]
        hist, xedges, yedges = np.histogram2d(
            dd["%_Div"],
            dd["%_of_Ref"] * 100,
            bins=[20, int(args.b)],
            range=[[0, 20], [0, 100]],
        )
        # Construct arrays for the anchor positions.
        xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
        xpos = xpos.ravel()
        ypos = ypos.ravel()
        zpos = 0

        # Construct arrays with the dimensions for the bars.
        dx = dy = 0.5 * np.ones_like(zpos)
        dz = hist.ravel()

        ax.view_init(elev=None, azim=-25)
        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort="average", shade=True)
    else:
        dd = df
        dd["%_Div"].hist(bins=int(args.b), by=dd["Family"])

    plt.savefig(args.o, dpi=300)
