import sys
import os
import string
import re

def normalize(s):
    s = re.sub(r" 's", "'s", s)
    #return re.sub(r'^the ', '', s.translate(string.maketrans("",""), string.punctuation), re.IGNORECASE)
    return re.sub(r'^the ', '', s.replace('.',''), re.IGNORECASE)


class Dictionaries:
    def __init__(self, dictDir, dict2index):
        self.word2dictionaries = {}
        self.dictionaries = []
        for d in os.listdir(dictDir):
            if re.search(r'.conf~?$', d):       #Skip .conf files
                continue
            self.dictionaries.append(d)
            for line in open(dictDir + "/" + d):
                word = line.rstrip('\n')
                word = word.strip(' ').lower()
                word = normalize(word)
                if not self.word2dictionaries.has_key(word):
                    self.word2dictionaries[word] = []
                self.word2dictionaries[word].append(d)
        #Get the dictionaries into the right order
        self.dictionaries.sort(lambda a,b: cmp(dict2index[a], dict2index[b]))
    
    #Gets a vector with one entry for each dictionary (in the order in "self.dictionaries")
    #if the entry in the vector is "1", the word is in the dictionary, if "0" is not.
    def GetDictVector(self, word):
        dictionaries = set(self.word2dictionaries.get(normalize(word.lower()),[]))
        result = []
        for d in self.dictionaries:
            if d in dictionaries:
                result.append(1)
            else:
                result.append(0)
        return result
