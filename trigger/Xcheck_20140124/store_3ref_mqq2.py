#!/usr/bin/env python

import os
import sys

import ROOT
from ROOT import *

def main():
#	gROOT.SetBatch(1)

	print "LOADING FILES..."
	f = [None]*4
	f[0] = TFile("/data/UAData/autumn2013/flatTree_QCD100_reformatted.root")
	f[1] = TFile("/data/UAData/autumn2013/flatTree_QCD250_reformatted.root")
	f[2] = TFile("/data/UAData/autumn2013/flatTree_QCD500_reformatted.root")
	f[3] = TFile("/data/UAData/autumn2013/flatTree_QCD1000_reformatted.root")
	f5 = TFile("store_3ref_mqq2.root","update")

	scale = [18280./x for x in [4.827581,98.051,3631.531688,67862.073529]]
	tags = ["num80","den80","numnoref","dennoref"]
	cutstring = "(runNo==1) && (jetPt[3]>30.) && (mqq[2]>700) && (mjjTrig>700) && (dEtaqq[2]>3.5) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1]) > 80.)"
	colours = {'40':kBlue-4,'80':kGreen-4,'noref':kOrange-2}
	markers = {'40':20,'80':20,'noref':22}

	print "FILLING..."
	for i in range(4):
		print "\033[1;31m\nSet %i\033[m"%i
		events = f[i].Get("Hbb/events")
		f5.cd()
		for j in tags:
			h = f5.Get("h%i%s;1"%(i,j))
			if h==None:
				h = TH1F("h%i%s"%(i,j),"h%i%s"%(i,j),21,2,9)
				h.Sumw2()
				print "(%s %s %s)*(%.10f)"%(cutstring,"&& (triggerResult[9]==49)" if 'num' in j else "","&& (triggerResult[14]==49)" if "40" in j else ("&& (triggerResult[15]==49)" if "80" in j else ""),scale[i]) 
				events.Draw("mqq[2]>>h%i%s"%(i,j),"(%s %s %s)*(%.10f)"%(cutstring,"&& (triggerResult[9]==49)" if 'num' in j else "","&& (triggerResult[14]==49)" if "40" in j else ("&& (triggerResult[15]==49)" if "80" in j else ""),scale[i]))
				h.Write(h.GetName(),TH1.kOverwrite)
	f5.Close()

	f5 = TFile("store_3ref_mqq2.root","update")
	hs = {}
	for j in tags: 
		hs[j] = THStack("hs%s"%j,"hs%s"%(j))

	print "REREADING..."
	for i in range(4):
		for j in tags:
			hadd = f5.Get("h%i%s;1"%(i,j))
			hs[j].Add(hadd)

	print "STACKED & DIVIDING..."
	hrat = {}
	rtags = sorted(list(set([x[3:] for x in tags])))
	for j in rtags:
		hrat[j] = TEfficiency()
		hrat[j].SetPassedHistogram(hs["num%s"%j].GetStack().Last(),'f')
		hrat[j].SetTotalHistogram(hs["den%s"%j].GetStack().Last(),'f')

	c = TCanvas("c1","c1",3000,2000)
	c.cd()
		
	for j in rtags: hrat[j].Paint("")

	hrat['noref'].Draw()
	gPad.Update()
	gPad.Modified()
	c.Update()
	c.Modified()
	
	legend = TLegend(0.1,0.75,0.2,0.9,"QCD")
	legend.SetTextSize(0.030)

	grat = {}
	for jj,j in enumerate(rtags): 
		grat[j] = hrat[j].GetPaintedGraph()
		grat[j].GetXaxis().SetTitle('m_{q#bar{q}} (b-lik VBF)')
		grat[j].GetYaxis().SetTitle('trigger efficiency')
		grat[j].GetYaxis().SetRangeUser(0,1.0)
		grat[j].SetMarkerColor(colours[j])
		grat[j].SetMarkerStyle(markers[j])
		grat[j].SetMarkerSize(2.0)
		gPad.Modified()
		if jj==0: grat[j].Draw("AP")
		grat[j].Draw("EPsame")
		gPad.WaitPrimitive()
		legend.AddEntry(grat[j],j,'P')
	legend.Draw()
	
	c.SaveAs("trigger_1d_mqq2.png")
	c.Close()

	for i in range(4):
		f[i].Close()
	f5.Close()



if __name__=="__main__":
	main()
