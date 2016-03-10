OSU Twitter NLP Tools
====================
contact: ritter.1492@osu.edu

Example Usage:
--------------
**UPDATED:** : Added support for reading from file and writing to a tab seperated file which can have text in any column.

```
export TWITTER_NLP=./
python python/ner/extractEntities.py test.1k.txt -o output.txt
```

If the file is a tab separated file. Use the i-th (starting from 0) column as a text column to read from. 
Output file will have that column data replaced with the annotated text.

**CAUTION**: Make sure there are no newline characters in the text column. This will break the format.


Shortened options for other features:
```
$ python/ner/extractEntities.py -h
usage: extractEntities.py [-h] [--text-pos TEXT_POS]
                          [--output-file OUTPUT_FILE] [--chunk] [--pos]
                          [--event] [--classify]
                          input_file

positional arguments:
  input_file            Path to the input file. Each line should have the
                        text.Optionally it can be a tab delimited file.

optional arguments:
  -h, --help            show this help message and exit
  --text-pos TEXT_POS, -t TEXT_POS
                        Column number (starting from 0) of the column
                        containing text
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Path to the output file
  --chunk, -k
  --pos, -p
  --event, -e
  --classify, -c
```


### OLD USAGE (Reading from stdin):

	export TWITTER_NLP=./
	cat test.1k.txt | python python/ner/extractEntities2.py

note: this takes a minute or so to read in models from files


To include classification, simply add the --classify switch:

	cat test.1k.txt | python python/ner/extractEntities2.py --classify


For higher quality, but slower results, optionally include features based on POS and chunk tags
(chunk tags require POS)

	cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos
	cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos --chunk

Also has the ability to include event tags (requires POS):

	cat test.1k.txt | python python/ner/extractEntities2.py --classify --pos --event

Output:
-------------
The output contains the tokenized and tagged words separated by spaces with tags separated
by forward slash '/'
Example output:

	The/B-movie/DT/B-NP/O Town/I-movie/NNP/I-NP/O might/O/MD/B-VP/O be/O/VB/I-VP/O one/O/CD/B-NP/O of/O/IN/B-PP/O the/O/DT/B-NP/O best/O/JJS/I-NP/O movies/O/NNS/I-NP/O I/O/PRP/B-NP/O have/O/VBP/B-VP/O seen/O/VBN/I-VP/O all/O/DT/B-NP/O year/O/NN/I-NP/O ./O/./O/O So/O/RB/O/O ,/O/,/O/O so/O/RB/B-ADJP/O good/O/JJ/I-ADJP/O ./O/./O/O And/O/CC/O/O don't/O/NN/B-NP/O worry/O/NN/I-NP/O Ben/B-person/NNP/I-NP/O ,/O/,/O/O we/O/PRP/B-NP/O already/O/RB/B-ADVP/O forgave/O/VBP/B-VP/B-EVENT you/O/PRP/B-NP/O for/O/IN/B-PP/O Gigli/B-movie/NNP/B-NP/O ./O/./O/O Really/O/RB/B-INTJ/O ./O/./I-INTJ/O

Looking at just one word:

	The/B-movie/DT/B-NP/O

The fields are as follows:

<table>
<tr>
  <td>Word:</td>
  <td>The</td>
  <td></td>
</tr>
<tr>
  <td>Entity:</td>
  <td>B-movie</td>
  <td>Begins a named entity of type "movie"</td>
</tr>
<tr>
  <td>Chunk:</td>
  <td>B-NP</td>
  <td>Begins a noun phrase</td>
</tr>
<tr>
  <td>Event:</td>
  <td>O</td>
  <td>Not part of an event phrase</td>
</tr>
</table>

The BIO encoding is used for encoding phrases (Named Entities, event phrases, and chunks), for example:

    The/B-movie Town/I-movie might/O ...

Indicates that the word "The" begins a named entity of type movie, "Town" continues that entity, and "might" is outside of an entity mention.  For more details see: http://nltk.org/book/ch07.html

Requirements:
-------------
1. Linux
2. Libraries and executables can be compiled with build.sh

Relevant papers:
--------------

	@inproceedings{Ritter11,
	  author = {Ritter, Alan and Clark, Sam and Mausam and Etzioni, Oren},
	  title = {Named Entity Recognition in Tweets: An Experimental Study},
	  booktitle = {EMNLP},
	  year = {2011}
	}

	@inproceedings{Ritter12,
	  author = {Ritter, Alan and Mausam and Etzioni, Oren and Clark, Sam},
	  title = {Open Domain Event Extraction from Twitter},
	  booktitle = {KDD},
	  year = {2012}
	}

Demo:
-----
[statuscalendar.com](http://statuscalendar.com)

Acknowledgments (bug fixes, etc...):
------------------------------------
Junming Sui

Ming-Wei Chang

Tuan Anh Hoang Vu

sumant81

Yiye Ruan

Lu Wang

napsternxg
