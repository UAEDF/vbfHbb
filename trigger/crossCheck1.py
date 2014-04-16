#!/usr/bin/env python

import ROOT
from ROOT import *
import os,sys,re

basedir="trigger" if not os.getcwd().split('/')[-1]=="trigger" else "."

f1a = TFile("%s/rootfiles/trigger_2DMaps_NOM_jetBtag00-jetBtag10.root"%basedir,"read")
f1b = TFile("%s/rootfiles/trigger_2DMaps_NOM_jetBtag00-mqq1.root"%basedir,"read")
f2a = TFile("%s/rootfiles/trigger_DistMaps_NOM_jetBtag00-jetBtag10.root"%basedir,"read")
f2b = TFile("%s/rootfiles/trigger_DistMaps_NOM_jetBtag00-mqq1.root"%basedir,"read")

h1a_dat_num = "2DMaps/JetMon/2DMap_JetMon-Num_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
h1a_dat_den = "2DMaps/JetMon/2DMap_JetMon-Den_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
h1a_qcd_num = "2DMaps/QCD/2DMap_QCD-Num_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"
h1a_qcd_den = "2DMaps/QCD/2DMap_QCD-Den_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-jetBtag10"

h1b_dat_num = "2DMaps/JetMon/2DMap_JetMon-Num_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
h1b_dat_den = "2DMaps/JetMon/2DMap_JetMon-Den_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
h1b_qcd_num = "2DMaps/QCD/2DMap_QCD-Num_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"
h1b_qcd_den = "2DMaps/QCD/2DMap_QCD-Den_sBtag0_LL-dEtaqq1_gt2p5-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-tNOMMC-rAV80-dNOMMC_jetBtag00-mqq1"

h2a_vbf_num = "2DMaps/VBF125/2DMap_VBF125-Num_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-nLeptons-tNOMMC-rNone-dNOM_jetBtag00-jetBtag10"
h2b_vbf_num = "2DMaps/VBF125/2DMap_VBF125-Num_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-nLeptons-tNOMMC-rNone-dNOM_jetBtag00-mqq1"

h1aname = [h1a_dat_num, h1a_dat_den, h1a_qcd_num, h1a_qcd_den]
h1bname = [h1b_dat_num, h1b_dat_den, h1b_qcd_num, h1b_qcd_den]
h2aname = [h2a_vbf_num]
h2bname = [h2b_vbf_num]

h1a = [None]*4
h1b = [None]*4
h2a = [None]*1
h2b = [None]*1

h1aX = [None]*4
h1bX = [None]*4
h2aX = [None]*1
h2bX = [None]*1

gROOT.SetBatch(1)
gStyle.SetOptStat(0)

for ih,h in enumerate(h1aname): h1a[ih] = f1a.Get(h)
for ih,h in enumerate(h1bname): h1b[ih] = f1b.Get(h)
for ih,h in enumerate(h2aname): h2a[ih] = f2a.Get(h)
for ih,h in enumerate(h2bname): h2b[ih] = f2b.Get(h)

for ih,h in enumerate(h1a): h1aX[ih] = h.ProjectionX() 
for ih,h in enumerate(h1b): h1bX[ih] = h.ProjectionX() 
for ih,h in enumerate(h2a): h2aX[ih] = h.ProjectionX() 
for ih,h in enumerate(h2b): h2bX[ih] = h.ProjectionX() 

for h in h1aX + h1bX + h2aX + h2bX: 
#	h.SetLabelColor(kBlack,"XY")
#	h.SetTitleSize(0.02,"XY")
#	h.SetLabelSize(0.02,"XY")
	h.SetTitleOffset(3,"XY")
for h in h1aX[:2]: h.SetLineColor(kBlack) 
for h in h1bX[:2]: h.SetLineColor(kGreen) 
for h in h1aX[2:]: h.SetLineColor(kBlue) 
for h in h1bX[2:]: h.SetLineColor(kRed) 
for h in h2aX: h.SetLineColor(kOrange)
for h in h2bX: h.SetLineColor(kViolet)

for h in h1aX + h2aX: h.SetLineStyle(7) 
for h in h1bX + h2bX: h.SetLineStyle(10) 

leg = [TLegend(0.2,0.7,0.4,0.9),TLegend(0.2,0.7,0.4,0.9),TLegend(0.2,0.7,0.4,0.9),TLegend(0.2,0.7,0.4,0.9),TLegend(0.2,0.7,0.4,0.9)]

c = TCanvas("c","c",2000,3000)
c.Divide(2,3)
c.cd(1)	
h1aX[0].Draw("hist,text")
h1bX[0].Draw("hist,same")
leg[0].AddEntry(h1aX[0],"data,pass,map1")
leg[0].AddEntry(h1bX[0],"data,pass,map2")
c.cd(2)	
h1aX[1].Draw("hist,text")
h1bX[1].Draw("hist,same")
leg[1].AddEntry(h1aX[1],"data,total,map1")
leg[1].AddEntry(h1bX[1],"data,total,map2")
c.cd(3)	
h1aX[2].Draw("hist,text")
h1bX[2].Draw("hist,same")
leg[2].AddEntry(h1aX[2],"qcd,pass,map1")
leg[2].AddEntry(h1bX[2],"qcd,pass,map2")
c.cd(4)	
h1aX[3].Draw("hist,text")
h1bX[3].Draw("hist,same")
leg[3].AddEntry(h1aX[3],"qcd,total,map1")
leg[3].AddEntry(h1bX[3],"qcd,total,map2")
c.cd(5)
h2aX[0].Draw("hist,text")
h2bX[0].Draw("hist,same")
leg[4].AddEntry(h2aX[0],"vbf,pass,map1")
leg[4].AddEntry(h2bX[0],"vbf,pass,map2")

c.Update()

for i in range(5): 
	c.cd(i+1)
	leg[i].Draw("same")

c.Update()
if not os.path.exists("%s/plots/crossChecks/"%basedir): os.makedirs("%s/plots/crossChecks/"%basedir)
c.SaveAs("%s/plots/crossChecks/2DMap_Xproj.pdf"%basedir)
c.Close()

f1a.Close()
f1b.Close()
f2a.Close()
f2b.Close()
