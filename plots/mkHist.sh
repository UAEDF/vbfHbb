#!/bin/sh

if [ "$(basename `pwd`)" == "plots" ]; then 
	basepath="."
else 
	basepath="plots"
fi

defaultopts="$basepath/../common/vbfHbb_defaultOpts_2013.json"
globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
samplesNOM="JetMon,DataVA,DataVB,DataVC,DataVD,VBF115,VBF120,VBF130,VBF135"
samplesVBF="JetMon,DataA,DataB,DataC,DataD,VBF115,VBF120,VBF130,VBF135"
usebool="--usebool"

limits1="jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001"
limits2="jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000#5000"
limits3="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0"
limits4="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.75#4.0#4.4#4.9#5.2#5.5#5.8#6.1#6.4#6.7#7.0#10.0"

preselNOM="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
preselVBF="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700"
preselVBFLL="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;Btag0_LL"
preselVBFNOMveto="$preselVBFNOMveto;NOMveto"
preselVBFNOMvetoNoBtag="$preselVBFNOMveto;NOMvetoNoBtag"
preselVBFNOMvetoSelNoBtag="$preselVBFNOMveto;NOMvetoSelNoBtag"

preselselNOM="$preselNOM;nLeptons;dPhibb1_lt2"
preselselVBF="$preselVBF;Btag0_ML;nLeptons;dPhibb2_lt2"
preselselVBFNOMveto="$preselselVBF;NOMveto"
preselselVBFNOMvetoNoBtag="$preselselVBF;NOMvetoNoBtag"
preselselVBFNOMvetoSelNoBtag="$preselselVBF;NOMvetoSelNoBtag"

maps1="$basepath/../trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root"
maps2="$basepath/../trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root"
maps3="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root"
maps4="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_bins2.root"
maps5="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_NOMveto_mqq2-dEtaqq2_bins2.root"
maps6="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2.root"
maps7="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2.root"
maps8="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_LL.root"
maps9="$basepath/../trigger/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_corrected.root"
map1="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
map2="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
map3="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map5="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMveto-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map6="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMvetoNoBtag-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map7="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMvetoSelNoBtag-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map8="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"

controlNOM1="$basepath/rootfiles/control_NOM.root"
controlNOM2="$basepath/rootfiles/control_NOM_jetBtag00-jetBtag10.root"
controlNOM3="$basepath/rootfiles/control_NOM_jetBtag00-mqq1.root"
controlVBF11="$basepath/rootfiles/control_VBF.root"
controlVBF12="$basepath/rootfiles/control_VBF_mqq2-dEtaqq2.root"
controlVBF13="$basepath/rootfiles/control_VBF_mqq2-dEtaqq2_bins2.root"
controlVBF14="$basepath/rootfiles/control_VBF_mqq2-dEtaqq2_corrected.root"
controlVBF21="$basepath/rootfiles/control_VBF_NOMveto.root"
controlVBF23="$basepath/rootfiles/control_VBF_NOMveto_mqq2-dEtaqq2_bins2.root"
controlVBF31="$basepath/rootfiles/control_VBF_NOMvetoNoBtag.root"
controlVBF33="$basepath/rootfiles/control_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2.root"
controlVBF41="$basepath/rootfiles/control_VBF_NOMvetoSelNoBtag.root"
controlVBF43="$basepath/rootfiles/control_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2.root"
controlVBF5="$basepath/rootfiles/control_VBF_mqq2-dEtaqq2_bins2_LL.root"

weightNOMtrg="19800.,PU#3;XSEC;LUMI"
weightVBFtrg="18300.,PU#3;XSEC;LUMI"
weightNOM="19800.,PU#0;XSEC;LUMI;KFAC"
weightVBF="18300.,PU#0;XSEC;LUMI;KFAC"

variablesNOM="mqq1,dEtaqq1,jetPt0,jetPt1,jetPt2,jetPt3,mbbReg1,dPhibb1,mvaNOM,jetBtag00,jetBtag10"
variablesVBF="mqq2,dEtaqq2,mjjTrig,dEtaTrig,jetPt0,jetPt1,jetPt2,jetPt3,ptAve,mbbReg2,dPhibb2,mvaVBF,jetBtag00,jetBtag10"
variablesVBF="dEtaqq2,mqq2,mvaVBF"

