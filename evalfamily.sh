#!/bin/bash

usage() {
  echo "Usage: evalfamily.sh OPTIONS

  OPTIONS:
  -g|--genome FILE  Fasta genome file 
  -a|--annot   FILE  Annotation gff file 
  -n|--name   TEXT  TE Family name 
  -f|--flank  NUM   Flanking bases 
  -t|--thread NUM   Number of threads 
  [-m|--mafft]      Align with Mafft\n"
}

mafft=0

while [ "$1" != "" ]; do
  case $1 in
    -g | --genome )
      shift
      genome=$1
      ;;
    -n | --name )
      shift
      fam=$1
      ;;
    -a | --annot )
      shift
      annot=$1
      ;;
    -f | --flank )
      shift
      flank=$1
      ;;
    -t | --threads )
      shift
      thread=$1
      ;;
    -m | --mafft )
      mafft=1
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

# grep -E "\b${fam}\b" $gff | cut -f 1,4,5 > ${fam}-positions.bed
sed -i~ -e 's/ \+/\t/g' $annot
awk 'OFS="\t" {if ($10 == fam) {print $5,$6,$7}}' fam=$fam $annot > ${fam}-positions.bed

bedtools merge -d $flank -i ${fam}-positions.bed > ${fam}-positions-merge.bed

getseq.py -i $genome -p ${fam}-positions-merge.bed -f ${flank} -o ${fam}-seqs.fa

if [ mafft = "1" ]
then
  mafft --quiet --reorder --thread ${thread} ${fam}-seqs.fa > ${fam}-seqs.mft
fi

