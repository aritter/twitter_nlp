#!/usr/bin/python

import sys
import os
import re
import subprocess
import time

from signal import *

#sys.path.append("/home/aritter/local/lib64/python2.4/site-packages")
#from guppy import hpy

#BASE_DIR = '/home/aritter/twitter_nlp'
#BASE_DIR = os.environ['HOME'] + '/twitter_nlp'
#BASE_DIR = '/homes/gws/aritter/twitter_nlp'
BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))
sys.path.append('%s/python/ner' % (BASE_DIR))
sys.path.append('%s/hbc/python' % (BASE_DIR))

import Features
import twokenize

sys.path.append('%s/python' % (BASE_DIR))

def GetNer():
    return subprocess.Popen('java -Xmx256m -Xms256m -XX:+UseSerialGC -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --weights sparse --model-file %s/models/event/event.model' % (BASE_DIR, BASE_DIR, BASE_DIR),
                           shell=True,
                           close_fds=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)

ner = GetNer()

fe = Features.FeatureExtractor('%s/data/dictionaries_event' % (BASE_DIR))

#if len(sys.argv) > 1:
#    posTagger = pos_tagger_stdin.PosTagger()
#else:
#    posTagger = None
#posTagger = pos_tagger_stdin.PosTagger()
#chunker = chunker_stdin.Chunker()

#h = hpy()
#print h.heap()
#print "================================================"

nLines = 1
for line in sys.stdin:
    line = unicode(line, errors='ignore')
    line = line.rstrip(u'\n')
    fields = line.split(u'\t')
    words = twokenize.tokenize(fields[6])
    seq_features = []
    tags = []

    pos = fields[-2].split(u' ')

    quotes = Features.GetQuotes(words)
    for i in range(len(words)):
        features = fe.Extract(words, pos, None, i, False) + [u'DOMAIN=Twitter']
        if quotes[i]:
            features.append(u"QUOTED")
        seq_features.append(" ".join(features))
    ner.stdin.write("\t".join(seq_features) + u"\n")
        
    for i in range(len(words)):
        tags.append(ner.stdout.readline().rstrip(u'\n').strip(u' '))

    print line + u"\t%s" % u" ".join(tags)
    sys.stdout.flush()

    #seems like there is a memory leak comming from mallet, so just restart it every 1,000 tweets or so
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
        #sys.stderr.write(u"%s\t%s\n" % (nLines, time.time() - start))
    nLines += 1
