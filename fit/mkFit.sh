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
	globalpath="/data/UAdata/autumn2013/"
	globalpathtrigger="/data/UAdata/autumn2013/"
fi
variablesslim="$basepath/../common/vbfHbb_variables_2013_bareslim.json"
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

mvaBins="mvaNOM#5#-1.0;-0.6;0.0;0.7;0.84;1.0,mvaVBF#4#-1.0;-0.1;0.4;0.8;1.0"

flatprefix="--flatprefix fit"
flatsuffixNOM="--flatsuffix _NOM"
flatsuffixVBF="--flatsuffix _VBF"

ws_signal="../kostas/workspace/signal_shapes_workspace_0.00_0.70_0.84.root"

varsMbb="mbbReg1,mbbReg2"
binningMbb="mbbReg1;15;50;200,mbbReg2;15;50;200"
weightBoth="NOM_19784._LUMI;XSEC;PU#0;TNOM;KF,VBF_18281._LUMI;XSEC;PU#0;TVBF;KF"


###   OPTIONS
###   
###   1    1		FitFlatTrees				NOM 
###   1    2										VBF
###   2    1      Yields						NOM
###   2    2            						VBF
###   3    1		SigOverBkg					NOM
###   3    2										VBF
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
	if [ ! -d ./flat/DataSeparate ]; then mkdir ./flat/DataSeparate; fi
	if [ ! -f ./flat/fitFlatTree_MultiJetA_NOM.root ]; then mv ./flat/DataSeparate/fitFlatTree_{MultiJet,BJetPlusX,VBF1Parked}*.root ./flat/; fi

	if [ -f "./flat/fitFlatTree_Data_NOM.root" ]; then mv ./flat/fitFlatTree_Data_NOM.root ./flat/DataSeparate/fitFlatTree_Data_NOM.root.backup; fi
	hadd ./flat/fitFlatTree_Data_NOM.root ./flat/fitFlatTree_{MultiJet,BJetPlusX}*_NOM.root
	mv ./flat/fitFlatTree_{MultiJet,BJetPlusX}*_NOM.root ./flat/DataSeparate/

	if [ -f "./flat/fitFlatTree_Data_VBF.root" ]; then mv ./flat/fitFlatTree_Data_VBF.root ./flat/DataSeparate/fitFlatTree_Data_VBF.root.backup; fi
	hadd ./flat/fitFlatTree_Data_VBF.root ./flat/fitFlatTree_VBF1Parked*_VBF.root
	mv ./flat/fitFlatTree_VBF1Parked*_VBF.root ./flat/DataSeparate/
fi


##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_yields_NOM.root" -t "None" --datatrigger "None" -p "MBBREG1,MBBREG1;mvaNOMC0,MBBREG1;mvaNOMC1,MBBREG1;mvaNOMC2,MBBREG1;mvaNOMC3,MBBREG1;mvaNOMC4" --nosample "JetMon,DataV" -w "$weightNOM" $usebool $notext $flatprefix $flatsuffixNOM -y --latex #-K
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_yields_VBF.root" -t "None" --datatrigger "None" -p "MBBREG2,MBBREG2;mvaVBFC0,MBBREG2;mvaVBFC1,MBBREG2;mvaVBFC2,MBBREG2;mvaVBFC3" --nosample "JetMon,DataA,DataB,DataC,DataD" -w "$weightVBF" $usebool $notext $flatprefix $flatsuffixVBF -y --latex #-K
	fi
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "3" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM
	# with width 
	$basepath/mkSigOverBkg.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_sigbkg_NOM.root" --nosample "JetMon,DataV" --sample "$samples_SoB_NOM" -w "$weightNOM" $usebool $notext $flatprefix $flatsuffixNOM --wsig "$ws_signal"  -t "None" --datatrigger "None" -p "None,mvaNOMC0,mvaNOMC1,mvaNOMC2,mvaNOMC3,mvaNOMC4"	
	# with range
	$basepath/mkSigOverBkg.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_sigbkg_NOM.root" --nosample "JetMon,DataV" --sample "$samples_SoB_NOM" -w "$weightNOM" $usebool $notext $flatprefix $flatsuffixNOM --xmin 80 --xcen 125 --xmax 200  -t "None" --datatrigger "None" -p "None,mvaNOMC0,mvaNOMC1,mvaNOMC2,mvaNOMC3,mvaNOMC4"	
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF
	# with width 
	$basepath/mkSigOverBkg.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_sigbkg_VBF.root" --nosample "JetMon,DataA,DataB,DataC,DataD" --sample "$samples_SoB_VBF" -w "$weightVBF" $usebool $notext $flatprefix $flatsuffixVBF --wsig "$ws_signal"  -t "None" --datatrigger "None" -p "None,mvaVBFC0,mvaVBFC1,mvaVBFC2,mvaVBFC3"
	# with range
	$basepath/mkSigOverBkg.py -d -D "$defaultopts" -G "$globalpathskimslim" -V "$variablesslim" -o "rootfiles/vbfHbb_sigbkg_VBF.root" --nosample "JetMon,DataA,DataB,DataC,DataD" --sample "$samples_SoB_VBF" -w "$weightVBF" $usebool $notext $flatprefix $flatsuffixVBF --xmin 80 --xcen 125 --xmax 200  -t "None" --datatrigger "None" -p "None,mvaVBFC0,mvaVBFC1,mvaVBFC2,mvaVBFC3"	
	fi
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "4" ]; then
	$basepath/mk-01-TransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200"
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "5" ]; then
	$basepath/mk-02-CreateBkgTemplates.py -D "$defaultopts" -G "$globalpathskimslim" -o "rootfiles/vbfHbb_bkgTemplates.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --sample $samplesBkg --nosample $nosamplesBkg --complexWeight $weightBoth $usebool -v $varsMbb --binning $binningMbb
fi

##################################################
#notext=""
#done
