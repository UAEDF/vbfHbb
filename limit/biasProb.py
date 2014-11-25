#!/usr/bin/env python
import ROOT
from ROOT import *
import re,os,sys
from glob import glob
from optparse import OptionParser

mp = OptionParser()
opts,args = mp.parse_args()

muval = float(args[2])

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x /afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/common/styleCMSTDR.C")
gStyle.SetPadTopMargin(0.04)
gStyle.SetPadRightMargin(0.04)

o = TFile.Open(args[1],"recreate")
h = TH1F("h","h;Fitted signal strength;Probability",52,-6,7)
h2 = TH1F("h2","h2",52,-6,7)
h.Sumw2()
h2.Sumw2()

files = glob(args[0])
for f in sorted(files): 
	print f
	i = TFile.Open(f,"read")
	#t = i.Get("limit;1")
	t = i.Get("tree_fit_sb;1")
	for iEv in t:
		#if iEv.limitErr>0: 
		#	h.Fill(iEv.limit)
		#	h2.Fill((iEv.limit-1.)/iEv.limitErr)
		h.Fill(iEv.mu)
	i.Close()

o.cd()
gDirectory.cd("%s:/"%o.GetName())
h.Write()
h2.Write()

c = TCanvas("c1","c1",900,750)
h.Scale(1./h.Integral())

h.Draw("hist")

fit = TF1("g","gaus",-7,7)
fit.FixParameter(1,1.0)
h.Fit(fit,"RN")
fit.SetLineColor(kBlue)
fit.SetLineWidth(2)
fit.Draw("same")

fitcopy = fit.Clone()
fitcopy.SetLineColor(kRed)
fitcopy.SetFillColor(kRed-10)
fitcopy.SetFillStyle(1001)
fitcopy.SetRange(muval,7)
fitcopy.Draw("samechist")
pval = fit.Integral(muval,10)/fit.Integral(-10,10)

gPad.Update()
line1 = TLine(1.0,gPad.GetUymin(),1.0,gPad.GetUymax())
line1.SetLineStyle(2)	
line1.Draw("same")

line2 = TLine(muval,gPad.GetUymin(),muval,gPad.GetUymax())
line2.SetLineStyle(7)
line2.SetLineWidth(2)
line2.SetLineColor(kRed)	
line2.Draw("same")

pave = TPaveText(0.72,0.7,0.94,0.93,"NDC")
pave.SetFillStyle(-1)
pave.SetBorderSize(0)
pave.SetTextFont(62)
pave.SetTextSize(0.040)
pave.SetTextColor(kRed)
pave.SetTextAlign(31)
pave.AddText("#mu^{obs} = %.2f"%muval)
pave.AddText("p-value = %.3f"%pval)
gPad.Update()
pave.SetY1(pave.GetY2()-pave.GetListOfLines().GetSize()*0.055)
pave.Draw()

gPad.RedrawAxis()

c.SaveAs("biasProb.pdf")

#h2.Draw()
#c.SaveAs("h2.pdf")
c.Close()

o.Close()
