#!/usr/bin/python

import sys
import re

sentence = []
for line in sys.stdin:
    if re.match(r'^\s*$', line):
        print " ".join(sentence)
        sentence = []
    else:
        (word,tag) = line.rstrip('\n').split(' ')
        sentence.append(word)
