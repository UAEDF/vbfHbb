#!/usr/bin/env python

import os,re,sys
import ROOT
from ROOT import *
from optparse import OptionParser

def PAVE(x1,y1,x2,y2,text,color):
	p = TPaveText(x1,y1,x2,y2)
	p.SetTextAlign(31)
	p.SetBorderSize(0)
	p.SetFillStyle(-1)
	p.SetTextFont(82)
	p.SetTextSize(0.018)
	p.SetTextColor(color)
	l = p.AddText(text)
	l.SetTextAngle(90.)
	return p

def PLOTNUISS(tag,mass):
	if not os.path.exists('plots'): os.makedirs('plots')
	
#	f = open("combine/nuissances%s.mH%s.txt"%(tag,mass),"r+")
#	lines = []
#	for il,l in enumerate(f.read().split('\n')):
#		l = l.replace('!','').replace('*','')
#		if il==0: continue
#		if l=="": continue
#		if "qcd_norm" in l: continue
#		entries = re.search('([A-Za-z0-9_\-]*) *([0-9+\-.]*), ([0-9+\-.]*) *([0-9+\-.]*), ([0-9+\-.]*) *([0-9+\-.]*).*',l).groups()
#		lines += [{}]
#		lines[-1]['name']  = entries[0] 
#		lines[-1]['b']  = float(entries[1]) 
#		lines[-1]['bsig']  = float(entries[2]) 
#		lines[-1]['bs'] = float(entries[3]) 
#		lines[-1]['bssig'] = float(entries[4]) 
#		lines[-1]['rho']   = float(entries[5]) 
#	
#	f.close()
	
	f = TFile.Open("combine/pulls%s_mH%s.root"%(tag,mass),"read")
	hbin = f.Get("h_pull_b")
	hbsin = f.Get("h_pull_s")
	hbsigin = f.Get("h_unc_b")
	hbssigin = f.Get("h_unc_s")
	
	gROOT.ProcessLineSync('gErrorIgnoreLevel = kWarning;')
	gROOT.ProcessLineSync('.x ../../../common/styleCMSTDR.C')
	gROOT.SetBatch(1)
	gStyle.SetPadRightMargin(0.02)
	gStyle.SetPadLeftMargin(0.085)
	gStyle.SetPadBottomMargin(0.30)
	
	paves = []
	pavessig = []
	
	n = hbin.GetNbinsX()
	c = TCanvas("c","c",1600,800)
	hb = TH1F("hb",";;pull",n+2,0,n+2)
	hbs = TH1F("hbs",";;pull",n+2,0,n+2)
	hbsig = TH1F("hbsig",";;#sigma_{post}/#sigma_{pre} - 1",n+2,0,n+2)
	hbssig = TH1F("hbssig",";;#sigma_{post}/#sigma_{pre} - 1",n+2,0,n+2)
	for ibin in range(2,n+2): 
