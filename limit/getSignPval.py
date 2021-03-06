#!/usr/bin/env python

import sys,re,os
sys.path.append("../common")
from toolkit import filecontent,makeDirs
from optparse import OptionParser

import ROOT
from ROOT import *

def getPlots():
	mp = OptionParser()
	opts,args = mp.parse_args()
	basedir = os.getcwd()
	os.chdir(args[0])
	makeDirs("limitplots")

	gROOT.ProcessLine(".x /afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/kostas/../common/styleCMSTDR.C")
	gROOT.ProcessLine('gROOT->ForceStyle();')
	gStyle.SetPadLeftMargin(0.13)
	gStyle.SetPadRightMargin(0.04)
	gStyle.SetPadTopMargin(0.06)
	gStyle.SetStripDecimals(0)
	gStyle.SetTitleOffset(1.0,"Y")
	gROOT.SetBatch(1)
	
	signObs = {}
	signExp = {}
	signInj = {}
	pvalObs = {}
	pvalExp = {}
	pvalInj = {}
	signNSExp = {}
	pvalNSExp = {}
	limObs  = {}
	limExp  = {}
	limInj  = {}
	limNSObs  = {}
	limNSExp  = {}
	limNSInj  = {}
	mu = {}
	
	inp = filecontent(basedir+"/"+args[1])
	for line in inp.split('\n'):
		if 'exp' in line:
			fields = line.split()
			signExp[int(fields[1])] = float(fields[2])
			pvalExp[int(fields[1])] = float(fields[3])
		elif 'obs' in line:
			fields = line.split()
			signObs[int(fields[1])] = float(fields[2])
			pvalObs[int(fields[1])] = float(fields[3])
		elif 'oin' in line:
			fields = line.split()
			signInj[int(fields[1])] = float(fields[2])
			pvalInj[int(fields[1])] = float(fields[3])
		elif 'ens' in line:
			fields = line.split()
			signNSExp[int(fields[1])] = float(fields[2])
			pvalNSExp[int(fields[1])] = float(fields[3])
		elif 'lim' in line:
			fields = line.split()
			limObs[int(fields[1])] = float(fields[2])
			limExp[int(fields[1])] = float(fields[3])
		elif 'lns' in line:
			fields = line.split()
			limNSObs[int(fields[1])] = float(fields[2])
			limNSExp[int(fields[1])] = float(fields[3])
		elif 'inj' in line:
			fields = line.split()
			limInj[int(fields[1])] = float(fields[2])
		elif 'mu' in line:
			fields = line.split()
			mu[int(fields[1])] = float(fields[2])
	
	hpvalObs = TH1F("pvalObs","pvalObs",11,97.5,152.5)
	hsignObs = TH1F("signObs","signObs",11,97.5,152.5)
	hpvalExp = TH1F("pvalExp","pvalExp",11,97.5,152.5)
	hsignExp = TH1F("signExp","signExp",11,97.5,152.5)
	hpvalInj = TH1F("pvalInj","pvalInj",11,97.5,152.5)
	hsignInj = TH1F("signInj","signInj",11,97.5,152.5)
	hlimNSExp = TH1F("limNSExp","limNSExp",11,97.5,152.5)
	hlimExp   = TH1F("limExp","limExp",11,97.5,152.5)
	hlimObs   = TH1F("limObs","limObs",11,97.5,152.5)
	hpvalNSExp = TH1F("pvalNSExp","pvalNSExp",11,97.5,152.5)
	hsignNSExp = TH1F("signNSExp","signNSExp",11,97.5,152.5)
	
	for mass,val in signExp.iteritems():  hsignExp.SetBinContent(hsignExp.FindBin(mass),val)
	for mass,val in pvalExp.iteritems():  hpvalExp.SetBinContent(hpvalExp.FindBin(mass),val)
	for mass,val in signObs.iteritems():  hsignObs.SetBinContent(hsignObs.FindBin(mass),val)
	for mass,val in pvalObs.iteritems():  hpvalObs.SetBinContent(hpvalObs.FindBin(mass),val)
	for mass,val in signInj.iteritems():  hsignInj.SetBinContent(hsignInj.FindBin(mass),val)
	for mass,val in pvalInj.iteritems():  hpvalInj.SetBinContent(hpvalInj.FindBin(mass),val)
	for mass,val in limObs.iteritems():   hlimObs.SetBinContent(hlimObs.FindBin(mass),val)
	for mass,val in limExp.iteritems():   hlimExp.SetBinContent(hlimExp.FindBin(mass),val)
	for mass,val in limNSExp.iteritems(): hlimNSExp.SetBinContent(hlimNSExp.FindBin(mass),val)
	for mass,val in signNSExp.iteritems():  hsignNSExp.SetBinContent(hsignNSExp.FindBin(mass),val)
	for mass,val in pvalNSExp.iteritems():  hpvalNSExp.SetBinContent(hpvalNSExp.FindBin(mass),val)
	
	pcms1 = TPaveText(gStyle.GetPadLeftMargin()+0.01,1.-gStyle.GetPadTopMargin(),0.35,1.,"NDC")
	pcms1.SetTextFont(62)
	pcms1.SetTextSize(gStyle.GetPadTopMargin()*3./4.)
	pcms1.SetBorderSize(0)
	pcms1.SetFillStyle(-1)
	pcms1.SetTextAlign(12)
	pcms1.AddText("CMS")
	
	pcms2 = TPaveText(0.5,1.-gStyle.GetPadTopMargin(),1.-gStyle.GetPadRightMargin(),1.,"NDC")
	pcms2.SetTextFont(42)
	pcms2.SetTextSize(gStyle.GetPadTopMargin()*3./4.)
	pcms2.SetBorderSize(0)
	pcms2.SetFillStyle(-1)
	pcms2.SetTextAlign(32)
	pcms2.AddText("19.8 fb^{-1} (8TeV)")#+ 18.2 
	
	lines = [None]*2
	lines[0] = TF1("line1s","(1.-0.6827)/2.0",97.5,152.5) 
	lines[1] = TF1("line2s","(1.-0.9545)/2.0",97.5,152.5) 
	#lines[2] = TF1("line3s","(1.-0.9973)/2.0",99,151) 
	for l in lines:
		l.SetLineStyle(kDashed)
		l.SetLineWidth(1)
		l.SetLineColor(kRed)
	
	ps1 = TPaveText(149,((1.-0.6827)/2.0)*0.85,151,(1.-0.6827)/2.0*0.85)
	ps1.SetTextFont(42)
	ps1.SetTextSize(gStyle.GetPadTopMargin()*2.5/4.)
	ps1.SetBorderSize(0)
	ps1.SetFillStyle(-1)
	ps1.SetTextAlign(32)
	ps1.SetTextColor(kRed)
	ps1.AddText("1#sigma")
	
	ps2 = TPaveText(149,((1.-0.9545)/2.0)*0.85,151,(1.-0.9545)/2.0*0.85)
	ps2.SetTextFont(42)
	ps2.SetTextSize(gStyle.GetPadTopMargin()*2.5/4.)
	ps2.SetBorderSize(0)
	ps2.SetFillStyle(-1)
	ps2.SetTextAlign(32)
	ps2.SetTextColor(kRed)
	ps2.AddText("2#sigma")

	csign = TCanvas("csign","csign",900,750)
	csign.cd()
	gPad.SetTickx(1)
	hsignObs.SetMarkerStyle(20)
	hsignObs.SetMarkerSize(1.5)
	hsignObs.SetLineWidth(2)
	hsignExp.SetLineWidth(2)
	hsignInj.SetLineWidth(2)
	hsignNSExp.SetLineWidth(2)
	hsignExp.SetLineColor(kBlue)
	hsignNSExp.SetLineColor(kGreen+2)
	hsignInj.SetLineColor(kBlue)
	hsignInj.SetLineStyle(kDashed)
	hsignNSExp.SetLineStyle(kDashDotted)
	hsignObs.GetXaxis().SetLimits(97.5,152.5)
	hsignExp.GetXaxis().SetLimits(97.5,152.5)
	hsignInj.GetXaxis().SetLimits(97.5,152.5)
	hsignObs.GetXaxis().SetTitle("Higgs Mass (GeV)")
	hsignObs.GetYaxis().SetTitle("Significance")
	hsignObs.Draw("PL")
	hsignExp.Draw("Lsame")
	hsignInj.Draw("Lsame")
	hsignNSExp.Draw("Lsame")
	#leg = TLegend(0.58,0.1,1.-gPad.GetRightMargin()-0.03,1.-gPad.GetTopMargin()-0.03)
	leg = TLegend(0.48,0.1,1.-gPad.GetRightMargin()-0.03,0.37)
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	leg.AddEntry(hsignObs,"Observed","PL")
	leg.AddEntry(hsignExp,"Expected","L")
	leg.AddEntry(hsignNSExp,"Expected (No Syst)","L")
	leg.AddEntry(hsignInj,"Injected (m_{H}=125)","L")
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.055)
	leg.Draw()
	pcms1.Draw()
	pcms2.Draw()
	gPad.RedrawAxis()
	csign.SaveAs("limitplots/Significance_NoSyst.pdf")
	csign.SaveAs("limitplots/Significance_NoSyst.png")
	
	csign = TCanvas("csign","csign",900,750)
	csign.cd()
	gPad.SetTickx(1)
	hsignObs.SetMarkerStyle(20)
	hsignObs.SetMarkerSize(1.5)
	hsignObs.SetLineWidth(2)
	hsignExp.SetLineWidth(2)
	hsignInj.SetLineWidth(2)
	hsignExp.SetLineColor(kBlue)
	hsignInj.SetLineColor(kBlue)
	hsignInj.SetLineStyle(kDashed)
	hsignObs.GetXaxis().SetLimits(97.5,152.5)
	hsignExp.GetXaxis().SetLimits(97.5,152.5)
	hsignInj.GetXaxis().SetLimits(97.5,152.5)
	hsignObs.GetXaxis().SetTitle("Higgs Mass (GeV)")
	hsignObs.GetYaxis().SetTitle("Significance")
	hsignObs.Draw("PL")
	hsignExp.Draw("Lsame")
	hsignInj.Draw("Lsame")
	#leg = TLegend(0.58,0.1,1.-gPad.GetRightMargin()-0.03,1.-gPad.GetTopMargin()-0.03)
	leg = TLegend(0.48,0.1,1.-gPad.GetRightMargin()-0.03,0.37)
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	leg.AddEntry(hsignObs,"Observed","PL")
	leg.AddEntry(hsignExp,"Expected","L")
	leg.AddEntry(hsignInj,"Injected (m_{H}=125)","L")
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.055)
	leg.Draw()
	pcms1.Draw()
	pcms2.Draw()
	gPad.RedrawAxis()
	csign.SaveAs("limitplots/Significance.pdf")
	csign.SaveAs("limitplots/Significance.png")

	cpval = TCanvas("cpval","cpval",900,750)
	cpval.cd()
	gPad.SetTickx(1)
	hpvalObs.SetMarkerStyle(20)
	hpvalObs.SetMarkerSize(1.5)
	hpvalObs.SetLineWidth(2)
	hpvalExp.SetLineWidth(2)
	hpvalNSExp.SetLineWidth(2)
	hpvalInj.SetLineWidth(2)
	hpvalNSExp.SetLineColor(kGreen+2)
	hpvalExp.SetLineColor(kBlue)
	hpvalInj.SetLineColor(kBlue)
	hpvalInj.SetLineStyle(kDashed)
	hpvalNSExp.SetLineStyle(kDashDotted)
	gPad.SetLogy(1)
	hpvalObs.GetXaxis().SetLimits(97.5,152.5)
	hpvalExp.GetXaxis().SetLimits(97.5,152.5)
	hpvalInj.GetXaxis().SetLimits(97.5,152.5)
	hpvalObs.GetYaxis().SetRangeUser(0.003,1.0)
	hpvalObs.GetXaxis().SetTitle("Higgs Mass (GeV)")
	hpvalObs.GetYaxis().SetTitle("p-value")
	hpvalObs.Draw("PL")
	hpvalExp.Draw("Lsame")
	hpvalInj.Draw("Lsame")
	hpvalNSExp.Draw("Lsame")
	#leg = TLegend(0.3,0.1,0.55,1-gPad.GetTopMargin()-0.03)
	leg = TLegend(0.58,0.1,1.-gPad.GetRightMargin()-0.03,0.37)
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	leg.AddEntry(hpvalObs,"Observed","PL")
	leg.AddEntry(hpvalExp,"Expected","L")
	leg.AddEntry(hpvalNSExp,"Expected (No Syst)","L")
	leg.AddEntry(hpvalInj,"Injected (m_{H}=125)","L")
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.055)
	leg.Draw()
	pcms1.Draw()
	pcms2.Draw()
	ps1.Draw()
	ps2.Draw()
	for l in lines: l.Draw("same")
	gPad.RedrawAxis()
	cpval.SaveAs("limitplots/pValue_NoSyst.pdf")
	cpval.SaveAs("limitplots/pValue_NoSyst.png")
	
	cpval = TCanvas("cpval","cpval",900,750)
	cpval.cd()
	gPad.SetTickx(1)
	hpvalObs.SetMarkerStyle(20)
	hpvalObs.SetMarkerSize(1.5)
	hpvalObs.SetLineWidth(2)
	hpvalExp.SetLineWidth(2)
	hpvalInj.SetLineWidth(2)
	hpvalExp.SetLineColor(kBlue)
	hpvalInj.SetLineColor(kBlue)
	hpvalInj.SetLineStyle(kDashed)
	gPad.SetLogy(1)
	hpvalObs.GetXaxis().SetLimits(97.5,152.5)
	hpvalExp.GetXaxis().SetLimits(97.5,152.5)
	hpvalInj.GetXaxis().SetLimits(97.5,152.5)
	hpvalObs.GetYaxis().SetRangeUser(0.003,1.0)
	hpvalObs.GetXaxis().SetTitle("Higgs Mass (GeV)")
	hpvalObs.GetYaxis().SetTitle("p-value")
	hpvalObs.Draw("PL")
	hpvalExp.Draw("Lsame")
	hpvalInj.Draw("Lsame")
	#leg = TLegend(0.3,0.1,0.55,1-gPad.GetTopMargin()-0.03)
	leg = TLegend(0.58,0.1,1.-gPad.GetRightMargin()-0.03,0.37)
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	leg.AddEntry(hpvalObs,"Observed","PL")
	leg.AddEntry(hpvalExp,"Expected","L")
	leg.AddEntry(hpvalInj,"Injected (m_{H}=125)","L")
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.055)
	leg.Draw()
	pcms1.Draw()
	pcms2.Draw()
	ps1.Draw()
	ps2.Draw()
	for l in lines: l.Draw("same")
	gPad.RedrawAxis()
	cpval.SaveAs("limitplots/pValue.pdf")
	cpval.SaveAs("limitplots/pValue.png")

	climi = TCanvas("climi","climi",900,750)
	climi.cd()
	gPad.SetTickx(1)
	hlimObs.SetMarkerStyle(20)
	hlimObs.SetMarkerSize(1.5)
	hlimObs.SetLineWidth(2)
	hlimExp.SetLineWidth(2)
	hlimNSExp.SetLineWidth(2)
	hlimNSExp.SetLineColor(kGreen+2)
	hlimNSExp.SetLineStyle(kDashDotted)
	hlimObs.GetXaxis().SetLimits(97.5,152.5)
	hlimExp.GetXaxis().SetLimits(97.5,152.5)
	hlimNSExp.GetXaxis().SetLimits(97.5,152.5)
	hlimExp.GetYaxis().SetRangeUser(0.0,hlimExp.GetBinContent(hlimExp.GetMaximumBin())*1.1)
	hlimExp.GetXaxis().SetTitleOffset(0.9)
	hlimExp.GetXaxis().SetTitle("Higgs Mass (GeV)")
	hlimExp.GetYaxis().SetTitle("95% Asymptotic CL Limit on #sigma/#sigma_{SM}")
	hlimExp.Draw("L")
	hlimNSExp.Draw("Lsame")
	#hlimObs.Draw("LPsame")
	#leg = TLegend(0.3,0.1,0.55,1-gPad.GetTopMargin()-0.03)
	leg = TLegend(gPad.GetLeftMargin()+0.04,0.1,0.5,1.-gPad.GetTopMargin()-0.04)
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	#leg.AddEntry(hlimExp,"CL_{s} Observed","PL")
	leg.AddEntry(hlimExp,"CL_{s} Expected","L")
	leg.AddEntry(hlimNSExp,"CL_{s} Expected (No Syst)","L")
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.055)
	leg.Draw()
	line = TF1("line1","1.0",97.5,152.5)
	line.SetLineColor(kGray+2)
	line.SetLineStyle(kDotted)
	line.Draw("same")
	pcms1.Draw()
	pcms2.Draw()
	gPad.RedrawAxis()
	climi.SaveAs("limitplots/limit_NoSyst.pdf")
	climi.SaveAs("limitplots/limit_NoSyst.png")

	print "%8s | %26s | %26s | %26s | %8s "%("","expected","observed","injected","mu")
	print "%8s | %8s %8s %8s | %8s %8s %8s | %8s %8s %8s |"%("mass","limit","sign.","p-val","limit","sign.","p-val","limit","sign.","p-val")
	print "-"*(9*14+10)
	for mass in sorted(signExp.iterkeys()):
		print "%8d | %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f | %8.3g "%(mass,limExp[mass],signExp[mass],pvalExp[mass],limObs[mass],signObs[mass],pvalObs[mass],limInj[mass],signInj[mass],pvalInj[mass],mu[mass])

	print

	print "%8s | %26s | %26s | %26s | %8s "%("","expected","observed","injected","mu")
	print "%8s | %8s %8s %8s | %8s %8s %8s | %8s %8s %8s |"%("mass","limit","sign.","p-val","limit","sign.","p-val","limit","sign.","p-val")
	print "-"*(9*14+10)
	for mass in sorted(signExp.iterkeys()):
		print "%8d | %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f | %8.3f %8.3f %8.3f | %8.3g "%(mass,limNSExp[mass],signNSExp[mass],pvalNSExp[mass],0,0,0,0,0,0,0)

	os.chdir(basedir)


if __name__=='__main__':
	getPlots()
