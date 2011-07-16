#!/usr/bin/python

############################################################################################
# Converts sample dumps from HBC into format readable by HBC
############################################################################################

import sys

##################################################
# How many samples to use?
##################################################
nSamples = int(sys.argv[2])

zOut = open(sys.argv[1], 'w')

z = []
s = []
for line in sys.stdin:
    line = line.rstrip('\n')
    if line[0:4] == "z = ":
        z.append(line[4:])
    if line[0:4] == "s = ":
        s.append(line[4:])

z = ' ;  ;; '.join(z[len(z)-nSamples:])

for entitySamples in z.split(' ;  ;; '):
    if entitySamples == '':
        continue
    zOut.write("\t".join(entitySamples.strip().split(' ; ')) + "\n")

if len(s) > 0:
    sOut = open('s.hbc', 'w')
    for entitySamples in s.split(' ;  ;; '):
        if entitySamples == '':
            continue
        sOut.write("\t".join(entitySamples.strip().split(' ; ')) + "\n")
