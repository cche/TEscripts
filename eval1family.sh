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
fam=""
flank=0

while [ "$1" != "" ]; do
	case $1 in
		-g | --genome )
			shift
			genome=$1
			;;
		-n | --name )
			shift
			name=$1
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

# grep -E "\b${fam}\b" $gff | cut -f 1,4,5 > ${fam}-positions.bed
# sed -i~ -e 's/ \+/\t/g' $annot
if ! [ -f ${name}-positions-merge.bed ]; then
	awk 'OFS="\t" {if ($10 == fam) {print $5,$6,$7, $10, $1, $9}}' fam=$name $annot > ${name}-positions.bed
	sed -i.ori 's/C/-/g' ${name}-positions.bed
	bedtools sort -i ${name}-positions.bed > ${name}-positions-sort.bed
	bedtools merge -d $flank -s -c 6 -o first -i ${name}-positions-sort.bed > ${name}-positions-merge.bed
	# rm ${name}-positions.bed 	${name}-positions.bed.ori
fi

if ! [ -f ${name}-seqs.fa ]; then
	getseq.py -i $genome -p ${name}-positions-merge.bed -f ${flank} -o ${name}-seqs.fa
fi

if [ "$mafft" = "1" ] && ! [ -f ${name}-seqs.mft ]; then
	mafft --quiet --reorder --thread ${thread} ${name}-seqs.fa > ${name}-seqs.mft
	if [ "$erode" = "1" ]; then
		erode_alignment.py -i ${name}-seqs.mft -w 5 -c 0.7 -f 0.2 -o ${name}-seqs-eroded.mft
	fi
fi
