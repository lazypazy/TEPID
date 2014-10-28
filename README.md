locaTE
======

Uses paired-end sequencing data to find transposable element insertion points.

Usage
-----

```
locate.sh [options] -p <proc> -s <size> -x <path/to/bowtie2/index> -y <path/to/yaha/index> -c <path/to/repository> -g <genome>
```

where:
  * `<proc>` is number of processors to use
  * `<size>` is average size of PE fragments sequenced
  * `<genome>` is the organism. Currently supports *Arabidopsis thaliana* and *Brachypodium distachyon*.

Options:

  * ` -k <path>` keep concordantly mapped reads, store at <path>  
  * `-r` run on all subdirectories (recursive)
  * `-h` display help and exit

Output files:
  * bowtie log file: `<name>.log`
  * discordant reads bedfile
  * optional concordant reads samfile (use `-k <path>`)
  * split reads bedfile
  * TE insertions bedfile
  * TE deletions bedfile (TE present in reference but not sample). Limited to finding TEs >200 bp, <20000 bp
  * compressed fastq files

Required tools
--------------

* [bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml) >= v2.1.0
* [yaha](http://faculty.virginia.edu/irahall/yaha/) >= v0.1.82
* [samtools](http://samtools.sourceforge.net) >= v0.1.19
* [samblaster](https://github.com/GregoryFaust/samblaster) >= v0.1.19
* [bedtools](http://bedtools.readthedocs.org/en/latest/) >= v2.21
* [python](https://www.python.org) v2.7

License
-------

This software is licensed under the GNU General Public License. See ./LICENSE
for further details. If this license is incompatible with your open source
project, talk to us (raise an issue) and we will negotiate suitable re- or
dual-licensing.