#	for il,l in enumerate(lines):
		hb.SetBinContent(ibin,hbin.GetBinContent(ibin-1))
		hbs.SetBinContent(ibin,hbsin.GetBinContent(ibin-1))
		hbsig.SetBinContent(ibin,hbsigin.GetBinContent(ibin-1))
		hbssig.SetBinContent(ibin,hbssigin.GetBinContent(ibin-1))
		hbs.GetXaxis().SetBinLabel(ibin,"%s"%hbin.GetXaxis().GetBinLabel(ibin-1))
		hbssig.GetXaxis().SetBinLabel(ibin,hbsin.GetXaxis().GetBinLabel(ibin-1))
		paves += [PAVE(hbs.GetBinLowEdge(ibin),0.51,hbs.GetBinLowEdge(ibin)+hbs.GetBinWidth(ibin),0.73,"%.3f"%hb.GetBinContent(ibin),kBlack)]
		paves += [PAVE(hbs.GetBinLowEdge(ibin),0.73,hbs.GetBinLowEdge(ibin)+hbs.GetBinWidth(ibin),0.95,"%.3f"%hbs.GetBinContent(ibin),kRed)]
		pavessig += [PAVE(hbssig.GetBinLowEdge(ibin),-0.25,hbssig.GetBinLowEdge(ibin)+hbssig.GetBinWidth(ibin),-0.15,"%.3f"%(hbsig.GetBinContent(ibin)),kBlack)]
		pavessig += [PAVE(hbssig.GetBinLowEdge(ibin),-0.15,hbssig.GetBinLowEdge(ibin)+hbssig.GetBinWidth(ibin),-0.05,"%.3f"%(hbssig.GetBinContent(ibin)),kRed)]
	for ibin in [1,n+2]:
		hbs.GetXaxis().SetBinLabel(ibin,"")
		hbssig.GetXaxis().SetBinLabel(ibin,"")
	
	hb.SetLineColor(kBlack)
	hb.SetLineWidth(1)
	hbs.SetLineColor(kRed)
	hbs.SetLineWidth(1)
	hbs.SetFillColor(kRed-10)
	hbs.SetFillStyle(1001)
	hbs.GetXaxis().LabelsOption("v")
	hbs.GetXaxis().SetLabelSize(0.027)
	hbs.GetXaxis().SetTickLength(0.02)
	hbs.GetYaxis().SetRangeUser(-1.0,1.0)
	hbs.GetYaxis().SetTitleOffset(0.7)
	hbs.GetYaxis().SetNdivisions(505)
	gPad.SetTicks(1,1)
	

	leg = TLegend(0.8,0.4,0.9,0.5)
	leg.SetHeader("m_{H} = %s GeV"%mass)
	leg.AddEntry(hb,"b","L")
	leg.AddEntry(hbs,"b+s","F")
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(62)
	leg.SetTextSize(0.035)
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.038)
	
	hbs.Draw("hist")
	hb.Draw("histsame")
	lin = TLine(hbs.GetBinLowEdge(1),0.,hbs.GetBinLowEdge(hbs.GetNbinsX()),0.0)
	lin.SetLineStyle(7)
	lin.Draw("same")
	leg.Draw()
	c.SaveAs("plots/nuissances%s_mH%s_1.pdf"%(tag,mass))
	c.SaveAs("plots/nuissances%s_mH%s_1.png"%(tag,mass))

	for p in paves: p.Draw()
	c.SaveAs("plots/nuissances%s_mH%s_2.pdf"%(tag,mass))
	c.SaveAs("plots/nuissances%s_mH%s_2.png"%(tag,mass))

	hbsig.SetLineColor(kBlack)
	hbsig.SetLineWidth(1)
	hbssig.SetLineColor(kRed)
	hbssig.SetLineWidth(1)
	hbssig.SetFillColor(kRed-10)
	hbssig.SetFillStyle(1001)
	hbssig.GetXaxis().LabelsOption("v")
	hbssig.GetXaxis().SetLabelSize(0.027)
	hbssig.GetXaxis().SetTickLength(0.02)
	hbssig.GetYaxis().SetRangeUser(-0.3,0.3)
	hbssig.GetYaxis().SetTitleOffset(0.7)
	hbssig.GetYaxis().SetNdivisions(505)
	gPad.SetTicks(1,1)
	
	leg = TLegend(0.8,0.8,0.9,0.9)
	leg.SetHeader("m_{H} = %s GeV"%mass)
	leg.AddEntry(hb,"b","L")
	leg.AddEntry(hbs,"b+s","F")
	leg.SetFillStyle(-1)
	leg.SetBorderSize(0)
	leg.SetTextFont(62)
	leg.SetTextSize(0.035)
	leg.SetY1(leg.GetY2()-leg.GetNRows()*0.038)
	
	hbssig.Draw("hist")
	hbsig.Draw("histsame")
	lin = TLine(hbssig.GetBinLowEdge(1),0.,hbssig.GetBinLowEdge(hbssig.GetNbinsX()),0.0)
	lin.SetLineStyle(7)
	lin.Draw("same")
	leg.Draw()
	c.SaveAs("plots/nuissances%s_mH%s_3.pdf"%(tag,mass))
	c.SaveAs("plots/nuissances%s_mH%s_3.png"%(tag,mass))

	for p in pavessig: p.Draw()
	c.SaveAs("plots/nuissances%s_mH%s_4.pdf"%(tag,mass))
	c.SaveAs("plots/nuissances%s_mH%s_4.png"%(tag,mass))
	
	c.Close()
	f.Close()

if __name__=='__main__':
	mp = OptionParser()
	opts,args = mp.parse_args()

	PLOTNUISS(args[0],args[1])


