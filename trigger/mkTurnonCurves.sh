#!/bin/sh

if [ "$(basename `pwd`)" == "trigger" ]; then 
	basepath="."
else 
	basepath="trigger"
fi

defaultopts="$basepath/../common/vbfHbb_defaultOpts_2013.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013"
	globalpathtrigger="/data/UAdata/autumn2013"
fi
samples="JetMon,QCD"
usebool="--usebool" 

limits1="jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001"
limits2="jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000#5000"
limits3="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0"
limits4="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.75#4.0#4.4#4.9#5.2#5.5#5.8#6.1#6.4#6.7#7.0#10.0"

preselNOM="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
preselVBF="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700"
preselVBFLL="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;Btag0_LL"
preselVBFNOMveto="$preselVBF;NOMveto"
preselVBFNOMvetoNoBtag="$preselVBF;NOMvetoNoBtag"
preselVBFNOMvetoSelNoBtag="$preselVBF;NOMvetoSelNoBtag"

#preselselNOM="$preselNOM;nLeptons;dPhibb1_lt2"
#preselselVBF="$preselVBF;Btag0_ML;nLeptons;dPhibb2_lt2"
#preselselVBFNOMveto="$preselselVBF;NOMveto"
#
maps1="$basepath/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root"
maps2="$basepath/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root"
maps3="$basepath/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root"
maps4="$basepath/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_bins2.root"
maps5="$basepath/rootfiles/trigger_2DMaps_VBF_NOMveto_mqq2-dEtaqq2_bins2.root"
maps6="$basepath/rootfiles/trigger_2DMaps_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2.root"
maps7="$basepath/rootfiles/trigger_2DMaps_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2.root"
maps8="$basepath/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_LL.root"
maps9="$basepath/rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2_corrected.root"
map1="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
map2="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
map3="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map5="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMveto-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map6="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMvetoNoBtag-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map7="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sNOMvetoSelNoBtag-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"
map8="2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2"

Nmin11="$basepath/rootfiles/trigger_Nmin1_NOM_jetBtag00-jetBtag10.root"
Nmin12="$basepath/rootfiles/trigger_Nmin1_NOM_jetBtag00-mqq1.root"
Nmin13="$basepath/rootfiles/trigger_Nmin1_VBF_mqq2-dEtaqq2.root"
Nmin14="$basepath/rootfiles/trigger_Nmin1_VBF_mqq2-dEtaqq2_bins2.root"
Nmin15="$basepath/rootfiles/trigger_Nmin1_VBF_NOMveto_mqq2-dEtaqq2_bins2.root"
Nmin16="$basepath/rootfiles/trigger_Nmin1_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2.root"
Nmin17="$basepath/rootfiles/trigger_Nmin1_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2.root"
Nmin18="$basepath/rootfiles/trigger_Nmin1_VBF_mqq2-dEtaqq2_LL.root"
Nmin19="$basepath/rootfiles/trigger_Nmin1_VBF_mqq2-dEtaqq2_corrected.root"

biasNOM="$basepath/rootfiles/trigger_Nmin1_NOM_bias.root"
biasVBF="$basepath/rootfiles/trigger_Nmin1_VBF_bias.root"

weightNOMtrg="19800.,PU#3;XSEC;LUMI"
weightVBFtrg="18300.,PU#3;XSEC;LUMI"
weightNOM="19800.,PU#0;XSEC;LUMI"
weightVBF="18300.,PU#0;XSEC;LUMI"

variablesNOM="mqq1,dEtaqq1,jetPt0,jetPt1,jetPt2,jetPt3,mbbReg1,dPhibb1,mvaNOM,jetBtag00,jetBtag10"
variablesVBF="mqq2,dEtaqq2,mjjTrig,dEtaTrig,jetPt0,jetPt1,jetPt2,jetPt3,ptAve,mbbReg2,dPhibb2,mvaVBF,jetBtag00,jetBtag10"
#variablesVBF="dEtaqq2,mqq2,mvaVBF"

