#!/usr/bin/env python

import ROOT
from ROOT import *

import sys,os,re

gROOT.SetBatch(1)

f1 = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_VBFPowheg125.root","read")
t1 = f1.Get("Hbb/events")

c = TCanvas("c","c",1800,1800)
c.cd()

mvaNOM = ["(mvaNOM>=-1.00 && mvaNOM<0.00)","(mvaNOM>=0.00 && mvaNOM<0.25)","(mvaNOM>=0.25 && mvaNOM<0.70)","(mvaNOM>=0.70 && mvaNOM<0.88)","(mvaNOM>=0.88 && mvaNOM<1.001)","(1.)"]
mvaVBF = ["(mvaVBF>=-1.00 && mvaVBF<0.00)","(mvaVBF>=0.00 && mvaVBF<0.30)","(mvaVBF>=0.30 && mvaVBF<0.65)","(mvaVBF>=0.65 && mvaVBF<1.001)","(1.)"]
#NOM = "((mqq[1]>250.) && (jetPt[2]>50.) && (dPhibb[1]<2.0) && (jetPt[0]>80.) && (dEtaqq[1]>2.5) && (jetPt[3]>40.) && (jetBtag[b1[0]]>0.244 && jetBtag[b2[0]]>0.244) && (jetPt[1]>70.))"
NOM = "selNOM"
#VBF = "((0.5*(jetPt[0]+jetPt[1])>80.) && (mqq[2]>700.) && (dEtaqq[2]>3.5) && (jetBtag[b1[0]]>0.679 && jetBtag[b2[0]]>0.244) && (mjjTrig>700.) && (runNo==1) && (nLeptons==0) && (dEtaTrig>3.5) && (dPhibb[2]<2.0) && (jetPt[3]>30.) && !((dEtaqq[2]>2.5 && dPhibb[2]<2.0 && jetPt[0]>80. && jetPt[1]>65. && jetPt[2]>50. && jetPt[3]>35. && mqq[2]>300.) && (triggerResult[0]==1 || triggerResult[1]==1)))"
VBF = "selVBF"
NOMveto = "!(selNOM && (triggerResult[0]||triggerResult[1]))" 

# NOM [0]
for imva,mva in enumerate(mvaNOM):
	if not imva==len(mvaNOM)-1: print "\033[1;34mNOM CAT%d:\033[m"%imva,
	else: print "\033[1;34mNOM all: \033[m",
	t1.Draw("1.>>h1","(%s && %s) * (%.6f)"%(NOM,mva,1.0)) 
	t1.Draw("1.>>h2","(%s && %s) * (%s)"%(NOM,mva,"trigWtNOM[0]"))
	unwghtd = ROOT.h1.Integral()
	wghtd   = ROOT.h2.Integral()
	print "(bjet0,bjet1 map):             %20s = %.2f"%("%d / %-d"%(wghtd,unwghtd),float(wghtd)/float(unwghtd))

print

# NOM [1]
for imva,mva in enumerate(mvaNOM):
	if not imva==len(mvaNOM)-1: print "\033[1;34mNOM CAT%d:\033[m"%imva,
	else: print "\033[1;34mNOM all: \033[m",
	t1.Draw("1.>>h3","(%s && %s) * (%.6f)"%(NOM,mva,1.0)) 
	t1.Draw("1.>>h4","(%s && %s) * (%s)"%(NOM,mva,"trigWtNOM[1]"))
	unwghtd = ROOT.h3.Integral()
	wghtd   = ROOT.h4.Integral()
	print "(bjet0,mqq1 map):              %20s = %.2f"%("%d / %-d"%(wghtd,unwghtd),float(wghtd)/float(unwghtd))

print 

# VBF
for imva,mva in enumerate(mvaVBF):
	if not imva==len(mvaVBF)-1: print "\033[1;34mVBF CAT%d:\033[m"%imva,
	else: print "\033[1;34mVBF all: \033[m",
	t1.Draw("1.>>h5","(%s && %s) * (%.6f)"%(VBF,mva,1.0))
	t1.Draw("1.>>h6","(%s && %s) * (%s)"%(VBF,mva,"trigWtVBF"))
	unwghtd = ROOT.h5.Integral()
	wghtd   = ROOT.h6.Integral()
	print "(mqq2,dEtaqq2 map):            %20s = %.2f"%("%d / %-d"%(wghtd,unwghtd),float(wghtd)/float(unwghtd))

print

# VBF NOMveto
for imva,mva in enumerate(mvaVBF):
	if not imva==len(mvaVBF)-1: print "\033[1;34mVBF CAT%d:\033[m"%imva,
	else: print "\033[1;34mVBF all: \033[m",
	t1.Draw("1.>>h5","(%s && %s && %s) * (%.6f)"%(VBF,NOMveto,mva,1.0))
	t1.Draw("1.>>h6","(%s && %s && %s) * (%s)"%(VBF,NOMveto,mva,"trigWtVBF"))
	unwghtd = ROOT.h5.Integral()
	wghtd   = ROOT.h6.Integral()
	print "(mqq2,dEtaqq2 map, NOMveto):   %20s = %.2f"%("%d / %-d"%(wghtd,unwghtd),float(wghtd)/float(unwghtd))

c.Close()

