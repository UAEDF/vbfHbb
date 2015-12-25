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
samplespath="$basepath/../../common/vbfHbb_samples_2015_fit.json"
variablesslim="$basepath/../../common/vbfHbb_variables_2013_bareslim.json"
globalpathskimslim="$basepath/../../fit/flat"
globalpathskimslim="$basepath/../../extra/BDTcorrelations/flat"
globalpathskimslim="/data/AA_UA/Workdir/git/vbfHbb/fit_v2/flat"
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
mvaBins="mvaNOM#3#-1.0;-0.6;0.0;1.0,mvaVBF#3#-1.0;-0.1;0.4;1.0"

#flatprefix="--flatprefix fit"
flatsuffixNOM="--flatsuffix _selNOM"
flatsuffixVBF="--flatsuffix _selVBF"

ws_signal="../kostas/workspace/signal_shapes_workspace_0.00_0.70_0.84.root"
ws_signal="../../fit_v2/thesis/root/sig_shapes_workspace_B80-200.root"

varsMbb="mbbReg1,mbbReg2"
binningMbb="mbbReg1;15;50;200,mbbReg2;15;50;200"
weightBoth="NOM_19784.0_PU#0;LUMI;XSEC;TNOM,VBF_18281.0_PU#0;LUMI;XSEC;TVBF"

globalpathskimslimZ="/data/AA_UA/Workdir/git/vbfHbb/largefiles/flatZ"
weightZ="19784.,LUMI;XSEC;PU#0;TNOM"
mvaBinsZ="mvaZ#3#-2;-0.02;0.02;2.0"


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
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,220" --complexWghts $weightBoth -s Data --typetag Data 
#		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s Data --typetag Data --merge
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,220" --complexWghts $weightBoth -s QCD500,QCD1000 --typetag QCD --unblind
#		$basepath/mkTransferFunctions.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_transferFunctions.root" --mvaBins $mvaBins --catTags "NOM,VBF" --fBound "80,200" --complexWghts $weightBoth -s QCD --typetag QCD --unblind --merge
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

##################################################
if [ "$1" == "" ] || [ "$1" == "3" ]; then
#	if [ "$2" == "" ] || [ "$2" == "1" ]; then
#		$basepath/mkMbbAverage.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_mbbRegProfiles.root" --mvaBins $mvaBins --catTags "NOM,VBF" --complexWghts $weightBoth -s Data --typetag Data 
#	fi
#	if [ "$2" == "" ] || [ "$2" == "2" ]; then
#		$basepath/mkMbbAverageZ.py -D "$defaultopts" -G "$globalpathskimslimZ" -S "$samplespath" -o "rootfiles/vbfHbb_mbbRegProfilesZ.root" --mvaBins $mvaBinsZ --catTags "NOM" --complexWghts $weightBoth -s Data --typetag Data 
#	fi
	if [ "$2" == "" ] || [ "$2" == "4" ]; then
		$basepath/mkMbbAverage.py -D "$defaultopts" -G "$globalpathskimslim" -S "$samplespath" -o "rootfiles/vbfHbb_mbbRegProfiles.root" --mvaBins $mvaBins --catTags "NOM,VBF" --complexWghts $weightBoth -s Data --typetag Data
	fi
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
		$basepath/mkMbbAverageZ.py -D "$defaultopts" -G "$globalpathskimslimZ" -S "$samplespath" -o "rootfiles/vbfHbb_mbbRegProfilesZ.root" --mvaBins $mvaBinsZ --catTags "NOM" --complexWghts $weightBoth -s Data,QCD250,QCD500,QCD1000 --typetag QCD
	fi
fi
	#notext=""
#done
