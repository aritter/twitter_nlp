#!/homes/gws/aritter/local/bin/python

###############################################################################
# Pos tags all tweets in a file.  One tweet per line.
#
###############################################################################

import sys

import mallet_wrapper
import twokenize_wrapper

#_MODEL_FP  = ('/home/ssclark/stable_twitter_nlp/models/pos/'
#              '50Kptb_40Knps_5Ktwit_model.model')
_MODEL_FP  = ('/home/ssclark/stable_twitter_nlp/models/pos/'
              '50Kptb_40Knps_7K_4_twit.model')

_TOKEN2POS_MAPS = ('/home/ssclark/stable_twitter_nlp/data/'
                   'pos_dictionaries/token2pos')
_TOKEN_MAPS = '/home/ssclark/stable_twitter_nlp/data/pos_dictionaries/token'
_BIGRAM = '/home/ssclark/stable_twitter_nlp/data/pos_dictionaries/bigram'
_TEMP_DIR = './'


def main(tweet_fp):
    pos_tagger = mallet_wrapper.MalletPOSTagger(_MODEL_FP, _TOKEN2POS_MAPS,
                                                _TOKEN_MAPS, _BIGRAM,
                                                _TEMP_DIR)
    tweet_tokens_list = []
    sys.stderr.write('Creating mallet test file.\n')
    for line in open(tweet_fp):
        tweet_tokens_list.append(twokenize_wrapper.tokenize(line.rstrip('\n')))
    return pos_tagger.pos_tag_tweets(tweet_tokens_list)

if __name__ == '__main__':
    pos_tag_list = main(sys.argv[1])
    for pos_tags in pos_tag_list:
        print ' '.join([tok + '/' + pos for tok, pos in pos_tags])
