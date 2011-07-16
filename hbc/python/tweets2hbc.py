#!/usr/bin/python

import sys
sys.path.append('/homes/gws/aritter/twitter_nlp/python')
from twokenize import tokenize

from LdaFeatures import LdaFeatures
from Vocab import Vocab
from Dictionaries import Dictionaries

vocab = Vocab()
eOut = open('entities', 'w')
lOut = open('labels', 'w')
dOut = open('dictionaries', 'w')

dictionaries = Dictionaries('/homes/gws/aritter/twitter_nlp/data/LabeledLDA_dictionaries2')

prevText = None
for line in sys.stdin:
    line = line.rstrip('\n')
    fields = line.split('\t')

    sid    = fields[0]
    text   = fields[6]
    words  = tokenize(text)
    confidence = 1.0 / float(fields[-1])
    eType  = fields[-2]
    entity = fields[-3]
    neTags = fields[-4].split(' ')
    pos    = fields[-5].split(' ')
    words  = fields[-6].split(' ')

    #Just skip duplicate texts (will come from tweets with more than one entiity)
    if prevText and prevText == text:
        continue
    prevText = text

    features = LdaFeatures(words, neTags, windowSize=3)
    for i in range(len(features.entities)):
        entity =  ' '.join(features.words[features.entities[i][0]:features.entities[i][1]])
        labels = dictionaries.GetDictVector(entity)

        if(sum(labels) == 0):
            continue

        eOut.write("%s\n" % entity)
        lOut.write(' '.join([str(x) for x in labels]) + "\n")
        #print [f for f in features.features[i] if(f[0:2] != 't=')]
        print ' '.join([str(vocab.GetID(x)) for x in [f for f in features.features[i] if(f[0:2] != 't=')]])

vocab.SaveVocab('vocab')

for d in dictionaries.dictionaries:
    dOut.write(d + "\n")
