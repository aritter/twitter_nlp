#!/usr/bin/python

#####################################################################
# tweets2yamcha.py
#
# Converts tokenized twitter posts to yamcha format
#####################################################################

import sys
import feature_extraction

for line in sys.stdin:
    line = line.rstrip("\n")
    words = line.split(' ')
    for word in words:
        print word + " " + " ".join(feature_extraction.token_features(word))
    print
