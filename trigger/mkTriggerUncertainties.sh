#!/bin/sh

if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
	globalpathtrigger="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/trigger"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/autumn2013"
	globalpathtrigger="/data/UAdata/autumn2013"
fi
samples="VBF115,VBF120,VBF125,VBF130,VBF135,GluGlu,singleT,TTJets,WJets,ZJets,QCD" #sample
#samples="JetMon,Data" #nosample
groups="VBF115,VBF120,VBF125,VBF130,VBF135,GF,Tall,WJets,ZJets,QCD" #sample

limits1="jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001"
limits2="jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000#5000"
limits3="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0"
limits4="mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0"

presel1="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
presel2="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
presel3="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700"
preselsel1="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2"
preselsel2="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2"
preselsel3="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;Btag0_ML;nLeptons;dPhibb2_lt2"
preselsel4="run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;Btag0_ML;nLeptons;dPhibb2_lt2;NOMveto"

maps1="rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root"
maps2="rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root"
maps3="rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root"
maps4="rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root"

dist1="rootfiles/trigger_DistMaps_NOM_jetBtag00-jetBtag10.root"
dist2="rootfiles/trigger_DistMaps_NOM_jetBtag00-mqq1.root"
dist3="rootfiles/trigger_DistMaps_VBF_mqq2-dEtaqq2.root"
dist4="rootfiles/trigger_DistMaps_VBF_NOMveto_mqq2-dEtaqq2.root"

output1="rootfiles/trigger_ScaleFactors_NOM_jetBtag00-jetBtag10.root"
output2="rootfiles/trigger_ScaleFactors_NOM_jetBtag00-mqq1.root"
output3="rootfiles/trigger_ScaleFactors_VBF_mqq2-dEtaqq2.root"
output4="rootfiles/trigger_ScaleFactors_VBF_NOMveto_mqq2-dEtaqq2.root"

overlay1="rootfiles/trigger_ScaleFactors_NOM_all.root"
overlay2="rootfiles/trigger_ScaleFactors_VBF_all.root"

usebool="--usebool"

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
	# NOM MAPS - jetBtag00-jetBtag10
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "JetMon,QCD" -p "$presel1" -r "AV80" -w "19800.,PU#3;XSEC;LUMI" -o "$maps1" -m "$limits1" $usebool $notext
	
	# NOM MAPS - jetBtag00-mqq1
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "$globalpathtrigger" -t "NOMMC" --datatrigger "NOMMC" -s "JetMon,QCD" -p "$presel2" -r "AV80" -w "19800.,PU#3;XSEC;LUMI" -o "$maps2" -m "$limits2" $usebool $notext
	
	# VBF MAPS - mqq2-dEtaqq2 
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "$globalpathtrigger" -t "VBF" --datatrigger "VBF" -s "JetMon,QCD" -p "$presel3" -r "AV80" -w "18300.,PU#3;XSEC;LUMI" -o "$maps3" -m "$limits3" $usebool $notext
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM DISTMAPS - jetBtag00-jetBtag10
	for i in `seq 0 4`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "NOMMC" --datatrigger "NOM" --sample "$samples" -p "$preselsel1;mvaNOMC$i" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "$dist1" -m "$limits1" --numonly $usebool $notext ; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "NOMMC" --datatrigger "NOM" --sample "$samples" -p "$preselsel1" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "$dist1" -m "$limits1" --numonly $usebool $notext
	
	# NOM DISTMAPS - jetBtag00-mqq
	for i in `seq 0 4`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "NOMMC" --datatrigger "NOM" --sample "$samples" -p "$preselsel2;mvaNOMC$i" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "$dist2" -m "$limits2" --numonly $usebool $notext; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "NOMMC" --datatrigger "NOM" --sample "$samples" -p "$preselsel2" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "$dist2" -m "$limits2" --numonly $usebool $notext
	fi	
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF DISTMAPS - mqq2-dEtaqq2
	for i in `seq 0 3`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "VBF" --datatrigger "VBF" --sample "$samples" -p "$preselsel3;mvaVBFC$i" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "$dist3" -m "$limits3" --numonly $usebool $notext; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "VBF" --datatrigger "VBF" --sample "$samples" -p "$preselsel3" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "$dist3" -m "$limits3" --numonly $usebool $notext
	
	# VBF DISTMAPS - mqq2-dEtaqq2 - EXCLUSIVE
	for i in `seq 0 3`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "VBF" --datatrigger "VBF" --sample "$samples" -p "$preselsel4;mvaVBFC$i" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "$dist4" -m "$limits4" --numonly $usebool $notext; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "$globalpath" -t "VBF" --datatrigger "VBF" --sample "$samples" -p "$preselsel4" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "$dist4" -m "$limits4" --numonly $usebool $notext
	fi
