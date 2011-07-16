#!/usr/bin/python

import sys
import re
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--entityTopic", dest='entityTopic', default='entity-topic')
parser.add_option("--topicWord", dest='topicWord', default=None)
parser.add_option("--dictFile", dest='dictFile', default='dictionaries')
(options, args) = parser.parse_args()

print options.entityTopic

###############################################################
# Prints out the top k entities for each topic
###############################################################

dictionaries = []
for line in open(options.dictFile):
    dictionaries.append(line.rstrip('\n'))

topicEntity = {}
topicWords = None

if options.topicWord:
    topicWords = {}
    for line in open(options.topicWord):
        fields = line.strip().split('\t')
        topicWords[dictionaries[int(fields[0])-1]] = [x.split(':')[0] for x in fields[1:41]]

for line in open(options.entityTopic):
    fields = line.strip().split('\t')
    entity = fields[0]
    type_ids = [int(x.split(':')[0]) for x in fields[1:]]
    counts = [float(x.split(':')[1]) for x in fields[1:]]

    if len(type_ids) == 0:
        continue

    if(sum(counts) < 40):
        continue

    topType = dictionaries[type_ids[0]-1]
    probTopTopic = counts[0] / sum(counts)
    
    if not topicEntity.has_key(topType):
        topicEntity[topType] = {}
    topicEntity[topType][entity] = probTopTopic

print "\\begin{centering}"
print "\\begin{longtable}{|l|p{2.5in}|p{2.5in}|}"
print "\\hline"
print "Type & Entities which assign higest prob. (not in FB) & Highest probability words given topic \\\\"
print "\\hline"
print "\\hline"
for t in topicEntity.keys():
    entities = sorted(topicEntity[t].keys(), lambda a,b: cmp(topicEntity[t][b], topicEntity[t][a]))
    if options.topicWord:
        words = topicWords[t]
        print t.replace('_', '\\_') + " & " + ", ".join([x.replace('_', '\\_').replace('&', '\\&').replace('#', '\\#') for x in entities[0:20]]) + " & " + ", ".join([x.replace('_', '\\_').replace('&', '\\&').replace('#', '\\#') for x in words]) + "\\\\"
    else:
        print t.replace('_', '\\_') + " & " + ", ".join([x.replace('_', '\\_').replace('&', '\\&').replace('#', '\\#') for x in entities[0:20]]) + "\\\\"
    print "\\hline"

print "\\end{longtable}"
print "\\end{centering}"
