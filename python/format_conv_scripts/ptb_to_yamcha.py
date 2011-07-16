#!/homes/gws/aritter/local/bin/python

###############################################################################
# Program to convert Penn Treebank text to the format accepted by Yamcha
#
# Usage: ./ptb_to_yamcha <wsj dir> <output train file>
# <output test file>
###############################################################################

import os
import re
import sys

import feature_extraction

SUFFIX = 'pos'
SPLIT_RATIO = 4
USE_ALL_FEATURES = True

def convert_all_wsj_files(wsj_dir):
    train_tags = []
    test_tags = []
    for elem_id, element_name in enumerate(os.listdir(wsj_dir)):
        epath =os.path.join(wsj_dir, element_name)
        if not os.path.isdir(epath):
            continue
        # Get tags for all sentences in all files in the dir
        all_tags = convert_all_files(epath)
        
        # Split between the test and training sets
        if elem_id % SPLIT_RATIO == 0:
            test_tags.extend(all_tags)
        else:
            train_tags.extend(all_tags)
    return train_tags, test_tags


def convert_all_files(dirname):
    tag_list = []
    for fn in os.listdir(dirname):
        if re.match('.*\.' + SUFFIX + '$', fn):
            file_tags = convert_file(os.path.join(dirname, fn))
            tag_list.extend(file_tags)
    return tag_list


def convert_file(filename):
    tag_list = []
    sent_tags = []
    for line in open(filename):
        line = line.strip()
        if not line:
            continue
        elif line == '======================================':
            # Check if there are any tags to record
            if sent_tags:
                tag_list.append(sent_tags)
                sent_tags = []
        else:
            # Check if the chunk is a NP
            np_match = re.match(r'^\[(.*)\]$', line)
            if np_match:
                tag_string = np_match.group(1).strip()
            else:
                tag_string = line

            for token_id, token_tag in enumerate(tag_string.split(' ')):
                # Watch out for cases where there are two+ spaces...
                if not token_tag:
                    continue

                # According the documentation NP Chunking isn't reliable
                """
                # Get target val
                target_val = 'O'
                if np_match and token_id == 0:
                    target_val = 'B'
                elif np_match:
                    target_val = 'I'
                """

                # Record features, watch out for escaped / and |
                token_tag = token_tag.replace('\/', ';;;')
                token_tag = token_tag.replace('\|', ':::')
                tp = token_tag.split('/')
                if len(tp) != 2:  # Handles unfiltered brackets
                    continue
                token, tag = tp
                token = token.replace(';;;', '\/')
                token = token.replace(':::', '\|')
                tag = tag.replace(';;;', '\/')
                tag = tag.replace(':::', '\|')

                # If multiple tags are given than take the first
                tag = tag.split('|')[0]

                # Check whether to include extra features
                features_list = [token]
                if USE_ALL_FEATURES:
                    features_list.extend(
                        feature_extraction.token_features(token))
                
                # Add tag and append tuple
                features_list.append(tag)
                sent_tags.append(tuple(features_list))

    return tag_list


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print ('USAGE: ./ptb_to_yamcha <wsj directory> <output train file>'
               ' <output test file>')
    else:
        dirname = sys.argv[1]
        train_filename = sys.argv[2]
        test_filename = sys.argv[3]

        # Split wsj articles into test and training, than get tags
        train_tags, test_tags = convert_all_wsj_files(dirname)

        # Write tags out to files
        for filename, all_tags in [(train_filename, train_tags),
                               (test_filename, test_tags)]:
            fw = open(filename, 'w')
            for sent_tags in all_tags:
                for tp in sent_tags:
                    fw.write(' '.join(tp) + '\n')
                fw.write('\n')
            fw.close()
