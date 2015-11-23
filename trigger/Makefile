SHELL := /bin/sh

all: 

www:
	rsync -avz --progress --exclude '*.pdf' --include '*/*/*' --include '*/*/*/*' --include '*.png' plots/* ~/www/vbfHbb/trigger/
	find ~/www/vbfHbb/trigger/ -type f -not -name *noleg.png -exec rm {} \;
	find ~/www/vbfHbb/trigger/ -type d -exec cp ~/www/vbfHbb/index.php {} \;

plotcopy:
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon-QCD/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/QCD/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon-QCD/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/QCD/*Rat*noleg*pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
	if [ ! -d /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOM ];then mkdir /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOM; fi
	if [ ! -d /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOMbias ];then mkdir /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOMbias; fi
	if [ ! -d /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBF ];then mkdir /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBF; fi
	if [ ! -d /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBFbias ];then mkdir /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBFbias; fi
	rsync -avz --progress plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/*noleg.pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBF/
	rsync -avz --progress plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/*noleg.pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOM/
	rsync -avz --progress plots/trigger_Nmin1_NOM_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/*noleg.pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/NOMbias/
	rsync -avz --progress plots/trigger_Nmin1_VBF_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/*noleg.pdf /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/VBFbias/



