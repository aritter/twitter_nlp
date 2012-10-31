#!/usr/bin/python

###############################################################################
# Library for extracting various types of features for a POS tagger
###############################################################################
import os
import re
import sys

import symbol_tag
import cluster_sim

class POSFeatureExtractor:
    def __init__(self, token2pos_dir, token_dir, bigram_dir=None,
                 cluster_fp=None):
        # Dictionaries with POS information
        self.dictionaries = {} 
        for dict_name in os.listdir(token2pos_dir):
            if dict_name == '.svn':
                continue
            dict_file = os.path.join(token2pos_dir, dict_name)
            self.dictionaries[dict_name] = Dictionary(dict_file, True)
        # Dictionaries with random info about tokens
        self.occurences = {}
        for dict_name in os.listdir(token_dir):
            if dict_name == '.svn':
                continue
            dict_file = os.path.join(token_dir, dict_name)
            self.occurences[dict_name] = Dictionary(dict_file, False)
        # Dictionaries with bigram information
        self.bigram_dictionaries = {} 
        if bigram_dir:
            for dict_name in os.listdir(bigram_dir):
                if dict_name == '.svn':
                    continue
                dict_file = os.path.join(bigram_dir, dict_name)
                self.bigram_dictionaries[dict_name] = Dictionary(dict_file,
                                                                 True)
        # Dictionaries with cluster information
        self.cluster_dictionary = None
        if cluster_fp:
            self.cluster_dictionary = ClusterDictionary(cluster_fp)

    def get_features(self, token):
        ltoken = token.lower()
        feature_list = [ltoken]

        # First off, if it looks like it's a RT, HT, USR, or URL don't
        # add any features but the symbol tags
        # Get potential symbol tags
        pos = symbol_tag.tag_token(ltoken)
        if pos:
            feature_list.append('SYMBOL_REGX=' + str(pos))        
        if pos in ['usr', 'rt', 'ht', 'url']:
            return ['SYMBOL_REGX=' + str(pos)]

        # Use the dictionaries to see what common tags exist
        in_pos_dict = False
        dictionary_list = []
        for dict_name, dictionary in self.dictionaries.iteritems():
            if ltoken in dictionary.token_pos_set:
                in_pos_dict = True
                # Record all POS tags the token has been seen with
                pos_set = dictionary.token_pos_set[ltoken]
                for pos in pos_set:
                    feature_list.append(dict_name + '=' + pos)
                # Record if it has only been seen with one
                if len(pos_set) == 1:
                    feature_list.append(dict_name + '_ONLY=' + pos)
                # Record the majority POS tag
                # Make sure the majority is a real majority
                pos_l = [(count, pos) for pos, count in pos_set.items()]
                pos_l.sort()
                pos_l.reverse()
                # If one tag and count greater than 1
                if len(pos_l) == 1 and pos_l[0][0] > 1:
                    feature_list.append(dict_name + '_MAJORITY=' + pos_l[0][1])
                elif len(pos_l) > 1 and (pos_l[0][0] > 1.5*pos_l[1][0]):
                    feature_list.append(dict_name + '_MAJORITY=' + pos_l[0][1])
                            
                # Record that dictionary found something
                dictionary_list.append(dict_name)

        # Check if the token occurs in new dictionaries (lexicons)
        for dictname, dictionary in self.occurences.iteritems():
            if ltoken in dictionary.token_pos_set:
                feature_list.append(dictname)

        # Get basic reg expression features
        # Check if the token is all caps and no symbols
        if len(token) > 1 and re.match('^[A-Z]*$', token):
            feature_list.append('ALL_CAPS')

        # Check if the token is capitalized  
        if re.match('[A-Z]', token[0]):
            feature_list.append('IS_CAPITALIZED')

        # Check if the token contains a number 
        if re.match('.*[0-9].*', token):
            feature_list.append('IS_NUM')

        # New ortho features
        if re.match(r'[0-9]', token):
            feature_list.append('SINGLEDIGIT')
        if re.match(r'[0-9][0-9]', token):
            feature_list.append('DOUBLEDIGIT')
        if re.match(r'.*-.*', token):
            feature_list.append('HASDASH')
        if re.match(r'[.,;:?!-+\'"]', token):
            feature_list.append('PUNCTUATION')

        # Only for words with 4 or longer chars
        if len(ltoken) >= 4:
            # Get prefixes
            for i in range(1, 5):
                if i <= len(ltoken):
                    feature_list.append('PREFIX=' + ltoken[:i])
            # Get suffixes                            
            for i in range(1, 5):
                if i <= len(ltoken):
                    feature_list.append('SUFFIX=' + ltoken[-1*i:])

        # Add cluster features (RAW)
        if self.cluster_dictionary:
            feature_list.extend(self.cluster_dictionary.get_clusters(token))

        # Add cluster similarity features
        if not in_pos_dict and token != '&lt;':
            m, s = cluster_sim.get_best_match(token.lower())
            if m: feature_list.append('CLUST_' + m)

        return feature_list

    def add_bigram_features(self, current_feature_list):
        new_current_feature_list = []
        for i in range(len(current_feature_list)):
            feature_list = current_feature_list[i]
            current_word = feature_list[0]
            if i > 0:
                before_word = current_feature_list[i - 1][0]
                feature_list.extend(self._check_bigrams(before_word,
                                                        current_word,
                                                        False))
            if i < len(current_feature_list) - 1:
                after_word = current_feature_list[i + 1][0]
                             
                feature_list.extend(self._check_bigrams(current_word,
                                                        after_word,
                                                        True))
            new_current_feature_list.append(feature_list)
        return new_current_feature_list

    def _check_bigrams(self, word1, word2, use_first):
        bigram = word1 + '_' + word2
        new_features = []
        for dict_name, d in self.bigram_dictionaries.iteritems():
            if bigram != ":_(" and bigram in d.token_pos_set:
                print bigram
                tag1, tag2 = d.token_pos_set[bigram].items()[0][0].split('_')
                tag = (use_first and tag1) or tag2
                ttype = (use_first and 'AFTER') or 'BEFORE'
                new_features.append(dict_name + '_BIGRAM_' + ttype + '_' + tag)
        return new_features


