#!/bin/sh

if [ "$(basename `pwd`)" == "fit_v2" ]; then 
	basepath="."
else 
	basepath="fit_v2"
fi

defaultopts="$basepath/../common/vbfHbb_defaultOpts_2013.json"
if [[ "`uname -a`" == *lxplus* ]]; then
	globalpath="~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/"
elif [[ "`uname -a`" == *schrodinger* ]]; then
	globalpath="$basepath/../largefiles/"
fi

if [ ${#@} -gt 1 ]; then
	workdir=$2
else
	workdir=case0
fi

###   OPTIONS
###   
options="\n
   ./mkAll.sh RUNOPT WORKDIR\n\n
   RUNOPTS:\n
   0	all\n
   1	mkTransferFunctions\n
   2	mkBkgTemplates\n
   3	mkSigTemplatesExtrapolate\n
   4	mkDataTemplates\n
   5	mkDatacardsExtrapolate\n
"
###
###

notext=""
## turning on/off legends
#if [ "$3" == "0" ]; then 
#	notext="--notext"
#else
#	notext=""
#fi

# OPTION OPTION OPTIONS ##########################
TF=POL1,POL2
#TF=AltPOL1,AltPOL2
massextra=100,105,110,140,145,150
massall=100,105,110,115,120,125,130,135,140,145,150

##################################################


if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
	echo -e $options
fi

##################################################
#for i in `seq 0 1`; do
#	if [ "$notext" == "" ] && [ "$i" == "0" ]; then continue; fi
##################################################
if [ "$1" == "0" ] || [ "$1" == "1" ];then
	cmd="./src/mkTransferFunctions.py --workdir ${workdir} --long --TF ${TF}"
	echo ${cmd}
	eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$"
fi
##################################################
if [ "$1" == "0" ] || [ "$1" == "2" ];then
	cmd="./src/mkBkgTemplates.py --workdir ${workdir} --long"
	echo ${cmd}
	eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$" | grep -v "setting parameter"
fi
##################################################
if [ "$1" == "0" ] || [ "$1" == "3" ];then
	cmd="./src/mkSigTemplatesExtrapolate.py --workdir ${workdir} --long --massextra ${massextra}"
	echo ${cmd}
	eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$"
fi
##################################################
if [ "$1" == "0" ] || [ "$1" == "4" ];then
	cmd="./src/mkDataTemplates.py --workdir ${workdir} --long --TF ${TF}"
	echo ${cmd}
	eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$"
fi
##################################################
if [ "$1" == "0" ] || [ "$1" == "5" ];then
	cmd="./src/mkDatacardsExtrapolate.py --workdir ${workdir} --long --TF ${TF} --MASS ${massall}"
	echo ${cmd}
	eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$"
	for c in "1" "2" "3" "5" "6" "4,5,6" "0,1,2,3"; do
		cmd="./src/mkDatacardsExtrapolate.py --workdir ${workdir} --long --TF ${TF} --CATveto $c --MASS ${massall}"
		echo ${cmd}
		eval ${cmd} | grep -v "Developed by Wouter" | grep -v "Copyright (C)" | grep -v "All rights reserved" | grep -v "^$"
	done
fi

##################################################
#notext=""
#done
