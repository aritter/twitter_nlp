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
#sys.path.append('%s/python/ner' % (BASE_DIR))
sys.path.append('%s/python/event' % (BASE_DIR))
sys.path.append('%s/hbc/python' % (BASE_DIR))

import Features
import twokenize

sys.path.append('%s/python' % (BASE_DIR))

class EventTagger:
    def __init__(self):
        self.fe = Features.FeatureExtractor('%s/data/dictionaries_event' % (BASE_DIR))
        self.GetTagger()
        self.nTagged = 0

    def GetTagger(self):
        self.tagger = subprocess.Popen('java -Xmx256m -Xms256m -XX:+UseSerialGC -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --weights sparse --model-file %s/models/event/event.model' % (BASE_DIR, BASE_DIR, BASE_DIR),
                                       shell=True,
                                       #close_fds=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE)

    def TagSentence(self, words, pos):
        if self.nTagged % 500 == 0:
            self.tagger.stdin.close()
            self.tagger.stdout.close()
            #self.tagger.kill()
            os.kill(self.tagger.pid, SIGTERM)       #Need to do this for python 2.4
            self.tagger.wait()
            self.GetTagger()

        features = []
        seq_features = []
        quotes = Features.GetQuotes(words)
        for i in range(len(words)):
            features = self.fe.Extract(words, pos, None, i, False) + [u'DOMAIN=Twitter']
            if quotes[i]:
                features.append(u"QUOTED")
            seq_features.append(" ".join(features))

        #print ("\t".join(seq_features) + "\n").encode('utf8')
        self.tagger.stdin.write(("\t".join(seq_features) + "\n").encode('utf8'))

        event_tags = []
        for i in range(len(words)):
            event_tags.append(self.tagger.stdout.readline().rstrip('\n').strip(' '))
        self.nTagged += 1
        return event_tags
