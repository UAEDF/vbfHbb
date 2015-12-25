#!/usr/bin/env python
import re,os,sys
import ROOT
from ROOT import *

global paves
paves = []

######################################################################################################################################################
def makeline(x1,y1,x2,y2,style=kDashed,width=2,color=kGray+2):
    global paves
    tl = TLine(x1,y1,x2,y2)
    tl.SetNDC(0)
    tl.SetLineWidth(width)
    tl.SetLineStyle(style)
    tl.SetLineColor(color)
    tl.Draw("same")
    paves += [tl]

######################################################################################################################################################
gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.06)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPadRightMargin(0.04)
gStyle.SetPadTopMargin(0.04)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.055,"XY")
gStyle.SetLabelSize(0.045,"XY")
gStyle.SetTitleOffset(1.0,"X")
gStyle.SetTitleOffset(1.2,"Y")
gStyle.SetStripDecimals(0)

#f = TFile.Open("BiasV10plots_limit_BRN5p4_dX0p1_B80-200_CAT0-6/output/signal_shapes_workspace_B80-200.root","read")
f = TFile.Open("thesis/root/sig_shapes_workspace_B80-200.root","read")

color = [kBlack,kGreen,kRed,kBlue,kMagenta]
marker = [20,21,22,23,24]
color = [kBlack,kOrange-2,kBlue,kGreen+3,kRed]
style = [5,8,6,7,1]

fwhmm  = []
mmH    = []
sigmam = []
for mass in range(115,140,5):
	fwhmm  += [TH1F("fwhm-m_m%d"%mass,"fwhm-m_m%d;Categories;FWHM / m"%mass,7,0,7)]
	mmH    += [TH1F("m-mH_m%d"%mass,"m-mH_m%d;Categories;m / m_{H}"%mass,7,0,7)]
	sigmam += [TH1F("sigma-m_m%d"%mass,"sigma-m_m%d;Categories;#sigma / m"%mass,7,0,7)]

leg = TLegend(0.2,0.30,0.6,0.9)
leg.SetFillStyle(-1)
leg.SetBorderSize(0)
leg.SetTextSize(0.06)
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

	fwhmm[imass].SetLineStyle(style[imass])
	mmH[imass].SetLineStyle(style[imass])
	sigmam[imass].SetLineStyle(style[imass])

	fwhmm[imass].GetYaxis().SetRangeUser(0.16,0.29)
	mmH[imass].GetYaxis().SetRangeUser(0.96,1.04)
	sigmam[imass].GetYaxis().SetRangeUser(0.06,0.13)
	
	fwhmm[imass].GetXaxis().SetLabelSize(0.07)
	mmH[imass].GetXaxis().SetLabelSize(0.07)
	sigmam[imass].GetXaxis().SetLabelSize(0.07)
	
	fwhmm[imass].GetYaxis().SetNdivisions(508)
	mmH[imass].GetYaxis().SetNdivisions(506)
	sigmam[imass].GetYaxis().SetNdivisions(506)

	leg.AddEntry(fwhmm[imass],"m_{H} = %d GeV"%mass,"P")

	print

c0 = TCanvas("c0","c0",900,700)
leg2 = leg.Clone("leg2")
leg2.SetTextSize(0.045)
leg2.SetNColumns(2)
leg2.SetX1(0.18)
leg2.SetX2(0.65)
leg2.SetY1(0.70)
leg2.SetY2(0.90)

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

gPad.SetGrid(1)

c = TCanvas("c","c",1800,1400)
c.Divide(2,2)
c.cd(1)
gPad.SetTicks(1,1)
for i in range(5): fwhmm[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): fwhmm[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
leg2.Draw()
c0.SaveAs("thesis/plot/signalProperties_1.png")
c0.SaveAs("thesis/plot/signalProperties_1.pdf")
c.cd(2)
gPad.SetTicks(1,1)
for i in range(5): mmH[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
makeline(gPad.GetUxmin(),1.,gPad.GetUxmax(),1.,kDotted,1,kGray+1)
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): mmH[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
leg2.Draw()
c0.SaveAs("thesis/plot/signalProperties_2.png")
c0.SaveAs("thesis/plot/signalProperties_2.pdf")
c.cd(3)
gPad.SetTicks(1,1)
for i in range(5): sigmam[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
c0.cd()
gPad.SetTicks(1,1)
for i in range(5): sigmam[i].Draw("PL" if i==0 else "PLsame")
#pcms1.Draw()
#pcms2.Draw()
gPad.Update()
makeline(4,gPad.GetUymin(),4,gPad.GetUymax())
leg2.Draw()
c0.SaveAs("thesis/plot/signalProperties_3.png")
c0.SaveAs("thesis/plot/signalProperties_3.pdf")
c.cd(4)
leg.Draw()
c.SaveAs("thesis/plot/signalProperties.png")
c.SaveAs("thesis/plot/signalProperties.pdf")

f.Close()