binningNOM1="mvaNOM;10;-1;1,mbbReg1;15;0;300,jetBtag00;20;0;1,jetBtag10;20;0;1,jetPt0;20;0;400,jetPt1;15;0;300,jetPt2;8;0;160,jetPt3;6;0;120,dEtaqq1;14;2;9,mqq1;20;0;2000,dPhibb1;10;0;2"
binningVBF1="mvaVBF;10;-1;1,mbbReg2;15;0;300,jetBtag00;20;0;1,jetBtag10;20;0;1,jetPt0;20;0;400,jetPt1;15;0;300,jetPt2;8;0;160,jetPt3;6;0;120,dEtaqq2;35;2;9,mqq2;20;0;2000,dPhibb2;10;0;2,dEtaTrig;35;2;9,mjjTrig;20;0;2000,ptAve;20;0;400"

###   OPTIONS
###   
###   1    1 NOM bjet0 bjet1
###        2 NOM bjet0 mqq1
###        3 VBF mqq2 deta2
###        4 VBF mqq2 deta2    bins2
###        5 VBF mqq2 deta2    bins2               BTag0_LL
###        6 VBF mqq2 deta2    bins2               exclusive	NOMveto
###        7 VBF mqq2 deta2    bins2               exclusive	NOMvetoNoBtag
###        8 VBF mqq2 deta2    bins2               exclusive	NOMvetoSelNoBtag
###   2    1 Nmin1 bias        NOM 
###        2                   VBF 
###   3    1 Nmin1 closure     NOM bjet0 bjet1
###        2                   NOM bjet0 mqq1
###        3                   VBF mqq2 dEtaqq2
###        4                   VBF mqq2 dEtaqq2    bins2
###        5                   VBF mqq2 dEtaqq2    bins2	NOMveto
###        6                   VBF mqq2 dEtaqq2    bins2	NOMvetoNoBtag
###        7                   VBF mqq2 dEtaqq2    bins2	NOMvetoSelNoBtag
###        8                   VBF mqq2 dEtaqq2    bins2	LL


# turning on/off legends
if [ "$3" == "0" ]; then 
	notext="--notext"
else
	notext=""
fi

##################################################
for i in `seq 0 1`; do
	if [ "$notext" == "" ] && [ "$i" == "0" ]; then continue; fi
