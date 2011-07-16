#!/usr/bin/bash

cat $1 | perl -0 -ne 's/printf\("\\n"\);/printf("\\n"); fflush(stdout);/g; print;' > $1-tmp
mv $1-tmp $1
