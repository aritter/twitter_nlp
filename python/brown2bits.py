#!/usr/bin/python

import sys
import re

for line in sys.stdin:
    line = line.rstrip('\n')
    (word, bits) = line.split(' ')
    bits = int(bits)
    
    bitstring = ""
    for i in range(20):
        if bits & (1 << i):
            bitstring += '1'
        else:
            bitstring += '0'

    print "%s %s" % (bitstring, word)

