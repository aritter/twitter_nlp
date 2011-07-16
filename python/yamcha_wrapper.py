#!/homes/gws/aritter/local/bin/python

############################################################################## 
# Wrapper around Yamcha.  Used to create/load a model and that can be used to
# tag sentences.
#
############################################################################## 

import os
import shutil
import subprocess

MAKEFILE_PATH = '/homes/gws/aritter/local/libexec/yamcha/Makefile'
YAMCHA_PATH = '/homes/gws/aritter/local/bin/yamcha'

class YamchaWrapper:

    def __init__(self, train_model, train_file, model_dir):
        # NOTE: If train_model is not None than it is assumed that it is a
        # trained model.  Otherwise, train_file is used to create a trained
        # model
        if train_model:
            self.model_path = train_model
        else:
            # Create model
            shutil.copyfile(MAKEFILE_PATH, os.path.join(model_dir, 'Makefile'))
            os.chdir(model_dir)
            os.system('make CORPUS=' + train_file + ' MODEL=model_name train')
            self.model_path = 'model_name.model'

        # Start subprocess that runs yamcha using the model
        self.proc = subprocess.Popen(YAMCHA_PATH + ' -m ' + self.model_path,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

    def get_POS_tags(self, sentence):
        # Format input string for the yamcha model and
        # send the input string to the yamcha subprocess
        for token_features in sentence:
            self.proc.stdin.write(' '.join(token_features) + '\n')
        self.proc.stdin.write('\n')

        # Read all of the output from the subprocess
        std_out = ''
        for i in range(len(sentence) + 1):
            std_out += self.proc.stdout.readline()

        # Parse the string
        std_out = std_out.strip()
        sent_tags = []
        for token_features in std_out.split('\n'):
            feature_list = token_features.strip().split('\t')
            sent_tags.append(tuple(feature_list))
        return sent_tags

if __name__ == '__main__':
    # Example usage
    """
    yw = YamchaWrapper(
        '/home/ssclark/YamchaModels/'
        'ExtraFeaturesMediumSize/model_name.model',
        None,
        None)
    """
    yw = YamchaWrapper(
        None,
        '/home/ssclark/YamchaModels/NpsChat/nps_train.txt',
        '/home/ssclark/YamchaModels/NpsChat')

    # Get tags for a sentence
    sentence = [
        ('I', 'Y', 'N', 'I', '__nil__', '__nil__', '__nil__', 'I',
         '__nil__', '__nil__', '__nil__'),
        ("'ve", 'N', 'N', "'", "'v", "'ve", '__nil__', 'e', 've', "'ve",
         '__nil__'),
        ('learned', 'N', 'N', 'l', 'le', 'lea', 'lear', 'd', 'ed', 'ned',
         'rned'),
        ('the', 'N', 'N', 't', 'th', 'the', '__nil__', 'e', 'he', 'the',
         '__nil__'),
        ('hard', 'N', 'N', 'h', 'ha', 'har', 'hard', 'd', 'rd', 'ard', 'hard'),
        ('way', 'N', 'N', 'w', 'wa', 'way', '__nil__', 'y', 'ay', 'way',
         '__nil__'),
        ('that', 'N', 'N', 't', 'th', 'tha', 'that', 't', 'at', 'hat', 'that'),
        ('too', 'N', 'N', 't', 'to', 'too', '__nil__', 'o', 'oo', 'too',
         '__nil__'),
        ('much', 'N', 'N', 'm', 'mu', 'muc', 'much', 'h', 'ch', 'uch', 'much'),
        ('booze', 'N', 'N', 'b', 'bo', 'boo', 'booz', 'e', 'ze', 'oze', 'ooze')
        ]
    tag_sent = yw.get_POS_tags(sentence)
    # Print tag results
    for tp in tag_sent:
        print tp[0], tp[-1]
