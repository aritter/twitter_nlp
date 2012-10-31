UW Twitter NLP Tools
====================
Authors: Alan Ritter, Sam Clark

contact: aritter@cs.washington.edu

Example Usage:
--------------

	export TWITTER_NLP=./
	cat test.1k.txt | python python/ner/extractEntities2.py

note: this takes a minute or so to read in models from files


To include classification, simply add the --classify switch:

	cat test.1k.txt | python python/ner/extractEntities2.py --classify


For higher quality, but slower results, optionally include features based on POS and chunk tags
(chunk tags require POS)

	cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos
	cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos --chunk

Requirements:
-------------
1. Linux
2. Libraries and executables can be compiled with build.sh

Relevant paper:
--------------

	@inproceedings{Ritter11,
	  author = {Ritter, Alan and Clark, Sam and Mausam and Etzioni, Oren},
	  title = {Named Entity Recognition in Tweets: An Experimental Study},
	  booktitle = {EMNLP},
	  year = {2011}
	}

Demo:
-----
[statuscalendar.cs.washington.edu](http://statuscalendar.cs.washington.edu)

Acknowlegements (bug fixes, etc...):
------------------------------------
Junming Sui

Ming-Wei Chang

Tuan Anh Hoang Vu
