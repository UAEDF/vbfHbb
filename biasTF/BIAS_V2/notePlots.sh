#!/bin/sh

source="BiasV10plots_limit_BRN5p4_dX0p1_B80-200_CAT0-6"
destin="/afs/cern.ch/user/s/salderwe/note/tdr2/notes/AN-13-358/trunk/figures/sara"

[ ! -d ${destin}/transfer ] && mkdir ${destin}/transfer;
[ ! -d ${destin}/sigTemp ] && mkdir ${destin}/sigTemp;
[ ! -d ${destin}/bkgTemp ] && mkdir ${destin}/bkgTemp;
#[ ! -d ${destin}/ ] && mkdir ${destin}/;

for i in `ls ${source}/plots/transferFunctions/*.pdf`; do 	
	j=$(basename $i)
	cp -v $i ${destin}/transfer/$j;
done

for i in `ls ${source}/plots/sigTemplates/*.pdf`; do
	j=$(basename $i);
	cp -v $i ${destin}/sigTemp/$j;
done

for i in `ls ${source}/plots/bkgTemplates/*.pdf`; do
	j=$(basename $i);
	cp -v $i ${destin}/bkgTemp/$j;
done

cp -v signalProperties.pdf ${destin}/sigTemp/
cp -v GFFraction.pdf ${destin}/sigTemp/