binningNOM1="mvaNOM;40;-1;1,mbbReg1;30;0;300,jetBtag00;25;0;1,jetBtag10;25;0;1,jetPt0;20;0;400,jetPt1;15;0;300,jetPt2;8;0;160,jetPt3;6;0;120,dEtaqq1;35;2;9,mqq1;20;0;2000,dPhibb1;30;0;2.4"
binningVBF1="mvaVBF;40;-1;1,mbbReg2;30;0;300,jetBtag00;25;0;1,jetBtag10;25;0;1,jetPt0;20;0;400,jetPt1;15;0;300,jetPt2;8;0;160,jetPt3;6;0;120,dEtaqq2;35;2;9,mqq2;20;0;2000,dPhibb2;30;0;2.4,dEtaTrig;35;2;9,mjjTrig;20;0;2000,ptAve;40;0;400"

###   OPTIONS
###   
###   1    MAPS ONLY
###   2    1 control plots     NOM
###        2                   NOM bjet0 bjet1
###        3                   NOM bjet0 mqq1
###        11                  VBF 
###        12                  VBF mqq2 dEtaqq2
###        13                  VBF mqq2 dEtaqq2							bins2
###        21                  VBF					NOMveto 	
###        23                  VBF mqq2 dEtaqq2		NOMveto				bins2
###        31                  VBF 					NOMvetoNoBtag
###        33                  VBF mqq2 dEtaqq2		NOMvetoNoBtag		bins2
###        41                  VBF 					NOMvetoSelNoBtag
###        43                  VBF mqq2 dEtaqq2		NOMvetoSelNoBtag	bins2
###        5                   VBF mqq2 dEtaqq2		LL	



##################################################
if [ "$1" == "" ] || [ "$1" == "1" ];then
	# NOM MAPS - jetBtag00-jetBtag10
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg" -o "$maps1" -m "$limits1" $usebool
	
	# NOM MAPS - jetBtag00-mqq1
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg" -o "$maps2" -m "$limits2" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" -o "$maps3" -m "$limits3" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 - bins2
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" -o "$maps4" -m "$limits4" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMveto
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMveto" -r "AV80" -w "$weightVBFtrg" -o "$maps5" -m "$limits4" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMvetoNoBtag
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMvetoNoBtag" -r "AV80" -w "$weightVBFtrg" -o "$maps6" -m "$limits4" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMvetoSelNoBtag
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMvetoSelNoBtag" -r "AV80" -w "$weightVBFtrg" -o "$maps7" -m "$limits4" $usebool
	
	# VBF MAPS - mqq2-dEtaqq2 - LL
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFLL" -r "AV80" -w "$weightVBFtrg" -o "$maps8" -m "$limits4" $usebool
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM plots - no map correction
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "NOMMC" --datatrigger "NOMMC" -r "None" -v "$variablesNOM" --nosample "$samplesNOM" -p "$preselselNOM" -w "$weightNOM" $usebool --binning "$binningNOM1" -o $controlNOM1 --drawstack 
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# NOM plots - bjet0 bjet1 
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "NOMMC" --datatrigger "NOMMC" -r "None" -v "$variablesNOM" --nosample "$samplesNOM" -p "$preselselNOM" -w "$weightNOM;MAP#jetBtag[b1[0]]#jetBtag[b2[0]],,$maps1;$map1" $usebool --binning "$binningNOM1" -o $controlNOM2 --drawstack 
	fi
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
	# NOM plots - bjet0 mqq1 
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "NOMMC" --datatrigger "NOMMC" -r "None" -v "$variablesNOM" --nosample "$samplesNOM" -p "$preselselNOM" -w "$weightNOM;MAP#jetBtag[b1[0]]#mqq[1],,$maps2;$map2" $usebool --binning "$binningNOM1" -o $controlNOM3 --drawstack 
	fi
