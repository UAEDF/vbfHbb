#!/usr/bin/env python

import ROOT
from ROOT import *

import os,sys,re

global paves
paves = []

####################################################################################################

def trpave(text):
    global paves
    p = TText(1.-gStyle.GetPadRightMargin(),1.0,text)
    p.SetNDC()
    p.SetTextSize(gStyle.GetPadTopMargin()*0.7)
    p.SetTextFont(42)
    p.SetTextAlign(33)
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]

####################################################################################################

gROOT.SetBatch(1)
gStyle.SetOptStat(0)
gStyle.SetTitleOffset(1.4,"Y")
gStyle.SetPadLeftMargin(0.14)
gStyle.SetGridColor(17)

#f1 = TFile.Open("weights/TMVA.root")
f1 = TFile.Open("rootfiles/bjetId_NOM_MVA.root")
#f2 = TFile.Open("weights/TMVA.Alt.root")

h2s,h2b,g2 = 0,0,0
#h1s = f1.Get("Method_BDT/BDT/MVA_BDT_effS")
#h1b = f1.Get("Method_BDT/BDT/MVA_BDT_effB")
h1s = f1.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_effS")
h1b = f1.Get("Method_BDT/BDT_GRAD2/MVA_BDT_GRAD2_effB")

#h2s = f2.Get("Method_BDT/BDT/MVA_BDT_effS")
#h2b = f2.Get("Method_BDT/BDT/MVA_BDT_effB")

c1s = f1.Get("CorrelationMatrixS")
c1b = f1.Get("CorrelationMatrixB")
#c2s = f2.Get("CorrelationMatrixS")
#c2b = f2.Get("CorrelationMatrixB")

g1 = TGraph()
#g2 = TGraph()
for ibin in range(1,h1s.GetNbinsX()):
    effS1 = h1s.GetBinContent(ibin)
    rejB1 = 1. - h1b.GetBinContent(ibin)
    g1.SetPoint(g1.GetN(),effS1,rejB1)
#    effS2 = h2s.GetBinContent(ibin)
#    rejB2 = 1. - h2b.GetBinContent(ibin)
#    g2.SetPoint(g2.GetN(),effS2,rejB2)

for h in [h1s,h1b,h2s,h2b,g1,g2]:
    if not h: continue
    h.GetXaxis().SetTitle("b-likelihood")
    h.GetYaxis().SetTitle("%s efficiency"%("Sig." if "effS" in h.GetName() else "Bkg."))
    h.GetXaxis().SetTitleSize(0.045)
    h.GetYaxis().SetTitleSize(0.045)
    h.GetYaxis().SetTitleOffset(1.4)
    if not "eff" in h.GetName():
        h.GetXaxis().SetTitle("Sig. efficiency")
        h.GetYaxis().SetTitle("Bkg. rejection")
        h.GetXaxis().SetRangeUser(0.6,1.1)
        h.GetYaxis().SetRangeUser(0.0,1.1)
        h.SetLineColor(kGreen+3)

c = TCanvas("c","c",900*2,750*3)
c.Divide(2,3)
c.cd(1)
h1s.Draw()
trpave("v1")
c.cd(2)
h1b.Draw()
trpave("v1")
#c.cd(3)
#h2s.Draw()
#trpave("v2")
#c.cd(4)
#h2b.Draw()
#trpave("v2")
c.cd(5)
g1.Draw("AL")
print g1.Integral()
trpave("v1")
#c.cd(6)
#g2.Draw("AL")
#trpave("v2")
for i in range(6): 
    c.cd(i+1)
    gPad.SetGrid(1,1)

c.SaveAs("plots/efficiencies.pdf")
c.Close()

c = TCanvas("c","c",900*2,750*1)
c.Divide(2,1)
c.cd(1)
c1s.Draw("colz,text")
c.cd(2)
c1b.Draw("colz,text")
c.SaveAs("plots/correlations-1.pdf")

#c.cd(1)
#c2s.Draw("colz,text")
#c.cd(2)
#c2b.Draw("colz,text")

c.SaveAs("plots/correlations-2.pdf")
c.Close()

f1.Close()
#f2.Close()