##################################################
if [ "$1" == "" ] || [ "$1" == "1" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM MAPS - jetBtag00-jetBtag10
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg" -o "$maps1" -m "$limits1" $usebool $notext 
	fi
	
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# NOM MAPS - jetBtag00-mqq1
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg" -o "$maps2" -m "$limits2" $usebool $notext
	fi
	
    if [ "$2" == "" ] || [ "$2" == "3" ]; then
	# VBF MAPS - mqq2-dEtaqq2 
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" -o "$maps3" -m "$limits3" $usebool $notext
	fi
	
    if [ "$2" == "" ] || [ "$2" == "9" ]; then
	# VBF MAPS - mqq2-dEtaqq2 
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" -o "$maps9" -m "$limits3" $usebool $notext
	fi

    if [ "$2" == "" ] || [ "$2" == "4" ]; then
    # VBF MAPS - mqq2-dEtaqq2 - bins2
    $basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" -o "$maps4" -m "$limits4" $usebool $notext
	fi
   
    if [ "$2" == "" ] || [ "$2" == "5" ]; then
    # VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMveto
    $basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMveto" -r "AV80" -w "$weightVBFtrg" -o "$maps5" -m "$limits4" $usebool $notext
	fi
   
    if [ "$2" == "" ] || [ "$2" == "6" ]; then
    # VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMvetoNoBtag
    $basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMvetoNoBtag" -r "AV80" -w "$weightVBFtrg" -o "$maps6" -m "$limits4" $usebool $notext
	fi
   
	if [ "$2" == "" ] || [ "$2" == "7" ]; then
    # VBF MAPS - mqq2-dEtaqq2 - bins2 - NOMvetoSelNoBtag
    $basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFNOMvetoSelNoBtag" -r "AV80" -w "$weightVBFtrg" -o "$maps7" -m "$limits4" $usebool $notext
	fi
   
    if [ "$2" == "" ] || [ "$2" == "8" ]; then
	# VBF MAPS - mqq2-dEtaqq2 - LL
	$basepath/../common/main.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "$samples" -p "$preselVBFLL" -r "AV80" -w "$weightVBFtrg" -o "$maps8" -m "$limits4" $usebool $notext
	fi
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM Nmin1 - no map correction - bias reftrig
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -v "$variablesNOM" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg" $usebool $notext --binning "$binningNOM1" -o $biasNOM --drawstack --closure --shade
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF Nmin1 - no map correction - bias reftrig
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg" $usebool $notext --binning "$binningVBF1" -o $biasVBF --drawstack --closure --shade
	fi
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "3" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM Nmin1 - jetBtag00-jetBtag10
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -v "$variablesNOM" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg;MAP#jetBtag[b1[0]]#jetBtag[b2[0]],,$maps1;$map1" $usebool $notext --binning "$binningNOM1" -o $Nmin11 --drawstack --overlay --shade
	fi	
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# NOM Nmin1 - jetBtag00-mqq1
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -v "$variablesNOM" -s "$samples" -p "$preselNOM" -r "AV80" -w "$weightNOMtrg;MAP#jetBtag[b1[0]]#mqq[1],,$maps2;$map2" $usebool $notext --binning "$binningNOM1" -o $Nmin12 --drawstack --overlay --shade
	fi	
	if [ "$2" == "" ] || [ "$2" == "3" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps3;$map3" $usebool $notext --binning "$binningVBF1" -o $Nmin13 --drawstack --overlay --shade
	fi
	if [ "$2" == "" ] || [ "$2" == "4" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 - bins2
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps4;$map3" $usebool $notext --binning "$binningVBF1" -o $Nmin14 --drawstack --overlay --shade
	fi
	if [ "$2" == "" ] || [ "$2" == "5" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 - bins2 - NOMveto
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBFNOMveto" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps5;$map5" $usebool $notext --binning "$binningVBF1" -o $Nmin15 --drawstack --overlay --shade
	fi
	if [ "$2" == "" ] || [ "$2" == "6" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 - bins2 - NOMvetoNoBtag
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBFNOMvetoNoBtag" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps6;$map6" $usebool $notext --binning "$binningVBF1" -o $Nmin16 --drawstack --overlay --shade
	fi
	if [ "$2" == "" ] || [ "$2" == "7" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 - bins2 - NOMvetoNoBtag
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBFNOMvetoSelNoBtag" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps7;$map7" $usebool $notext --binning "$binningVBF1" -o $Nmin17 --drawstack --overlay --shade
	fi
#	if [ "$2" == "" ] || [ "$2" == "8" ]; then
#	# VBF Nmin1 - mqq2-dEtaqq2 - LL 
#	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBFLL" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps8;$map8" $usebool $notext --binning "$binningVBF1" -o $Nmin111 --drawstack --overlay --shade
#	fi
	if [ "$2" == "" ] || [ "$2" == "9" ]; then
	# VBF Nmin1 - mqq2-dEtaqq2 - corrected
	$basepath/mkTurnonCurves.py -d -D "$defaultopts" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -v "$variablesVBF" -s "$samples" -p "$preselVBF" -r "AV80" -w "$weightVBFtrg;MAP#mqq[2]#dEtaqq[2],,$maps9;$map3" $usebool $notext --binning "$binningVBF1" -o $Nmin19 --drawstack --overlay --shade
	fi
fi

##################################################
notext=""
done
