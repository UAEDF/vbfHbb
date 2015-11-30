SHELL := /bin/sh
UNAME := $(shell uname -n)
DEST := 
ifeq ($(UNAME),heisenberg) 
	DEST := /data/Thesis/figures/ChapterTrigger/
endif
ifeq ($(UNAME),enterprise)
	DEST := /home/salderwe/BitBucket/thesis/figures/ChapterTrigger/
endif

all: 

maps:
	./mkTurnonCurves.sh 1 2 0
	./mkTurnonCurves.sh 1 3 0

curves:
	./mkTurnonCurves.sh 2 1 0
	./mkTurnonCurves.sh 2 2 0
	./mkTurnonCurves.sh 3 2 0
	./mkTurnonCurves.sh 3 3 0

www:
	rsync -avz --progress --exclude '*.pdf' --include '*/*/*' --include '*/*/*/*' --include '*.png' plots/* ~/www/vbfHbb/trigger/
	find ~/www/vbfHbb/trigger/ -type f -not -name *noleg.png -exec rm {} \;
	find ~/www/vbfHbb/trigger/ -type d -exec cp ~/www/vbfHbb/index.php {} \;

plotcopy:
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon/*Rat*noleg*pdf $(DEST)
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/JetMon-QCD/*Rat*noleg*pdf $(DEST)
	rsync -avz --progress plots/trigger_2DMaps_VBF_mqq2-dEtaqq2/2DMaps/QCD/*Rat*noleg*pdf $(DEST)
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon/*Rat*noleg*pdf $(DEST)
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/JetMon-QCD/*Rat*noleg*pdf $(DEST)
	rsync -avz --progress plots/trigger_2DMaps_NOM_jetBtag00-mqq1/2DMaps/QCD/*Rat*noleg*pdf $(DEST)
	if [ ! -d $(DEST)NOM ];then mkdir $(DEST)NOM; fi
	if [ ! -d $(DEST)NOMbias ];then mkdir $(DEST)NOMbias; fi
	if [ ! -d $(DEST)VBF ];then mkdir $(DEST)VBF; fi
	if [ ! -d $(DEST)VBFbias ];then mkdir $(DEST)VBFbias; fi
	rsync -avz --progress plots/trigger_Nmin1_VBF_mqq2-dEtaqq2/LUMI-MAP.mqq2.dEtaqq2-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/*noleg.pdf $(DEST)VBF/
	rsync -avz --progress plots/trigger_Nmin1_NOM_jetBtag00-mqq1/LUMI-MAP.jetBtagb10.mqq1-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/*noleg.pdf $(DEST)NOM/
	rsync -avz --progress plots/trigger_Nmin1_NOM_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250_tNOMMC/*noleg.pdf $(DEST)NOMbias/
	rsync -avz --progress plots/trigger_Nmin1_VBF_bias/LUMI-PU.3-XSEC/turnonCurves/global_global/sdEtaTrig_gt3p5-dEtaqq2_gt3p5-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-run194270_tVBF/*noleg.pdf $(DEST)VBFbias/



