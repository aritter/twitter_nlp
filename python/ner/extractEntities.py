#!/usr/bin/python

import sys
import os
import re
import subprocess
import time

from signal import *

#BASE_DIR = '/home/aritter/twitter_nlp'
#BASE_DIR = os.environ['HOME'] + '/twitter_nlp'
#BASE_DIR = '/homes/gws/aritter/twitter_nlp'
BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))
sys.path.append('%s/python/ner' % (BASE_DIR))

import Features
import twokenize

sys.path.append('%s/python/cap' % (BASE_DIR))
sys.path.append('%s/python' % (BASE_DIR))
import cap_classifier
import pos_tagger_stdin

#ner = subprocess.Popen('java -Xmx1024m -cp /homes/gws/aritter/mallet-2.0.6/lib/mallet-deps.jar:/homes/gws/aritter/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --include-input false --model-file /homes/gws/aritter/twitter_nlp/data/ner/tweets/combined_train2_nocap_100k.model',

def GetNer():
    #return subprocess.Popen('java -Xmx256m -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --weights sparse --model-file %s/experiments/domain_transfer/combined_train.model' % (BASE_DIR, BASE_DIR, BASE_DIR),
    return subprocess.Popen('java -Xmx256m -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --weights sparse --model-file %s/models/ner/noclass.model' % (BASE_DIR, BASE_DIR, BASE_DIR),
                           shell=True,
                           close_fds=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

ner = GetNer()

#df = Features.DictionaryFeatures('/homes/gws/aritter/twitter_nlp/data/dictionaries')
fe = Features.FeatureExtractor('%s/data/dictionaries' % (BASE_DIR))

if len(sys.argv) > 1:
    posTagger = pos_tagger_stdin.PosTagger()
else:
    posTagger = None
capClassifier = cap_classifier.CapClassifier()

nLines = 1
for line in sys.stdin:
    line = line.rstrip('\n')
    fields = line.split('\t')
    words = twokenize.tokenize(fields[6])
    seq_features = []
    tags = []

    goodCap = capClassifier.Classify(words) > 0.9

    if posTagger:
        pos = posTagger.TagSentence(words)
    else:
        pos = fields[-1].split(' ')

    quotes = Features.GetQuotes(words)
    for i in range(len(words)):
        features = fe.Extract(words, pos, i, goodCap) + ['DOMAIN=Twitter']
        if quotes[i]:
            features.append("QUOTED")
        seq_features.append(" ".join(features))
    ner.stdin.write("\t".join(seq_features) + "\n")
        
    for i in range(len(words)):
        tags.append(ner.stdout.readline().rstrip('\n').strip(' '))

    #for i in range(len(words)):
    #    sys.stdout.write(" %s/%s " % (words[i], tags[i]))
    #print ""

    entity = None
    tag = None
    score = None
    for i in range(len(words)):
        if tags[i][0:2] == "I-" or tags[i][0:2] == "B-":
            (tags[i], score) = tags[i].split(':')
        if entity and not tags[i][0:2] == "I-":
            print line + "\t%s\t%s\t%s\t%s" % (" ".join([x.split(':')[0] for x in tags]), " ".join(entity), tag, score)
            sys.stdout.flush()
            tag = None
            entity = None
        elif entity and tags[i][0:2] == "I-":
            entity.append(words[i])
        if tags[i][0:2] == 'B-':
            entity = [words[i]]
            tag = tags[i][2:]

    #This is pretty rediculous, but seems like mallet has a memory leak, so just restart it every 1,000 tweets or so
    #if nLines % 1000 == 0:
    if nLines % 500 == 0:
        start = time.time()
        ner.stdin.close()
        ner.stdout.close()
        #if ner.wait() != 0:
        #sys.stderr.write("error!\n")
        #ner.kill()
        os.kill(ner.pid, SIGTERM)       #Need to do this for python 2.4
        ner.wait()
        ner = GetNer()
#        posTagger.tagger.kill()                #NOTE: pos_tagger handles this...
#        posTagger.tagger.wait()
#        posTagger = pos_tagger_stdin.PosTagger()
        sys.stderr.write("%s\t%s\n" % (nLines, time.time() - start))
    nLines += 1
