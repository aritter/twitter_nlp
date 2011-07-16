#!/usr/bin/python

import sys
import re

from optparse import OptionParser
from operator import indexOf

from Vocab import Vocab

#import psyco
#psyco.full()

class DLCoTrain:
    def __init__(self):
        self.context = []
        self.spelling = []
        self.both = []
        self.labels = []
        self.seedlabels = []
        self.contextualCounts = {}
        self.spellingCounts = {}
        self.alpha = 1.0
        self.n = 5
        self.pmin = 0.95
        self.rules = None

    def AddData(self, words, labels):
        self.context.append([])
        self.spelling.append([])
        self.both.append([])
        for word in words:
            self.both[len(self.spelling)-1].append(word)
            if word[0:3] == 'in=':
                self.spelling[len(self.spelling)-1].append(word)
            else:
                self.context[len(self.spelling)-1].append(word)
                
        if sum(labels) == 1:
            self.labels.append(indexOf(labels, 1))
            self.seedlabels.append(indexOf(labels, 1)+1)
        else:
            self.labels.append(-1)
            self.seedlabels.append(-1)

    def Label(self, features, rules):
        labels = []
        for i in range(len(features)):
            maxLabel = None
            maxValue = -1.0

            if self.seedlabels[i] != -1:
                labels.append(self.seedlabels[i])
                continue

            for x in features[i]:
                for y in rules.keys():
                    if rules[y].has_key(x) and rules[y][x] > maxValue:
                        maxValue = rules[y][x]
                        maxLabel = y
            if maxLabel:
                labels.append(maxLabel)
            else:
                labels.append(-1)
        return labels

    def SupervisedDlTrain(self, features, labels, usePmin=True):
        countXY = {}
        countX = {}
        for i in range(len(features)):
            if labels[i] == -1:
                continue
            for f in features[i]:
                key = (f,labels[i])
                countXY[key] = countXY.get(key,0.0) + 1.0
                key = f
                countX[key] = countX.get(key,0.0) + 1.0

        rules = {}
        for (x,y) in countXY.keys():
            p = countXY[(x,y)] / countX[x]
            if p > self.pmin or not usePmin:
                if not rules.has_key(y):
                    rules[y] = {}
                rules[y][x] = countXY[(x,y)]

        topNrules = {}
        for y in rules.keys():
            topNrules[y] = {}
            topn = sorted(rules[y].keys(), cmp=lambda a,b: cmp(rules[y][b], rules[y][a]))[0:self.n]
            for x in topn:
                p = (countXY[(x,y)] + self.alpha) / (countX[x] + self.alpha * float(len(rules.keys())))
                topNrules[y][x] = p

        return topNrules

    def Train(self):
        while self.n < 2500:
#            print self.n
            contextrules = self.SupervisedDlTrain(self.context, self.labels)
            self.labels = self.Label(self.context, contextrules)
            spellingrules = self.SupervisedDlTrain(self.spelling, self.labels)
            self.labels = self.Label(self.spelling, spellingrules)
            self.n += 5

        #Combine rules
        rules = {}
        for y in contextrules.keys():
            rules[y] = {}
            for x in contextrules[y].keys():
                rules[y][x] = contextrules[y][x]
            for x in spellingrules[y].keys():
                rules[y][x] = spellingrules[y][x]

        self.labels = self.Label(self.both, rules)
        rules = self.SupervisedDlTrain(self.both, self.labels, usePmin=False)

        self.rules = rules

    def SaveRules(self, outFile):
        fOut = open(outFile, 'w')
        for y in self.rules.keys():
            for x in sorted(self.rules[y].keys(), cmp=lambda a,b: cmp(self.rules[y][b], self.rules[y][a])):
                fOut.write("%s\t%s\t%s\n" % (x,y,self.rules[y][x]))

    def LoadRules(self, inFile):
        self.rules = {}
        for line in open(inFile):
            (x,y,p) = line.rstrip('\n').split('\t')
            if not self.rules.has_key(y):
                self.rules[y] = {}
            self.rules[y][x] = p

    def Classify(self, words, labels=None):
        maxVal = -1
        maxClass = None
        for w in words:
            for y in self.rules.keys():
                for x in self.rules[y].keys():
                    if x == w and self.rules[y][x] > maxVal:
                        if labels and labels[int(y)-1] == 0:
                            continue
                        maxVal = self.rules[y][x]
                        maxClass = y
        return (maxClass, maxVal)
                        

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--unlabeled", dest='unlabeled', default=None)
    parser.add_option("--vocab", dest='vocab', default='vocab')
    parser.add_option("--labels", dest='labels', default='labels')
    parser.add_option("--rulesOut", dest='rulesOut', default=None)
    parser.add_option("--rulesIn", dest="rulesIn", default=None)
    parser.add_option("--test", dest="test", default=None)
    (options, args) = parser.parse_args()

    vocab = Vocab(options.vocab)
    
    cotrain = DLCoTrain()

    if options.unlabeled:
        fLabels = open(options.labels)
        for line in open(options.unlabeled):
            words = [vocab.GetWord(x) for x in line.rstrip('\n').split(' ')]
            labels = [int(x) for x in fLabels.readline().rstrip('\n').split(' ')]
            cotrain.AddData(words, labels)
    
        rules = cotrain.Train()

        cotrain.SaveRules(options.rulesOut)

    if options.rulesIn:
        cotrain.LoadRules(options.rulesIn)

    if options.test:
        fEnt = open('entities')
        fLabels = open(options.labels)
        for line in open(options.test):
            words = [vocab.GetWord(x) for x in line.rstrip('\n').split(' ')]
            labels = [int(x) for x in fLabels.readline().rstrip('\n').split(' ')]
            #print words
            entity = fEnt.readline().rstrip('\n')
            (pred, conf) = cotrain.Classify(words, labels=labels)
            if not pred:
                pred = 0
            print "%s\t%s:%s" % (entity, pred, conf)

#    for l in cotrain.rules.keys():
#        print l
#        print ["%s:%s" % (x, cotrain.rules[l][x]) for x in  sorted(cotrain.rules[l].keys(), cmp=lambda a,b: cmp(cotrain.rules[l][b], cotrain.rules[l][a]))]
