class LdaFeatures:
    def __init__(self, words, tags, windowSize=3):
        self.words = words
        self.tags  = tags
        self.entities = []
        self.entityTypes = []
        self.entityStrings = []
        bEntIdx = None
        for i in range(len(words)):
            if tags[i][0:2] == 'B-' and bEntIdx == None:
                bEntIdx = i
                self.entityTypes.append(tags[i][2:])
            elif tags[i][0:2] == 'B-' and bEntIdx != None:
                self.entities.append((bEntIdx,i))
                self.entityStrings.append(' '.join(words[bEntIdx:i]))
                self.entityTypes.append(tags[i][2:])
                bEntIdx = i
            elif tags[i][0:2] == 'O' and bEntIdx != None:
                self.entities.append((bEntIdx,i))
                self.entityStrings.append(' '.join(words[bEntIdx:i]))
                bEntIdx = None
        #End case
        if bEntIdx != None:
            self.entities.append((bEntIdx,len(words)))
            self.entityStrings.append(' '.join(words[bEntIdx:len(words)]))

        self.features = []
        for entity in self.entities:
            f = []
            f += ['in=%s' % x for x in  words[entity[0]:entity[1]]]
            f += ['l=%s' % x for x in  words[max(0,entity[0]-windowSize):entity[0]]]
            f += ['r=%s' % x for x in  words[entity[1]:min(len(words),entity[1]+windowSize)]]
            #f += ['t=%s' % x for x in words[0:max(0,entity[0]-windowSize)]]
            #f += ['t=%s' % x for x in words[min(len(words),entity[1]+windowSize):len(words)]]
            self.features.append(f)

    #Compares against gold segmentation, changing the "entityType" of any improperly segmented string to "ERROR"
    def CheckSegmentation(self, gold):
        i = 0
        for e1 in self.entities:
            isError = True
            goldType = None
            j = 0
            for e2 in gold.entities:
                if e1[0] == e2[0] and e1[1] == e2[1]:
                    isError = False
                    goldType = gold.entityTypes[j]
                    break
                j += 1
            if isError:
                self.entityTypes[i] = 'error'
            else:
                self.entityTypes[i] = goldType
            i += 1

    #test that there are the same numbers of B-* tags ans entiteies
    def Test(self):
        nEntities = len([x for x in self.tags if x[0:2] == "B-"])
        if(nEntities != len(self.entities)):
            print self.words
            print self.tags
            print self.entityStrings
        assert(nEntities == len(self.entities))
