#!/bin/sh

if [ "$1" == "all" ]; then
### TRIGGER
./trigger/mkTurnonCurves.sh 1				# MAPS
./trigger/mkTurnonCurves.sh 2 1			# bias NOM
./trigger/mkTurnonCurves.sh 2 2			# bias VBF
./trigger/mkTurnonCurves.sh 3 1			# NOM map1
./trigger/mkTurnonCurves.sh 3 2			# NOM map2
./trigger/mkTurnonCurves.sh 3 3			# VBF map3

### TRIGGER UNCERTAINTY
./trigger/mkTriggerUncertainty.sh 1		# MAPS 
./trigger/mkTriggerUncertainty.sh 2		# DISTMAPS
./trigger/mkTriggerUncertainty.sh 3		# SCALEFACTORS
./trigger/mkTriggerUncertainty.sh 4		# OVERLAYS

### PLOTS
./plots/mkHist.sh 1						# MAPS
./plots/mkHist.sh 2 1					# NOM
./plots/mkHist.sh 2 2					# NOM map1
./plots/mkHist.sh 2 3					# NOM map2
./plots/mkHist.sh 2 4					# VBF
./plots/mkHist.sh 2 5					# VBF map3
./plots/mkHist.sh 2 6					# VBF      NOMveto
./plots/mkHist.sh 2 7					# VBF map3 NOMveto

### JEx
./uncertainties/mkUncJEx.sh 			# NOM (1) & VBF (2)
#./uncertainties/mkUncJEx.sh 999     # other selections
fi

### WEBPAGE
if [ "$1" == "cpweb" ]; then
	indexphp="/afs/cern.ch/user/s/salderwe/www/vbfhbb/index.php"
	red="\033[0;31m"
	green="\033[0;32m"
	plain="\033[m"
