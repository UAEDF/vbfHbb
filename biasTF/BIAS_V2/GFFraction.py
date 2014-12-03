#!/usr/bin/env python

import re,os,sys
import ROOT
from ROOT import *

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.06)
gStyle.SetPaintTextFormat(".2g")

fs_ggf = {}
fs_vbf = {}
t_ggf = {}
t_vbf = {}
n_ggf = {}
n_vbf = {}

xsec = [[],[]]
xsec[0] = [15.93,13.52,11.12,8.82,6.69]
xsec[1] = [1.215,1.069,0.911,0.746,0.585]


for sel in ["NOM","VBF"]:
	fs_ggf[sel] = []
	fs_vbf[sel] = []
	t_ggf[sel] = []
	t_vbf[sel] = []
	n_ggf[sel] = []
	n_vbf[sel] = []
	for mass in range(115,140,5):
		fs_ggf[sel] += [TFile.Open("flat/Fit_GFPowheg%d_sel%s.root"%(mass,sel))]
		fs_vbf[sel] += [TFile.Open("flat/Fit_VBFPowheg%d_sel%s.root"%(mass,sel))]
		t_ggf[sel] += [fs_ggf[sel][-1].Get("Hbb/events")]
		t_vbf[sel] += [fs_vbf[sel][-1].Get("Hbb/events")]
		n_ggf[sel] += [fs_ggf[sel][-1].Get("TriggerPass")]
		n_vbf[sel] += [fs_vbf[sel][-1].Get("TriggerPass")]

for ii,i in enumerate(xsec[0]): xsec[0][ii] = i/n_ggf['NOM'][ii].GetBinContent(1)
for ii,i in enumerate(xsec[1]): xsec[1][ii] = i/n_vbf['NOM'][ii].GetBinContent(1)

mbb = ["MbbReg[1]","MbbReg[2]"]
mva = ["mvaNOM","mvaVBF"]
nom = [-0.6,0.0,0.7,0.84,1.001]
vbf = [-0.1,0.4,0.8,1.001]

h = TH2F("h","h;Category;Higgs mass (GeV)",7,0,7,5,0,5)

for cat in range(7):
	for imass,mass in enumerate(range(115,140,5)):
		print cat, mass
		if cat < 4:
			nggf = t_ggf['NOM'][imass].GetEntries("%s>%f && %s<=%f"%(mva[0],nom[cat],mva[0],nom[cat+1]))
			nvbf = t_vbf['NOM'][imass].GetEntries("%s>%f && %s<=%f"%(mva[0],nom[cat],mva[0],nom[cat+1]))
			print "%s>%f && %s<=%f"%(mva[0],nom[cat],mva[0],nom[cat+1])
		else:
			nggf = t_ggf['VBF'][imass].GetEntries("%s>%f && %s<=%f"%(mva[1],vbf[cat-4],mva[1],vbf[cat-4+1]))
			nvbf = t_vbf['VBF'][imass].GetEntries("%s>%f && %s<=%f"%(mva[1],vbf[cat-4],mva[1],vbf[cat-4+1]))
			print "%s>%f && %s<=%f"%(mva[1],vbf[cat-4],mva[1],vbf[cat+1-4])
		print
		print cat+1,imass+1, float(nggf)*xsec[0][imass], float(nvbf)*xsec[1][imass]
		h.SetBinContent(cat+1,imass+1,float(nggf)*xsec[0][imass]/(float(nggf)*xsec[0][imass]+float(nvbf)*xsec[1][imass]))
		h.GetXaxis().SetBinLabel(cat+1,"CAT%d"%cat)
		h.GetYaxis().SetBinLabel(imass+1,"%d"%mass)
		h.GetXaxis().SetLabelSize(0.07)
		h.GetYaxis().SetLabelSize(0.07)

c = TCanvas("c","c",900,600)
gPad.SetGrid(1)
gPad.SetTicks(1)
h.SetMaximum(0.6)#round(h.GetBinContent(h.GetMaximumBin())*1.01,2))
h.SetMinimum(0.052)#round(h.GetBinContent(h.GetMinimumBin())/1.01,2))
h.SetMarkerSize(1.7)
h.Draw("text,col")
c.SaveAs("GFFraction.pdf")
c.SaveAs("GFFraction.png")


fout = TFile.Open("GFFraction.root","recreate")
h.Write()
fout.Close()
