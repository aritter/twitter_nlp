#!/usr/bin/python

import sys
import re

from Vocab import Vocab
from optparse import OptionParser

vocab = Vocab('vocab')

topicCounts = {}
topicTotals = {}
entityTopicCounts = {}

sample = None

parser = OptionParser()
parser.add_option("--sampleFile", dest='sampleFile', default='samples')
parser.add_option("--docFile", dest='docFile', default='docs.hbc')
parser.add_option("--entityFile", dest='entityFile', default='entities')
parser.add_option("--topicWordOut", dest='topicWordOut', default='topic-word')
parser.add_option("--entityTopicOut", dest='entityTopicOut', default='entity-topic')
(options, args) = parser.parse_args()

print "sampleFile=%s" % options.sampleFile
print "docFile=%s" % options.docFile
print "entityFile=%s" % options.entityFile

##################################################
# NOTE: this just keeps the last sample
##################################################
stop = None
for line in open(options.sampleFile):
    line = line.rstrip('\n')
    if line[0:4] == "z = ":
        sample = line[4:]
    if line[0:4] == "s = ":
        stop = line[4:]

words    = open(options.docFile)
entities = open(options.entityFile)

tOut = open(options.topicWordOut, 'w')

stopDist = {}
if stop:
    stop = stop.split(' ;  ;; ')
    stop = [x.strip().split(' ; ') for x in stop]

sample = sample.split(' ;  ;; ')
sample = [x.strip().split(' ; ') for x in sample]

entityList = []

i = 0
#for entitySamples in sample.split(' ;  ;; '):
for e in range(len(sample)):
    if sample[e] == '':
        continue
    entity       = entities.readline().rstrip('\n')
    entityList.append(entity)
    entityTopicCounts[entity] = {}
    tweetWords   = words.readline().strip().split('\t')
    for i in range(len(sample[e])):
        w = tweetWords[i].strip().split(' ')
        z = sample[e][i].strip().split(' ')
        s = None
        if stop:
            s = stop[e][i].strip().split(' ')
        #sys.stderr.write(str(len(w)) + " " + str([vocab.GetWord(x) for x in w]) + "\n")
        #sys.stderr.write(str(len(z)) + " " + str(z) + "\n")
        for j in range(len(w)):
            if w[j] == '':
                continue
            if not topicCounts.has_key(z[j]):
                topicCounts[z[j]] = {}
                topicTotals[z[j]] = 0
            word = vocab.GetWord(w[j])
            if stop and s[j] == '2':
                stopDist[word] = stopDist.get(word, 0) + 1
                continue
            topicCounts[z[j]][word] = topicCounts[z[j]].get(word,0) + 1
            topicTotals[z[j]] += 1
            entityTopicCounts[entity][z[j]] = entityTopicCounts[entity].get(z[j],0) + 1

for topic in sorted(topicCounts.keys(), cmp=lambda a,b: cmp(topicTotals[b], topicTotals[a])):
    terms = topicCounts[topic].keys()
    terms.sort(cmp=lambda a,b: cmp(topicCounts[topic][b], topicCounts[topic][a]))
    tOut.write("%s\t%s\n" % (topic, "\t".join(["%s:%s" % (x,topicCounts[topic][x]) for x in terms])))

eOut = open(options.entityTopicOut, 'w')
#for entity in sorted(entityTopicCounts.keys(), cmp=lambda a,b: cmp(sum(entityTopicCounts[b].values()), sum(entityTopicCounts[a].values()))):
#for entity in entityTopicCounts.keys():
for entity in entityList:
    topics = entityTopicCounts[entity].keys()
    topics.sort(cmp=lambda a,b: cmp(entityTopicCounts[entity][b], entityTopicCounts[entity][a]))
    eOut.write("%s\t%s\n" % (entity, "\t".join(["%s:%s" % (str(x),str(entityTopicCounts[entity][x])) for x in topics])))

if stop:
    sOut = open('stop-dist', 'w')
    for w in sorted(stopDist.keys(), lambda a,b: cmp(stopDist[b], stopDist[a])):
        sOut.write('%s\t%s\n' % (w, stopDist[w]))
