UW Twitter NLP Tools
====================
Authors: Sam Clark, Alan Ritter
-------------------------------
contact: aritter@cs.washington.edu

Example Usage:

<code>
export TWITTER_NLP=./
cat test.1k.txt | python python/ner/extractEntities2.py
note: this takes a minute or so to read in models from files
</code>


To include classification, simply add the --classify switch:
<code>
cat test.1k.txt | python python/ner/extractEntities2.py --classify
</code>

For higher quality, but slower results, optionally include features based on POS and chunk tags
(chunk tags require POS)
<code>
cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos
cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos --chunk
</code>

Requirements:
-------------
1. Linux
2. Libraries and executables can be compiled with build.sh

Relevant paper:
--------------
<code>
@inproceedings{Ritter11,
  author = {Ritter, Alan and Clark, Sam and Mausam and Etzioni, Oren},
  title = {Named Entity Recognition in Tweets: An Experimental Study},
  booktitle = {EMNLP},
  year = {2011}
}
</code>

Acknowlegements (bug fixes, etc...):
------------------------------------
Junming Sui
Ming-Wei Chang
