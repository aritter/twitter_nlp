#!/usr/bin/python

import sys
from random import shuffle

proportionTrain = float(sys.argv[1])

#Read in the data
tweets = []
tokens = []

for line in sys.stdin:
    if line.strip() == '':
        tweets.append(tokens)
        tokens = []
    else:
        (word, label) = line.strip().split('\t')
        tokens.append((word,label))

shuffle(tweets)

trainOut = open('train', 'w')
devOut   = open('dev', 'w')

for i in range(len(tweets)):
    out = None
    if i < int(proportionTrain * len(tweets)):
        out = trainOut
    else:
        out = devOut

    t = tweets[i]
    for w in t:
        out.write("%s\t%s\n" % w)
    out.write("\n")
