####################################################################################################################
# tweets2entityWords.py
# Reads in (entity tagged) tweets, and spits out (entity, feature) pairs.
# For building LabeledLDA training dataset.
####################################################################################################################

import sys
import os
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--windowSize", dest='windowSize', default='2')
(options, args) = parser.parse_args()

BASE_DIR = 'twitter_nlp.jar'

sys.path.append('%s/hbc/python' % (BASE_DIR))
sys.path.append('%s/python' % (BASE_DIR))

from LdaFeatures import LdaFeatures
from twokenize import tokenize

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

    features = LdaFeatures(words, neTags, windowSize=int(options.windowSize))
    for i in range(len(features.entities)):
        entity =  ' '.join(features.words[features.entities[i][0]:features.entities[i][1]])
        for f in features.features[i]:
            print "%s\t%s\t%s" % (sid, entity.lower(), f.lower())
