---------------------------------------------------------------------
- WNUT Named Entity Recognition in Twitter Shared task
---------------------------------------------------------------------
- Organizers: Benjamin Strauss, Marie-Catherine de Marneffe, Alan Ritter
---------------------------------------------------------------------

1) Data
- Training and development data is in the "data" directory.  This is represented using the ConLL data format (http://www.cnts.ua.ac.be/conll2002/ner/).
- There are 2 datasets corresponding to 2 seperate evaluations: one where the task is to predict fine-grained types and the other in which no type information is to be predicted.
- The "train" data is the "2015 train" + "2015 dev" data
- The "dev" data is the "2015 test" data
  a) "train" and "dev" are annotated with 10 fine-grained NER categories: person, geo-location, company, facility, product,music artist, movie, sports team, tv show and other.  
  b) "train_notype" and "dev_notype" entities are annotated without any type information.

2) Baseline System
- For convenience we have provided a baseline script based on crfsuite (http://www.chokkan.org/software/crfsuite/).  
  The baseline includes gazateer features generated from the files in the "lexicon" directory.  To run the baseline system, simply install
  crfsuite on your local machine and run the script "./baseline.sh".
  To install crfsuite on OSX using homebrew ( http://brew.sh/ ) you can do:
  > brew tap homebrew/science
  > brew install crfsuite
  > ./baseline.sh

- You can change between the 10 types and no types data by adjusting the "TRAIN_DATA" and "TEST_DATA" variables in "baseline.sh".

Here are the results:

10 Entity Types:
accuracy:  93.68%; precision:  40.34%; recall:  32.22%; FB1:  35.83
          company: precision:  43.48%; recall:  25.64%; FB1:  32.26  23
         facility: precision:  19.44%; recall:  18.42%; FB1:  18.92  36
          geo-loc: precision:  49.18%; recall:  51.72%; FB1:  50.42  122
            movie: precision:  16.67%; recall:   6.67%; FB1:   9.52  6
      musicartist: precision:   0.00%; recall:   0.00%; FB1:   0.00  10
            other: precision:  28.57%; recall:  18.18%; FB1:  22.22  84
           person: precision:  52.04%; recall:  59.65%; FB1:  55.59  196
          product: precision:  12.00%; recall:   8.11%; FB1:   9.68  25
       sportsteam: precision:  33.33%; recall:   8.57%; FB1:  13.64  18
           tvshow: precision:   0.00%; recall:   0.00%; FB1:   0.00  8

No Types:
accuracy:  95.01%; precision:  54.21%; recall:  49.62%; FB1:  51.82
                 : precision:  54.21%; recall:  49.62%; FB1:  51.82  605
                 : precision:  54.21%; recall:  49.62%; FB1:  51.82  605

3) Evaluation
- Evaluation is performed using the ConLL evaluation script (http://www.cnts.ua.ac.be/conll2002/ner/bin/conlleval.txt)
- The baseline script prints out results using the ConLL evaluation script.
- At the beginning of the evaluation period we will release test data without annotations, participating teams will submit their predictions in ConLL format, 
  we will score the resutls against gold annotations using the ConLL evaluation script and release the predictions, precision, recall and F1 and rankings (by F1 score) for all participating teams.  
  We will release the gold test annotations after the evaluation period.
