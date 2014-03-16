#!/bin/sh

##################################################
if [ "$1" == "" ] || [ "$1" == "1" ];then
	# NOM MAPS - jetBtag00-jetBtag10
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOMMC" -s "JetMon,QCD" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL" -r "AV80" -w "19800.,PU#3;XSEC;LUMI" -o "rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001"
	
	# NOM MAPS - jetBtag00-mqq1
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOMMC" -s "JetMon,QCD" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL" -r "AV80" -w "19800.,PU#3;XSEC;LUMI" -o "rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000"
	
	# VBF MAPS - mqq2-dEtaqq2 
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -G "/data/UAData/autumn2013" -t "VBF" --datatrigger "VBF" -s "JetMon,QCD" -p "run194270;jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700" -r "AV80" -w "18300.,PU#3;XSEC;LUMI" -o "rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root" -m "mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0"
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "2" ];then
	# NOM DISTMAPS - jetBtag00-jetBtag10
	for i in `seq 0 3`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOM" --nosample "JetMon,Data" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2;mvaNOMC$i" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_NOM_jetBtag00-jetBtag10.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001" --numonly; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOM" --nosample "JetMon,Data" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_NOM_jetBtag00-jetBtag10.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001" --numonly
	
	# NOM DISTMAPS - jetBtag00-mqq
	for i in `seq 0 3`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOM" --nosample "JetMon,Data" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2;mvaNOMC$i" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_NOM_jetBtag00-mqq1.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000" --numonly; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "NOMMC" --datatrigger "NOM" --nosample "JetMon,Data" -p "jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL;nLeptons;dPhibb1_lt2" -r "None" -w "19800.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_NOM_jetBtag00-mqq1.root" -m "jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000" --numonly
	
	# VBF DISTMAPS - mqq2-dEtaqq2
	for i in `seq 0 2`; do echo $i; ./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "VBF" --datatrigger "VBF" --nosample "JetMon,Data" -p "dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;jetPt3_gt30;jetPtAve_gt80;Btag0_ML;nLeptons;dPhibb2_lt2;mvaNOMC$i" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_VBF_mqq2-dEtaqq2.root" -m "mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0" --numonly; done
	./../common/main.py -d -D "../common/vbfHbb_defaultOpts_2013.json" -I "../common/vbfHbb_info_2013_allTGrouped.json" -G "/data/UAData/autumn2013" -t "VBF" --datatrigger "VBF" --nosample "JetMon,Data" -p "dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700;jetPt3_gt30;jetPtAve_gt80;Btag0_ML;nLeptons;dPhibb2_lt2" -r "None" -w "18300.,PU#0;XSEC;LUMI" -o "rootfiles/trigger_DistMaps_VBF_mqq2-dEtaqq2.root" -m "mqq2;600#700#750#800#850#900#950#1000#1050#1100#1200#1400#1600#1800#2000#2500#3000,dEtaqq2;3.5#3.8#4.0#4.5#5.0#5.5#6.0#6.5#7.0#10.0" --numonly
fi

##################################################
if [ "$1" == "" ] || [ "$1" == "3" ];then
	# NOM SCALEFACTORS - jetBtag00-jetBtag10
	./mkTriggerUncertainties.py -o rootfiles/trigger_ScaleFactors_NOM_jetBtag00-jetBtag10.root --ftwodmaps rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root --fdistmaps rootfiles/trigger_DistMaps_NOM_jetBtag00-jetBtag10.root -s "VBF,QCD,Tall,WJets,ZJets,GF" -b 0.0,0.25,0.70,0.88,1.001
	
	# NOM SCALEFACTORS - jetBtag00-mqq1
	./mkTriggerUncertainties.py -o rootfiles/trigger_ScaleFactors_NOM_jetBtag00-mqq1.root --ftwodmaps rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root --fdistmaps rootfiles/trigger_DistMaps_NOM_jetBtag00-mqq1.root -s "VBF,QCD,Tall,WJets,ZJets,GF" -b 0.0,0.25,0.70,0.88,1.001
	
	# VBF SCALEFACTORS - mqq2-dEtaqq2 
	./mkTriggerUncertainties.py -o rootfiles/trigger_ScaleFactors_VBF_mqq2-dEtaqq2.root --ftwodmaps rootfiles/trigger_2DMaps_VBF_mqq2-dEtaqq2.root --fdistmaps rootfiles/trigger_DistMaps_VBF_mqq2-dEtaqq2.root -s "VBF,QCD,Tall,WJets,ZJets,GF" -b 0.0,0.3,0.65,1.001
fi
