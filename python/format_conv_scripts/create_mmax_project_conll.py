#!/homes/gws/aritter/local/bin/python

###############################################################################
# Create all files needed for a MMax2 project.  
#
# Assumes tweets are already tokenized and POS tagged in "CoNLL format"
#
# Usage: python create_mmax_project.py <tweets file> <template dir>
# <project dir> <project name>
###############################################################################

import os
import re
import shutil
import sys

# TODO: Find a better way to import TweetNLP
PYTHON_SCRIPTS_DIR = "python/"
sys.path.append(PYTHON_SCRIPTS_DIR)

import mallet_wrapper
import twokenize_wrapper
from pos_tag import symbol_tag
#import TweetNLP

# Variables for picking the model to tag with
_model_location  = ('/home/ssclark/FeatureSelectTests/DomainTransferTest'
                    '/50Kptb_40Knps_3Ktwit_NewDicts/model_name.model')
_token2pos = ('/home/ssclark/stable_twitter_nlp/data/'
                     'pos_dictionaries/token2pos')
_token = '/home/ssclark/stable_twitter_nlp/data/pos_dictionaries/token'
_temp_dir = './'


def create_project(sent_file, template_folder, new_proj_folder, new_proj_name):
    # Check that directories/files exist (or don't)
    if not os.path.isdir(template_folder):
        print 'Template folder DNE: ', template_folder
        return
    elif os.path.isdir(new_proj_folder):
        print 'Will overwrite the following directory: ', new_proj_folder
        return
    elif not os.path.exists(sent_file):
        print 'Sentence files does not exist: ', sent_file
        return

    # Make sure the project name doesn't have spaces
    new_proj_name = re.sub(' ', '_', new_proj_name)

    # Copy over all standard mmax2 files
    shutil.copytree(template_folder, new_proj_folder)
    f = open(os.path.join(new_proj_folder, new_proj_name + '.mmax'), 'w')
    f.write(MMAX_STRING % new_proj_name)
    f.close()

    # Creating word, pos, and sentence files
    f_word = open(os.path.join(new_proj_folder,
                               new_proj_name + '_words.xml'), 'w')
    f_pos = open(os.path.join(new_proj_folder,
                              new_proj_name + '_POS_level.xml'), 'w')
    f_ner = open(os.path.join(new_proj_folder,
                              new_proj_name + '_NER_level.xml'), 'w')
    f_sent = open(os.path.join(new_proj_folder,
                               new_proj_name + '_sentence_level.xml'), 'w')

    # Add headers
    f_word.write(WORDS_HEADER_STRING)
    f_pos.write(POS_HEADER_STRING)
    f_ner.write(NER_HEADER_STRING)
    f_sent.write(SENT_HEADER_STRING)

    # For each sentence(tweet) in the file.
    pos_tagged_tweets = []
    tweet = []
    for line in open(sent_file):
        line = line.strip()
        if line == '':
            pos_tagged_tweets.append(tweet)
            tweet = []
            continue
        (word, pos) = line.split(' ')
        tweet.append((word,pos))

    # Add markables  
    word_count = 1
    tweet_count = 1
    for tagged_tweet in pos_tagged_tweets:
        start_count = word_count
        # For each word/pos in the sentence
        for word, pos in tagged_tweet:
            # Check if the word is a user, RT, or hash tag
            new_pos = symbol_tag.tag_token(word)
            if new_pos:
                pos = new_pos
            f_word.write(WORD_STRING % (word_count, word))
            f_pos.write(POS_STRING % (word_count, word_count, pos.lower()))
            word_count += 1

        f_sent.write(SENT_STRING % (tweet_count, start_count, word_count - 1))
        tweet_count += 1

    # Add closing tags
    f_word.write('</words>')
    f_pos.write('</markables>')
    f_ner.write('</markables>')
    f_sent.write('</markables>')

    f_word.close()
    f_pos.close()
    f_ner.close()
    f_sent.close()

# STRINGS USED TO GENERATE MMAX2 FILES

MMAX_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<mmax_project>
<words>%s_words.xml</words>
<keyactions></keyactions>
<gestures></gestures>
</mmax_project>
"""

WORDS_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE words SYSTEM "words.dtd">
<words>
"""

POS_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE markables SYSTEM "markables.dtd">
<markables xmlns="www.eml.org/NameSpaces/POS">
"""

NER_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE markables SYSTEM "markables.dtd">
<markables xmlns="www.eml.org/NameSpaces/NER">
"""

SENT_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE markables SYSTEM "markables.dtd">
<markables xmlns="www.eml.org/NameSpaces/sentences">
"""

WORD_STRING = '<word id="word_%d">%s</word>\n'
POS_STRING = ('<markable id="markable_%d" span="word_%d" mmax_level="pos" '
              ' tag="%s" />\n')
SENT_STRING = ('<markable id="markable_%d" span="word_%d..word_%d" '
               'mmax_level="sentences" />\n')

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print ('USAGE: ./create_mmax_project <sentence file> '
               '<template folder> <new project folder> <new project name>')
    else:
        sent_file = sys.argv[1]
        template_folder = sys.argv[2]
        new_proj_folder = sys.argv[3]
        new_proj_name = sys.argv[4]
        create_project(sent_file, template_folder, new_proj_folder,
                       new_proj_name)
