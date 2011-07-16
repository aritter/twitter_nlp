#!/usr/bin/python

import re
import sys
import subprocess
import os

#BASE_DIR = '/home/aritter/twitter_nlp'
#BASE_DIR = '/homes/gws/aritter/twitter_nlp'
#BASE_DIR = os.environ['HOME'] + '/../aritter/twitter_nlp'
BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))
import twokenize

os.environ['LD_LIBRARY_PATH'] = '%s/lib' % (BASE_DIR)

class CapClassifier:
#    def __init__(self, model='%s/data/cap/tweets_cap_labeled.csv.model' % (BASE_DIR)):
#        self.capClassifier = subprocess.Popen('%s/python/cap/cap_classify %s/data/cap/tweets_cap_labeled.csv.model' % (BASE_DIR, BASE_DIR),
    def __init__(self, model='%s/data/cap2/tweets.annotated.csv.model' % (BASE_DIR)):
        self.capClassifier = subprocess.Popen('%s/python/cap/cap_classify %s/data/cap2/tweets.annotated.csv.model' % (BASE_DIR, BASE_DIR),
                                              shell=True,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE)
#        self.fe = FeatureExtractor('%s/data/cap/tweets_cap.vocab' % (BASE_DIR))
        self.fe = FeatureExtractor('%s/data/cap2/tweets_cap.vocab' % (BASE_DIR))

    def Classify(self, words):
        self.capClassifier.stdin.write("%s\n" % self.fe.Extract(' '.join(words)))
        (features, prediction) = self.capClassifier.stdout.readline().rstrip('\n').split('\t')
        #print "%s\t%s" % (' '.join(words), prediction)
        return float(prediction)


class FeatureVocab:
    def __init__(self):
        self.nextID = 1
        self.str2id = {}
        self.id2str = {}

    def GetID(self, string):
        if not self.str2id.has_key(string):
            self.str2id[string] = self.nextID
            self.id2str[self.nextID] = string
            self.nextID += 1
        return self.str2id[string]

    def GetString(self, ID):
        return self.id2str[ID]

    def Save(self, outFile):
        fOut = open(outFile, 'w')
        for string in self.str2id.keys():
            fOut.write("%s\t%s\n" % (string, self.str2id[string]))
        fOut.close()

    def Load(self, inFile):
        for line in open(inFile):
            line = line.rstrip('\n')
            (string, ID) = line.split('\t')
            ID = int(ID)
            self.nextID = max([ID, self.nextID]) + 1
            self.str2id[string] = ID
            self.id2str[ID] = string

class IdentityFeatureVocab:
    def GetID(self, string):
        return string

    def GetString(self, ID):
        return ID

    def Save(self, f):
        pass

    def Load(self, f):
        pass

class FeatureExtractor:
    def __init__(self, vocabFile, capFile='%s/data/cap/nyt_cap_llr' % (BASE_DIR), useFeatureVocab=True):
        self.vocabFile = vocabFile
        
        if useFeatureVocab:
            self.fVocab = FeatureVocab()
            if os.path.exists(vocabFile):
                self.fVocab.Load(vocabFile)
        else:
            self.fVocab = IdentityFeatureVocab()

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

    def Extract(self, text):
        features = []
        words = twokenize.tokenize(text)

        #hand-crafted features
        iCapitalized = True
        nCapitalized = 0.1
        nAllCaps = 0.1
        nCapLowerViolated = 0.1
        nCapUpperViolated = 0.1
        nWords = 0.1
        for i in range(len(words)):
            capitalized = re.search(r'^([A-Z]|[a-z][A-Z])', words[i])

            if capitalized and not (i == 0 or re.match(r"\.|\?|!|@.+|http:.+|:|\"", words[i-1])):
                nCapitalized += 1.0

            if not (i == 0 or re.match(r"\.|\?|!|@.+|http:.+|:|\"", words[i-1])):
                if capitalized and self.capDict.get(words[i].lower(), '1') != '1':
                    nCapUpperViolated += 1.0
                    features.append(self.fVocab.GetID('upperViolated=%s' % words[i].lower()))
                elif not capitalized and re.match(r'[a-z]+', words[i]) and self.capDict.get(words[i].lower(), '1') != '0':
                    nCapLowerViolated += 1.0
                    #features.append(self.fVocab.GetID('lowerViolated=%s' % words[i].lower()))
                if re.match(r'\w+', words[i][0:1]):
                    nWords += 1
            if re.match(r"i|i'm|im|u", words[i]):
                iCapitalized = False
            if re.match(r"[A-Z]{2,}", words[i]):
                nAllCaps += 1
                
        features.append(self.fVocab.GetID('iCapitalized=%s' % iCapitalized))

        return ' '.join(["%s:1" % x for x in features]) + " %s:%s" % (self.fVocab.GetID('nAllCaps'), nAllCaps/nWords) + " %s:%s" % (self.fVocab.GetID('nCapitalized'), nCapitalized/nWords) + " %s:%s" % (self.fVocab.GetID('nCapLowerViolated'), nCapLowerViolated/nWords) + " %s:%s" % (self.fVocab.GetID('nCapUpperViolated'), nCapUpperViolated/nWords)

    def SaveVocab(self):
        if self.vocabFile:
            self.fVocab.Save(self.vocabFile)

def Train(trainingFile, vocabFile):
    fe = FeatureExtractor(vocabFile)
    fOut = open(trainingFile + '.svm', 'w')
    for line in open(trainingFile):
        line = line.rstrip('\n')
        fields = line.split('\t')
        #if fields[len(fields)-1 - prediction] == "1":
        #if fields[-1] == "0" and fields[-2] == "0":
        if fields[-1] == "1":
            #fOut.write("+1 %s\n" % fe.Extract(fields[6]))
            fOut.write("+1 %s\n" % fe.Extract(fields[0]))
        else:
            #fOut.write("-1 %s\n" % fe.Extract(fields[6]))
            fOut.write("-1 %s\n" % fe.Extract(fields[0]))
    fOut.close()
    fe.SaveVocab()

    os.system("svm_learn %s %s" % (trainingFile + '.svm', trainingFile + '.model'))
    #os.system("svm_learn -t 1 -d 2 -c 10 %s %s" % (trainingFile + '.svm', trainingFile + '.model'))

if __name__ == '__main__':
    #Train('data/cap/tweets_cap_labeled.csv', vocabFile='data/cap/tweets_cap.vocab')
    #Train('data/cap/tweets_cap_train.csv', vocabFile='data/cap/tweets_cap.vocab')
    #Train('data/cap/tweets_cap_test.csv', vocabFile='data/cap/tweets_cap.vocab')
    Train('data/cap2/tweets.annotated.csv', vocabFile='data/cap2/tweets_cap.vocab')

    Train('data/cap2/train1', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/train2', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/train3', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/train4', vocabFile='data/cap2/tweets_cap.vocab')

    Train('data/cap2/fold1', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/fold2', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/fold3', vocabFile='data/cap2/tweets_cap.vocab')
    Train('data/cap2/fold4', vocabFile='data/cap2/tweets_cap.vocab')
