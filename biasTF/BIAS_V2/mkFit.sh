#!/bin/sh

basepath="."

defaultopts="$basepath/../../common/vbfHbb_defaultOpts_2013.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013/"
	globalpathtrigger="/data/UAdata/autumn2013/"
fi
variablesslim="$basepath/../../common/vbfHbb_variables_2013_bareslim.json"
globalpathskimslim="$basepath/flat"
samples="VBF,GluGlu,Data,T,WJets,ZJets,QCD"
samples_SoB_NOM="VBF125,GluGlu-Powheg125,DataA,DataB,DataC,DataD,T,WJets,ZJets"
samples_SoB_VBF="VBF125,GluGlu-Powheg125,DataV,T,WJets,ZJets"

usebool="--usebool" 

preselNOM="sNOM;nLeptons"
preselVBF="sVBF;nLeptons;sNOMveto"

NOweight="1."
weightNOM="19784.,LUMI;XSEC;PU#0;TNOM;KF"
weightVBF="18281.,LUMI;XSEC;PU#0;TVBF;KF"
#19784,18281

###   OPTIONS
###   
###   1    1		FitFlatTrees				NOM 
###   1    2										VBF
###
###

notext=""
## turning on/off legends
#if [ "$3" == "0" ]; then 
#	notext="--notext"
#else
#	notext=""
#fi

##################################################
#for i in `seq 0 1`; do
#	if [ "$notext" == "" ] && [ "$i" == "0" ]; then continue; fi
##################################################
if [ "$1" == "" ] || [ "$1" == "1" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "./flat/" -t "NOM" --datatrigger "NOM" -p "$preselNOM" -s "$samples" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "./flat/" -t "VBF" --datatrigger "VBF" -p "$preselVBF" -s "$samples" -w "$NOweight" $usebool $notext
	fi
fi

if ([ "$1" == "" ] || [ "$1" == "1" ]) && ([ "$2" == "3" ] || [ "2" == "" ]); then
	if [ ! -d ./flat/dataSeparate ]; then mkdir ./flat/dataSeparate; fi
	if [ ! -f ./flat/Fit_MultiJetA_selNOM.root ]; then mv ./flat/dataSeparate/Fit_{MultiJet,BJetPlusX,VBF1Parked}*.root ./flat/; fi

	if [ -f "./flat/Fit_data_selNOM.root" ]; then mv ./flat/Fit_data_selNOM.root ./flat/dataSeparate/Fit_data_selNOM.root.backup; fi
	hadd ./flat/Fit_data_selNOM.root ./flat/Fit_{MultiJet,BJetPlusX}*_selNOM.root
	mv ./flat/Fit_{MultiJet,BJetPlusX}*_selNOM.root ./flat/dataSeparate/

	if [ -f "./flat/Fit_data_selVBF.root" ]; then mv ./flat/Fit_data_selVBF.root ./flat/dataSeparate/Fit_data_selVBF.root.backup; fi
	hadd ./flat/Fit_data_selVBF.root ./flat/Fit_VBF1Parked*_selVBF.root
	mv ./flat/Fit_VBF1Parked*_selVBF.root ./flat/dataSeparate/
fi

