#!/bin/sh

folder=B80-200_BRN5-4_TFPOL1-POL2_SIG100-150/output

em=()
om=()
im=()
es=()
os=()
is=()
ep=()
op=()
ip=()
lm=()
lo=()
le=()
li=()
lu=()
lmi=()
lei=()
ensm=()
enss=()
ensp=()
lnsm=()
lnso=()
lnse=()

for i in ${folder}/logs/*SignifExp* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`cat $i | grep Sign | sed -e "s#.* \([0-9.]*\)#\1#g"`
	l=`cat $i | grep "p-value" | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	em=(${em[@]} $j)
	es=(${es[@]} $k)
	ep=(${ep[@]} $l)
done

for i in ${folder}/logs/*SignifObs* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`cat $i | grep Sign | sed -e "s#.* \([0-9.]*\)#\1#g"`
	l=`cat $i | grep "p-value" | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	#if [ "$k" == "" ]; then k=0.0; fi
	#if [ "$l" == "" ]; then l=0.0; fi
	om=(${om[@]} $j)
	os=(${os[@]} $k)
	op=(${op[@]} $l)
done

for i in ${folder}/logs/*SignifInj* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`cat $i | grep Sign | sed -e "s#.* \([0-9.]*\)#\1#g"`
	l=`cat $i | grep "p-value" | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	#if [ "$k" == "" ]; then k=0.0; fi
	#if [ "$l" == "" ]; then l=0.0; fi
	im=(${im[@]} $j)
	is=(${is[@]} $k)
	ip=(${ip[@]} $l)
done

for i in ${folder}/logs/*SignifNoSystExp* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`cat $i | grep Sign | sed -e "s#.* \([0-9.]*\)#\1#g"`
	l=`cat $i | grep "p-value" | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	#if [ "$k" == "" ]; then k=0.0; fi
	#if [ "$l" == "" ]; then l=0.0; fi
	ensm=(${ensm[@]} $j)
	enss=(${enss[@]} $k)
	ensp=(${ensp[@]} $l)
done

for i in ${folder}/logs/*CombineExpObs* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`tail -n8 $i | grep Expected | grep 50.0 | sed -e "s#.*r < \([0-9.]*\)#\1#g"`
	l=`tail -n8 $i | grep Observed | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	lm=(${lm[@]} $j)
	le=(${le[@]} $k)
	lo=(${lo[@]} $l)
done

for i in ${folder}/logs/*CombineNoSystExpObs* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`tail -n8 $i | grep Expected | grep 50.0 | sed -e "s#.*r < \([0-9.]*\)#\1#g"`
	l=`tail -n8 $i | grep Observed | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	lnsm=(${lnsm[@]} $j)
	lnse=(${lnse[@]} $k)
	lnso=(${lnso[@]} $l)
done

#for i in ${folder}/logs/*CombineExpObs* ; do 
for i in ${folder}/logs/*MLFit* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	#k=`cat $i | grep "minimum of data" | sed -e "s#.*r = \([0-9.e\-]*\).*#\1#g"`
	k=`cat $i | grep "Best fit" | sed -e "s#.*r: \([0-9.e\-]*\) .*#\1#g"`
	lmu=(${lmu[@]} $j)
	lu=(${lu[@]} $k)
done

for i in ${folder}/logs/*CombineInj125* ; do 
	j=`echo $i | sed -e "s#.*_\(...\).*#\1#g"` 
	k=`tail -n8 $i | grep Expected | grep 50 | sed -e "s#.* \([0-9.]*\)#\1#g"`
	l=`tail -n8 $i | grep Observed | sed -e "s#.* \([0-9.]*\).*#\1#g"`
	lmi=(${lmi[@]} $j)
	lei=(${lei[@]} $k)
	li=(${li[@]} $l)
done

for i in `seq 0 10`; do
	printf "exp %5d%8.4f%8.4f\n" ${em[$i]} ${es[$i]} ${ep[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "obs %5d%8.4f%8.4f\n" ${om[$i]} ${os[$i]} ${op[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "oin %5d%8.4f%8.4f\n" ${im[$i]} ${is[$i]} ${ip[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "ens %5d%8.4f%8.4f\n" ${ensm[$i]} ${enss[$i]} ${ensp[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "lim %5d%8.4f%8.4f\n" ${lm[$i]} ${lo[$i]} ${le[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "lns %5d%8.4f%8.4f\n" ${lnsm[$i]} ${lnso[$i]} ${lnse[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "inj %5d%8.4f%8.4f\n" ${lmi[$i]} ${li[$i]} ${lei[$i]} >> getSignPval_tmp.txt
done
for i in `seq 0 10`; do
	printf "mu  %5d%8.4f%8.4f\n" ${lmu[$i]} ${lu[$i]} ${lu[$i]} >> getSignPval_tmp.txt
done

python getSignPval.py ${folder} getSignPval_tmp.txt

rm getSignPval_tmp.txt
