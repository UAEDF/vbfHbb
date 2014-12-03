
source="BiasV10_limit_BRN5p4_dX0p1_B80-200_CAT0-6/output"
destin="/afs/cern.ch/user/s/salderwe/note/tdr2/notes/AN-13-358/trunk/figures/sara"

list1=("/plots/channelComp_mH125_2.pdf"  \
"/plots/channelComp_mH115_2.pdf" \
"/plots/channelComp_mH135_2.pdf" \
"/plots/channelComp_mH120_2.pdf" \
"/plots/channelComp_mH130_2.pdf" \
)
list2=("/plots/Fit_mH125_CAT0.pdf" \
"/plots/Fit_mH125_CAT1.pdf" \
"/plots/Fit_mH125_CAT2.pdf" \
"/plots/Fit_mH125_CAT3.pdf" \
"/plots/Fit_mH125_CAT4.pdf" \
"/plots/Fit_mH125_CAT5.pdf" \
"/plots/Fit_mH125_CAT6.pdf" \
"/plots/Fit_mH115_CAT0.pdf" \
"/plots/Fit_mH115_CAT1.pdf" \
"/plots/Fit_mH115_CAT2.pdf" \
"/plots/Fit_mH115_CAT3.pdf" \
"/plots/Fit_mH115_CAT4.pdf" \
"/plots/Fit_mH115_CAT5.pdf" \
"/plots/Fit_mH115_CAT6.pdf" \
"/plots/Fit_mH135_CAT0.pdf" \
"/plots/Fit_mH135_CAT1.pdf" \
"/plots/Fit_mH135_CAT2.pdf" \
"/plots/Fit_mH135_CAT3.pdf" \
"/plots/Fit_mH135_CAT4.pdf" \
"/plots/Fit_mH135_CAT5.pdf" \
"/plots/Fit_mH135_CAT6.pdf" \
"/plots/Fit_mH120_CAT0.pdf" \
"/plots/Fit_mH120_CAT1.pdf" \
"/plots/Fit_mH120_CAT2.pdf" \
"/plots/Fit_mH120_CAT3.pdf" \
"/plots/Fit_mH120_CAT4.pdf" \
"/plots/Fit_mH120_CAT5.pdf" \
"/plots/Fit_mH120_CAT6.pdf" \
"/plots/Fit_mH130_CAT0.pdf" \
"/plots/Fit_mH130_CAT1.pdf" \
"/plots/Fit_mH130_CAT2.pdf" \
"/plots/Fit_mH130_CAT3.pdf" \
"/plots/Fit_mH130_CAT4.pdf" \
"/plots/Fit_mH130_CAT5.pdf" \
"/plots/Fit_mH130_CAT6.pdf" \
)
list3=("/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH125_1.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH125_3.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH115_1.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH115_3.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH135_1.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH135_3.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH120_1.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH120_3.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH130_1.pdf" \
"/plots/nuissances_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2_mH130_3.pdf" \
)

list4=("/limitplots/limit_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2.pdf" \
)

[ ! -d ${destin}/channelCompat ] && mkdir ${destin}/channelCompat
[ ! -d ${destin}/fits ] && mkdir ${destin}/fits
[ ! -d ${destin}/nuissances ] && mkdir ${destin}/nuissances
[ ! -d ${destin}/limits ] && mkdir ${destin}/limits

for i in ${list1[@]}; do 
  j=$(basename $i)
  cp -v ${source}${i} ${destin}/channelCompat/${j//_2/};
done 

for i in ${list2[@]}; do 
  j=$(basename $i)
  cp -v ${source}${i} ${destin}/fits/$j;
done

for i in ${list3[@]}; do
  j=$(basename $i)
  j=${j//_vbfhbb_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2/}
  if [[ $i == *_1* ]]; then
	 cp -v ${source}${i} ${destin}/nuissances/${j//_1/_pull};
  elif [[ $i == *_3* ]]; then
	 cp -v ${source}${i} ${destin}/nuissances/${j//_3/_unc};
  fi
done

for i in ${list4[@]}; do
	cp -v ${source}${i} ${destin}/limits/limit.pdf;
done

cp -v ${source}/datacards/datacard_m125_BRN5p4_B80-200_CAT0-CAT6_FitPOL1-POL2.txt ${destin}/limits/datacard_mH125.txt
cp -v tables.txt ${destin}/limits/tables.txt
cp -v numbers.txt ${destin}/limits/numbers.txt
cp -v numbers2.txt ${destin}/limits/numbers2.txt

cp -v muScan.pdf ${destin}/muScan.pdf
