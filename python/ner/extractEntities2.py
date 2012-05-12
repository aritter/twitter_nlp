#!/usr/bin/python

import sys
import os
import re
import subprocess
import platform
import time
import codecs

from signal import *

from optparse import OptionParser

BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))
sys.path.append('%s/python/ner' % (BASE_DIR))
sys.path.append('%s/hbc/python' % (BASE_DIR))

import Features
import twokenize
from LdaFeatures import LdaFeatures
from Dictionaries import Dictionaries
from Vocab import Vocab

sys.path.append('%s/python/cap' % (BASE_DIR))
sys.path.append('%s/python' % (BASE_DIR))
import cap_classifier
import pos_tagger_stdin
import chunk_tagger_stdin

def GetNer(ner_model):
    return subprocess.Popen('java -Xmx256m -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --weights sparse --model-file %s/models/ner/%s' % (BASE_DIR, BASE_DIR, BASE_DIR, ner_model),
                           shell=True,
                           close_fds=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

def GetLLda():
    return subprocess.Popen('%s/hbc/models/LabeledLDA_infer_stdin.out %s/hbc/data/combined.docs.hbc %s/hbc/data/combined.z.hbc 100 100' % (BASE_DIR, BASE_DIR, BASE_DIR),
                           shell=True,
                           close_fds=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

#if platform.architecture() != ('64bit', 'ELF'):
#    sys.exit("Requires 64 bit Linux")

start_time = time.time()

parser = OptionParser()
parser.add_option("--chunk", action="store_true", default=False)
parser.add_option("--pos", action="store_true", default=False)
parser.add_option("--classify", action="store_true", default=False)
(options, args) = parser.parse_args()

if options.pos:
    posTagger = pos_tagger_stdin.PosTagger()
else:
    posTagger = None

if options.chunk and options.pos:
    chunkTagger = chunk_tagger_stdin.ChunkTagger()
else:
    chunkTagger = None

if options.classify:
    llda = GetLLda()
else:
    llda = None

if options.pos and options.chunk:
    ner_model = 'ner.model'
elif options.pos:
    ner_model = 'ner_nochunk.model'
else:
    ner_model = 'ner_nopos_nochunk.model'

ner = GetNer(ner_model)
fe = Features.FeatureExtractor('%s/data/dictionaries' % (BASE_DIR))

capClassifier = cap_classifier.CapClassifier()

vocab = Vocab('%s/hbc/data/vocab' % (BASE_DIR))

dictMap = {}
i = 1
for line in open('%s/hbc/data/dictionaries' % (BASE_DIR)):
    dictionary = line.rstrip('\n')
    dictMap[i] = dictionary
    i += 1

dict2index = {}
for i in dictMap.keys():
    dict2index[dictMap[i]] = i

if llda:
    dictionaries = Dictionaries('%s/data/LabeledLDA_dictionaries3' % (BASE_DIR), dict2index)
entityMap = {}
i = 0
if llda:
    for line in open('%s/hbc/data/entities' % (BASE_DIR)):
        entity = line.rstrip('\n')
        entityMap[entity] = i
        i += 1

dict2label = {}
for line in open('%s/hbc/data/dict-label3' % (BASE_DIR)):
    (dictionary, label) = line.rstrip('\n').split(' ')
    dict2label[dictionary] = label

nLines = 1
reader = codecs.getreader("utf-8")(sys.stdin)
line = reader.readline().strip()
while line:
    words = twokenize.tokenize(line)
    seq_features = []
    tags = []

    goodCap = capClassifier.Classify(words) > 0.9

    if posTagger:
        pos = posTagger.TagSentence(words)
        pos = [p.split(':')[0] for p in pos]  # remove weights   
    else:
        pos = None

    # Chunking the tweet
    if posTagger and chunkTagger:
        word_pos = zip(words, [p.split(':')[0] for p in pos])
        chunk = chunkTagger.TagSentence(word_pos)
        chunk = [c.split(':')[0] for c in chunk]  # remove weights      
    else:
        chunk = None

    quotes = Features.GetQuotes(words)
    for i in range(len(words)):
        features = fe.Extract(words, pos, chunk, i, goodCap) + ['DOMAIN=Twitter']
        if quotes[i]:
            features.append("QUOTED")
        seq_features.append(" ".join(features))
    ner.stdin.write(("\t".join(seq_features) + "\n").encode('utf8'))
        
    for i in range(len(words)):
        tags.append(ner.stdout.readline().rstrip('\n').strip(' '))

    features = LdaFeatures(words, tags)

    #Extract and classify entities
    for i in range(len(features.entities)):
        type = None
        wids = [str(vocab.GetID(x.lower())) for x in features.features[i] if vocab.HasWord(x.lower())]
        if llda and len(wids) > 0:
            entityid = "-1"
            if entityMap.has_key(features.entityStrings[i].lower()):
                entityid = str(entityMap[features.entityStrings[i].lower()])
            labels = dictionaries.GetDictVector(features.entityStrings[i])

            if sum(labels) == 0:
                labels = [1 for x in labels]
            llda.stdin.write("\t".join([entityid, " ".join(wids), " ".join([str(x) for x in labels])]) + "\n")
            sample = llda.stdout.readline().rstrip('\n')
            labels = [dict2label[dictMap[int(x)]] for x in sample[4:len(sample)-8].split(' ')]

            count = {}
            for label in labels:
                count[label] = count.get(label, 0.0) + 1.0
            maxL = None
            maxP = 0.0
            for label in count.keys():
                p = count[label] / float(len(count))
                if p > maxP or maxL == None:
                    maxL = label
                    maxP = p

            if maxL != 'None':
                tags[features.entities[i][0]] = "B-%s" % (maxL)
                for j in range(features.entities[i][0]+1,features.entities[i][1]):
                    tags[j] = "I-%s" % (maxL)
            else:
                tags[features.entities[i][0]] = "O"
                for j in range(features.entities[i][0]+1,features.entities[i][1]):
                    tags[j] = "O"
        else:
            tags[features.entities[i][0]] = "B-ENTITY"
            for j in range(features.entities[i][0]+1,features.entities[i][1]):
                tags[j] = "I-ENTITY"

    if pos:
        sys.stdout.write((" ".join(["%s/%s/%s" % (words[x], tags[x], pos[x]) for x in range(len(words))]) + "\n").encode('utf8'))
    else:
        sys.stdout.write((" ".join(["%s/%s" % (words[x], tags[x]) for x in range(len(words))]) + "\n").encode('utf8'))        
    sys.stdout.flush()

    #seems like there is a memory leak comming from mallet, so just restart it every 1,000 tweets or so
    if nLines % 1000 == 0:
        start = time.time()
        ner.stdin.close()
        ner.stdout.close()
        #if ner.wait() != 0:
        #sys.stderr.write("error!\n")
        #ner.kill()
        os.kill(ner.pid, SIGTERM)       #Need to do this for python 2.4
        ner.wait()
        ner = GetNer(ner_model)
    nLines += 1
    
    line = reader.readline().strip()

end_time = time.time()

print "Average time per tweet = %ss" % (str((end_time-start_time) / nLines))
