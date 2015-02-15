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
globalpathslim="./flatslim/"
usebool="--usebool" 

samples="VBF125,Data,T,WJets,ZJets,QCD" #GluGlu
samplesNOM=_sNOM
samplesVBF=_sVBF
samplesveto=`echo {VBF,Powheg}{115,120,130,135} | sed "s# #,#g"`,GF
sampleslargejson="../common/vbfHbb_samples_2015_large.json"
sampleslarge="VBF125,Data,T,WJets,ZJets,QCD,GF"

preselNOM="NOM"
preselVBF="VBF;NOMveto"

NOweight="1."
weightNOM="19784.,LUMI;XSEC;PU#0;TNOM;KF"
weightVBF="18281.,LUMI;XSEC;PU#0;TVBF;KF"
weightBoth="NOM_19784._LUMI;XSEC;PU#0;TNOM;KF,VBF_18281._LUMI;XSEC;PU#0;TVBF;KF"
#19784,18281

variablesNOM="mbbReg1,mqq1,dEtaqq1,jetPt0"
variablesVBF="mbbReg2,mqq2,dEtaqq2,jetPt0"


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
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} --destination "$globalpathslim" -t "NOM" --datatrigger "NOM" -p "$preselNOM" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF FitFlatTrees
	$basepath/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} --destination "$globalpathslim" -t "VBF" --datatrigger "VBF" -p "$preselVBF" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
fi

if ([ "$1" == "" ] || [ "$1" == "1" ]) && ([ "$2" == "3" ] || [ "2" == "" ]); then
	if [ ! -d ${globalpathslim}/DataSeparate ]; then mkdir ${globalpathslim}/DataSeparate; fi
	if [ ! -f ${globalpathslim}/flatTree_MultiJetA_sNOM.root ]; then mv ${globalpathslim}/DataSeparate/flatTree_{MultiJet,BJetPlusX,VBF1Parked}*.root ${globalpathslim}/; fi

#	if [ -f "${globalpathslim}/flatTree_Data_sNOM.root" ]; then mv ${globalpathslim}/flatTree_Data_sNOM.root ${globalpathslim}/DataSeparate/flatTree_Data_sNOM.root.backup; fi
#	hadd ${globalpathslim}/flatTree_Data_sNOM.root ${globalpathslim}/flatTree_{MultiJet,BJetPlusX}*_sNOM.root
#	mv ${globalpathslim}/flatTree_{MultiJet,BJetPlusX}*_sNOM.root ${globalpathslim}/DataSeparate/

	if [ -f "${globalpathslim}/flatTree_Data_sVBF.root" ]; then mv ${globalpathslim}/flatTree_Data_sVBF.root ${globalpathslim}/DataSeparate/flatTree_Data_sVBF.root.backup; fi
	hadd ${globalpathslim}/flatTree_Data_sVBF.root ${globalpathslim}/flatTree_VBF1Parked*_sVBF.root
	mv ${globalpathslim}/flatTree_VBF1Parked*_sVBF.root ${globalpathslim}/DataSeparate/
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
