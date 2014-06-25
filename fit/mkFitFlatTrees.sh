#!/bin/sh

if [ "$(basename `pwd`)" == "fit" ]; then 
	basepath="."
else 
	basepath="fit"
fi

defaultopts="$basepath/../common/vbfHbb_defaultOpts_2013.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013"
	globalpathtrigger="/data/UAdata/autumn2013"
fi
samples="VBF125,GluGlu-Powheg125,Data,T,WJets,ZJets,QCD"
usebool="--usebool" 

preselNOM="sNOM;nLeptons"
preselVBF="sVBF;nLeptons;sNOMveto"

weightNOM="1."
weightVBF="1."

###   OPTIONS
###   
###   1    1		FitFlatTrees				NOM 
###   1    2										VBF
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
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "./" -t "NOM" --datatrigger "NOM" -p "$preselNOM" -s "$samples" -w "$weightNOM" $usebool $notext
	rm -f $basepath/fitFlatTree_data_NOM.root
	hadd $basepath/fitFlatTree_data_NOM.root $basepath/fitFlatTree_*{BJet,Multi}*_NOM.root
	rm $basepath/fitFlatTree_*{BJet,Multi}*_NOM.root
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "./" -t "VBF" --datatrigger "VBF" -p "$preselVBF" -s "$samples" -w "$weightVBF" $usebool $notext
	rm -f $basepath/fitFlatTree_data_VBF.root
	hadd $basepath/fitFlatTree_data_VBF.root $basepath/fitFlatTree_*Parked*_VBF.root
	rm $basepath/fitFlatTree_*Parked*_VBF.root
	fi
fi

##################################################
#notext=""
#done
