#!/homes/gws/aritter/local/bin/python

###############################################################################
# Tokinizes strings using the 'twokenize' module, but also splits up
# contractions, which 'twokenize' fails to do.
#
###############################################################################
import sys
import twokenize

def tokenize(tweet):
    tokens = twokenize.tokenize(tweet)
    return split_contractions(tokens)

def split_contractions(tokens):

    # Fix "n't", "I'm", "'re", "'s", "'ve", "'ll"  cases
    new_token_list = []
    for token in tokens:
        new_tk = None
        if token[-3:] == 'n\'t':
            new_tk = token[:-3]
            new_token_list.append('n\'t')
        elif token == 'I\'m' or token == 'i\'m':
            new_token_list.append('I')
            new_token_list.append('\'m')
        elif token[-3:] == '\'re':
            new_tk = token[:-3]
            new_token_list.append('\'re')
        elif token[-2:] == '\'s':
            new_tk = token[:-2]
            new_token_list.append('\'s')
        elif token[-3:] == '\'ve':
            new_tk = token[:-3]
            new_token_list.append('\'ve')
        elif token[-3:] == '\'ll':
            new_tok = token[:-3]
            new_token_list.append('\'ll')
        else:
            new_token_list.append(token)
        # Add new token if one exists  
        if new_tk:
            #sys.stderr.write('Split following contraction: %s\n' % token)
            new_token_list.insert(-1, new_tk)
    return new_token_list


if __name__=='__main__':
  for line in sys.stdin:
    print u" ".join(tokenize(line[:-1])).encode('utf-8')
