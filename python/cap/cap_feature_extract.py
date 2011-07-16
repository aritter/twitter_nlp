#!/usr/bin/python

import sys
import re

from cap_classifier import FeatureExtractor

fe = FeatureExtractor('data/cap/tweets_cap.vocab')

for line in sys.stdin:
    line = line.rstrip('\n')
    fields = line.split('\t')
    for i in range(len(fields)):
        if len(fields[i]) == 0:
            fields[i] = "none"
    print "%s\t%s" % (fe.Extract(fields[6]), "\t".join(fields))
