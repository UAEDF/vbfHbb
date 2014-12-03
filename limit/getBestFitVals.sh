#!/bin/sh

if [ $1 == "-h" ] || [ $1 == "--help" ]; then
	echo "1) Limit file (4)"
	echo "2) MLFit file (2)"
	echo "3) Significance file (3)"
	exit
fi

cat $1 | egrep "Observed|Expected 50.0|combine.*m" | sed "s#-n _vbfhbb_BRN5p4_B80-200_CAT0-CAT6_Fit.*POL1-POL2_\(Combine.*\)_1...log#\1#g" | sed "s#\t##g"

echo
cat $2 | awk '/-- MaxLikelihoodFit/ {for(i=0; i<=4; i++) { print; getline;} print "\n";}'

echo
cat $3 | awk '/-- Profile Likelihood/ {for(i=0; i<=4; i++) { print; getline;} print "\n";}'