#########################
	if [ "$2" == "" ] || [ "$2" == "11" ]; then
	# VBF plots - no map correction
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBF" -w "$weightVBF,1.439143" $usebool --binning "$binningVBF1" -o $controlVBF11 --drawstack 
	fi
	if [ "$2" == "" ] || [ "$2" == "12" ]; then
	# VBF plots - mqq2 dEtaqq2
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBF" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps3;$map3" $usebool --binning "$binningVBF1" -o $controlVBF12 --drawstack 
	fi
	if [ "$2" == "" ] || [ "$2" == "13" ]; then
	# VBF plots - mqq2 dEtaqq2 - bins2
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBF" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps4;$map3" $usebool --binning "$binningVBF1" -o $controlVBF13 --drawstack 
	fi
	if [ "$2" == "" ] || [ "$2" == "14" ]; then
	# VBF plots - mqq2 dEtaqq2
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBF" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],1.721785,$maps9;$map3" $usebool --binning "$binningVBF1" -o $controlVBF14 --drawstack 
	fi
#########################
	if [ "$2" == "" ] || [ "$2" == "21" ]; then
	# VBF plots - no map correction - NOMveto
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMveto" -w "$weightVBF" $usebool --binning "$binningVBF1" -o $controlVBF21 --drawstack 
	fi
#	if [ "$2" == "" ] || [ "$2" == "22" ]; then
#	# VBF plots - mqq2 dEtaqq2 - NOMveto
#	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMveto" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps3;$map3" $usebool --binning "$binningVBF1" -o $controlVBF22 --drawstack 
#	fi
	if [ "$2" == "" ] || [ "$2" == "23" ]; then
	# VBF plots - mqq2 dEtaqq2 - bins2 - NOMveto
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMveto" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps5;$map5" $usebool --binning "$binningVBF1" -o $controlVBF23 --drawstack 
	fi
#########################
	if [ "$2" == "" ] || [ "$2" == "31" ]; then
	# VBF plots - no map correction - NOMvetoNoBtag
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoNoBtag" -w "$weightVBF" $usebool --binning "$binningVBF1" -o $controlVBF31 --drawstack 
	fi
#	if [ "$2" == "" ] || [ "$2" == "32" ]; then
#	# VBF plots - mqq2 dEtaqq2 - NOMvetoNoBtag
#	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoNoBtag" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps3;$map3" $usebool --binning "$binningVBF1" -o $controlVBF32 --drawstack 
#	fi
	if [ "$2" == "" ] || [ "$2" == "33" ]; then
	# VBF plots - mqq2 dEtaqq2 - bins2 - NOMvetoNoBtag
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoNoBtag" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps6;$map6" $usebool --binning "$binningVBF1" -o $controlVBF33 --drawstack 
	fi
#########################
	if [ "$2" == "" ] || [ "$2" == "41" ]; then
	# VBF plots - no map correction - NOMvetoSelNoBtag
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoSelNoBtag" -w "$weightVBF" $usebool --binning "$binningVBF1" -o $controlVBF41 --drawstack 
	fi
#	if [ "$2" == "" ] || [ "$2" == "42" ]; then
#	# VBF plots - mqq2 dEtaqq2 - NOMvetoSelNoBtag
#	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoSelNoBtag" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps3;$map3" $usebool --binning "$binningVBF1" -o $controlVBF42 --drawstack 
#	fi
	if [ "$2" == "" ] || [ "$2" == "43" ]; then
	# VBF plots - mqq2 dEtaqq2 - bins2 - NOMvetoSelNoBtag
	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBFNOMvetoSelNoBtag" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps7;$map7" $usebool --binning "$binningVBF1" -o $controlVBF43 --drawstack 
	fi
#########################
#	if [ "$2" == "" ] || [ "$2" == "4" ]; then
#	# VBF plots - mqq2 dEtaqq2 - LL
#	$basepath/mkHist.py -d -K -D "$defaultopts" -G "$globalpath" -t "VBF" --datatrigger "VBF" -r "None" -v "$variablesVBF" --nosample "$samplesVBF" -p "$preselselVBF" -w "$weightVBF;MAP#mqq[2]#dEtaqq[2],,$maps8;$map8" $usebool --binning "$binningVBF1" -o $controlVBF5 --drawstack 
#	fi
fi

