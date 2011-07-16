#!/usr/bin/python

######################################################################################
# Assumes all topics in a (test) entity in context
# are drawn from the same hidden topic.  Basically becomes naive bayes.
######################################################################################

import sys
import re
import math

from optparse import OptionParser

from Vocab import Vocab

parser = OptionParser()
parser.add_option("--topicWord", dest='topicWord', default='topic-word')
parser.add_option("--test", dest='test', default='test.hbc')
parser.add_option("--testEnt", dest='testEnt', default='entities')
parser.add_option("--vocab", dest='vocab', default='vocab')
parser.add_option("--entityTopic", dest='entityTopic', default='entity-topic')
parser.add_option("--labels", dest='labels', default=None)
(options, args) = parser.parse_args()

#TODO: need to include labels

#Read in entity/topic distributions
entityTopic = {}
entityTotals = {}
for line in open(options.entityTopic):
    fields = line.rstrip('\n').split('\t')
    entity = fields[0]
    entityTopic[entity] = {}
    for tc in fields[1:]:
        if tc == "":
            continue
        (topic, count) = re.search(r"(.*):([0-9]+)", tc).groups()
        topic = int(topic)
        count = float(count)
        entityTopic[entity][topic] = count
        entityTotals[entity] = entityTotals.get(entity, 0.0) + count

#Read in counts
topicWord = {}
topicTotals = {}
N = 0.0
for line in open(options.topicWord):
    fields = line.rstrip('\n').split('\t')
    tid = int(fields[0])
    topicWord[tid] = {}
    for wc in fields[1:]:
        (word, count) = re.search(r"(.*):([0-9]+)", wc).groups()
        count = float(count)
        topicWord[tid][word] = count
        topicTotals[tid] = topicTotals.get(tid, 0.0) + count
        N += count

vocab = Vocab(options.vocab)

alpha = 1.0

def normalizePosterior(post):
    #Log-exp-sum trick
    b = max(post.values())
    s = 0.0
    for t in post.keys():
        s += math.exp(post[t]-b)
    s = math.log(s)+b

    for t in post.keys():
        post[t] -= s
        

#Make predictions
eIn = open(options.testEnt)
if options.labels:
    lIn = open(options.labels)
for line in open(options.test):
    entity = eIn.readline().rstrip('\n')
    if options.labels:
        labels = [int(x) for x in lIn.readline().rstrip('\n').split(' ')]
    else:
        labels = [1 for x in topicWord.keys()]
    wids = [x for x in line.rstrip('\n').split(' ')]
    words = []
    for w in wids:
        if vocab.HasId(w):
            words.append(vocab.GetWord(w))

    #Compute N:
    N = 0.0
    for t in topicWord.keys():
        if labels[t-1] == 1:
            N += topicTotals[t]

    post = {}
    for t in topicWord.keys():
        likelihood = 0.0
        prior = 0.0

        #Use FB constraints
        if labels[t-1] == 0:
            continue

        for w in words:
            likelihood += math.log((topicWord[t].get(w,0.0) + alpha) / (topicTotals[t] + vocab.GetVocabSize() * alpha))
        if entityTotals.has_key(entity):
            prior = math.log((entityTopic[entity].get(t,0.0) + alpha) / (entityTotals[entity] + len(topicTotals.keys()) * alpha))
        else:
            prior = math.log((topicTotals[t] + alpha) / (N + float(sum(labels)) * alpha))

        #NOTE: this un-normalized
        post[t] = likelihood + prior
#        print "%s\t%s" % (likelihood, prior)
#    print ""

    #Normalize and convert back from log-space
    normalizePosterior(post)
    for t in post.keys():
        post[t] = math.exp(post[t])

    #Sanity check:
    #print sum(post.values())

    maxT = None
    maxVal = -1
    for t in post.keys():
        if post[t] > maxVal:
            maxT = t
            maxVal = post[t]

    print "%s\t%s:%s" % (entity, maxT, maxVal)
