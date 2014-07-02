#!/bin/sh

if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="/data/UAdata/"
fi
samples="VBF125"
samplesGF="GluGlu-Powheg125"
groups="VBF125" #sample

#limits1=
#limits2=

preselNone="None"
preselNOMeta1="jetUnsPt0_gt80;jetUnsPt1_gt70;jetUnsPt2_gt50;jetUnsPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
preselNOMeta2="jetUnsPt0_gt80;jetUnsPt1_gt70;jetUnsPt2_gt50;jetUnsPt3_gt40;dEtaqq1_gt3p5;mqq1_gt250;Btag0_LL"
preselNOM="jetPt0_gt80;jetPt1_gt70;jetPt2_gt50;jetPt3_gt40;dEtaqq1_gt2p5;mqq1_gt250;Btag0_LL"
preselVBF="jetPt3_gt30;jetPtAve_gt80;dEtaqq2_gt3p5;mqq2_gt700;dEtaTrig_gt3p5;mjjTrig_gt700"
preselselNone="${preselNone}"
preselselNOM="${preselNOM};nLeptons;dPhibb1_lt2"
preselselNOMeta1="${preselNOMeta1};nLeptons;dPhibb1_lt2"
preselselNOMeta2="${preselNOMeta2};nLeptons;dPhibb1_lt2"
preselselVBF="${preselVBF};nLeptons;dPhibb2_lt2"
preselselVBFveto="${preselVBF};nLeptons;dPhibb2_lt2;Btag0_ML;NOMveto"

lumiNOM="19800."
lumiVBF="18300."
weightNone="XSEC;LUMI;PU#0"
weightNOM="XSEC;LUMI;PU#0;TNOM"
weightVBF="XSEC;LUMI;PU#0;TVBF"

varsNOM="mbb1,jetPt0,jetPt1,jetPt2,jetPt3,mvaNOM,jetUnsPt0,jetUnsPt1,jetUnsPt2,jetUnsPt3,dEtaqq1"
varsVBF="mbb2,jetPt0,jetPt1,jetPt2,jetPt3,mvaVBF,jetUnsPt0,jetUnsPt1,jetUnsPt2,jetUnsPt3,dEtaqq2"

bins="mbb1;75;50;200,jetPt0;40;0;400,jetPt1;40;0;350,jetPt2;40;0;300,jetPt3;40;0;250,mbb2;75;50;200,jetUnsPt0;40;0;400,jetUnsPt1;40;0;350,jetUnsPt2;40;0;300,jetUnsPt3;40;0;250,dEtaqq1;24;0;6,dEtaqq2;24;0;6"

jsonvar="../common/vbfHbb_variables_2013_bare.json"
output1="rootfiles/vbfHbb_uncertainties_PDF.root"

# NOM + VBF ### VBF ##############################
if [ "$1" == "" ] || [ "$1" == "1" ]; then
	./mkUncPDF.py -D "../common/vbfHbb_defaultOpts_2013.json" -G "$globalpath" -o "$output1" -s "$samples" -p "$preselselNOM" -t "NOMMC" --weight "${lumiNOM},${weightNOM}" -v "$varsNOM" --binning "$bins"
fi
if [ "$1" == "" ] || [ "$1" == "2" ]; then
	./mkUncPDF.py -D "../common/vbfHbb_defaultOpts_2013.json" -G "$globalpath" -o "$output1" -s "$samples" -p "$preselselVBF" -t "VBF" --weight "${lumiVBF},${weightVBF}" -v "$varsVBF" --binning "$bins"
fi

