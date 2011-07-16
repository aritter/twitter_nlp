#!/homes/gws/aritter/local/bin/python 

###############################################################################
# Function for doing best guesses at symbol tagging.
#
###############################################################################

_sym_tags = {
    '?':'.',
    '"':'\'\'',
    '\'':'\'\'',
    '(':'(',
    ')':')',
    '...':':',
    '&':'CC',
    '&lt':'CC',
    '&lt;':'CC',
    '&amp;':'CC',
    '+':'SYM',
    '|':':',
    '=':'SYM'
    }

def tag_token(token):
    pos = None
    if token in _sym_tags:
        pos = _sym_tags[token]
    elif token[0] == '@' and len(token) > 1:
        pos = 'usr'
    elif token.lower() == 'rt':
        pos = 'rt'
    elif token[0] == '#':
        pos = 'ht'
    elif token[0:7] == 'http://':
        pos = 'url'
    return pos

if __name__ == '__main__':
    tag_token('@usr')
    tag_token('http://website.com')    
