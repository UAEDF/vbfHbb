#!/usr/bin/env python

import os
import sys

import ROOT
from ROOT import *

def main():
	f1 = TFile("/data/UAData/autumn2013.old/flatTree_QCD100_reformatted.root")
	f2 = TFile("/data/UAData/autumn2013.old/flatTree_QCD250_reformatted.root")
	f3 = TFile("/data/UAData/autumn2013.old/flatTree_QCD500_reformatted.root")
	f4 = TFile("/data/UAData/autumn2013.old/flatTree_QCD1000_reformatted.root")
	f5 = TFile("store.root","update")

	events = f1.Get("Hbb/events")
	f5.cd()
	print "Set 1"
	h1num = f5.Get("h1num;1")
	h1den = f5.Get("h1den;1")
	h1numnoref = f5.Get("h1numnoref;1")
	h1dennoref = f5.Get("h1dennoref;1")
	if h1num == None:
		events.Draw("mqq[2]>>h1num(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49) && (triggerResult[15]==49))*(18200*1./4.837581)")
		ROOT.h1num.Write()
		events.Draw("mqq[2]>>h1den(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[15]==49))*(18200*1./4.837581)")
		ROOT.h1den.Write()
		events.Draw("mqq[2]>>h1numnoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49))*(18200*1./4.837581)")
		ROOT.h1numnoref.Write()
		events.Draw("mqq[2]>>h1dennoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5))*(18200*1./4.837581)")
		ROOT.h1dennoref.Write()
	events = f2.Get("Hbb/events")
	f5.cd()
	print "Set 2"
	h2num = f5.Get("h2num;1")
	h2den = f5.Get("h2den;1")
	h2numnoref = f5.Get("h2numnoref;1")
	h2dennoref = f5.Get("h2dennoref;1")
	if h2num == None:
		events.Draw("mqq[2]>>h2num(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49) && (triggerResult[15]==49))*(18200*1./98.051000)")
		ROOT.h2num.Write()
		events.Draw("mqq[2]>>h2den(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[15]==49))*(18200*1./98.051000)")
		ROOT.h2den.Write()
		events.Draw("mqq[2]>>h2numnoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49))*(18200*1./98.051000)")
		ROOT.h2numnoref.Write()
		events.Draw("mqq[2]>>h2dennoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5))*(18200*1./98.051000)")
		ROOT.h2dennoref.Write()
	events = f3.Get("Hbb/events")
	f5.cd()
	print "Set 3"
	h3num = f5.Get("h3num;1")
	h3den = f5.Get("h3den;1")
	h3numnoref = f5.Get("h3numnoref;1")
	h3dennoref = f5.Get("h3dennoref;1")
	if h3num == None:
		events.Draw("mqq[2]>>h3num(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49) && (triggerResult[15]==49))*(18200*1./3631.531688)")
		ROOT.h3num.Write()
		events.Draw("mqq[2]>>h3den(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[15]==49))*(18200*1./3631.531688)")
		ROOT.h3den.Write()
		events.Draw("mqq[2]>>h3numnoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49))*(18200*1./3631.531688)")
		ROOT.h3numnoref.Write()
		events.Draw("mqq[2]>>h3dennoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5))*(18200*1./3631.531688)")
		ROOT.h3dennoref.Write()
	events = f4.Get("Hbb/events")
	f5.cd()
	print "Set 4"
	h4num = f5.Get("h4num;1")
	h4den = f5.Get("h4den;1")
	h4numnoref = f5.Get("h4numnoref;1")
	h4dennoref = f5.Get("h4dennoref;1")
	if h4num == None:
		events.Draw("mqq[2]>>h4num(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49) && (triggerResult[15]==49))*(18200*1./67862.073529)")
		ROOT.h4num.Write()
		events.Draw("mqq[2]>>h4den(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[15]==49))*(18200*1./67862.073529)")
		ROOT.h4den.Write()
		events.Draw("mqq[2]>>h4numnoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5) && (triggerResult[9]==49))*(18200*1./67862.073529)")
		ROOT.h4numnoref.Write()
		events.Draw("mqq[2]>>h4dennoref(100,0,2000)","((runNo==1) && (jetPt[1]>35.) && (dEtaqq[2]>3.5))*(18200*1./67862.073529)")
		ROOT.h4dennoref.Write()
	
	f5.ls()

	hsnum = THStack("hsnum","hsnum")
	hsden = THStack("hsden","hsden")
	hsnumnoref = THStack("hsnumnoref","hsnumnoref")
	hsdennoref = THStack("hsdennoref","hsdennoref")

	f5.ls()

	hsnum.Add(h1num)
	hsnum.Add(h2num)
	hsnum.Add(h3num)
	hsnum.Add(h4num)
	hsden.Add(h1den)
	hsden.Add(h2den)
	hsden.Add(h3den)
	hsden.Add(h4den)
	hsnumnoref.Add(h1numnoref)
	hsnumnoref.Add(h2numnoref)
	hsnumnoref.Add(h3numnoref)
	hsnumnoref.Add(h4numnoref)
	hsdennoref.Add(h1dennoref)
	hsdennoref.Add(h2dennoref)
	hsdennoref.Add(h3dennoref)
	hsdennoref.Add(h4dennoref)

	f5.ls()

	#hrat = TEfficiency(hsnum.GetStack().Last(),hsden.GetStack().Last())
	#hratnoref = TEfficiency(hsnumnoref.GetStack().Last(),hsdennoref.GetStack().Last())
	hrat = TEfficiency()
	hrat.SetPassedHistogram(hsnum.GetStack().Last(),'f')
	hrat.SetTotalHistogram(hsden.GetStack().Last(),'f')
	hratnoref = TEfficiency()
	hratnoref.SetPassedHistogram(hsnumnoref.GetStack().Last(),'f')
	hratnoref.SetTotalHistogram(hsdennoref.GetStack().Last(),'f')

	c = TCanvas()
	c.cd()
	hrat.Draw()
	hrat.Draw("same")
	c.SaveAs("quick.png")
	c.Close()

	f1.Close()
	f2.Close()
	f3.Close()
	f4.Close()
	f5.Close()



if __name__=="__main__":
	main()
