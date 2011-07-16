#!/homes/gws/aritter/local/bin/python

###############################################################################
# TweetNLP.py
# Classes for natuarl language processing (tokenizing, POS tagging, chunking)
# on tweets.  This is mostly heurisitic rule-based stuff....
###############################################################################

import sys
import os
#os.environ['NLTK_DATA'] = '/home/aritter/nltk_data/'

import nltk
from nltk.corpus import brown

sys.path.append("/homes/gws/aritter/modules")

tokens = r"""(?x)      # set flag to allow verbose regexps "
     http://[^ ]+       #urls
   | \@[^ ]+            # Twitter usernames
   | \#[^ ]+            # Twitter hashtags
   | [A-Z]([A-Z]|\.|&)+        # abbreviations, e.g. U.S.A., AT&T
   | \w+(-\w+)*        # words with optional internal hyphens
   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
   | \.\.\.            # ellipsis
   | \'s                # various things
   | \'t
   | n\'t
   | [][.,;"'?():-_`]  # these are separate tokens
"""

grammar = r"""
NP: {<(NNP.?|CD)>+}
    {<DT|PP\$>?<(JJ|CD)>*<(NN[A-Z]?|CD)>+}
"""

cp =  nltk.RegexpParser(grammar)

######################################################################
# For fixing casing issues due to improper capitalization of
# verbs (capitalized verbs cause a ton of problems)
######################################################################
class NLP:
    def Tokenize(self, text):
        return nltk.regexp_tokenize(text, tokens)

    def POSTag(self, text):
        """ Returns POS tags for tokens in a sentence.

        Args:
          text- Sentence of space concatenated tokens.  No new line character.
        """
        return [nltk.pos_tag(text.split(' '))]

    def Chunk(self, text):
        sentences = nltk.sent_tokenize(text)
        return [cp.parse(nltk.pos_tag(self.Tokenize(x))) for x in sentences]

    def NER(self, text):
        sentences = nltk.sent_tokenize(text)
        return [nltk.ne_chunk(nltk.pos_tag(self.Tokenize(x)), binary=False) for x in sentences]


if __name__ == "__main__":
    nlp = NLP()
    for line in sys.stdin.readlines():
        line = line.rstrip("\n")
        print " ".join([x.pprint() for x in nlp.Chunk(line)]).replace("\n", "")
