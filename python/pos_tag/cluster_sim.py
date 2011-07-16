import math
import os
import sys

# NEED REPO LOCATION
BASE_DIR = 'twitter_nlp.jar'

if os.environ.has_key('TWITTER_NLP'):
    BASE_DIR = os.environ['TWITTER_NLP']

sys.path.append('%s/python' % (BASE_DIR))

# DON'T SET
CLUSTER_FP = os.path.join(BASE_DIR, 'data/brown_clusters/60K_clusters.txt')
SEED_POS_DIR = os.path.join(BASE_DIR, 'data/brown_clusters/comb_pos')
OOV_WORDS_GOLD = os.path.join(BASE_DIR, 'data/brown_clusters/oov_words.txt')

DEPTHS = range(6, 18)
KNOWN_LIM = 5

# read in clusters
orig_clusters = []
for line in open(CLUSTER_FP):
    w, cid = line.strip().split(' ')
    orig_clusters.append((int(cid), w))

# read in POS dictionaries
pos_words = {}
known_words = set([])
for fp in os.listdir(SEED_POS_DIR):
    if fp == '.svn':
        continue
    s = set([])
    for line in open(os.path.join(SEED_POS_DIR, fp)):
        w = line.split('\t')[0]
        s.add(w)
        known_words.add(w)
    pos_words[fp] = s

# Get cluster information (multiple depths
modifiers = [(1 << d) - 1 for d in sorted(DEPTHS)]
w_cid = {}
clusters = {}
clusters_known = {}
for cid_raw, w in orig_clusters:
    w_cid[w] = []
    for modifier in modifiers:
        cid = cid_raw & modifier
        clusters.setdefault(cid, set([]))
        clusters[cid].add(w)
        clusters_known.setdefault(cid, set([]))
        if w in known_words:
            clusters_known[cid].add(w)
        # Keep track of cluster it is in at each depth
        w_cid[w].append(cid)

# Calculate stats about each cluster
cluster_prob = {}
for cid, clust_words in clusters_known.iteritems():
    temp_counts = {}
    if len(clust_words) < KNOWN_LIM:
        continue
    for pos, pws in pos_words.iteritems():
        for w in clust_words:
            if w in pws:
                temp_counts.setdefault(pos, 0)
                temp_counts[pos] += 1
    d_given_c = {}
    for pos, c in temp_counts.iteritems():
        d_given_c[pos] = float(c) / len(clust_words)
    cluster_prob[cid] = d_given_c


# Getting OOV probs
tot = 0
pos_prob = {}
for line in open(OOV_WORDS_GOLD):
    line = line.strip()
    if not line:
        continue
    w, pos_raw = line.split(' ')
    pos = 'POS_' + pos_raw
    pos_prob.setdefault(pos, 0)
    pos_prob[pos] += 1
    tot += 1
for pos, c in pos_prob.items():
    pos_prob[pos] = float(c) / tot


def get_cos_sim(s1, s2):
    ovlp = 0
    for w in s1:
        if w in s2:
            ovlp += 1
    return float(ovlp) / (math.pow(len(s1), 0.5)*math.pow(len(s2), 0.5))


# A(c,d) = P(d|c) log [ P(d|c) / P(d) ] / S(c)
# c = cluster
# d = dictionary
# P(d|c) = just the overall count of words in the cluster that are from a dictionary
# P(d) = the percentage of tokens given a certain tag (just compute directly from tagged tweets)
def get_assoc_strength(cid, pos):
    if pos not in pos_prob or cid not in cluster_prob or pos not in cluster_prob[cid]:
        return 0.0
    d_give_c = cluster_prob[cid][pos]
    return d_give_c * math.log(d_give_c / pos_prob[pos])

def get_best_match(w):
    if w not in w_cid:
        return None, None
    # Find the cluster to use for w
    cid = -1
    for cid in sorted(w_cid[w], reverse=True):
        if len(clusters_known[cid]) >= KNOWN_LIM:
            break

    s2 = clusters[cid]
    best_score = None
    best_pos = None
    for pos, s1 in pos_words.iteritems():
#        score = get_cos_sim(s1, s2)    
        score = get_assoc_strength(cid, pos)
        if not best_score or score > best_score:
            best_score = score
            best_pos = pos
    return best_pos, list(clusters_known[cid]) + [w]


if __name__ == '__main__':
    # Get the top cluster matches
    top_clusters = []
    for i in range(8, 9):
        modifier = (1 << i) - 1
        clusters = {}
        for cid_raw, w in orig_clusters:
            cid = cid_raw & modifier
            clusters.setdefault(cid, set([]))
            clusters[cid].add(w)

        for pos, s1 in pos_words.iteritems():
            for cid, s2 in clusters.iteritems():
                s = get_cos_sim(s1, s2)
                top_clusters.append((s, pos, cid, s2))

    top_clusters.sort()
    top_clusters.reverse()

    for s, pos, cid, s2 in top_clusters[0:40]:
        s2_l = list(s2)
        print s, pos, cid, s2_l[0:20]
