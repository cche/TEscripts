# Tools to analyse transposable elements


Collection of tools that I've used in analysing transposable elements. Not all scripts are
transposable element specific but I decided to group them all in this repository.

----

## getregions.py 

### Description

Script that extracts columns from a TAB separated file (tsv)
that has been sorted for Chrom and Start position
and will produce a BED3 or BED6 file.


If a threshold is given, the output will merge consecutive lines that are 
greater or equal to the threshold (**Important:** files have to be sorted).
Otherwise all lines will be returned.


The column positions are given in a specific order corresponding to a BED3 or BED6
file depending on the data available and the output that you want.


The order is **chrom,start,end[,name,score,strand]** and, as ilustrated, should not
have spaces i.e. -p 2,4,5 or -p 2,4,5,6,8,10. Be sure to give either 3 or 6 column
numbers.

The numerical column that is used to filter the output does not need to be one of
the output columns. The program will merge contiguous reported region that
are above the given threshold.

### Example usage

After a bedtools multicov using a RepeatMasker gff annotation file and several bam files
I used this script to identify genomic regions enriched in expressed Transposable elements.
```bash
python3 getregions.py -i repeats-rnaseq2.csv -p "1,4,5" -c 10 -t 50 -o repeats-expressed-50.bed
```