# prepare
	basefolders=(\
	"/afs/cern.ch/user/s/salderwe/www/vbfhbb/trigger" \
	"/afs/cern.ch/user/s/salderwe/www/vbfhbb/plots" \
	"/afs/cern.ch/user/s/salderwe/www/vbfhbb/systematics" 
	)
	sources=(\
	"trigger/plots/trigger_Nmin1_NOM_bias" \
	"trigger/plots/trigger_Nmin1_VBF_bias" \
	"trigger/plots/trigger_Nmin1_NOM_jetBtag00-jetBtag10" \
	"trigger/plots/trigger_Nmin1_NOM_jetBtag00-mqq1" \
	"trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2" \
	"trigger/plots/trigger_2DMaps_NOM_jetBtag00-jetBtag10" \
	"trigger/plots/trigger_2DMaps_NOM_jetBtag00-mqq1" \
	"trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2" \
#	"plots/plots/control_NOM" \
#	"plots/plots/control_NOM_jetBtag00-jetBtag10" \
#	"plots/plots/control_NOM_jetBtag00-mqq1" \
#	"plots/plots/control_VBF" \
#	"plots/plots/control_VBF_mqq2-dEtaqq2" \
#	"plots/plots/control_VBF_mqq2-dEtaqq2_bins2" \
#	"plots/plots/control_VBF_mqq2-dEtaqq2_corrected" \
#	"plots/plots/control_VBF_NOMveto" \
#	"plots/plots/control_VBF_NOMveto_mqq2-dEtaqq2_bins2" \
#	"plots/plots/control_VBF_NOMvetoNoBtag" \
#	"plots/plots/control_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2" \
#	"plots/plots/control_VBF_NOMvetoSelNoBtag" \
#	"plots/plots/control_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2" \
	"trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-jetBtag10" \
	"trigger/plots/trigger_ScaleFactors_NOM_jetBtag00-mqq1" \
	"trigger/plots/trigger_ScaleFactors_VBF_mqq2-dEtaqq2" \
	"trigger/plots/trigger_ScaleFactors_NOM_all" \
	"trigger/plots/trigger_ScaleFactors_VBF_all" \
#	"trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_Nmin1_VBF_NOMveto_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_Nmin1_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_Nmin1_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2_LL" \
#	"trigger/plots/trigger_Nmin1_VBF_mqq2-dEtaqq2_corrected" \
#	"trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2_corrected" \
#	"trigger/plots/trigger_2DMaps_VBF_NOMveto_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_2DMaps_VBF_NOMvetoNoBtag_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_2DMaps_VBF_NOMvetoSelNoBtag_mqq2-dEtaqq2_bins2" \
#	"trigger/plots/trigger_2DMaps_VBF_mqq2-dEtaqq2_LL" \
	"uncertainties/plots/uncertainties/LUMI-PU.0-TNOM-XSEC_noleg" \
	"uncertainties/plots/uncertainties/LUMI-PU.0-TVBF-XSEC_noleg" \
	)
	folders=()
	for s in ${sources[@]}; do
		if [ ! -d $s ]; then 
			suffix="";
		elif [[ $s == *control* ]]; then
			path=`ls $s`;
			if [ ! "$path" == "" ]; then suffix="${s/plots\//}/$(basename `ls $s/`)"; fi
		elif [[ $s == *Nmin1* ]]; then 
			suffix=${s/plots\//};
			suffix=${suffix/trigger/trigger\/Nmin1};
		elif [[ $s == *2DMaps* ]]; then
			suffix=${s/plots\//};
			suffix=${suffix/trigger/trigger\/2DMaps};
		elif [[ $s == *ScaleFactors* ]]; then
			suffix=${s/plots\//};
			suffix=${suffix/trigger/trigger\/ScaleFactors};
		elif [[ $s == *uncertainties* ]]; then
			suffix=${s/plots\//};
			if [[ $s == *TNOM* ]]; then suffix=${suffix/uncertainties*/systematics\/JEx\/NOM};
			elif [[ $s == *TVBF* ]]; then suffix=${suffix/uncertainties*/systematics\/JEx\/VBF};
			else suffix=${suffix/uncertainties*/JEx\/other};
			fi
		else
			suffix="";
		fi
		folders=(${folders[@]} "/afs/cern.ch/user/s/salderwe/www/vbfhbb/$suffix")
	done
	
# start copying
	for f in ${basefolders[@]}; do 
		echo -e "${red}Cleaning${plain} $f";
		rm -rf $f;
		if [ ! -d $f ]; then mkdir $f; fi
		cp $indexphp $f/index.php
	done
	for i in `seq 0 $((${#folders[@]}-1))`; do
		s=${sources[$i]};
		f=${folders[$i]};
		echo -e "${green}Copying from${plain} $s ${green}to${plain} $f"
		if [ ! -d $f ]; then 
			map0=$f
			map1=${f/\/$(basename $f)/}
			map2=${map1/\/$(basename $map1)/}
			if [[ $f == *control* ]] || [[ $f == *Nmin1* ]] || [[ $f == *2DMaps* ]] || [[ $f == *ScaleFactors* ]] || [[ $f == *JEx* ]]; then 
				[ ! -d $map1 ] && mkdir $map1;
				cp $indexphp "$map1/index.php";
				[ ! -d $map0 ] && mkdir $map0;
				cp $indexphp "$map0/index.php";
			fi
		fi
		if [[ $f == *2DMaps* ]]; then
			source=$s/*/*/*.png;
		elif [[ $f == *ScaleFactors* ]]; then
			source=$s/*/ScaleFactors1D_*.png;
		elif [[ $f == *Nmin1* ]] || [[ $f == *control* ]]; then
		   source=$s/*/*/*/*/*.png;
		elif [[ $f == *JEx* ]]; then
			source=$s/*.png;
		else
			echo -e "${red}Empty:${plain} $s";
			continue;#break;	
		fi
		if [ "`ls $s`" == "" ]; then 
			echo -e "${red}Empty:${plain} $s";
			continue;#break; 
		fi
		[ ! -d $f/noleg ] && mkdir $f/noleg && cp $indexphp $f/noleg/;
		cp $source $f/;
		if [ ! "`ls $f/*noleg.png 2> /dev/null`" == "" ]; then mv $f/*noleg.png $f/noleg/; fi;
		tar -cjf $f/$(basename $f)_pdf.tar.bz2 ${source//png/pdf};
		tar -cjf $f/$(basename $f)_png.tar.bz2 ${source};
	done
fi
