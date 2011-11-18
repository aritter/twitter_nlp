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

import chunking_features

_MODEL_FP = ('%s/models/chunk/200Kptb_14Ktwit.model' % (BASE_DIR))

_CLUSTERS = '%s/data/brown_clusters/60K_clusters.txt' % (BASE_DIR)


class ChunkTagger:
    def __init__(self):
        self.GetTagger()
        self.nTagged = 0

    def GetTagger(self):
        self.tagger = subprocess.Popen('java -Xmx400m -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --model-file %s' % (BASE_DIR, BASE_DIR, _MODEL_FP),
                                       shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE)

    def TagSentence(self, word_pos):
        #if self.nTagged % 1000 == 0:
        if self.nTagged % 500 == 0:
            self.tagger.stdin.close()
            self.tagger.stdout.close()
            #self.tagger.kill()
            os.kill(self.tagger.pid, SIGTERM)       #Need to do this for python 2.4
            self.tagger.wait()
            self.GetTagger()

        feat_list = []
        for i in range(len(word_pos)):
            features = chunking_features.nltk_features(word_pos, i)
            features.extend(chunking_features.turian_features(word_pos, i))
            feat_list.append(features)

        # Create string to feed into Mallet
        feat_list_str = []
        for word_feats in feat_list:
            feat_list_str.append(' '.join(word_feats))

        self.tagger.stdin.write(("\t".join(feat_list_str) + "\n").encode('utf8'))
        chunks = []
        for i in range(len(feat_list)):
            chunks.append(self.tagger.stdout.readline().rstrip('\n').strip(' '))
        self.nTagged += 1
        return chunks
