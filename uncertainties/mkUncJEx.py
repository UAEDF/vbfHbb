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
def time01(tstart,tnow,previous=[]):
	tdelta    = tnow - tstart
	previous += [tdelta]
	taverage  = sum(previous)/float(len(previous)) 
	return taverage

##################################################
def style01(h,color=kBlack,fill=None,line=1):
	h.SetLineColor(color)
	h.SetLineStyle(line)
	if fill==None: h.SetLineWidth(2)
	if not fill==None: 
		h.SetFillColor(fill)
		h.SetFillStyle(4030)
	return h
	
##################################################
def struct01(c,h,hp,hm):
	c.cd()
	p1 = TPad("ptop","ptop",0.0,0.30,1.0,1.0)
	p2 = TPad("pbot","pbot",0.0,0.0,1.0,0.30)
	p1.SetRightMargin(0.22)
	p1.SetBottomMargin(0)
	p2.SetRightMargin(0.22)
	p2.SetTopMargin(0)
	p1.Draw()
	p2.Draw()

	c.Update()

	h.Scale(1./h.Integral())
	hp.Scale(1./hp.Integral())
	hm.Scale(1./hm.Integral())

	p2.cd()
	rhp = hp.Clone("rhp")
	rhp.Divide(h)
	rhp.GetYaxis().SetRangeUser(0.8,1.2)
	rhm = hm.Clone("rhm")
	rhm.Divide(h)
	rhm.GetYaxis().SetRangeUser(0.8,1.2)
	rhp.DrawCopy("")
	rhm.DrawCopy("same")

	p2.Update()
	l = TLine(p2.GetUxmin(),1,p2.GetUxmax(),1)
	l.SetLineWidth(2)
	l.SetLineColor(kBlack)
	l.Draw()
	p2.Update()

	p1.cd()
	h.Draw("hist")
	hp.Draw("same,hist")
	hm.Draw("same,hist")

	c.Update()
	return c

