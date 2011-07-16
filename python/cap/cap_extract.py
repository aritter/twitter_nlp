#!/usr/bin/python

import sys

############################################################################################
# Rule-based script for extracting entities using simple capitalization rules
# input format is same as CRF
############################################################################################

def hasDict(fields):
    for f in fields:
        if f[0:5] == 'DICT=':
            return True
    return False

prevLabel  = None
for line in sys.stdin:
    line = line.rstrip('\n')
    fields = line.split(' ')
    label = "O"

    if len(fields) < 10:
        print line
        prevLabel = 'O'
        continue

    if 'INITCAP_AND_GOODCAP' in fields:
    #if 'INITCAP' in fields:
        if 'DICT=lower.100' in fields or 'DICT=lower.500' in fields or 'DICT=lower.1000' in fields or 'DICT=lower.5000' in fields or 'DICT=lower.10000' in fields or 'DICT=english.stop' in fields:
            label = 'O'
        #elif 'DICT=people.person' in fields or 'DICT=film.film' in fields or 'DICT=firstname.1000' in fields or 'dict=lastname.1000' in fields or 'DICT=automotive.make' in fields or 'DICT=buisness.brand' in fields or 'DICT=music.musical_group' in fields:
        #elif hasDict(fields):
        elif True:
            if prevLabel and prevLabel == 'B' or prevLabel == 'I':
                label = 'I'
            else:
                label = 'B'
    elif (prevLabel == 'B' or prevLabel == 'I') and 'HASDIGIT' in fields:
        label = 'I'

    print "%s %s" % (line, label)
    prevLabel  = label
