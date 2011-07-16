#!/usr/bin/python

####################################################################################
# conll2hbc.py
#
# Converts manually labeled data in CoNLL format (each line contains word+tag)
# into HBC format for LabeledLDA
####################################################################################

import sys
import re

from LdaFeatures import LdaFeatures
from Vocab import Vocab
from Dictionaries import Dictionaries
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--noDict", action='store_true', dest='noDict', default=False)
parser.add_option("--predictedSeg", action='store_true', dest='predictedSeg', default=False)
parser.add_option("--windowSize", dest='windowSize', default='2')
(options, args) = parser.parse_args()
#sys.argv = [None] + sys.argv

class TaggedSentence:
    def __init__(self):
        self.words = []
        self.tags  = []
        self.gold = []

    def Add(self, word, tag, gold=None):
        self.words.append(word)
        self.tags.append(tag)
        if gold:
            self.gold.append(gold)

class EntityMap:
    def __init__(self, eFile):
        i = 0
        self.entityNumbers = {}
        for line in open(eFile):
            entity = line.rstrip('\n')
            self.entityNumbers[entity] = i
            i += 1
            
    def GetID(self, entity):
        if self.entityNumbers.has_key(entity):
            return self.entityNumbers[entity]
        else:
            return -1

ts = TaggedSentence()
vocab = Vocab(sys.argv[2])
entityMap = EntityMap(sys.argv[3])
dictionaries = Dictionaries(sys.argv[4])

hbcOut = open('test.hbc', 'w')
entitiesOut = open('entities', 'w')
entityMapOut = open('entityMap', 'w')
goldOut = open('gold', 'w')
labelsOut = open('labels', 'w')
dictOut = open('dictionaries', 'w')
nInVocabOut = open('nInVocab', 'w')

for dictionary in dictionaries.dictionaries:
    dictOut.write('%s\n' % dictionary)

for line in open(sys.argv[1]):
    line = line.strip()
    fields = re.split(r'\s+', line)
    if re.match(r'^\s*$', line):
        features = LdaFeatures(ts.words, ts.tags, windowSize=int(options.windowSize))

        if options.predictedSeg:
            gold_features = LdaFeatures(ts.words, ts.gold)
            gold_features.Test()
            features.CheckSegmentation(gold_features)

        #print features.entityTypes

        for i in range(len(features.entities)):
#            words = [str(vocab.GetID(x)) for x in features.features[i] if vocab.HasWord(x)]
            words = [str(vocab.GetID(x)) for x in features.features[i]]
            nInVocabOut.write("%s\n" % len(words))
            if len(words) == 0:
                #words = [str(vocab.GetID(x)) for x in features.features[i]]                
                continue
            hbcOut.write('%s\n' % ' '.join(words))
            entitiesOut.write('%s\n' % features.entityStrings[i].lower())
            entityMapOut.write('%s\n' % entityMap.GetID(features.entityStrings[i].lower()))
            goldOut.write('%s\n' % features.entityTypes[i])
            labels = dictionaries.GetDictVector(features.entityStrings[i])
            #labelsOut.write('%s\n' % ' '.join([str(1) for x in labels]))

            if sum(labels) > 0 and not options.noDict:
                labelsOut.write('%s\n' % ' '.join([str(x) for x in labels]))
            else:
                labelsOut.write('%s\n' % ' '.join([str(1) for x in labels]))
        
        ts = TaggedSentence()
        continue
    word = fields[0].split('=')[1]
    if options.predictedSeg:
        tag = fields[-2]
        gold = fields[-1]
        ts.Add(word, tag, gold)
    else:
        tag = fields[-1]
        ts.Add(word, tag)

vocab.SaveVocab('vocab')
