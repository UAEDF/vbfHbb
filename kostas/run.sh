#!/bin/sh

if [ "$1" == "1" ] ; then
	BRN_ORDER_NOM=5;
	BRN_ORDER_VBF=4;
	dX=0.1;
	XMIN=80;
	XMAX=200;
	XMINTRANSFERNOM=80;
	XMAXTRANSFERNOM=300;
	XMINTRANSFERVBF=80;
	XMAXTRANSFERVBF=300;
	USETRANSFER=true;
	TRORDERNOM=1;
	TRORDERVBF=1;
	CATMIN=0;
	CATMAX=6;
	SUFFIX="" #"_WRONGVAR"
	FOLDER="limit_BRN"${BRN_ORDER_NOM}"+"${BRN_ORDER_VBF}"_dX"${dX//\./p}"_"${XMIN}"-"${XMAX}"_CAT"${CATMIN}"-"${CATMAX}${SUFFIX};
	echo -e "\033[1;31m"$FOLDER"\033[m";
	
	roottask=./src/TransferFunctions.C"("${XMINTRANSFERNOM},${XMAXTRANSFERNOM},${TRORDERNOM},${XMINTRANSFERVBF},${XMAXTRANSFERVBF},${TRORDERVBF},\"${FOLDER}\"")";
	echo -e "\033[1;31m"$roottask"\033[m";
	root -b ${roottask} -q
	
#	roottask=./src/CreateBkgTemplates.C"("${XMIN},${XMAX},\"${FOLDER}\"")";
#	echo -e "\033[1;31m"$roottask"\033[m";
#	root -b ${roottask} -q
#	
#	roottask=./src/CreateSigTemplates.C"("${dX},${XMIN},${XMAX},\"${FOLDER}\"")";
#	echo -e "\033[1;31m"$roottask"\033[m";
#	root -b ${roottask} -q
#	
#	roottask=./src/CreateDataTemplates.C"("${dX},${XMIN},${XMAX},${BRN_ORDER_NOM},${BRN_ORDER_VBF},\"${FOLDER}\"",${USETRANSFER},${TRORDERNOM},${TRORDERVBF})";
#	echo -e "\033[1;31m"$roottask"\033[m";
#	root -b ${roottask} -q
#	
#	roottask=./src/CreateDatacards.C"("${CATMIN},${CATMAX},${BRN_ORDER_NOM},${BRN_ORDER_VBF},${TRORDERNOM},${TRORDERVBF},\"${FOLDER}\"")";
#	echo -e "\033[1;31m"$roottask"\033[m";
#	root -b ${roottask} -q
fi
