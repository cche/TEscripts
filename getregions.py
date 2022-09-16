#!/usr/bin/env python3
"""Extract columns from chrom-start sorted tsv file and produce
a BED3 or BED6 file. The file must have a numerical column that
can be used to filter the lines that will be output.
"""


def bed_from_line(line, cols, regionchrom, regionstart, regionstop):
    """Extract columns from file and return a BED3 of BED6 line"""
    (chrom, start, end, *dummy) = cols.split(",")
    chrom = int(chrom) - 1
    start = int(start) - 1
    end = int(end) - 1
    if dummy != []:
        name, score, strand = dummy
        name = int(name) - 1
        score = int(score) - 1
        strand = int(strand) - 1
    else:
        name = score = strand = -1

    fields = line.strip().split('\t')
    if name >= 0:
        return "\t".join(
            [fields[chrom], str(regionstart), str(regionstop),
                fields[name], fields[score], fields[strand]])
    else:
        return "\t".join([fields[chrom], str(regionstart), str(regionstop)])


def get_regions_2_bed(infile: str, columns, col: int = 0, threshold: int = 0):
    """Extract columns from tsv file with threshold for a column
    Returns: List with BED3 or BED6 formatted lines.
    """
    result = []

    (chrom, start, end, *dummy) = columns.split(",")
    chrom = int(chrom) - 1
    start = int(start) - 1
    end = int(end) - 1
    if dummy != []:
        name, score, strand = dummy
        name = int(name) - 1
        score = int(score) - 1
        strand = int(strand) - 1
    else:
        name = score = strand = -1

    if col == 0:
        col = start if score == -1 else score
        threshold = 0
    else:
        col -= 1

    regionchrom = ''
    regionstart = -1
    regionstop = 0
    inregion = False
    with open(infile) as fi:
        for line in fi:
            fields = line.strip().split('\t')
            if threshold == 0:
                if name >= 0:
                    result.append("\t".join(
                        [fields[chrom], str(start), str(end),
                            fields[name], fields[score], fields[strand]]))
                else:
                    result.append(
                        "\t".join([fields[chrom], str(start), str(end)]))
            else:
                if fields[chrom] != regionchrom:
                    if inregion:
                        result.append(
                            "\t".join([regionchrom, str(regionstart), str(regionstop)]))
                    regionchrom = fields[chrom]
                    regionstart = -1
                    regionstop = 0
                    inregion = False

                if int(fields[col]) > threshold and inregion == False:
                    regionstart = fields[start]
                    inregion = True

                if int(fields[col]) <= threshold and inregion:
                    result.append(
                        "\t".join([regionchrom, str(regionstart), str(regionstop)]))
                    inregion = False
                    regionstart = -1
                    regionstop = 0

                if inregion:
                    regionstop = fields[end]

        if regionchrom != "" and regionstart != -1 and regionstop != 0:
            result.append(
                "\t".join([regionchrom, str(regionstart), str(regionstop)]))
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse tsv file and extract contiguous non zero regions in BED format")
    parser.add_argument(
        "-i", help="TAB separated file with at least a Chrom, star and end column")
    parser.add_argument("-c", type=int, help="Column number to filter")
    parser.add_argument("-t", type=int, default=0,
                        help="Threshold to consider region")
    parser.add_argument(
        "-p", help="Column numbers describing position in the form 'chrom,start,end[,name,score,strand]' no spaces and comma delimited")
    parser.add_argument("-o", help="Output in bed format")
    options = parser.parse_args()

    regions = get_regions_2_bed(options.i, options.p, options.c, options.t)
    with open(options.o, 'w') as fo:
        for region in regions:
            fo.write(region + '\n')
