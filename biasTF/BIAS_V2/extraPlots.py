#!/usr/bin/env python
import re,os,sys
import ROOT
from ROOT import *

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.06)

f = TFile.Open("BiasV10plots_limit_BRN5p4_dX0p1_B80-200_CAT0-6/output/signal_shapes_workspace_B80-200.root","read")

color = [kBlack,kGreen,kRed,kBlue,kMagenta]
marker = [20,21,22,23,24]

fwhmm  = []
mmH    = []
sigmam = []
for mass in range(115,140,5):
	fwhmm  += [TH1F("fwhm-m_m%d"%mass,"fwhm-m_m%d;;FWHM / m"%mass,7,0,7)]
	mmH    += [TH1F("m-mH_m%d"%mass,"m-mH_m%d;;m / M_{H}"%mass,7,0,7)]
	sigmam += [TH1F("sigma-m_m%d"%mass,"sigma-m_m%d;;#sigma / m"%mass,7,0,7)]

leg = TLegend(0.2,0.25,0.6,0.9)
leg.SetFillStyle(-1)
leg.SetBorderSize(0)
leg.SetTextSize(0.07)
leg.SetTextFont(42)

for imass,mass in enumerate(range(115,140,5)): 
	print mass,
	for icat,cat in enumerate(range(0,7)):
		print cat,
		fwhm  = w.obj("fwhm_m%d_CAT%d"%(mass,cat)).getVal()
		mean  = w.obj("mean_m%d_CAT%d"%(mass,cat)).getVal()
		sigma = w.obj("sigma_m%d_CAT%d"%(mass,cat)).getVal()

		fwhmm[imass].SetBinContent(icat+1,fwhm/mean)
		mmH[imass].SetBinContent(icat+1,mean/mass)
		sigmam[imass].SetBinContent(icat+1,sigma/mean)

		fwhmm[imass].GetXaxis().SetBinLabel(icat+1,"CAT%d"%cat)
		mmH[imass].GetXaxis().SetBinLabel(icat+1,"CAT%d"%cat)
		sigmam[imass].GetXaxis().SetBinLabel(icat+1,"CAT%d"%cat)

#		fwhmm[imass].GetXaxis().SetBinError(icat+1,0.5)
#		mmH[imass].GetXaxis().SetBinError(icat+1,0.5)
#		sigmam[imass].GetXaxis().SetBinError(icat+1,0.5)
#
		
	fwhmm[imass].SetMarkerSize(2)
	mmH[imass].SetMarkerSize(2)
	sigmam[imass].SetMarkerSize(2)
	
	fwhmm[imass].SetMarkerStyle(marker[imass])
	mmH[imass].SetMarkerStyle(marker[imass])
	sigmam[imass].SetMarkerStyle(marker[imass])
	
	fwhmm[imass].SetMarkerColor(color[imass])
	mmH[imass].SetMarkerColor(color[imass])
	sigmam[imass].SetMarkerColor(color[imass])
	
	fwhmm[imass].SetLineColor(color[imass])
	mmH[imass].SetLineColor(color[imass])
	sigmam[imass].SetLineColor(color[imass])

	fwhmm[imass].GetYaxis().SetRangeUser(0.13,0.3)
	mmH[imass].GetYaxis().SetRangeUser(0.93,1.07)
	sigmam[imass].GetYaxis().SetRangeUser(0.05,0.14)
	
	fwhmm[imass].GetXaxis().SetLabelSize(0.07)
	mmH[imass].GetXaxis().SetLabelSize(0.07)
	sigmam[imass].GetXaxis().SetLabelSize(0.07)
	
	fwhmm[imass].GetYaxis().SetNdivisions(509)
	mmH[imass].GetYaxis().SetNdivisions(508)
	sigmam[imass].GetYaxis().SetNdivisions(506)

	leg.AddEntry(fwhmm[imass],"M_{H} = %d GeV"%mass,"P")

	print

c0 = TCanvas("c0","c0",900,600)
leg2 = leg.Clone("leg2")
leg2.SetTextSize(0.045)
leg2.SetNColumns(2)
leg2.SetX1(0.18)
leg2.SetX2(0.65)
leg2.SetY1(0.70)
leg2.SetY2(0.90)
c = TCanvas("c","c",1800,1200)
c.Divide(2,2)
c.cd(1)
gPad.SetTicks(1,1)
for i in range(5): fwhmm[i].Draw("PL" if i==0 else "PLsame")
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): fwhmm[i].Draw("PL" if i==0 else "PLsame")
leg2.Draw()
c0.SaveAs("signalProperties_1.png")
c0.SaveAs("signalProperties_1.pdf")
c.cd(2)
gPad.SetTicks(1,1)
for i in range(5): mmH[i].Draw("PL" if i==0 else "PLsame")
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): mmH[i].Draw("PL" if i==0 else "PLsame")
leg2.Draw()
c0.SaveAs("signalProperties_2.png")
c0.SaveAs("signalProperties_2.pdf")
c.cd(3)
gPad.SetTicks(1,1)
for i in range(5): sigmam[i].Draw("PL" if i==0 else "PLsame")
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): sigmam[i].Draw("PL" if i==0 else "PLsame")
leg2.Draw()
c0.SaveAs("signalProperties_3.png")
c0.SaveAs("signalProperties_3.pdf")
c.cd(4)
leg.Draw()
c.SaveAs("signalProperties.png")
c.SaveAs("signalProperties.pdf")

f.Close()
