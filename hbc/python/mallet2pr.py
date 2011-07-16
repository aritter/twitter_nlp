#!/usr/bin/python

import sys
import re

threshold = float(sys.argv[1])

tp = 0
fp = 0
fn = 0

typePr = {}

for line in sys.stdin:
    if re.search(r'^\d', line):
        fields = line.rstrip('\n').split(' ')
        gold = fields[1]
        (predicted, conf) = fields[2].split(':')
        print "%s\t%s\t%s" % (gold, predicted, conf)
        conf = float(conf)

        if not typePr.has_key(gold):
            typePr[gold] = [0.0, 0.0, 0.0]      #tp, fp, fn

        if conf > threshold and predicted != 'error':
            if predicted == gold:
                tp += 1.0
                typePr[gold][0] += 1.0
            else:
                fp += 1.0
                typePr[gold][1] += 1.0
                fn += 1.0
                typePr[gold][2] += 1.0
        elif gold != 'error':
            fn += 1

print "tp=%s\tfp=%s\tfn=%s" % (tp, fp, fn)

p = float(tp) / float(tp + fp)
r = float(tp) / float(tp + fn)
f = 2 * p * r / (p + r)

print "p=%s\tr=%s\tf=%s" % (p,r,f)

for t in typePr.keys():
    tp = typePr[t][0]
    fp = typePr[t][1]
    fn = typePr[t][2]

    if tp + fp > 0:
        p = float(tp) / float(tp + fp)
    else:
        p = 0.0
    if tp + fn > 0:
        r = float(tp) / float(tp + fn)
    else:
        r = 0.0
    if p + r > 0:
        f = 2 * p * r / (p + r)
    else:
        f = 0.0

    print "%s\tp=%s\tr=%s\tf=%s" % (t,p,r,f)
