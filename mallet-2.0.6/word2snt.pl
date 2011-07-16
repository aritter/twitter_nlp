#!/usr/bin/perl -w

#Converts features in word-per line format to sentence-per line format (tab seperated)

use strict;

my @sentence;
while(<STDIN>) {
    chomp;
    if($_ eq "") {
        print join("\t", @sentence) . "\n";
        @sentence = ();
    } else {
        push @sentence, $_;
    }
}
