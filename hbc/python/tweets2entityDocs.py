#!/usr/bin/python

import sys
sys.path.append('/homes/gws/aritter/twitter_nlp/python')
from twokenize import tokenize

from LdaFeatures import LdaFeatures
from Vocab import Vocab

from Dictionaries import Dictionaries

entityDocs = {}

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

    features = LdaFeatures(words, neTags)
    for i in range(len(features.entities)):
        entity =  ' '.join(features.words[features.entities[i][0]:features.entities[i][1]])
        entityDocs[entity] = entityDocs.get(entity,[])
        entityDocs[entity].append(features.features[i])

dictionaries = Dictionaries('/homes/gws/aritter/twitter_nlp/data/LabeledLDA_dictionaries')
vocab = Vocab()
keys = entityDocs.keys()
keys.sort(cmp=lambda a,b: cmp(len(entityDocs[b]),len(entityDocs[a])))
eOut = open('entities', 'w')
lOut = open('labels', 'w')
dOut = open('dictionaries', 'w')
for e in keys:
    labels = dictionaries.GetDictVector(e)
    ###############################################################################
    #NOTE: For now, only include entities which appear in one or more dictionary
    #      we could modify this to give them membership in all, or no dictionaries
    #      (in LabeledLDA, don't impose any constraints)
    ###############################################################################
    if sum(labels) > 0:
        lOut.write(' '.join([str(x) for x in labels]) + "\n")
        eOut.write("%s\n" % e)
        print '\t'.join([' '.join([str(vocab.GetID(x)) for x in f]) for f in entityDocs[e]])
vocab.SaveVocab('vocab')

for d in dictionaries.dictionaries:
    dOut.write(d + "\n")
