#!/usr/bin/python

import sys
import re

labelMap = {}
for line in open(sys.argv[3]):
    (source, target) = line.rstrip('\n').split(' ')
    labelMap[source] = target

def MapLabel(string):
    if labelMap.has_key(string):
        return labelMap[string]
    else:
        return string

i = 0
hbcIn = open(sys.argv[1])
for line in open(sys.argv[2]):
    label = MapLabel(line.rstrip('\n'))
    words = hbcIn.readline().rstrip('\n')
    print "%s\t%s\t%s" % (i, label, words)
    i += 1
