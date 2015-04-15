#! /bin/bash

index=  proc=  yhindex=  size=  recursive=  zip=  

usage="$(basename "$0") -- map paired-end data using bowtie2 and yaha
  -h  show help and exit
  -x  path to bowtie2 index
  -y  path to yaha index
  -p  number of cores to use
  -s  average insert size
  -r  recursive (optional)
  -z  gzip fastq files (optional)"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1
fi

while getopts :x:p:y:s:rzh opt; do
  case $opt in
    h)  echo "$usage"
        exit
        ;;
    x)  index=$OPTARG
        ;;
    p)  proc=$OPTARG
        ;;
    y)  yhindex=$OPTARG
        ;;
    s)  size=$OPTARG
        ;;
    r)  recursive=true
        ;;
    z)  zip=true
        ;;
    :)  printf "missing argument for -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1
        ;;
    \?) printf "illegal option: -%s\n" "$OPTARG" >&2
        echo "$usage" >&2
        exit 1
        ;;
  esac
done
shift $((OPTIND - 1))

map () {

  for myfile in $(ls -d *_1.fastq);do

    fname=(${myfile//_1.fastq/ })

    echo "Mapping ${fname}"
    bowtie2 --local --dovetail -p$proc --fr -q -R5 -N1 -x $index -X $size\
     -1 "${fname}_1.fastq" -2 "${fname}_2.fastq" \
    | samblaster -e -u "${fname}.umap.fastq" \
    | samtools view -b - > "${fname}_unsort.bam"

    yaha -t $proc -x $yhindex -q "${fname}.umap.fastq" -L 11 -H 2000 -M 15 -osh stdout \
    | samblaster -s "${fname}.split.sam" > /dev/null

    echo "Converting to bam"
    samtools view -Sb@ $proc "${fname}.split.sam" > "${fname}.split.bam"
    rm "${fname}.split.sam"

    echo "Sorting alignment"
    samtools sort -@ $proc "${fname}_unsort.bam" "${fname}"
    rm "${fname}_unsort.bam"

    echo "Indexing alignment"
    samtools index "${fname}.bam"

    if [ "$zip" == true ]; then
      echo "Zipping fastq files"
      gzip *.fastq
    fi

done
}

if [ "$recursive" == true ]; then
  for directory in ./*; do
      if [ -d "$directory" ]; then
          cd $directory
          map
          cd ..
      fi
  done

else
  map
fi