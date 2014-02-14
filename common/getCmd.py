#!/usr/bin/env python

def getCommandline():
	#s1 = str(raw_input("basepath (-G)? "))
	s2 = str(raw_input("k-factor? "))
	s3 = str(raw_input("selection (-p)? "))
	s4 = str(raw_input("variable (-v)? "))
	#s5 = str(raw_input("output file (-o)? "))
	s6 = str(raw_input("output file suffix (-o)? "))
	s7 = str(raw_input("file source (-G) [usb/(L)ocal]? "))

	s1 = "/usb/Corsair/autumn2013" if s7=="U" else "/data/UAData/autumn2013"
	s5 = "vbfHbb_2013_2DFunCorrected_controlplots-%s.root"%s6

	#b1 = ";FUN#mqq[2]#ht" if str(raw_input("correct (FUN) [y/N]? ")) == "y" else ""
	b1 = ";MAP#mqq[2]#ht" if str(raw_input("correct (FUN) [y/N]? ")) == "y" else ""
	b2 = "redrawstack" if str(raw_input("REdrawstack [y/N]? ")) == "y" else "drawstack"

	full = '''
./mkHist.py -D ../common/vbfHbb_defaultOpts_2013.json -G "%s" -w '18000,XSEC;LUMI;PU;KFAC%s,,%s,../trigger/rootfiles/vbfHbb_2DMaps_corrections_mqq2-ht.root;2DFits/H2DFun_QCD-Rat_sdEtaqq2-jetPt1-run194270-tVBF-rAV40-dVBFOR_mqq2-ht_HT400AV40AV80;1' -d -t 'VBF' --datatrigger 'VBFOR'  -o rootfiles/%s --binning 'mqq2;50;500;3000,mbb2;30;0;300,ht;50;0;1000,dEtaqq2;60;2;8,mbbReg2;30;0;300,jetPt0;40;0;400,jetPt1;30;0;300,mvaVBF;20;-1;1' --nosample 'JetMon,VBF115,VBF120,VBF130,VBF135,DataA,DataB,DataC,DataD' -p "%s" -v "%s" --%s -K
'''%(s1,b1,s2,s5,s3,s4,b2)
	return full

if __name__=="__main__":
	print getCommandline()
