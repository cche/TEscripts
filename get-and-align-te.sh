#!/bin/bash

usage() {
  echo "Usage: evalfamily.sh OPTIONS

  OPTIONS:
  -b|--bed FILE  BED file 
  -f|--flank  NUM   Flanking bases 
  -t|--thread NUM   Number of threads 
  [-d|--dot]        Create dotplot image with Gepard
  [-m|--mafft]      Align with Mafft
  [-e|--erode]      Erode alignements"
}

mafft=0
flank=0
thread=1

while [ "$1" != "" ]; do
  case $1 in
    -b | --bed )
      shift
      bedfile=$1
      ;;
    -f | --flank )
      shift
      flank=$1
      ;;
    -t | --threads )
      shift
      threads=$1
      ;;
    -d | --dotplot )
      dot=1
      ;;
    -m | --mafft )
      mafft=1
      ;;
    -e | --erode )
      erode=1
      ;;
    -h | --help )
      usage
      exit
      ;;
    * )
      usage
      exit 1
  esac
  shift
done

basename=${bedfile%%.*}-merge-${flank}
merged=${basename}.bed
fasta=${basename}.fa
alignment=${basename}.mft
eroded=${basename}-eroded.mft
png=${basename}.png

bedtools merge -d $1 -i $bedfile > $merged
getseq.py -i ~/work/schisto/v8/schisto_hic.curated.final.v8.fa -p $merged -f $1 -o $fasta

if [ "$dot" = "1" ]
then
  java -cp ~/src/gepard-master/dist/Gepard-1.40.jar org.gepard.client.cmdline.CommandLine \
    -matrix ~/src/gepard-master/resources/matrices/edna.mat  \
    -seq1 $fasta -seq2 $fasta \
    -outfile $png
fi
if [ "$mafft" = "1" ]
then
  mafft -reorder -thread $threads $fasta > $alignment
fi

if [ "$erode" = "1" ]
then
  erode_alignment.py -i $alignment -w 5 -c 0.7 -f 0.2 -o $eroded
fi

