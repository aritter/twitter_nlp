#!/usr/bin/python

###################################################################################
# cap_eval.py
#
# Evaluates how well we can identify whether a given tweet is properly capitalized
###################################################################################

import re
import sys
sys.path.append('/homes/gws/aritter/twitter_nlp/python')

import twokenize

class DictEval:
    def __init__(self, capFile):
        #Read in capitalization dictionary from NYT data
        self.capDict = {}
        capDictSize = 5000
        for line in open(capFile):
            line = line.rstrip('\n')
            (llr, word, cap, cw, cc, cwc, N) = line.split('\t')
            self.capDict[word] = cap
            
            capDictSize -= 1
            if capDictSize == 0:
                break

    def Eval(self, tweet):
        words = tweet[6].split(' ')
        for i in range(len(words)):
            capitalized = re.search(r'^[A-Z]|[a-z][A-Z]', words[i])
            if i > 0 and not re.match(r"\.|\?|!|@.+|http:.+|:|\"", words[i-1]):
                if capitalized and self.capDict.get(words[i].lower(), '1') != '1':                
                    return False
                #elif not capitalized and re.match(r'[a-z]+', words[i]) and self.capDict.get(words[i].lower(), '1') != '0':
                #    return False
        return True

######################################################################
# Simple heuristic: at least one word is capitalized and at least
# one noun or verb is lowercase
######################################################################
def SimpleEval(tweet):
    words = tweet[6].split(' ')
    
    capFound = False
    lowFound = False

    for i in range(len(words)):
        if re.search(r'[A-Z]', words[i][0:1]):
            capFound = True
        elif i > 0 and not re.match(r"\.|\?|!|@.+|http:.+|:|\"", words[i-1]) and re.match(r'[^a-z]+', words[i]):
            lowFound = True

    return capFound and lowFound

def Baseline(tweet):
    return True

class CapEval:
    def __init__(self, testData):
        self.labeledTweets = []
        for line in open(testData):
            line = line.rstrip('\n')
            fields = line.split('\t')
            fields[6] = ' '.join(twokenize.tokenize(fields[6]))
            self.labeledTweets.append(fields)

    def Eval(self, classifier):
        fp = 0.0
        fn = 0.0
        tp = 0.0
        tn = 0.0

        for tweet in self.labeledTweets:
            if classifier(tweet) and tweet[len(tweet)-1] == '1':
                tp += 1.0
            elif not classifier(tweet) and tweet[len(tweet)-1] == '1':
                fn += 1.0
            elif not classifier(tweet) and tweet[len(tweet)-1] == '0':
                tn += 1.0
            elif classifier(tweet) and tweet[len(tweet)-1] == '0':
                fp += 1.0

        #Avoid division by 0
        if tp > 0.0:
            return (tp, tn, fp, fn, tp / (tp + fp), tp / (tp + fn))
        else:
            return (tp, tn, fp, fn, 0, 0)

if __name__ == "__main__":
    ce = CapEval('/homes/gws/aritter/twitter_nlp/data/cap/tweets_cap_test.csv')
    de = DictEval('/homes/gws/aritter/twitter_nlp/data/cap/nyt_cap_llr')
    print "dict:\t" + str(ce.Eval(de.Eval))
    print "simple:\t" + str(ce.Eval(SimpleEval))
