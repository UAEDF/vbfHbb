#!/usr/bin/env python

import re,os,sys
import ROOT
from ROOT import *
sys.path.append("../common")
from toolkit import *

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.04)
gStyle.SetPadRightMargin(0.13)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPaintTextFormat(".2g")
gStyle.SetLabelSize(0.035,"X")
gStyle.SetLabelSize(0.06,"XY")
gStyle.SetTitleSize(0.05,"XY")
gStyle.SetTitleOffset(1.1,"X")
gStyle.SetTitleOffset(1.2,"Y")
#gStyle.SetPalette(20)
set_palette(999,False,0.3)

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

h = TH2F("h","h;Category;Higgs boson mass (GeV)",7,0,7,5,0,5)

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
#		h.GetXaxis().SetLabelSize(0.07)
#		h.GetYaxis().SetLabelSize(0.07)


c = TCanvas("c","c",900,700)
pcms1 = TPaveText(gPad.GetLeftMargin(),1.-gPad.GetTopMargin(),0.4,1.,"NDC")
pcms1.SetTextAlign(12)
pcms1.SetTextFont(62)
pcms1.SetTextSize(gPad.GetTopMargin()*2.5/4.)
pcms1.SetFillStyle(-1)
pcms1.SetBorderSize(0)
pcms1.AddText("CMS")

pcms2 = TPaveText(0.5,1.-gPad.GetTopMargin(),1.-gPad.GetRightMargin()+0.02,1.,"NDC")
pcms2.SetTextAlign(32)
pcms2.SetTextFont(62)
pcms2.SetTextSize(gPad.GetTopMargin()*2.5/4.)
pcms2.SetFillStyle(-1)
pcms2.SetBorderSize(0)
pcms2.AddText("19.8 fb^{-1} (8 TeV)")

tl = TLine(4,-0.2,4,5.1)
tl.SetLineStyle(kDashed)
tl.SetLineWidth(3)
tl.SetLineColor(kBlack)
tl.SetNDC(0)

gPad.SetGrid(1)
gPad.SetTicks(1)
h.GetZaxis().SetNdivisions(5)
h.SetMaximum(0.52)#round(h.GetBinContent(h.GetMaximumBin())*1.01,2))
h.SetMinimum(0.06)#round(h.GetBinContent(h.GetMinimumBin())/1.01,2))
h.SetMarkerSize(1.7)
h.Draw("text,colz")
tl.Draw("same")
#pcms1.Draw()
#pcms2.Draw()
c.SaveAs("thesis/plot/GFFraction.pdf")
c.SaveAs("thesis/plot/GFFraction.png")


fout = TFile.Open("thesis/root/GFFraction.root","recreate")
h.Write()
fout.Close()
