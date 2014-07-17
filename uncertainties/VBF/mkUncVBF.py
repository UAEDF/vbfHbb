#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

import main
from optparse import OptionParser,OptionGroup
from copy import deepcopy as dc
from toolkit import *
from dependencyFactory import *
from write_cuts import *
from array import array
from random import random

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mgm  = OptionGroup(mp,cyan+"Main options"+plain)
	mgm.add_option('-o','--outputfile',help=blue+"Name of output file."+plain,dest='outputfile',default="%s/../uncertainties/rootfiles/vbfHbb.root"%basepath)

	mgtc = OptionGroup(mp,cyan+"Uncertainty settings"+plain)
	mgtc.add_option('-s','--samples',help=blue+'List of samples (VBF).'+plain,dest='samples',type="str",default=[],action='callback',callback=optsplit)
	mgtc.add_option('-c','--categoryboundaries',help=blue+'Boundaries for categories.'+plain,dest='categoryboundaries',type="str",default=[0,0.25,0.70,0.88,1.001],action='callback',callback=optsplit)

	mp.add_option_group(mgm)
	mp.add_option_group(mgtc)
	return mp

####################################################################################################
def getResult(opts,fout):
# setup
	c = TCanvas("c_Unc_VBF_Acceptance","Unc_VBF_Acceptance",1800,1200)
	binsx = array('f',opts.categoryboundaries)
	binlabelsx = ["CAT%d"%x for x in range(len(binsx))]
	h = TH1F("h_Unc_VBF_Acceptance","Unc_VBF_Acceptance;MVA;Acceptance",len(binsx)-1,binsx)
	for i in range(1000): h.Fill(random())
	for i in range(1,h.GetNbinsX()+1): h.GetXaxis().SetBinLabel(i,binlabelsx[i-1])
	h.GetXaxis().SetTickLength(0)
	h.GetYaxis().SetTickLength(0.02)
	h.GetYaxis().SetRangeUser(0,500)
# draw
	c.cd()
	h.Draw()
# add lines
	gPad.Update()
	lines = []
	for ii,i in enumerate(binsx[1:-1]): 
		lines += [TLine(i,gPad.GetUymin(),i,gPad.GetUymax()*0.04)]
		lines[ii].SetLineWidth(1)
		lines[ii].Draw("same")
# show/save
	c.Update()
	c.WaitPrimitive()
	c.Close()

	return 0

####################################################################################################
def getCanvases(opts,fout):
	return 0

####################################################################################################
###def extraText(hcenter,vcenter,line,fontSize=0.018,fontColor=kBlack):
###	text = TPaveText(hcenter-0.2+0.15,vcenter-0.2+0.05,hcenter+0.2+0.15,vcenter+0.2+0.05)
###	text.SetTextAlign(22)
###	text.SetTextSize(fontSize)
###	text.SetTextColor(fontColor)
###	text.SetFillStyle(0)
###	text.SetBorderSize(0)
###	theline = text.AddText(line)
###	theline.SetTextAngle(70)
###	return text
###
###def printText(top,left,sample,fontSize=0.020,fontColor=kBlack):
###	nlines = 4
###	right = left + 0.13
###	bottom = top - nlines*(fontSize+0.018)
###	text = TPaveText(left,bottom,right,top,"NDC")
###	text.SetFillColor(0)
###	text.SetFillStyle(0)
###	text.SetBorderSize(0)
###	text.SetTextSize(fontSize)
###	text.SetTextColor(fontColor)
###	text.SetTextAlign(11)
###	text.AddText("CMS preliminary")
###	text.AddText("VBF H#rightarrow b#bar{b}")
###	text.AddText("Nominal selection")
###	text.AddText("sample: %s"%sample)
###	thisline = text.AddText("#varepsilon = #frac{#varepsilon_{%s #times data}}{#varepsilon_{%s #times qcd}}"%(sample,sample))
###	thisline.SetTextAlign(13)
###	return text

####################################################################################################
def mkTriggerUncertainties():
	mp = parser()
	opts,args = mp.parse_args()

	fout = TFile(opts.outputfile,"update")
	gROOT.SetBatch(0)
	gStyle.SetOptStat(0)

	getResult(opts,fout)
	getCanvases(opts,fout)

	fout.Close()

if __name__=='__main__':
	mkTriggerUncertainties()
