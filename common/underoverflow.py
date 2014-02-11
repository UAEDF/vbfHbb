#!/usr/bin/env python

import os
import sys
import array
from optparse import OptionParser

import ROOT
from ROOT import *

def main(fname,hname):
	gStyle.SetOptStat(0)

	f = TFile(fname,'read')
	h = f.Get(hname)
	
	print h

	binsX = []
	for i in range(h.GetNbinsX()+2): binsX += [h.GetXaxis().GetBinLowEdge(i)]
	binsX += [h.GetXaxis().GetBinLowEdge(i)+h.GetXaxis().GetBinWidth(i)]
	binsY = []
	for i in range(h.GetNbinsY()+2): binsY += [h.GetYaxis().GetBinLowEdge(i)]
	binsY += [h.GetYaxis().GetBinLowEdge(i)+h.GetYaxis().GetBinWidth(i)]

	binsX_array = array.array('f',binsX)
	binsY_array = array.array('f',binsY)

	hbig = TH2F("extended","extended",h.GetNbinsX()+2,binsX_array,h.GetNbinsY()+2,binsY_array)
	hbig.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
	hbig.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
	hbig.SetTitle(h.GetTitle())

	for i in range(h.GetNbinsX()+2):
		for j in range(h.GetNbinsY()+2):
			hbig.SetBinContent(i+1,j+1,h.GetBinContent(i,j))
			hbig.SetBinError(i+1,j+1,h.GetBinError(i,j))
	c = TCanvas("extended","extended",1600,1200)
	c.cd()
	hbig.Draw("error,text,colz")
	gPad.Update()
	x0 = h.GetXaxis().GetBinLowEdge(1)
	y0 = h.GetYaxis().GetBinLowEdge(1)
	x1 = h.GetXaxis().GetBinLowEdge(h.GetNbinsX()+1)
	y1 = h.GetYaxis().GetBinLowEdge(h.GetNbinsY()+1)
	l1 = TLine(x0,y0,x1,y0)
	l2 = TLine(x0,y0,x0,y1)
	l3 = TLine(x1,y0,x1,y1)
	l4 = TLine(x0,y1,x1,y1)
	l1.SetLineWidth(3)
	l2.SetLineWidth(3)
	l3.SetLineWidth(3)
	l4.SetLineWidth(3)
	l1.SetLineColor(kMagenta)
	l2.SetLineColor(kMagenta)
	l3.SetLineColor(kMagenta)
	l4.SetLineColor(kMagenta)
	l1.Draw("same")
	l2.Draw("same")
	l3.Draw("same")
	l4.Draw("same")

	c.SaveAs("extended.png")
	c.Close()

if __name__=="__main__":
	mp = OptionParser()
	opts,args = mp.parse_args()
	main(args[0],args[1])