_WINDOW = 3

def add_context_features(current_feature_list):
    new_current_feature_list = []
    for i in range(len(current_feature_list)):
        feature_list = current_feature_list[i]
        check_context(current_feature_list, i - 1, 'PREV_TWIT',
                      feature_list)
        check_context(current_feature_list, i + 1, 'NEXT_TWIT',
                      feature_list)
        # Won't find windows for special characters
        if _WINDOW > 0 and feature_list[0].lstrip('SYMBOL_REGX=') not in \
                ['url', 'usr', 'ht', 'rt']:
            window_context(current_feature_list, max(i - _WINDOW, 0), i, 'PWIN',
                           feature_list)
            window_context(current_feature_list, i + 1, i + _WINDOW + 1, 'NWIN',
                           feature_list)

        new_current_feature_list.append(feature_list)
    return new_current_feature_list

def check_context(current_feature_list, index, ctype, feature_list):
    if index < 0 or index >= len(current_feature_list):
        return
    cont_feature_list = current_feature_list[index]
    if 'SYMBOL_REGX=usr' in cont_feature_list:
        feature_list.insert(-1, ctype + '=USR')
    if 'SYMBOL_REGX=url' in cont_feature_list:
        feature_list.insert(-1, ctype + '=URL')
    if 'SYMBOL_REGX=rt' in cont_feature_list:
        feature_list.insert(-1, ctype + '=RT')

def window_context(current_feature_list, si, ei, ctype, feature_list):
    for cont_feature_list in current_feature_list[si:ei]:
        feature_list.insert(-1, ctype + '=' + cont_feature_list[0])

class Dictionary:
    def __init__(self, dictionary_file, has_tags):
        self.token_pos_set = {}
        self.token_pos_majority = {}
        for line in open(dictionary_file):
            if has_tags:
                tp_list = line.strip().split('\t')
                pos_counts = {}
                max_count = None
                max_pos = None
                for tp in tp_list[1:]:
                    pos, count = tp.split(';;')
                    count = int(count)
                    pos_counts[pos] = count
                    if not max_count or max_count < count:
                        max_count = count
                        max_pos = pos
                self.token_pos_set[tp_list[0]] = pos_counts
                self.token_pos_majority[tp_list[0]] = max_pos
            else:
                self.token_pos_set[line.strip()] = 1

def create_dt_features(feature_list, data_src):
    new_feature_list = []
    new_feature_list.extend(['DEFAULT=' + ft for ft in feature_list[:-1]])
    new_feature_list.extend([data_src + '=' + ft for ft in feature_list[:-1]])
    new_feature_list.append(feature_list[-1])
    return new_feature_list

class ClusterDictionary:
    def __init__(self, cluster_fp, cluster_list=[4,8,12]):
        self.word_cid = {}
        for line in open(cluster_fp):
            word, cid = line.strip().split(' ')
            self.word_cid[word] = int(cid)
        self.cluster_list = []
        for cid in cluster_list:
            self.cluster_list.append((1<<cid) - 1)

    def get_clusters(self, word):
        if word.lower() not in self.word_cid:
            return []
        else:
            cid = self.word_cid[word.lower()]
            clusters = []
            for cs in self.cluster_list:
                clusters.append('CS' + str(cs) + '_' + str(cid & cs))
            return clusters

# Sample usage
_REPO_DIR = '/home/ssclark/Desktop/release_pos_chunk/'
_TEMP_DIR = '/tmp/'

# DON'T NEED TO SET                                     
_token2pos = os.path.join(_REPO_DIR, 'data/pos_dictionaries/token2pos')
_token = os.path.join(_REPO_DIR, 'data/pos_dictionaries/token')
_bigram = os.path.join(_REPO_DIR, 'data/pos_dictionaries/bigram')
_clusters = os.path.join(_REPO_DIR, 'data/brown_clusters/60K_clusters.txt')

_oov = True

#_clusters = None
#_oov = False

if __name__ == '__main__':
    mfe = POSFeatureExtractor(_token2pos, _token, _bigram, _clusters, _oov)

    cur_tok_features = []
    cur_tags = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            if not cur_tok_features:
                continue
            else:
                # Features that need the entire tweet
                cur_tok_features = add_context_features(cur_tok_features)
                mfe.add_bigram_features(cur_tok_features)

                for i, features in enumerate(cur_tok_features):
                    if cur_tags:
                        features.append(cur_tags[i])
                    print ' '.join(features)
                print ''
                cur_tok_features = []
                cur_tags = []
        else:
            tp = line.split(' ')
            word = tp[0]
            cur_tok_features.append(mfe.get_features(word))
            if len(tp) == 2:
                cur_tags.append(tp[1])
