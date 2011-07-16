#!/usr/bin/python

import sys
import re

############################################################################################
# For computing P/R of cap_extract.py
############################################################################################

goldEntity      = None
predictedEntity = None

tp = 0
fp = 0
fn = 0
tn = 0

type_tp = {}
type_fn = {}

inFile = None
if sys.argv > 1:
    inFile = open(sys.argv[1])

i = 0
goldType = None
for line in sys.stdin:
    line = line.rstrip('\n').rstrip(' ')
    fields = line.split(' ')

    if line == "":
        gold      = 'O'
        if inFile:
            inFile.readline()
        predicted = 'O'
    else:
        if inFile:
            l2 = inFile.readline().rstrip('\n')
            if l2 == "":
                l2 = inFile.readline().rstrip('\n')
            gold = l2.split(' ')[-1]
        else:
            gold = fields[-2]
        predicted = fields[-1]

    print "%s\t%s" % (predicted, gold)

    ge = None
    pe = None

    if gold[0] == 'B' and not goldEntity:
        goldEntity = [i]
        goldType = gold
    elif gold[0] == 'I':
        goldEntity.append(i)
    elif gold[0] == 'O' and goldEntity:
        ge = ' '.join([str(x) for x in goldEntity])
        goldEntity = None
    elif gold[0] == 'B' and goldEntity:
        ge = ' '.join([str(x) for x in goldEntity])
        goldEnity = [i]
        goldType = gold

    #print "%s\t%s" % (fields[0], predicted[0])
    if predicted[0] == 'B' and not predictedEntity:
        predictedEntity = [i]
    elif predicted[0] == 'I':
        predictedEntity.append(i)
    elif predicted[0] == 'O' and predictedEntity:
        pe = ' '.join([str(x) for x in predictedEntity])
        predictedEntity = None
    elif predicted[0] == 'B' and predictedEntity:
        pe = ' '.join([str(x) for x in predictedEntity])
        predictedEntity = [i]

    predicted = re.sub(r':.*$', '', predicted)

    if ge:
        if pe and pe == ge:
            tp += 1
            type_tp[goldType] = type_tp.get(goldType,0) + 1
        else:
            type_fn[goldType] = type_fn.get(goldType,0) + 1
            fn += 1
    
    if pe and pe != ge:
        fp += 1

    i += 1

for t in type_fn.keys():
    r = float(type_tp.get(t,0)) / (type_tp.get(t,0) + type_fn.get(t,0))
    print "%s\t%s" % (t, r)

print "%s\t%s\t%s\t%s" % (tp, tn, fp, fn)

p = float(tp) / float(tp + fp)
r = float(tp) / float(tp + fn)
f = 2 * p * r / (p + r)

print "P:%s\nR:%s\nF:%s" % (p,r,f)
