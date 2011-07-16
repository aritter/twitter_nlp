#!/usr/bin/python

import sys
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
from xml.sax.saxutils import quoteattr

for line in sys.stdin:
    line = line.rstrip('\n')
    print quoteattr(unescape(line)).strip('"')
