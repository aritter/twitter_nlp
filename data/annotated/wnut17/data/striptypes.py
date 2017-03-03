import sys

for line in open(sys.argv[1]):
    fields = line.strip().split('\t')
    if len(fields) > 1:
        fields[-1] = fields[-1][0]
    print "\t".join(fields)
