#!/usr/bin/env python

import ROOT
from ROOT import *
from array import array
from string import Template
import sys

def selections():
	f = TFile("/data/UAData/autumn2013/flatTree_VBFPowheg125_reformatted.root","read")
	t = f.Get("Hbb/events")

	trg = "(triggerResult[9]==49)"
	s = {}
	s["00-none"] = ""
	s["11-mqq600-avePt80"] = "(mqq[2]>600.) && (dEtaqq[2]>3.5) && (mjjTrig>600.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>80.) && (jetPt[3]>30.)"
	s["12-mqq700-avePt80"] = "(mqq[2]>700.) && (dEtaqq[2]>3.5) && (mjjTrig>700.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>80.) && (jetPt[3]>30.)"
	s["13-mqq800-avePt80"] = "(mqq[2]>800.) && (dEtaqq[2]>3.5) && (mjjTrig>800.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>80.) && (jetPt[3]>30.)"
	s["14-mqq900-avePt80"] = "(mqq[2]>900.) && (dEtaqq[2]>3.5) && (mjjTrig>900.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>80.) && (jetPt[3]>30.)"
	s["20-mqq700-avePt90"] = "(mqq[2]>700.) && (dEtaqq[2]>3.5) && (mjjTrig>700.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>90.) && (jetPt[3]>30.)"
	s["21-mqq700-avePt100"] = "(mqq[2]>700.) && (dEtaqq[2]>3.5) && (mjjTrig>700.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>100.) && (jetPt[3]>30.)"
	s["22-mqq700-avePt110"] = "(mqq[2]>700.) && (dEtaqq[2]>3.5) && (mjjTrig>700.) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>110.) && (jetPt[3]>30.)"
	
	c = {}
	for n,v in s.iteritems():
		print ' && '.join([v,trg])
		#c[n] = t.GetEntries('&&'.join([v,trg]))
		c[n] = 1
		print c[n]
	print
	
	for i1,(n1,v1) in enumerate(sorted(c.iteritems(),key=lambda (x,y):x)):
		if i1==0:
			print "%30s"%"selections" + " |",
			print "%20s |"%"entries"
			print "-"*(33+23-1)
		print "%30s |"%(n1),
		print "%20i |"%(v1)
	print

	for i1,(n1,v1) in enumerate(sorted(c.iteritems(),key=lambda (x,y):x)):
		if i1==0:
			print "%30s"%"selections" + " |",
			for i2,(n2,v2) in enumerate(sorted(c.iteritems(),key=lambda (x,y):x)):
				print "%10s |"%(n2[0:2]),
			print "\n"+"-"*(33+len(c.keys())*13-1)
		for i2,(n2,v2) in enumerate(sorted(c.iteritems(),key=lambda (x,y):x)):
			if i2==0: print "%30s |"%(n1),
			n1short = n1[:2]
			n2short = n2[:2]
			if n1short in ["20","21","22"] and n2short in ["12","13","14"]: print "%10s |"%"-",
			elif i2<=i1: print "%9.1f%% |"%(float(v1)/float(v2)*100.),
			else: print "%10s |"%"-",
		print
	print

	gStyle.SetOptStat(0)
	binsx = array('f',[600,650,700,750,800,850,900,950])#,1000,1050,1100])
	binsy = array('f',[0,20,40,60,80,100,125,150,175,200])#,225,250,275,300])
	signal_distribution = TH2F("signal_distribution","signal distribution after trigger and selection cuts;m_{q#bar{q}} [GeV/c^{2}];ptAve [GeV/c];",len(binsx)-1,binsx,len(binsy)-1,binsy)
	nentries = t.GetEntries("(dEtaqq[2]>3.5) && (runNo==1) && (dEtaTrig>3.5) && (jetPt[3]>30.) && (triggerResult[9]==49) && (mqq[2]>600) && (mjjTrig[2]>600) && (0.5*(jetPt[0]+jetPt[1])>0.)")
	sel = Template("(mqq[2]>$mqq) && (dEtaqq[2]>3.5) && (mjjTrig>$mqq) && (runNo==1) && (dEtaTrig>3.5) && (0.5*(jetPt[0]+jetPt[1])>$ptAve) && (jetPt[3]>30.) && (triggerResult[9]==49)")
	for ix,x in enumerate(binsx):
		for iy,y in enumerate(binsy):
			print sel.safe_substitute(mqq=x,ptAve=y)
			signal_distribution.Fill(x+0.1,y+0.1,float(t.GetEntries(sel.safe_substitute(mqq=x,ptAve=y)))/float(nentries))
			print "bin (%5i , %5i): %.f"%(x,y,signal_distribution.GetBinContent(ix,iy))
	print "Integral of 2D plot: %f"%signal_distribution.Integral()

	c = TCanvas("c","c",3000,2000)
	c.cd()
	signal_distribution.Draw("colz,text")
	c.SaveAs("signal_distribution-mqq2_dEtaqq2.png")
	c.SaveAs("signal_distribution-mqq2_dEtaqq2.pdf")
	c.Close()

	f.Close()

if __name__=='__main__':
	selections()
