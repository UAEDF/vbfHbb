#!/bin/sh

if [ "$1" == "0" ]; then 
	prefix='echo';
else
	prefix='';
fi

binstrigger="--binning mvaNOM;10;-1;1,mbbReg1;15;0;300,jetBtag00;20;0;1,jetBtag10;20;0;1,jetPt0;20;0;400,jetPt1;15;0;300,jetPt2;8;0;160,jetPt3;6;0;120,dEtaqq1;14;2;9,mqq1;20;0;2000,dPhibb1;10;0;2"
binscomparison="--binning mvaNOM;40;-1;1,mbbReg1;60;0;300,jetBtag00;50;0;1,jetBtag10;50;0;1,jetPt0;80;0;400,jetPt1;60;0;300,jetPt2;24;0;160,jetPt3;24;0;120,dEtaqq1;56;2;9,mqq1;80;0;2000,dPhibb1;40;0;2"

#********************
#* TRIGGER BIAS NOM *
#********************
baseoptions="-d -S common/vbfHbb_samples_2013.json -V common/vbfHbb_variables_2013.json -C common/vbfHbb_cuts.json -I common/vbfHbb_info_2013.json -G /data/UAData/autumn2013 --fileformat 2"
trigger="-t NOMMC --datatrigger NOMMC -r AV80"
selection="-p jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;mqq1_gt250;dEtaqq1_gt2p5;Btag0_LL"
weight="-w 19800.,XSEC;LUMI;PU#3"
samples="-s JetMon,QCD"
variables="-v mqq1,mbbReg1,dEtaqq1,mvaNOM,jetBtag00,jetBtag10,jetPt0,jetPt1,jetPt2,jetPt3,dPhibb1"
outfile="-o trigger/rootfiles/trigger_Nmin1_NOM_bias.root"
execute="--drawstack --closure --shade"

if [ "$1" == "1" || "$1" == "0" ]; then
	$prefix ./trigger/mkTurnonCurves.py $baseoptions $binstrigger $trigger $selection $weight $samples $variables $outfile $execute
fi

$prefix

#********************
#* TRIGGER MAPS NOM *
#********************
outfile="-o trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root"
mapstring="-m jetBtag00;0.0#0.244#0.679#0.898#1.001,jetBtag10;0.0#0.244#0.679#0.898#1.001"
if [ "$1" == "2" || "$1" == "0" ]; then
	$prefix ./common/main.py $baseoptions $trigger $selection $weight $samples $outfile $mapstring
fi

outfile="-o trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root"
mapstring="-m jetBtag00;0.0#0.244#0.679#0.898#1.001,mqq1;0#250#450#700#1200#2000"
if [ "$1" == "2" || "$1" == "0" ]; then
	$prefix ./common/main.py $baseoptions $trigger $selection $weight $samples $outfile $mapstring
fi

$prefix

#***********************
#* TRIGGER CLOSURE NOM *
#***********************
execute="--drawstack --overlay --shade"

outfile="-o trigger/rootfiles/trigger_Nmin1_NOM_closure.root"
weight="-w 19800.,XSEC;LUMI;PU#3;MAP#jetBtag[b1[0]]#jetBtag[b2[0]],,trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq0_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
if [ "$1" == "3" || "$1" == "0" ]; then
	$prefix ./trigger/mkTurnonCurves.py $baseoptions $binstrigger $trigger $selection $weight $samples $variables $outfile $execute
fi

outfile="-o trigger/rootfiles/trigger_Nmin1_NOM_closure.root"
weight="-w 19800.,XSEC;LUMI;PU#3;MAP#jetBtag[b1[0]]#mqq[1],,trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq0_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
if [ "$1" == "4" || "$1" == "0" ]; then
	$prefix ./trigger/mkTurnonCurves.py $baseoptions $binstrigger $trigger $selection $weight $samples $variables $outfile $execute
fi

$prefix

######################################################################################################################################################
#***************
#* data/mc NOM *
#***************
trigger="-t NOMMC --datatrigger NOM -r NOM"
selection="-p jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;mqq1_gt250;dEtaqq1_gt2p5;Btag0_LL;nLeptons;dPhibb_lt2"
outfile="-o plots/rootfiles/control_NOM.root"
execute="--drawstack"

weight="-w 19800.,XSEC;LUMI;PU#0;KFAC"
if [ "$1" == "5" || "$1" == "0" ]; then
	$prefix ./plots/mkPlots.py $baseoptions $binscomparison $trigger $trigger $selection $weight $samples $variables $outfile $execute 
fi

weight="-w 19800.,XSEC;LUMI;PU#0;KFAC;MAP#jetBtag[b1[0]]#jetBtag[b2[0]],,trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq0_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
if [ "$1" == "6" || "$1" == "0" ]; then
	$prefix ./plots/mkPlots.py $baseoptions $binscomparison $trigger $trigger $selection $weight $samples $variables $outfile $execute 
fi

weight="-w 19800.,XSEC;LUMI;PU#0;KFAC;MAP#jetBtag[b1[0]]#mqq[1],,trigger/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq0_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
if [ "$1" == "7" || "$1" == "0" ]; then
	$prefix ./plots/mkPlots.py $baseoptions $binscomparison $trigger $trigger $selection $weight $samples $variables $outfile $execute 
fi

######################################################################################################################################################

