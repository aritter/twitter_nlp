#!/usr/bin/python

import sys
import re
from optparse import OptionParser

from LdaFeatures import LdaFeatures

parser = OptionParser()
parser.add_option("--gold", dest='gold', default='gold')
parser.add_option("--dictionaries", dest='dictionaries', default='dictionaries')
parser.add_option("--dictmap", dest='dictmap', default='dict-label')
parser.add_option("--labelmap", dest='labelmap', default=None)
parser.add_option("--entityTopic", dest='entityTopic', default='entity-topic')
parser.add_option("--entities", dest='entities', default='entities')
parser.add_option("--fbBaseline", action='store_true', dest='fbBaseline', default=False)
parser.add_option("--predictedSeg", dest='predictedSeg', default=None)
parser.add_option("--pInc", action='store_true', dest='pInc', default=False)
parser.add_option("--threshold", dest='threshold', type='float', default=0.0)
(options, args) = parser.parse_args()

#Read in dictionaries
dictionaries = []
for line in open(options.dictionaries):
    dictionaries.append(line.rstrip('\n'))

#Read in mappings from dictionaries to labels
dict2label = {}
for line in open(options.dictmap):
    (d, l) = line.rstrip('\n').split(' ')
    dict2label[d] = l

label2label = None
if options.labelmap:
    label2label = {}
    for line in open(options.labelmap):
        (l1, l2) = line.rstrip('\n').split(' ')
        label2label[l1] = l2

def MapLabel(label):
    if label2label and label2label.has_key(label):
        return label2label[label]
    else:
        return label

#Read in the gold labels
gold = []
for line in open(options.gold):
    gold.append(MapLabel(line.rstrip('\n')))

#Read in entities
entities = []
for line in open(options.entities):
    entities.append(line.rstrip('\n'))

#Read in labels
labels = []
for line in open('labels'):
    labels.append([int(x) for x in  line.rstrip('\n').split(' ')])

#Read in predicted segmentation
goldTypeCounts = None
if options.predictedSeg:
    goldTypeCounts = {}
    for line in open(options.predictedSeg):
        (word, predicted, g) = line.rstrip('\n').split('\t')
        if g[0:2] == "B-":
            #print g
            g = MapLabel(g[2:])
            print g
            if g != 'error':
                goldTypeCounts[g] = goldTypeCounts.get(g,0.0) + 1.0
                goldTypeCounts['all'] = goldTypeCounts.get('all',0.0) + 1.0

print goldTypeCounts

#Read in predictions and probabilities
i = 0
pred = []
dictLabelCnt = {}
confusionMatrix = {}
tp = {}
fp = {}
tn = {}
fn = {}
n = {}
for line in open(options.entityTopic):
    fields  = line.rstrip('\n').split('\t')
    counts  = [float(x.split(':')[1]) for x in fields[1:]]
    dictIds = [int(x.split(':')[0]) for x in fields[1:]]
    
    dictionary = dictionaries[dictIds[0]-1]
    if options.pInc:
        p = counts[0]
    else:
        p = counts[0] / sum(counts)

#    if dict2label[dictionary] == 'NONE' and len(dictIds) > 1:
#        dictionary = dictionaries[dictIds[1]-1]
#        p = counts[1] / sum(counts)

    if dict2label[dictionary] != gold[i]:
        pred.append((entities[i],dictionary,dict2label[dictionary],gold[i],p))

    if gold[i] != 'error':
        dictLabelCnt["%s\t%s" % (dictionary, gold[i])] = dictLabelCnt.get("%s\t%s" % (dictionary, gold[i]),0) + 1
        confusionMatrix["%s\t%s" % (dict2label[dictionary], gold[i])] = confusionMatrix.get("%s\t%s" % (dict2label[dictionary], gold[i]),0) + 1

    if gold[i] != 'error':
        n[gold[i]] = n.get(gold[i],0.0) + 1.0
        n['all'] = n.get('all',0.0) + 1.0    
    
    if (options.fbBaseline and (sum(labels[i]) == 1)) or (not options.fbBaseline and p >= options.threshold and dict2label[dictionary] != 'NONE'):
        if dict2label[dictionary] == gold[i]:
            tp[dict2label[dictionary]] = tp.get(dict2label[dictionary],0.0) + 1.0
            tp['all'] = tp.get('all',0.0) + 1.0
        else:
            fp[dict2label[dictionary]] = fp.get(dict2label[dictionary],0.0) + 1.0
            fp['all'] = fp.get('all',0.0) + 1.0
            if gold[i] != 'error':
                fn[gold[i]] = fn.get(gold[i],0.0) + 1.0
                fn['all'] = fn.get('all',0.0) + 1.0
    else:
        #print "%s\t%s\t%s" % (dictionary, dict2label[dictionary], gold[i])
        if gold[i] != 'error':
            fn[gold[i]] = fn.get(gold[i],0.0) + 1.0
            fn['all'] = fn.get('all',0.0) + 1.0

    i += 1

print "\n".join([str(x) for x in pred])

for pair in sorted(dictLabelCnt.keys(), cmp=lambda a,b: cmp(dictLabelCnt[b], dictLabelCnt[a])):
    print "%s\t%s" % (pair, str(dictLabelCnt[pair]))

print "\nConfusion matrix:"
for pair in sorted(confusionMatrix.keys(), cmp=lambda a,b: cmp(confusionMatrix[b], confusionMatrix[a])):
    (pred, gold) = pair.split('\t')
    print "%s\t%s\t%s\t%s\t%s" % (gold, pred, str(confusionMatrix[pair]), confusionMatrix[pair] / n.get(gold,-1), n.get(gold,-1))


if goldTypeCounts:
    n = goldTypeCounts

for t in sorted(tp.keys(), lambda a,b: cmp(n[b],n[a])):
    p = tp.get(t,0.0) / (tp.get(t,0.0) + fp.get(t,0.0))
    if options.predictedSeg:
        #r = tp.get(t,0.0) / (tp.get(t,0.0) + goldTypeCounts[t])
        r = tp.get(t,0.0) / (goldTypeCounts[t])
        f = 2 * p * r / (p + r)
        print "%s\tP=%s\tR=%s\tF=%s\tN=%s" % (t, p, r, f, goldTypeCounts[t])
    else:
        r = tp.get(t,0.0) / (tp.get(t,0.0) + fn.get(t,0.0))
        f = 2 * p * r / (p + r)
        print "%s\tP=%s\tR=%s\tF=%s\tN=%s" % (t, p, r, f, n[t])

