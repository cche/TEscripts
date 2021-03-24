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


The order is **chrom,start,end[,name,score,strand]** and, as illustrated, should not
have spaces i.e. -p 2,4,5 or -p 2,4,5,6,8,10. Be sure to give either 3 or 6 column
numbers.

The numerical column that is used to filter the output does not need to be one of
the output columns. The program will merge contiguous reported region that
are above the given threshold.

### Output

This script will produce a BED with Chromosome, star and end position or a BED6 which will include
the name, score and strand position.

### Example usage

After a bedtools multicov using a RepeatMasker gff annotation file and several bam files
I used this script to identify genomic regions enriched in expressed Transposable elements.
```bash
python3 getregions.py -i repeats-rnaseq2.csv -p "1,4,5" -c 10 -t 50 -o repeats-expressed-50.bed
```

## evalfamily.sh

### Description

Take a RepeatMasker .out file and extract all loci for a given family with a given flanking region,
merge overlapping regions, extract the sequences, align and produce a cleaned alignment.

### Usage

    Usage: evalfamily.sh OPTIONS

      OPTIONS:
      -g|--genome FILE  Fasta genome file 
      -a|--annot   FILE  Annotation gff file 
      -n|--name   TEXT  TE Family name 
      -f|--flank  NUM   Flanking bases 
      -t|--thread NUM   Number of threads 
      [-m|--mafft]      Align with Mafft
      [-e|--erode]      Erode the borders of the alignment

### Output

It produces:
- Fasta File with the elements and flanking regions
- Alignment file in fasta format (*.mft)
- Alignment file without the unaligned beginning and end.

### Example usage

Use the fasta file to inspect with a dotplot program like Gepard (ref here).
Inspect the correct borders and produce a consensus sequence by inspecting the alignment files.

```bash
evalfamily.sh -g mygenome.fa -n rnd-1_family-1 -a mygenome.fa.out -f 500 -t 10 -m -e
```


## correct\_one-code\_with-name.py


### Description

The script takes a one_code_to_find_them_all.pl output file and will rename LTR elements
according to the internal part that was identified. If no internal part is found the name
will be taken from the LTR part. The name is stripped of \_I and \_LTR parts so that the LTR
family name is used. It also eliminates duplicate lines identified as different parts of
non autonomous elements. This helps with downstream processing.

### Usage

    usage: correct_one-code_with-name.py [-h] [-i I] [-o O]
    
    Parse one-code output and eliminate lines that are contained in previously identified loci
    
    optional arguments:
      -h, --help  show this help message and exit
      -i I        One code output file
      -o O        Output file name

### Output

The output file resembles the one_code_to_find_them_all output but has the names of LTR elements
changed to the family name without the \_I or \_LTR suffixes and the duplicated lines deleted.

### Example usage
```bash
python3 correct_one-code_with-name.py -i one_code_output.csv -o one_code_output-corrected.csv
```


## graphbyage3d.py

### Description

Graphs the 3d histogram of percentage of divergence and percentage of completeness with respect
to the representative element of the family.

### Usage

    usage: graphbyage3d.py [-h] [-i I] [-b B] [-s S] [-f F] [-o O]
    
    Parse RepeatMasker .out file and graph percent similarity by repeat family
    
    optional arguments:
      -h, --help  show this help message and exit
      -i I        Onecode .elem_sorted.csv file
      -b B        Number of bins
      -s S        Size of image in WxH in inches
      -f F        Class to filter
      -o O        Filename for graph

### Output

Creates a PNG image of the TE element given in the command line (-f)

### Example usage
```bash
python3 graphbyage3d.py -i onecode-corrected-output.csv -b 20 -s 9x9 -f SACI5 -o saci5.png
```


## graphbycontour.py

### Description
Graphs a 2d histogram of percentage of divergence and percentage of completeness with respect
to the representative element of the family with the histogram values being color coded.

### Usage

    usage: graphbycontour.py [-h] [-i I] [-b B] [-s S] [-f F] [-o O]
    
    Parse RepeatMasker .out file and graph percent similarity by repeat family
    
    optional arguments:
      -h, --help  show this help message and exit
      -i I        Onecode .elem_sorted.csv file
      -b B        Number of bins
      -s S        Size of image in WxH format (inches)
      -f F        Class to filter
      -o O        Filename for graph

### Output
Creates a PNG image of the TE element given in the command line (-f)

### Example usage
```bash
python3 graphbycontour.py -i onecode-corrected-output.csv -b 20 -s 9x9 -f SACI5 -o saci5.png
```
