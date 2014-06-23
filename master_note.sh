#!/bin/sh

if [ "$1" == "" ]; then prefix="/afs/cern.ch/user/s/salderwe/fornote/"
else prefix=$1;
fi
[ ! -d $prefix ] && mkdir ${prefix};
echo "Copying to $prefix..."

echo "2D maps..."
plots=( \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon/2DMap_JetMon-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/QCD/2DMap_QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1_noleg.pdf' \

'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon/2DMap_JetMon-Rat_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/QCD/2DMap_QCD-Rat_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270-tVBF-rAV80-dVBF_mqq2-dEtaqq2_noleg.pdf' \
)

for i in ${plots[@]}; do
	j=${prefix}${i//\/afs\/cern.ch\/work\/s\/salderwe\/private\/2014\/vbfHbb\/common\/..\/trigger\/plots\//}
	map0=${j/\/$(basename $j)/}
	map1=${map0/\/$(basename $map0)/}
	map2=${map1/\/$(basename $map1)/}
	map3=${map2/\/$(basename $map2)/}
	for d in $map3 $map2 $map1 $map0; do
		[ ! -d $d ] && mkdir $d;
	done
	cp $i $j 
done

echo "Scale factors..."
plots=( \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_VBF_all/TriggerUncertainty/ScaleFactors1D_GF_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_VBF_all/TriggerUncertainty/ScaleFactors1D_ZJets_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_VBF_all/TriggerUncertainty/ScaleFactors1D_QCD_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_VBF_all/TriggerUncertainty/ScaleFactors1D_Tall_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_VBF_all/TriggerUncertainty/ScaleFactors1D_VBF125_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1/TriggerUncertainty/ScaleFactors1D_GF_noleg.pdf'
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1/TriggerUncertainty/ScaleFactors1D_QCD_noleg.pdf'
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1/TriggerUncertainty/ScaleFactors1D_Tall_noleg.pdf'
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1/TriggerUncertainty/ScaleFactors1D_VBF125_noleg.pdf'
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1/TriggerUncertainty/ScaleFactors1D_ZJets_noleg.pdf'
)

for i in ${plots[@]}; do
	j=${prefix}${i//\/afs\/cern.ch\/work\/s\/salderwe\/private\/2014\/vbfHbb\/common\/..\/trigger\/plots\//}
	map0=${j/\/$(basename $j)/}
	map1=${map0/\/$(basename $map0)/}
	map2=${map1/\/$(basename $map1)/}
	for d in $map2 $map1 $map0; do
		[ ! -d $d ] && mkdir $d;
	done
	cp $i $j
done

echo "Nmin1 bias..."
plots=( \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_mbbReg1-B15-0-300_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_mbbReg2-B15-0-300_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
)

for i in ${plots[@]}; do
	j=${prefix}${i//\/afs\/cern.ch\/work\/s\/salderwe\/private\/2014\/vbfHbb\/common\/..\/trigger\/plots\//}
	map0=${j/\/$(basename $j)/}
	map1=${map0/\/$(basename $map0)/}
	map2=${map1/\/$(basename $map1)/}
	map3=${map2/\/$(basename $map2)/}
	map4=${map3/\/$(basename $map3)/}
	for d in $map4 $map3 $map2 $map1 $map0; do
		[ ! -d $d ] && mkdir $d;
	done
	cp $i $j
done

echo "Nmin1 closure..."
plots=( \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_dEtaqq1-B14-2-9_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_dPhibb1-B10-0-2_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetBtag00-B20-0-1_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetBtag10-B20-0-1_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetPt0-B20-0-400_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetPt1-B15-0-300_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetPt2-B8-0-160_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_jetPt3-B6-0-120_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_mbbReg1-B15-0-300_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_mqq1-B20-0-2000_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/t_mvaNOM-B10--1-1_global_global_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC_dNOMMC_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_dEtaqq2-B35-2-9_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_dEtaTrig-B35-2-9_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_dPhibb2-B10-0-2_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetBtag00-B20-0-1_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetBtag10-B20-0-1_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetPt0-B20-0-400_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetPt1-B15-0-300_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetPt2-B8-0-160_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_jetPt3-B6-0-120_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_mbbReg2-B15-0-300_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_mjjTrig-B20-0-2000_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_mqq2-B20-0-2000_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_mvaVBF-B10--1-1_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
'/afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/../trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/t_ptAve-B20-0-400_global_global_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF_dVBF_rAV80_noleg.pdf' \
)

for i in ${plots[@]}; do
	j=${prefix}${i//\/afs\/cern.ch\/work\/s\/salderwe\/private\/2014\/vbfHbb\/common\/..\/trigger\/plots\//}
	map0=${j/\/$(basename $j)/}
	map1=${map0/\/$(basename $map0)/}
	map2=${map1/\/$(basename $map1)/}
	map3=${map2/\/$(basename $map2)/}
	map4=${map3/\/$(basename $map3)/}
	for d in $map4 $map3 $map2 $map1 $map0; do
		[ ! -d $d ] && mkdir $d;
	done
	cp $i $j
done

echo "Nmin1 closure..."


