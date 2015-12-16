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
	globalpath="/usb/MrBig/UAdata/"
#	globalpath="/usb/data2/UAData/2015/"
	globalpathtrigger="/data/UAdata/largefiles/trigger/"
	globalpathtrigger="/usb/MrBig/UAdataTrigger/"
fi
globalpathslim="./flatslim/"
usebool="--usebool" 

samples="VBF125,Data,T,WJets,ZJets,QCD,GF"
samplesNOM=_sNOM
samplesVBF=_sVBF
samplesveto=`echo {VBF,Powheg}{115,120,130,135} | sed "s# #,#g"`
sampleslargejson="../common/vbfHbb_samples_2015_large.json"
sampleslarge="VBF125,Data,T,WJets,ZJets,QCD,GluGlu"

samplesTPN=_sTPN
samplesTPV=_sTPV

preselNOM="NOM"
preselVBF="VBF;NOMveto"
preselTPN="TPN"
preselTPV="TPV;NOMveto"

NOweight="1."
weightNOM="19784.,LUMI;XSEC;PU#0;TNOM;KF"
weightVBF="18281.,LUMI;XSEC;PU#0;TVBF;KF"
weightTPN="19784.,LUMI;XSEC;PU#0;TNOM;KF"
weightTPV="18281.,LUMI;XSEC;PU#0;TVBF;KF"
weightBoth="NOM_19784._LUMI;XSEC;PU#0;TNOM;KF,VBF_18281._LUMI;XSEC;PU#0;TVBF;KF"
#19784,18281

variablesTOPjson="../common/vbfHbb_variables_2015_top.json"
infoTOPjson="../common/vbfHbb_info_2015_Tsplit.json"
variablesNOM="mbbReg1,mqq1,dEtaqq1,jetPt0,jetPt1,jetPt2,jetPt3,dPhibb1,jetBtag00,jetBtag01,jetBlikNOM0,jetBlikNOM1,jetBlikNOM2,jetBlikNOM3,dPhiqq1,softHt,softN2,etabb1,ptbb1,cosTheta1,jetEta0,jetEta1,jetEta2,jetEta3,jetEtab11,jetEtab21,jetEtaq11,jetEtaq21,rho,nvtx,met,mvaNOM,mvaZ,jetQGLb11,jetQGLb21,jetQGLq11,jetQGLq21"
variablesVBF="mbbReg2,mqq2,dEtaqq2,jetPt0,jetPt1,jetPt2,jetPt3,dPhibb2,jetBtag00,jetBtag01,jetBlikVBF0,jetBlikVBF1,jetBlikVBF2,jetBlikVBF3,dPhiqq2,softHt,softN2,etabb2,ptbb2,cosTheta2,jetEta0,jetEta1,jetEta2,jetEta3,jetEtab12,jetEtab22,jetEtaq12,jetEtaq22,rho,nvtx,met,mvaVBF,mvaZ,jetQGLb12,jetQGLb22,jetQGLq12,jetQGLq22"
variablesTPN="mbbReg1,mqq1,dEtaqq1,jetPt0,jetPt1,jetPt2,jetPt3,dPhibb1,jetBtag00,jetBtag01,dPhiqq1,cosTheta1,etabb1,ptbb1,jetBtag00,jetBtag01,jetBlikNOM0,jetBlikNOM1,jetBlikNOM2,jetBlikNOM3,jetQGLb11,jetQGLb21,jetQGLq11,jetQGLq21,softHt,softN2,mvaNOM,mvaZ"
variablesTPV="mbbReg2,mqq2,dEtaqq2,jetPt0,jetPt1,jetPt2,jetPt3,dPhibb2,jetBtag00,jetBtag01,dPhiqq2,cosTheta2,etabb2,ptbb2,jetBtag00,jetBtag01,jetBlikVBF0,jetBlikVBF1,jetBlikVBF2,jetBlikVBF3,jetQGLb12,jetQGLb22,jetQGLq12,jetQGLq22,softHt,softN2,mvaVBF,mvaZ"

###   OPTIONS
###   
###   1    1	FlatTrees				NOM 
###   1    2							VBF
###   1    3							TPN
###   1    4							TPV
###   1    5							Combo
###   2    1    DataMC					NOM
###   2    2    						VBF
###   2    3    						TPN
###   2    4    						TPV
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
	$basepath/src/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} --destination "$globalpathslim" -t "NOM" -p "$preselNOM" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF FitFlatTrees
	$basepath/src/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} --destination "$globalpathslim" -t "VBF" -p "$preselVBF" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
	# TOPNOM FitFlatTrees
	$basepath/src/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} -V ${variablesTOPjson} --destination "$globalpathslim" -t "TPN" -p "$preselTPN" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
	if [ "$2" == "" ] || [ "$2" == "4" ]; then
	# TOPVBF FitFlatTrees
	$basepath/src/mkFitFlatTrees.py -d -D "$defaultopts" -G "$globalpath" -S ${sampleslargejson} -V ${variablesTOPjson} --destination "$globalpathslim" -t "TPV" -p "$preselTPV" -s "$sampleslarge" -w "$NOweight" $usebool $notext
	fi
fi

if ([ "$1" == "" ] || [ "$1" == "1" ]) && ([ "$2" == "5" ] || [ "2" == "" ]); then
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
	$basepath/src/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -s "$samplesNOM" -p "${preselNOM}" -t "NOM" -w "$weightNOM" $usebool $notext -v "$variablesNOM" --nosample $samplesveto
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF
	$basepath/src/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -s "$samplesVBF" -p "${preselVBF}" -t "VBF" -w "$weightVBF" $usebool $notext -v "$variablesVBF" --nosample $samplesveto
	fi
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
	# TOPNOM
	$basepath/src/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -V ${variablesTOPjson} -I ${infoTOPjson} -s "$samplesTPN" -p "${preselTPN}" -t "TPN" -w "$weightTPN" $usebool $notext -v "$variablesTPN" --nosample $samplesveto
	fi
	if [ "$2" == "" ] || [ "$2" == "4" ]; then
	# TOPVBF
	$basepath/src/mkDataMC.py -d -D "$defaultopts" -G "$globalpathslim" -V ${variablesTOPjson} -I ${infoTOPjson} -s "$samplesTPV" -p "${preselTPV}" -t "TPV" -w "$weightTPV" $usebool $notext -v "$variablesTPV" --nosample $samplesveto
	fi
fi

##################################################
