############################################################################## 
# Library for extracting various types of features for chunking.
############################################################################## 

import os
import sys

BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))

LOWERCASE = False
USE_CLUSTERS = True
PLUS_TURIAN = True

# Building clusters
cluster_fp = os.path.join(BASE_DIR, 'data/brown_clusters/60K_clusters.txt')
pref_cluster_list=[4,6,10,20]
word_cid = {}
for line in open(cluster_fp):
    word, cid = line.strip().split(' ')
    word_cid[word] = int(cid)
cluster_list = []
for cid in pref_cluster_list:
    cluster_list.append((1<<cid) - 1)

def nltk_features(word_tag_list, i):
    w, t = word_tag_list[i]
    feature_list = [w, t]
    if USE_CLUSTERS: feature_list.extend(add_clst(w, 'CUR'))
    if i == 0:
        feature_list.extend(['<LW_START>', '<LP_START>'])
    else:
        w, t = word_tag_list[i-1]
        feature_list.extend([w + ';;LW', t + ';;LT'])
        if USE_CLUSTERS: feature_list.extend(add_clst(w, 'LW'))
    if i == len(word_tag_list) - 1:
        feature_list.extend(['<NW_END>', '<NP_END>'])
    else:
        w, t = word_tag_list[i+1]
        feature_list.extend([w + ';;NW', t + ';;NT'])
        if USE_CLUSTERS: feature_list.extend(add_clst(w, 'NW'))
    feature_list.append('LDT::' + tags_since_dt(word_tag_list, i))
    return feature_list

def add_clst(w, pre):
    feature_list = []
    lw = w.lower()
    if lw not in word_cid:
        return feature_list
    cid = word_cid[lw]
    for cs in cluster_list:
        feature_list.append(pre + '_CS_' + str(cs) + '_' + str(cid & cs))
    return feature_list
    

def turian_features(word_tag_list, i):
    """ Features:
    -All words within 2 in front and 2 behind the given word.
    -All tags in same range.
    -Bigrams that the word is in.
    -Bigrams and Trigrams that tags are in.
    """
    feature_list = []
    for wi in range(max(i-2, 0), min(i+3, (len(word_tag_list) - 1))):
        # Word/Tag Unigra
        w, t = word_tag_list[wi]
        t = t[0:2]
        """
        feature_list.append('WUNI_' + str(i - wi) + '_' + w)
        feature_list.append('TUNI_' + str(i - wi) + '_' + t)
        """
        # Word/Tag Bigrams
        if wi > 0 and (i - wi >= -1):
            wb, tb = word_tag_list[wi - 1]
            tb = tb[0:2]
            feature_list.append('TBIG_' + str(i - wi) + '_' + tb + '_' + t)
            if wi == i or wi == (i + 1):
                feature_list.append('WBIG_' + str(i - wi) + '_' + wb + '_' + w)
            # Tag Trigrams
            if wi + 1 < len(word_tag_list) and (i - wi >= 0):
                wa, ta = word_tag_list[wi + 1]
                ta = ta[0:2]
                feature_list.append('TRIG_' + str(i - wi) + '_' + tb + '_'
                                    + t + '_' + ta)
        # Adding cluster info
        """
        if USE_CLUSTERS:
            lw = w.lower()
            if lw not in word_cid:
                continue
            cid = word_cid[lw]
            for cs in cluster_list:
                feature_list.append('CS_' + str(i - wi) + '_' + str(cs) + '_' +
                                    str(cid & cs))
        """
    return feature_list

def tags_since_dt(word_tag_list, i):
    tags = set()
    for word, pos in word_tag_list[:i]:
        if pos == 'DT':
            tags = set()
        else:
            tags.add(pos)
    return '+'.join(sorted(tags))

if __name__ == '__main__':
    cur_tok_features = []
    cur_tags = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            if not cur_tok_features:
                continue
            else:
                for i in range(len(cur_tok_features)):
                    features = nltk_features(cur_tok_features, i)
                    if PLUS_TURIAN:
                        features.extend(turian_features(cur_tok_features, i))
                    if cur_tags:
                        features.append(cur_tags[i])
                    print ' '.join(features)
                print ''
                cur_tok_features = []
                cur_tags = []
        else:
            tp = line.split(' ')
            word = tp[0]
            if LOWERCASE:
                word = word.lower()
            pos = tp[1]
            cur_tok_features.append((word, pos))
            if len(tp) == 3:
                cur_tags.append(tp[2])
