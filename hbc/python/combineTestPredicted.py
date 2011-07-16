#!/usr/bin/python

import sys
import re

predIn = open(sys.argv[2])
for line in open(sys.argv[1]):
    goldFields = line.rstrip('\n').split(' ')
    predFields = predIn.readline().rstrip('\n').split('\t')

    goldFields[0] = re.sub(r'^word=','', goldFields[0])
    predFields[0] = re.sub(r'^word=','', predFields[0])

    #Just checking...
    if goldFields[0] != predFields[0]:
        print "AAAAARRRRGGGGG!!!!!"
        print ">>>>>%s\t%s" % (goldFields[0], predFields[0])
        exit

    word = goldFields[0]
    gold = goldFields[-1]
    pred = predFields[-1]

    print "%s\t%s\t%s" % (word, pred, gold)
