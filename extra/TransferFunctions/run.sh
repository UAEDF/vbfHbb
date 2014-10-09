#!/bin/sh

basepath=`pwd`

defaultopts="$basepath/../../common/vbfHbb_defaultOpts_2013.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013/"
	globalpathtrigger="/data/UAdata/autumn2013/"
fi
samplespath="$basepath/../../common/vbfHbb_samples_2014_fit.json"
variablesslim="$basepath/../../common/vbfHbb_variables_2013_bareslim.json"
globalpathskimslim="$basepath/../../fit/flat"
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
weightBoth="NOM_19784.0_PU#0;LUMI;XSEC;TNOM,VBF_18281.0_PU#0;LUMI;XSEC;TVBF"


###   OPTIONS
###   
###	  1   -    TransferFunctions - all   
###

notext=""
## turning on/off legends
#if [ "$3" == "0" ]; then 
#	notext="--notext"
#else
#	notext=""
#fi

##################################################
if [ "$1" == "" ] || [ "$1" == "1" ]; then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
		echo $basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s Data --typetag Data 
		echo $basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s Data --typetag Data --merge
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s QCD --typetag QCD --unblind 
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s QCD --typetag QCD --unblind --merge
	fi
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s Z --typetag Z --unblind 
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s Z --typetag Z --unblind --merge
	fi
	if [ "$2" == "" ] || [ "$2" == "4" ]; then
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s T --typetag Top --unblind --merge
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s T --typetag Top --unblind 
	fi
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "2" ]; then
	$basepath/olTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" 
fi
	#notext=""
#done
