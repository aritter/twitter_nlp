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

import twokenize_wrapper
from pos_tag import cluster_sim
from pos_tag import features

#_MODEL_FP  = ('%s/models/pos/50Kptb_40Knps_5Ktwit_model.model' % (BASE_DIR))
#_MODEL_FP  = ('%s/models/pos/50Kptb_40Knps_7K_4_twit.model' % (BASE_DIR))
_MODEL_FP = ('%s/models/pos/50Kptb_40Knps_12K_best_feats.model' % (BASE_DIR))

_TOKEN2POS_MAPS = ('%s/data/pos_dictionaries/token2pos' % (BASE_DIR))
_TOKEN_MAPS = '%s/data/pos_dictionaries/token' % (BASE_DIR)
_BIGRAM = '%s/data/pos_dictionaries/bigram' % (BASE_DIR)
_CLUSTERS = '%s/data/brown_clusters/60K_clusters.txt' % (BASE_DIR)


class PosTagger:
    def __init__(self):
        self.fe = features.POSFeatureExtractor(_TOKEN2POS_MAPS, _BIGRAM,
                                               _TOKEN_MAPS, _CLUSTERS)
        self.GetTagger()
        self.nTagged = 0

    def GetTagger(self):
        self.tagger = subprocess.Popen('java -Xmx400m -cp %s/mallet-2.0.6/lib/mallet-deps.jar:%s/mallet-2.0.6/class cc.mallet.fst.SimpleTaggerStdin --model-file %s' % (BASE_DIR, BASE_DIR, _MODEL_FP),
                                       shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE)

    def TagSentence(self, words):
        #if self.nTagged % 1000 == 0:
        if self.nTagged % 500 == 0:
            self.tagger.stdin.close()
            self.tagger.stdout.close()
            #self.tagger.kill()
            os.kill(self.tagger.pid, SIGTERM)       #Need to do this for python 2.4
            self.tagger.wait()
            self.GetTagger()

        feat_list = []
        for word in words:
            feat_list.append(self.fe.get_features(word))
        # Add context features
        feat_list = features.add_context_features(feat_list)
        self.fe.add_bigram_features(feat_list)

        # Create string to feed into Mallet
        feat_list_str = []
        for word_feats in feat_list:
            feat_list_str.append(' '.join(word_feats))

        self.tagger.stdin.write(("\t".join(feat_list_str) + "\n").encode('utf8'))
        pos = []
        for i in range(len(feat_list)):
            pos.append(self.tagger.stdout.readline().rstrip('\n').strip(' '))
        self.nTagged += 1
        return pos


if __name__ == "__main__":
    posTagger = PosTagger()
    for line in sys.stdin:
        words = twokenize_wrapper.tokenize(line.strip())
        if not words:
            continue
        pos = posTagger.TagSentence(words)
        print "%s\t%s\t%s" % (line, " ".join(words), " ".join(pos))
