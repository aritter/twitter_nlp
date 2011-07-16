#!/usr/bin/perl -w

use strict;

my $tp;
my $tn;
my $fp;
my $fn;

while(<STDIN>) {
    chomp;
    if(/^-?1/) {
        my ($gold, $pred) = split / /;
        if($pred > $ARGV[0]) {
            if($gold == 1) {
                $tp++;
            } else {
                $fp++;
            }
        } else {
            if($gold == 1) {
                $fn++;
            } else {
                $tn++;
            }
        }
    }
}

print "tp=$tp\tfp=$fp\tfn=$fn\ttn=$tn\n";
my $p = $tp / ($tp + $fp);
my $r = $tp / ($tp + $fn);
my $f = 2.0 * $p * $r / ($p + $r);

print "p=$p\nr=$r\nf=$f\n";
