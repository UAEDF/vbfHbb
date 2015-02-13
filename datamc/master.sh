#!/bin/sh

basepath=.

defaultopts="../common/vbfHbb_defaultOpts_2015.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013/"
	globalpathtrigger="/data/UAdata/autumn2013/"
elif [[ "`uname -a`" == *heisenberg* ]]; then
	globalpath="/data/UAdata/largefiles/"
	globalpathtrigger="/data/UAdata/largefiles/trigger/"
fi
globalpathslim="./flatslim"
usebool="--usebool" 

samples="VBF125,GluGlu,Data,T,WJets,ZJets,QCD"
samplesNOM=_sNOM
samplesVBF=_sVBF
samplesveto=`echo {VBF,Powheg}{115,120,130,135} | sed "s# #,#g"`

preselNOM="NOM"
preselVBF="VBF,NOMveto"

NOweight="1."
weightNOM="19784.,LUMI;XSEC;PU#0;TNOM;KF"
weightVBF="18281.,LUMI;XSEC;PU#0;TVBF;KF"
weightBoth="NOM_19784._LUMI;XSEC;PU#0;TNOM;KF,VBF_18281._LUMI;XSEC;PU#0;TVBF;KF"
#19784,18281



###   OPTIONS
###   
###   1    1	FlatTrees				NOM 
###   1    2							VBF
###   2    1    DataMC					NOM
###   2    2    						VBF
###
###

notext=""
# turning on/off legends
if [ "$3" == "0" ]; then 
	notext="--notext"
else
	notext=""
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "1" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "$globalpathslim" -t "NOM" --datatrigger "NOM" -p "$preselNOM" -s "$samples" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" --destination "$globalpathslim" -t "VBF" --datatrigger "VBF" -p "$preselVBF" -s "$samples" -w "$NOweight" $usebool $notext
	fi
fi

if ([ "$1" == "" ] || [ "$1" == "1" ]) && ([ "$2" == "3" ] || [ "2" == "" ]); then
	if [ ! -d ${globalpathslim}/DataSeparate ]; then mkdir ${globalpathslim}/DataSeparate; fi
	if [ ! -f ${globalpathslim}/fitFlatTree_MultiJetA_NOM.root ]; then mv ${globalpathslim}/DataSeparate/fitFlatTree_{MultiJet,BJetPlusX,VBF1Parked}*.root ${globalpathslim}/; fi

	if [ -f "${globalpathslim}/fitFlatTree_Data_NOM.root" ]; then mv ${globalpathslim}/fitFlatTree_Data_NOM.root ${globalpathslim}/DataSeparate/fitFlatTree_Data_NOM.root.backup; fi
	hadd ${globalpathslim}/fitFlatTree_Data_NOM.root ${globalpathslim}/fitFlatTree_{MultiJet,BJetPlusX}*_NOM.root
	mv ${globalpathslim}/fitFlatTree_{MultiJet,BJetPlusX}*_NOM.root ${globalpathslim}/DataSeparate/

	if [ -f "${globalpathslim}/fitFlatTree_Data_VBF.root" ]; then mv ${globalpathslim}/fitFlatTree_Data_VBF.root ${globalpathslim}/DataSeparate/fitFlatTree_Data_VBF.root.backup; fi
	hadd ${globalpathslim}/fitFlatTree_Data_VBF.root ${globalpathslim}/fitFlatTree_VBF1Parked*_VBF.root
	mv ${globalpathslim}/fitFlatTree_VBF1Parked*_VBF.root ${globalpathslim}/DataSeparate/
fi


##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM
	$basepath/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -s "$samplesNOM" -p "${preselNOM}" -t "NOM" -w "$weightNOM" $usebool $notext -v "$variablesNOM" --nosample $samplesveto
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF
	$basepath/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -s "$samplesVBF" -p "${preselVBF}" -t "VBF" -w "$weightVBF" $usebool $notext -v "$variablesVBF" --nosample $samplesveto
	fi
fi

##################################################
