from sys import argv, exit

args = argv[1:]
if '-h' in args or '--help' in args:
    print(
            """
            find_te.py

            Created by Tim Stuart

            Usage:
            python find_te.py -n <sample_name>
                              -c <all_mapped_reads_bamfile>
                              -d <discordant_reads_bamfile>
                              -s <split_reads_bamfile>
                              -t <TE_annotation>

            find_te.py must be in the same folder as locate.py
            so that code can be imported

            Outputs TE insertions bedfile and TE deletions bedfile.
            """
            )
    exit()
else:
    pass

import pybedtools
import locate
import os
from glob import glob


# sample name
name = locate.checkArgs('-n', '--name')

# mapped bam file
all_mapped = locate.checkArgs('-c', '--conc')
# this needs to have unmapped reads removed first due to problem with pybedtools
# samtools view -hbF 0x04 -@ [number_threads] [input] > [output]
print 'Estimating mean insert size'
bam = pybedtools.BedTool(all_mapped)
mn, std = locate.calc_mean(bam[:20000])
max_dist = (3*std) + mn

# split read data
print 'Processing split reads'
split_mapped = locate.checkArgs('-s', '--split')
split = pybedtools.BedTool(split_mapped).bam_to_bed()\
.saveas('split.temp')
locate.convert_split_pairbed('split.temp', 'split_bedpe.temp')

split_bedpe = pybedtools.BedTool('split_bedpe.temp')
filtered_split = split.sort().merge(c='2,3', o='count_distinct,count_distinct')\
.filter(locate.filter_unique_break)\
.each(locate.break_coords).saveas('filtered_split.temp')

# discordant reads. Filter reads pairs more that 3 std insert size appart
# Can't use main bam file because problem when reads don't have their pair,
# due to filtering unmapped reads. This can be fixed when pybedtools problem
# with unmapped reads is fixed
print 'Processing discordant reads'
disc_mapped = locate.checkArgs('-d', '--disc')
pybedtools.BedTool(disc_mapped)\
.bam_to_bed(bedpe=True, mate1=True)\
.filter(locate.filter_lines, max_dist=max_dist)\
.saveas('disc.temp')
disc = pybedtools.BedTool('disc.temp').sort()

# TE bedfile
print 'Processing TE annotation'
te_bed = locate.checkArgs('-t', '--te')
te = pybedtools.BedTool(te_bed).sort()

print 'Intersecting TE coordinates with reads'
Split = split_bedpe.each(locate.append_origin, word='split').saveas()
Disc = disc.each(locate.append_origin, word='disc').saveas()
disc_split = Split.cat(Disc, postmerge=False).sort().saveas('disc_split.temp')

te_intersect = disc_split.pair_to_bed(te, f=0.05).saveas('intersect.temp')

# merge intersection coordinates where TE name is the same

# should firstly filter out those that both intersect the same TE
# note: same reads can appear multiple times if they intersect different TEs.

print 'Merging TE intersections'
locate.reorder('intersect.temp', 'reorder_intersect.temp')
locate.merge_te_coords('reorder_intersect.temp', 'merged_intersections.temp')

# need a step in here that groups reads and looks at how many TEs are intersected
# by each read, where the intersection is. Look at where
# intersections lie within TE sequence & decide which is the mobile TE in cases where
# there are multiple intersections.

# Find where there are breakpoints at insertion site
print 'Annotating insertions'
locate.annotate_insertions('merged_intersections.temp', 'insertions.temp')

# probably remove these steps
pybedtools.BedTool('insertions.temp')\
.intersect(filtered_split, c=True)\
.moveto('insertions_split_reads.temp')

locate.splitfile('insertions_split_reads.temp')
pybedtools.BedTool('single_break.temp')\
.intersect(filtered_split, wo=True)\
.moveto('single_break_intersect.temp')

pybedtools.BedTool('double_break.temp')\
.intersect(filtered_split, wo=True)\
.moveto('double_break_intersect.temp')

locate.annotate_single_breakpoint()
locate.annotate_double_breakpoint()
locate.separate_reads(name)
pybedtools.BedTool('insertions_unsorted.temp').sort().moveto('insertions_{}.bed'.format(name))

# Deletions
print 'Annotating deletions'
locate.create_deletion_coords(disc_split, 'del_coords.temp')
pybedtools.BedTool('del_coords.temp').intersect(te, wo=True).sort().saveas('deletions.temp')
locate.annotate_deletions('deletions.temp', name, 10, all_mapped, mn)

# remove temp files
# temp = glob('./*.temp')
# for i in temp:
#     os.remove(i)
