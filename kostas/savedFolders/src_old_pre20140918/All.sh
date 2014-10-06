#!/bin/sh

mkdir -p plots
mkdir -p plots/fitbkg
mkdir -p plots/fitsig
mkdir -p plots/fitdat
mkdir -p plots/transfer
mkdir -p plots/properties

if [ "$1" == "" ] || [ "$1" == "1" ] || [ $1 -eq 0 -a $2 -lt 1 -a $3 -gt -1 ]; then 
	root -b PrepareSamples.C -q; 
	hadd flat/Fit_data_selNOM.root flat/Fit_*{BJet,Multi}*_selNOM.root;
	rm flat/Fit_*{BJet,Multi}_selNOM.root;
	hadd flat/Fit_data_selVBF.root flat/Fit_*VBF1*_selVBF.root;
	rm flat/Fit_VBF1_selVBF.root;
fi
if [ "$1" == "" ] || [ "$1" == "2" ] || [ $1 -eq 0 -a $2 -lt 2 -a $3 -gt 0 ]; then root -b src/TransferFunctions.C'(80,200)' -q; fi
if [ "$1" == "" ] || [ "$1" == "3" ] || [ $1 -eq 0 -a $2 -lt 3 -a $3 -gt 1 ]; then root -b src/CreateBkgTemplates.C'()' -q; fi
if [ "$1" == "" ] || [ "$1" == "4" ] || [ $1 -eq 0 -a $2 -lt 4 -a $3 -gt 2 ]; then root -b src/CreateSigTemplates.C'(2.0)' -q; fi
if [ "$1" == "" ] || [ "$1" == "5" ] || [ $1 -eq 0 -a $2 -lt 5 -a $3 -gt 3 ]; then root -b src/CreateDataTemplates.C'(2.0,5,5)' -q; fi
if [ "$1" == "" ] || [ "$1" == "6" ] || [ $1 -eq 0 -a $2 -lt 6 -a $3 -gt 4 ]; then root -b src/DrawSignalProperties.C'("0.00_0.70_0.84")' -q; fi
if [ "$1" == "" ] || [ "$1" == "7" ] || [ $1 -eq 0 -a $2 -lt 7 -a $3 -gt 5 ]; then root -b src/CreateDatacards.C'(0.0,0.7,0.84,0,6,6)' -q; fi