fi
notext=""
done

##################################################
if [ "$1" == "" ] || [ "$1" == "3" ];then
	if [ "$2" == "" ] || [ "$2" == "1" ]; then
	# NOM SCALEFACTORS - jetBtag00-jetBtag10
	./mkTriggerUncertainties.py -o $output1 --ftwodmaps $maps1 --fdistmaps $dist1 -s "$groups" -b -1.0,0.0,0.25,0.70,0.88,1.001 --noleg
	./mkTriggerUncertainties.py -o $output1 --ftwodmaps $maps1 --fdistmaps $dist1 -s "$groups" -b -1.0,0.0,0.25,0.70,0.88,1.001
	
	# NOM SCALEFACTORS - jetBtag00-mqq1
	./mkTriggerUncertainties.py -o $output2 --ftwodmaps $maps2 --fdistmaps $dist2 -s "$groups" -b -1.0,0.0,0.25,0.70,0.88,1.001 --noleg
	./mkTriggerUncertainties.py -o $output2 --ftwodmaps $maps2 --fdistmaps $dist2 -s "$groups" -b -1.0,0.0,0.25,0.70,0.88,1.001
	fi
	if [ "$2" == "" ] || [ "$2" == "2" ]; then
	# VBF SCALEFACTORS - mqq2-dEtaqq2 
	./mkTriggerUncertainties.py -o $output3 --ftwodmaps $maps3 --fdistmaps $dist3 -s "$groups" -b -1.0,0.0,0.3,0.65,1.001 --noleg
	./mkTriggerUncertainties.py -o $output3 --ftwodmaps $maps3 --fdistmaps $dist3 -s "$groups" -b -1.0,0.0,0.3,0.65,1.001
	
	# VBF SCALEFACTORS - mqq2-dEtaqq2 - EXCLUSIVE
	./mkTriggerUncertainties.py -o $output4 --ftwodmaps $maps4 --fdistmaps $dist4 -s "$groups" -b -1.0,0.0,0.3,0.65,1.001 --noleg
	./mkTriggerUncertainties.py -o $output4 --ftwodmaps $maps4 --fdistmaps $dist4 -s "$groups" -b -1.0,0.0,0.3,0.65,1.001
	fi
fi

##################################################
# turning on/off legends
if [ "$3" == "0" ]; then 
	notext="--notext"
else
	notext=""
fi
for i in `seq 0 1`; do
	if [ "$notext" == "" ] && [ "$i" == "0" ]; then continue; fi
if [ "$1" == "" ] || [ "$1" == "4" ];then
	# NOM SCALEFACTOR OVERLAYS - jetBtag00-jetBtag10 and jetBtag00-mqq1
	./mkOverlay.py -o $overlay1 --files "$output1,$output2" --tags "2DMap bjet0-bjet1,2DMap bjet0-mqq1" $notext

	# VBF SCALEFACTOR OVERLAYS - inclusive/exclusive
	./mkOverlay.py -o $overlay2 --files "$output3,$output4" --tags "inclusive selection,exclusive selection" $notext
fi

notext=""
done
