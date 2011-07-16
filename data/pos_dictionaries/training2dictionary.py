#!/homes/gws/aritter/local/bin/python

###############################################################################
# Program to convert a training file into a dictionary of pos tags for each
# token.
###############################################################################

import sys

def get_dictionary(training_file):
    token_pos_lists = {}
    for line in open(training_file):
        line = line.strip()
        if not line:
            continue
        tp = line.split(' ')
        token = tp[0].lower()
        pos = tp[-1]

        token_pos_lists.setdefault(token, {})
        token_pos_lists[token].setdefault(pos, 0)
        token_pos_lists[token][pos] += 1
    return token_pos_lists

if __name__ == '__main__':
    token_pos_lists = get_dictionary(sys.argv[1])

    fout = open(sys.argv[2], 'w')
    for token, pos_hash in token_pos_lists.iteritems():
        pos_list = [pos + ';;' + str(count) for pos, count in pos_hash.items()]
        fout.write(token + '\t' + '\t'.join(pos_list) + '\n')
