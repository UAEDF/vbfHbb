#!/usr/bin/env python

import os,sys,re,json
from optparse import OptionParser,OptionGroup
from array import array
from time import time

sys.path.append("../common")

from toolkit import *
import main

import ROOT
from ROOT import *


##################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	return mp 

##################################################
def estimate(ientry,nentries,tstart,tnow):
	tdelta   = tnow - tstart
	taverage = tdelta / float(ientry)
	nleft    = float(nentries - ientry) * taverage
	percdone = 100 - float(nentries - ientry) / float(nentries) * 100
	return floor(nleft/60.), nleft%60, percdone

##################################################
def useTree(tree):
	variableNames = ["pdfX1","pdfX2","pdfQ"]
	x1 = array('f',[-1.0])
	x2 = array('f',[-1.0])
	q  = array('f',[-1.0])
#	id1 = array('i',[-999])
#	id2 = array('i',[-999])
	variablesBare = { \
			"pdfX1":x1  , \
			"pdfX2":x2,   \
			"pdfQ":q \
			}
	variablesPDF = {}
	tree.SetBranchStatus("*",0)
	for v in variablesBare.keys():
		tree.SetBranchStatus(v,1)
		tree.SetBranchAddress(v,variablesBare[v])
	for v in variablesPDF.keys():
		tree.SetBranchStatus(v,1)
		tree.SetBranchAddress(v,variablesPDF[v])
	
	return variableNames,variablesBare,variablesPDF

##################################################
def createHist():
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")

	hx1    = TH1F("hx1","parton x1;parton x1",50,0.,1.)
	hx2    = TH1F("hx2","parton x2;parton x2",50,0.,1.)
	hx1x2  = TH2F("hx1x2","x2 vs. x1;parton x1;parton x2",50,0.,1.,50,0.,1.)
#	hid1   = TH1F("hid1","parton id1;parton id1",14,-7,7) 
#	hid2   = TH1F("hid2","parton id2;parton id2",14,-7,7)
	hq     = TH1F("hq","q;q;q",100,0.,500.)

	hBare = {"pdfX1":hx1,"pdfX2":hx2,"pdfQ":hq,"x1x2":hx1x2}#"id1":hid1,"id2":hid2,"x1x2":hx1x2}
	hPDF  = {}

	return hBare,hPDF

##################################################
def fillBare(fout,hBare,tree,variables):
	for v in variables.keys():
		if v in hBare.keys(): tree.Draw("%s>>%s"%(v,hBare[v].GetName()))
		else: print "No histogram defined for %s"%v
	tree.Draw("pdfX2:pdfX1>>%s"%hBare["x1x2"].GetName())
	return hBare

##################################################
def fillPDF(fout,hPDF,variables):
	for v in variables.keys():
		if v in hPDF.keys(): hPDF[v].Fill(variables[v][0])
		else: print "No histogram defined for %s"%v
	return hPDF

##################################################
def plotHist(fout,histos):
	makeDirs("./plots/PDF")
	fout.cd()
	for hname,h in histos.iteritems():
		c = TCanvas("c%s"%hname,"c%s"%hname,1800,1200)
		c.cd()
		h.SetLineColor(kRed+2)
		h.SetLineWidth(2)
		if h.IsA().GetName()=="TH1F": h.Draw()
		elif h.IsA().GetName()=="TH2F": h.Draw("colz")
		else: h.Draw()
		h.Write("%s"%h.GetName(),TH1.kOverwrite)
		if any([hname=="pdfX1",hname=="pdfX2",hname=="pdfQ"]): gPad.SetLogy(1)
		if any([hname=="x1x2"]): gPad.SetLogz(1) 
		c.Update()
		c.Write("%s"%c.GetName(),TH1.kOverwrite)
		c.SaveAs("./plots/PDF/%s.pdf"%c.GetName())
		c.SaveAs("./plots/PDF/%s.png"%c.GetName())
		c.Close()

##################################################
def mkUncPDF():
	# initialising
	opts,fout = main.main(parser(),True)

	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))

	##################################################	
	# reading sample properties
	sampleproperties = {}
	for s in opts.sample:
		sampleproperties[s] = {}
		sprops = sampleproperties[s]
		# load sample properties
		sprops['tag']    = s
		sprops['group']  = jsoninfo['groups'][s]
		sprops['file']   = [k for (k,v) in jsonsamp['files'].iteritems() if v['tag']==s][0]
		sprops['scale']  = jsonsamp['files'][sprops['file']]['scale']
		sprops['colour'] = jsonsamp['files'][sprops['file']]['colour']
		sprops['tfile']  = TFile(opts.globalpath+'/'+sprops['file'],"read")
		print sprops['tfile'].GetName()
		if sprops['tfile'].Get("Hbb/events"): sprops['ttree']  = sprops['tfile'].Get("Hbb/events")
		else:                                 sprops['ttree']  = None
		
	# summarize load block
	l1("Loaded properties for:")
	print "%s%15s | %15s | %8s | %15s | %40s | %15s | %15s |%s"%(blue,"tag","group","colour","scale","file","tree name","object type",plain)
	print "-"*(18*3 + 11 + 43 + 36 - 1)
	for sp in sampleproperties.itervalues():
		print "%15s | %15s | %8s | %15s | %40s | %15s | %15s |"%(sp["tag"],sp["group"],sp["colour"],sp["scale"],sp["file"],sp["ttree"].GetName() if not sp["ttree"]==None else "%s%15s%s"%(Red,"None",plain),sp["ttree"].IsA().GetName() if not sp["ttree"]==None else "%s%15s%s"%(Red,"None",plain))

	##################################################	
	# some ROOT settings
	gStyle.SetOptStat(0)
	gROOT.SetBatch(1)
	ROOT.gErrorIgnoreLevel = kWarning

	##################################################	
	# disable unused branches and loop
	for sp in sampleproperties.itervalues():
		l1("Working with sample: %s"%sp['tag'])
		tree = sp['ttree']
		variableNames,variablesBare,variablesPDF = useTree(tree)
		hBare,hPDF = createHist()
		hBare = fillBare(fout,hBare,tree,variablesBare)

		ientry   = 0
		nentries = tree.GetEntriesFast()
		tstart = time()
		while tree.GetEntry(ientry):
			if ientry%(round(nentries/10.,0))==0: 
				if not ientry==0: estmin,estsec,percdone = estimate(ientry,nentries,tstart,time())
				l3("processing event %8s / %-8s %28s"%(ientry,nentries,"( %24s )"%"%12.0fm %3.0fs left, %2.0f%% done"%(estmin,estsec,percdone) if ientry>0 else ""))
				#print variables["x1"][0],variables["x2"][0],variables["id1"][0],variables["id2"][0]
			# ...
			hPDF  = fillPDF(fout,hPDF,variablesPDF)
			ientry += 1
		
		plotHist(fout,hBare)
		plotHist(fout,hPDF)
			
	##################################################	
	l1("Main Done.")

##################################################
if __name__=="__main__":
	mkUncPDF()
