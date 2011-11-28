export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`/../../lib
c++ -I. -static -L../../lib cap_classify.cpp -o cap_classify -ltinysvm
