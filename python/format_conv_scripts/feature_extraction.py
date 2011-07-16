#!/homes/gws/aritter/local/bin/python

###############################################################################
# Library for extracting various types of features
###############################################################################

import re

def token_features(token):
    """Extracts features from a token and puts them in a list.

    These features include whether the token is capitalized, whether the token
    contains a number, the first four prefixes, and the first four suffixes.
    """
    features_list = []
    # Check if the token is capitalized  
    if re.match('[A-Z]', token[0]):
        features_list.append('Y')
    else:
        features_list.append('N')

    # Check if the token contains a number  
    if re.match('.*[0-9].*', token):
        features_list.append('Y')
    else:
        features_list.append('N')

    # Get prefixes
    for i in range(1, 5):
        if i <= len(token):
            features_list.append(token[:i])
        else:
            features_list.append('__nil__')

    # Get suffixes
    for i in range(1, 5):
        if i <= len(token):
            features_list.append(token[-1*i:])
        else:
            features_list.append('__nil__')
    return features_list
