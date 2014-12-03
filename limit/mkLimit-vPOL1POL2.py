#!/bin/sh

####################################################################################################
getDatacard() {
	datacard="datacards/datacard_m${1}_${2}.txt"
	echo $datacard
}
####################################################################################################
getLogName() {
	name="";
	for i in $@; do
		name=${name}_${i}
	done
	name=${name:1:$((${#name}-1))}.log
	echo $name
}

####################################################################################################
parseThis() {
	bool1=$1
	
	shift
	declare -a arrayArg=("$@")

	if [ "$bool1" == "true" ]; then
		for c in ${arrayArg[@]}; do
			echo -e "\t${c}";
			eval ${c};
		done
		echo
	fi	
}

####################################################################################################
export OLDIFS=$IFS
export IFS=$'\n'
tabs 4

titles=(\
"Generate Asimov Toy mH=125" \
"Do MLFit mH=115-135" \
"Get Significance Exp/Obs" \
"Get Limits Exp/Obs" \
"Get Limits Inj (uses Toy)" \
"Get Limits Exp/Obs excluding CATs" \
"Plot Limits (Exp/Obs/Inj, CATs)" \
"Plot Fits mH=115-135" \
"Get Nuissances mH=115-135 " \
"Plot Nuissances mH=115-135 " \
"Get ChannelCompatibility mH=115-135" \
"Plot ChannelCompatibility mH=115-135" \
)
run=()
for i in ${titles[@]}; do run=(${run[@]} false); done

if [ ${#@} -eq 0 ]; then
	counter=0
	answer=""
	for i in `seq 0 $((${#titles[@]}+1))`; do
		if [ "$answer" == "y" ]; then 
			run[$(($i-1))]=true; 
			answer="";
		elif [ "$answer" == "n" ]; then 
			run[$(($i-1))]=false;
			answer="";
		fi
		if [ $i -eq $((${#titles[@]})) ]; then break; fi;
		title=${titles[$i]};
		echo -ne "Run $title [y/n]? ";
		read answer;
	done
elif [ "$1" == "-h" ]; then
	tc=0
	for t in ${titles[@]}; do
		tc=$(($tc+1))
		block=`ps x`
		for l in ${block[@]}; do 
			lp=${l// /_}
			if [[ "$lp" == *./mkLimit.sh_${tc} ]]; then 
				echo -ne $red; 
				break;
			fi
		done
		echo -e $tc") "$t
		echo -ne $plain
	done
	echo
	exit
else
	for a in $@; do
		run[$(($a-1))]=true
	done
fi

red="\033[1;31m"
blue="\033[1;34m"
cyan="\033[1;36m"
plain="\033[m"

name="BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2"
nameU="_vbfhbb_${name}"
nameN="vbfhbb_${name}"

folder="BiasV10_limit_BRN5p4_dX0p1_B80-200_CAT0-6/output/"
home=`pwd`

declare -a masses=("125" "115" "135" "120" "130")
#declare -a masses=("125")

cd $folder

##################################################
dirs=("plots" "logs" "limitplots" "combine")
for d in ${dirs[@]}; do
	[ ! -d $d ] && mkdir $d;
done

##################################################
mass="125"
datacard=`getDatacard ${mass} ${name}`

##################################################
# CMD 0
cmd0a="combine -M GenerateOnly -m ${mass} -t -1 --saveToys --expectSignal=1 -n ${nameU} ${datacard} 2>&1 | tee `getLogName ${nameN} "ToysAsimov" ${mass}`"
cmd0b="mv higgsCombine${nameU}.GenerateOnly.mH${mass}.*.root combine/"
cmd0c="mv `getLogName ${nameN} "ToysAsimov" ${mass}` logs/"
cmd0=($cmd0a $cmd0b $cmd0c)
#cmd0[0]=$cmd0a
#cmd0[1]=$cmd0b
#cmd0[2]=$cmd0c
parseThis ${run[0]} ${cmd0[@]}

##################################################
# CMD 1
for mass in ${masses[@]}; do 
   datacard=`getDatacard ${mass} ${name}`
	#old#cmd1a="combine -M MaxLikelihoodFit -v 2 --saveNormalizations --plots --stepSize=0.05 --preFitValue=1.5 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.005 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=1 --minimizerTolerance=0.001 --cminFallbackAlgo Minuit,0.001 --rMin=-60 --rMax=60 ${datacard} -n ${nameU}.mH${mass} -m ${mass} 2>&1 | tee `getLogName ${nameN}".mH"${mass} "MLFit" ${mass}`"
	#fail#cmd1a="combine -M MaxLikelihoodFit -v 2 --saveNormalizations --plots --stepSize=0.05 --preFitValue=1.5 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=1 --cminFallbackAlgo Minuit,0.001 --rMin=-4 --rMax=8 ${datacard} -n ${nameU}.mH${mass} -m ${mass} 2>&1 | tee `getLogName ${nameN}".mH"${mass} "MLFit" ${mass}`"
	#other#cmd1a="combine -M MaxLikelihoodFit -v 2 --saveNormalizations --plots --stepSize=0.05 --preFitValue=2.0 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.001 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=1 --minimizerTolerance=0.001 --cminFallbackAlgo Minuit,0.001 --rMin=-4 --rMax=8 ${datacard} -n ${nameU}.mH${mass} -m ${mass} 2>&1 | tee `getLogName ${nameN}".mH"${mass} "MLFit" ${mass}`"
	#125#cmd1a="combine -M MaxLikelihoodFit -v 2 --saveNormalizations --plots --stepSize=0.05 --preFitValue=1.0 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.01 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=1 --minimizerTolerance=0.01 --cminFallbackAlgo Minuit,0.001 --rMin=-4 --rMax=8 ${datacard} -n ${nameU}.mH${mass} -m ${mass} 2>&1 | tee `getLogName ${nameN}".mH"${mass} "MLFit" ${mass}`"
	cmd1b="mv higgsCombine${nameU}.mH${mass}.MaxLikelihoodFit.mH${mass}.root combine/"
	cmd1c="mv mlfit*${nameU}*mH${mass}* combine/"
	cmd1d="mv *.png plots/"
	cmd1e="mv `getLogName ${nameN}".mH"${mass} "MLFit" ${mass}` logs/"
	cmd1=($cmd1a $cmd1b $cmd1c $cmd1d $cmd1e)
	parseThis ${run[1]} ${cmd1[@]}
done

##################################################
# CMD 2 & 3
#mass="125"
for mass in ${masses[@]}; do 
   datacard=`getDatacard ${mass} ${name}`
	cmd2a="combine -M ProfileLikelihood --significance ${datacard} -m ${mass} -t -1 --expectSignal=1 --toysFreq 2>&1 | tee `getLogName ${nameN} "SignifExp" ${mass}`"
	cmd2b="mv `getLogName ${nameN} "SignifExp" ${mass}` logs/"
	cmd2=($cmd2a $cmd2b)
	parseThis ${run[2]} ${cmd2[@]}
	cmd3a="combine -M ProfileLikelihood --significance ${datacard} -m ${mass} --bruteForce --preFit 2>&1 | tee `getLogName ${nameN} "SignifObs" ${mass}`"
	cmd3b="mv `getLogName ${nameN} "SignifObs" ${mass}` logs/"
	cmd3=($cmd3a $cmd3b)
	parseThis ${run[2]} ${cmd3[@]}
done

##################################################
for mass in ${masses[@]}; do 
   datacard=`getDatacard ${mass} ${name}`
	
	##################################################
	# CMD 4
	cmd4a="combine -M Asymptotic -m ${mass} -n ${nameU} $datacard 2>&1 | tee `getLogName ${nameN} "CombineExpObs" ${mass}`"
	cmd4b="mv higgsCombine${nameU}.Asymptotic.mH${mass}* combine/"
	cmd4c="mv `getLogName ${nameN} "CombineExpObs" ${mass}` logs/"
	cmd4=($cmd4a $cmd4b $cmd4c)
	parseThis ${run[3]} ${cmd4[@]}
		
	##################################################
	# CMD 5
	cmd5a="combine -M Asymptotic -m ${mass} -n ${nameU}_Inj125 $datacard --toysFile combine/higgsCombine${nameU}.GenerateOnly.mH125.123456.root -t -1 --expectSignal=1 2>&1 | tee `getLogName ${nameN} "CombineInj125" ${mass}`"
	cmd5b="mv higgsCombine${nameU}_Inj125.Asymptotic.mH${mass}* combine/"
	cmd5c="mv `getLogName ${nameN} "CombineInj125" ${mass}` logs/"
	cmd5=($cmd5a $cmd5b $cmd5c)
	parseThis ${run[4]} ${cmd5[@]}
done

##################################################
CATvetos=("456" "0123" "1" "2" "3" "5" "6")
for CATveto in ${CATvetos[@]}; do
	for mass in ${masses[@]}; do 
		datacard=`getDatacard $mass ${name/CAT6/CAT6_CATveto${CATveto}}`	
		##################################################
		# CMD 6 
		if [ ${run[5]} == true ]; then
			cmd6a="combine -M Asymptotic -m ${mass} -n ${nameU}_CATveto${CATveto} $datacard 2>&1 | tee `getLogName ${nameN}_CATveto${CATveto} "CombineExpObs" ${mass}`"
			cmd6b="mv higgsCombine${nameU}_CATveto${CATveto}.Asymptotic.mH${mass}* combine/"
			cmd6c="mv `getLogName ${nameN}_CATveto${CATveto} "CombineExpObs" ${mass}` logs/"
			cmd6=($cmd6a $cmd6b $cmd6c)
		fi
		parseThis ${run[5]} ${cmd6[@]}
	done	
done

##################################################
if [ ${run[6]} == true ]; then
	if [ `ls combine/higgsCombine*CAT0-CAT6*Asymptotic*root | grep -v CATveto | grep CAT0-CAT6 | wc -l` -lt 1 ]; then echo "Not enough files present. Exiting.";  
	else
		cmd7a="${home}/plotLimit.py -t ${nameU} `ls -m combine/higgsCombine*CAT0-CAT6*Asymptotic*root | grep -v CATveto | grep CAT0-CAT6 | tr -d '\n' | sed "s#,# #g"` 2>&1 | tee `getLogName ${nameN} "limitplots"`";
		cmd7b="mv limit*{png,pdf} limitplots/";
		cmd7c="mv `getLogName ${nameN} "limitplots"` logs/";
		cmd7=($cmd7a $cmd7b $cmd7c)
	fi
fi
parseThis ${run[6]} ${cmd7[@]};
CATvetos=("456" "0123" "1" "2" "3" "5" "6")
for CATveto in ${CATvetos[@]}; do
	if [ "$CATveto" != "" ]; then 
		if [ ${run[6]} == true ]; then
			if [ `ls combine/higgsCombine*CATveto${CATveto}*Asymptotic*root 2> /dev/null | wc -l` -lt 1 ]; then echo -e "CATveto${CATveto}: Not enough files present. Exiting."; continue; fi 
			cmd7a="${home}/plotLimit.py -t ${nameU}_CATveto${CATveto} combine/higgsCombine*CATveto${CATveto}*Asymptotic*root 2>&1 | tee `getLogName ${nameN}"_CATveto"$CATveto "limitplots"`";
			cmd7b="mv limit*{png,pdf} limitplots/";
			cmd7c="mv `getLogName ${nameN}"_CATveto"${CATveto} "limitplots"` logs/";
			cmd7=($cmd7a $cmd7b $cmd7c)
		fi
		parseThis ${run[6]} ${cmd7[@]};
	fi
done

##################################################
for mass in ${masses[@]}; do 
	if [ -f "combine/mlfit${nameU}.mH${mass}.root" ]; then 
		if [ ${run[7]} == true ]; then
			cmd8a="root -l ${home}/DrawBestFit.C'(2.5,false,\"$mass\")' -q 2>&1 | tee `getLogName ${nameN} "fitplots"`";
			cmd8b="mv `getLogName ${nameN} "fitplots"` logs/";
			cmd8=($cmd8a $cmd8b)
		fi
		parseThis ${run[7]} ${cmd8[@]};
	fi
done

##################################################
for mass in ${masses[@]}; do 
	if [ -f "combine/mlfit${nameU}.mH${mass}.root" ]; then 
		if [ ${run[8]} == true ]; then
			cmd9a="${home}/diffNuisances.py -a -f text combine/mlfit${nameU}.mH${mass}.root -g pulls${nameU}_mH${mass}.root > nuissances${nameU}.mH${mass}.txt 2> `getLogName ${nameN} "GetNuissances" ${mass}`"
			cmd9b="${home}/diffNuisances.py -a -f latex combine/mlfit${nameU}.mH${mass}.root > nuissances${nameU}.mH${mass}.tex 2>> `getLogName ${nameN} "GetNuissances" ${mass}`"
			cmd9c="mv pulls${nameU}*${mass}*.root combine/";
			cmd9d="mv nuissances${nameU}*${mass}*{tex,txt} combine/";
			cmd9e="mv `getLogName ${nameN} "GetNuissances" ${mass}` logs/";
			cmd9=($cmd9a $cmd9b $cmd9c $cmd9d ${cmd9e})
		fi
		parseThis ${run[8]} ${cmd9[@]};
		if [ ${run[9]} == true ]; then
			cmd10e="${home}/DrawNuissances.py ${nameU} ${mass} 2>&1 | tee `getLogName ${nameN} "PlotNuissances" ${mass}`"
			cmd10f="mv `getLogName ${nameN} "PlotNuissances" ${mass}` logs/";
			cmd10=($cmd10e $cmd10f)
		fi
		parseThis ${run[9]} ${cmd10[@]};
	fi
done

##################################################
for mass in ${masses[@]}; do 
	if [ ${run[10]} == true ]; then
		datacard=`getDatacard $mass ${name}`	
		cmd11a="combine -M ChannelCompatibilityCheck --saveFitResult --stepSize=0.05 --preFitValue=1.5 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.01 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=1 --minimizerTolerance=0.01 --cminFallbackAlgo Minuit,0.001 --rMin=-50 --rMax=50 ${datacard} -n ${nameU} -m ${mass} 2>&1 | tee `getLogName ${nameN} "GetChannelCompatibility" ${mass}`";
		cmd11b="mv higgsCombine*${nameU}*ChannelCompatibility*mH${mass}*root combine/";
		cmd11c="mv `getLogName ${nameN} "GetChannelCompatibility" ${mass}` logs/";
		cmd11=($cmd11a $cmd11b $cmd11c)
		echo "tst"
	fi
	parseThis ${run[10]} ${cmd11[@]};
	if [ ${run[11]} == true ]; then
		cmd12a="root -l ${home}/DrawChannelCompatibility.C'(${mass})' -q 2>&1 | tee `getLogName ${nameN} "PlotChannelCompatibility" ${mass}`";
		cmd12b="mv channelComp_mH${mass}{,_2}.{pdf,png} plots/";
		cmd12c="mv `getLogName ${nameN} "PlotChannelCompatibility" ${mass}` logs/";
		cmd12=($cmd12a $cmd12b $cmd12c)
	fi
	parseThis ${run[11]} ${cmd12[@]};
done

##################################################

cd ../../

echo
echo -e $red"Done."$plain
export IFS=$OLDIFS