##################################################
def mkUncJEx():
	##################################################	
	# initialising
	opts,fout = main.main(parser(),True)
	fout.cd()

	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))

	##################################################	
	# some ROOT settings
	gStyle.SetOptStat(0)
	gROOT.SetBatch(1)
	ROOT.gErrorIgnoreLevel = kWarning
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")
	#gStyle.SetLabelFont(43,"XYZ")
	#gStyle.SetLabelSize(35,"XYZ")
	#gStyle.SetTitleFont(43,"XYZ")
	#gStyle.SetTitleSize(40,"XYZ")
	#gStyle.SetLabelOffset(4.0,"XY")
	#gStyle.SetTitleOffset(4.3,"XY")
	
	##################################################	
	# reading sample properties
	friends = ["HbbJESUp","HbbJESDn","HbbJERUp","HbbJERDn"] 
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
		#print sprops['tfile'].GetName()
		if sprops['tfile'].Get("Hbb/events"): 
			sprops['ttree'] = sprops['tfile'].Get("Hbb/events")
			for f in friends: 
				if sprops['tfile'].Get("%s/events"%f): sprops['ttree'].AddFriend("events%s = %s/events"%(f.lstrip("Hbb"),f))
		min = [0,0,0,-1,-1]
		max = [300,400,400,1,1]
		bin = [30,40,40,20,20]
		set = [None,None,None,array('f',[-1.001,0.0,0.25,0.70,0.88,1.001]),array('f',[-1.001,0.0,0.3,0.65,1.001])]

		for ncat in ["%s"%x for x in ['Hbb']+friends]:
			sprops[ncat] = {}
			for inh,nh in enumerate(['mbbReg','jetPt','jetPtUnsmeared','mvaNOM','mvaVBF']):
				if set[inh]: sprops[ncat][nh] = TH1F("h_%s_%s_%s"%(s,ncat,nh),"h_%s_%s_%s;%s;N"%(s,ncat,nh,nh),len(set[inh])-1,set[inh])
				else: sprops[ncat][nh] = TH1F("h_%s_%s_%s"%(s,ncat,nh),"h_%s_%s_%s;%s;N"%(s,ncat,nh,nh),bin[inh],min[inh],max[inh])

	# summarize load block
	l1("Loaded properties for:")
	print "%s%12s | %12s | %8s | %15s | %40s | %15s | %15s | %40s |%s"%(blue,"tag","group","colour","scale","file","tree name","object type","friends",plain)
	print "-"*(15*2 + 11 + 18 + 43 + 36 + 43 - 1)
	for sp in sampleproperties.itervalues():
		print "%12s | %12s | %8s | %15s | %40s | %15s | %15s | %40s"%( \
				sp["tag"],sp["group"],sp["colour"],sp["scale"],sp["file"], \
				sp["ttree"].GetName() if not sp["ttree"]==None else "%s%15s%s"%(Red,"None",plain), \
				sp["ttree"].IsA().GetName() if not sp["ttree"]==None else "%s%15s%s"%(Red,"None",plain), \
				", ".join([x.GetName() for x in sprops["ttree"].GetListOfFriends()]) if not sprops["ttree"].GetListOfFriends()==None else "%s%30s%s"%(Red,"None",plain) \
				)

	##################################################	
	# loop
	makeDirs("plots/uncertainties")
	c = {}
	c["JES"] = {}
	c["JER"] = {}
	for isp,sp in enumerate(sampleproperties.itervalues()):
		c["JES"][sp['tag']] = {}
		c["JER"][sp['tag']] = {}
		for inh,nh in enumerate(['mbbReg','jetPt','jetPtUnsmeared','mvaNOM','mvaVBF']):
			c["JES"][sp['tag']][nh] = TCanvas("c_JES_%s_%s"%(sp['tag'],nh),"c_JES_%s_%s"%(sp['tag'],nh),1800,1800)
			c["JER"][sp['tag']][nh] = TCanvas("c_JER_%s_%s"%(sp['tag'],nh),"c_JER_%s_%s"%(sp['tag'],nh),1800,1800)

	for isp,sp in enumerate(sampleproperties.itervalues()):
		# start
		l1("Working with sample: %s"%sp['tag'])
		tree = sp['ttree']
		treedraw = tree.Draw
		tarray = []

		for incat,ncat in enumerate(["Hbb"]+friends):
			l2("Category %s"%ncat)
			for inh,nh in enumerate(['mbbReg','jetPt','jetPtUnsmeared','mvaNOM','mvaVBF']):
				tstart = time()
				l3("%-40s %-40s"%("Variable %s"%nh,"(time expected %.fs + %d modules)"%(tarray[-1]*((5-inh)+(4-incat)*5) if len(tarray)>0 else -999,len(sampleproperties)-isp-1)))
	
				h = sp[ncat][nh]
				h.Reset()
				if not ncat=="Hbb": treedraw("%s.%s>>%s"%(ncat.replace("Hbb","events"),nh,h.GetName()),"")
				else: treedraw("%s>>%s"%(nh,h.GetName()),"")
				tnow = time()
				tarray += [time01(tstart,tnow,tarray)]

		for inh,nh in enumerate(['mbbReg','jetPt','jetPtUnsmeared','mvaNOM','mvaVBF']):
			# JES Up/Dn
			sp["Hbb"][nh] = style01(sp["Hbb"][nh],kBlack,kGray)
			sp["HbbJESUp"][nh] = style01(sp["HbbJESUp"][nh],kBlue+1,None,1)#7
			sp["HbbJESDn"][nh] = style01(sp["HbbJESDn"][nh],kRed+1,None,1)#10
			c["JES"][sp['tag']][nh] = struct01(c["JES"][sp['tag']][nh],sp["Hbb"][nh],sp["HbbJESUp"][nh],sp["HbbJESDn"][nh])
	
			# JER Up/Dn
			npad = 1 + inh + isp*5
			#sp["Hbb"][nh] = style01(sp["Hbb"][nh],kBlack,kGray)
			sp["HbbJERUp"][nh] = style01(sp["HbbJERUp"][nh],kBlue+1,None,1)#7
			sp["HbbJERDn"][nh] = style01(sp["HbbJERDn"][nh],kRed+1,None,1)#10
			c["JER"][sp['tag']][nh] = struct01(c["JER"][sp['tag']][nh],sp["Hbb"][nh],sp["HbbJERUp"][nh],sp["HbbJERDn"][nh])
			
			c["JES"][sp['tag']][nh].Update()
			c["JES"][sp['tag']][nh].SaveAs("plots/uncertainties/%s.png"%c["JES"][sp['tag']][nh].GetName())
			c["JES"][sp['tag']][nh].Close()
			c["JER"][sp['tag']][nh].Update()
			c["JER"][sp['tag']][nh].SaveAs("plots/uncertainties/%s.png"%c["JER"][sp['tag']][nh].GetName())
			c["JER"][sp['tag']][nh].Close()

	##################################################	
	l1("Main Done.")
	fout.Close()

##################################################
if __name__=="__main__":
	mkUncJEx()
