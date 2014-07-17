#!/usr/bin/env python

import ROOT
from ROOT import *

import sys,os,re

####################################################################################################
def fopen():
	f = TFile("~/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_BJetPlusXC.root")
	t = f.Get("Hbb/events")
	t.SetBranchStatus("*",0)
	for i in ['jetPt','dEtaqq','mqq','jetBtag','btagIdx','triggerResult']: t.SetBranchStatus(i,1)
	return f,t

def init():
	gStyle.SetOptStat(0)
#	gStyle.SetOptTitle(0)

def copen(name):
	c = TCanvas(name,name,1200,800)
	return c

def fwrite(obj):
	obj.Write(obj.GetName(),TH1.kOverwrite)

def fsave(obj,dir,ext):
	obj.SaveAs("%s/%s.%s"%(dir,obj.GetName(),ext))

####################################################################################################

def inputs():
	cutcpp = "jetPt[0]>80 && jetPt[1]>70 && jetPt[2]>50 && jetPt[3]>40 && dEtaqq[1]>2.5 && mqq[1]>250 && jetBtag[btagIdx[0]]>0.244 && jetBtag[btagIdx[1]]>0.244 && (triggerResult[0]==1||triggerResult[1]==1)"
	vars = {'mqqvsdetaqq':'mqq[1]:dEtaqq[1]>>mqqvsdetaqq(56,2,9,200,0,2000)','jetpt0vsdetaqq':'jetPt[0]:dEtaqq[1]>>jetpt0vsdetaqq(56,2,9,250,0,500)'}
	return cutcpp,vars

####################################################################################################
def main():
	init()
	cutcpp,vars = inputs()
	plain = "\033[m"
	green = "\033[1;38;5;28m"
	
	fout = TFile("triggerExtras.root","update")
	if not os.path.exists('plots'): os.makedirs("plots")

	keylist = [x.GetName() for x in fout.GetListOfKeys()]

########################################
## Copy tree with selection if non-existant
	print green,"+ Loading TTree",plain
	if not "events" in keylist:
		f,t = fopen()

		fout.cd()
		tsmall = t.CopyTree(cutpp)
		fwrite(tsmall)

		f.Close()
## else load tree
	else:
		tsmall = fout.Get("events")
## select branches
	tsmall.SetBranchStatus("*",0)
	for i in ['jetPt','dEtaqq','mqq','jetBtag','btagIdx','triggerResult']: tsmall.SetBranchStatus(i,1)


########################################
## plot 2D scatter if non-existant, else load
	print green,"+ 2D scatter",plain
	for key,var in vars.iteritems(): 
		print green,"  ++ %s"%key,plain
		canvas = copen("%s"%key)
		if not key in keylist:
			tsmall.Draw(var,cutcpp)
			h = fout.FindObjectAny(key)
		else:
			h = fout.Get(key)
	
		h.SetTitle("2D scatter;%s;%s"%((var.split(':')[1]).split('>>')[0],var.split(':')[0]))
		h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*1.15)
		h.SetMarkerColor(kBlue)
		fwrite(h)
	
		canvas.cd()
		h.Draw()
		canvas.Update()
		fsave(canvas,"plots","png")
		canvas.Close()

########################################
## plot jetPt curves if non-existant, else load
	print green,"+ jetPt[i] in dEtaqq slices",plain
	fout.cd()
	canvas = copen("jetPti_slicesdEtaqq")
	canvas.Divide(3,2)

	h = [[],[],[],[]]
	c = [kBlack,kRed+1,kBlue+1,kGreen+2]
	nentries = tsmall.GetEntries()
	
	# create or load
	for i in range(6):
		for j in range(4):
			n = "hpt%i_%i"%(j,i)
			if not n in keylist:
				h[j] += [TH1F(n,n,90,20,200)]
				h[j][-1].SetLineColor(c[j])
			else:
				h[j] += [fout.Get(n)]

			h[j][-1].SetTitle("jetPt[%i] in slice dEtaqq[%d,%d];jetPt[%i];N"%(j,i+2,i+3,j))
			h[j][-1].GetYaxis().SetTitleOffset(h[j][-1].GetYaxis().GetTitleOffset()*1.2)
	
	# optional fill
	if not "hpt0_0" in keylist:
		# event loop
		for iev,ev in enumerate(tsmall):
			if iev%10000==0: print iev, "/", nentries
			# selection
			if (ev.jetPt[0]>80 and ev.jetPt[1]>70 and ev.jetPt[2]>50 and ev.jetPt[3]>40 and ev.mqq[1]>250 and ev.dEtaqq[1]>2.5 and ev.jetBtag[ev.btagIdx[0]]>0.244 and ev.jetBtag[ev.btagIdx[1]]>0.244 and (ev.triggerResult[0]==1 or ev.triggerResult[1]==1)):
				# eta slices
				for detaqqcut in range(2,9):
					if ev.dEtaqq[1]>detaqqcut and ev.dEtaqq[1]>detaqqcut+1:
						# four pt's
						for j in range(4):
							h[j][detaqqcut-2].Fill(ev.jetPt[j])
	
	# draw
	for j,hj in reversed(list(enumerate(h))):
		for i,hji in enumerate(hj):
			print i,hji.GetName(),j==len(h)-1
			canvas.cd(i+1)
			gPad.SetLeftMargin(0.15)
			hji.Draw("" if j==len(h)-1 else "same")
			fwrite(hji)

	# save
	canvas.Update()
	fsave(canvas,"plots","png")

	fout.Close()

####################################################################################################
####################################################################################################
if __name__=='__main__':
	main()
