#!/homes/gws/aritter/local/bin/python

###############################################################################
# Program to convert a training file into a dictionary of pos tags for each
# token.
###############################################################################

import sys

def get_dictionary(training_file):
    token_pos_lists = {}
    last_token = None
    last_pos = None
    current_token = None
    current_pos = None
    for line in open(training_file):
        line = line.strip()
        if not line:
            last_token = None
            last_pos = None
            current_token = None
            current_pos = None
            continue
        tp = line.split(' ')
        current_token = tp[0].lower()
        current_pos = tp[-1]

        if last_token:
            bigram = last_token + '_' + current_token
            pos_tags = last_pos + '_' + current_pos
            token_pos_lists.setdefault(bigram, {})
            token_pos_lists[bigram].setdefault(pos_tags, 0)
            token_pos_lists[bigram][pos_tags] += 1

        last_token = current_token
        last_pos = current_pos

    return token_pos_lists

if __name__ == '__main__':
    token_pos_lists = get_dictionary(sys.argv[1])

    fout = open(sys.argv[2], 'w')
    for token, pos_hash in token_pos_lists.iteritems():
        if len(pos_hash) == 1:
            pos, count = pos_hash.items()[0]
            if count > 1:
                fout.write(token + '\t' + pos + ';;' + str(count) + '\n')
