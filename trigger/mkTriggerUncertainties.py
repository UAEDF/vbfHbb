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

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mgm  = OptionGroup(mp,cyan+"Main options"+plain)
	mgm.add_option('-o','--outputfile',help=blue+"Name of output file."+plain,dest='outputfile',default="%s/rootfiles/vbfHbb.root"%basepath)

	mgtc = OptionGroup(mp,cyan+"Trigger uncertainty settings"+plain)
#	mgtc.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
#	mgtc.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mgtc.add_option('--ftwodmaps',help=blue+'Filename for twodmaps.'+plain,dest='ftwodmaps',default="",type="str")
	mgtc.add_option('--fdistmaps',help=blue+'Filename for distmaps.'+plain,dest='fdistmaps',default="",type="str")
	mgtc.add_option('-s','--samples',help=blue+'List of samples (distmap).'+plain,dest='samples',type="str",default=[],action='callback',callback=optsplit)

	mp.add_option_group(mgm)
	mp.add_option_group(mgtc)
	return mp

####################################################################################################
def getTwoDMaps(opts,fout):
	fin = TFile(opts.ftwodmaps,"read")
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"2DMaps/")

	fin.cd()
	m = {}
	for i in ['JetMon','QCD','JetMon-QCD']:
		gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))
		for j in gDirectory.GetListOfKeys():
			#print i,j.GetName()
			if '%s-Rat'%i in j.GetName(): 
				m[i] = fin.Get("2DMaps/%s/%s"%(i,j.GetName()))
				m[i].SetName("ScaleFactorMap_%s"%i)
				gDirectory.cd("%s:/2DMaps/"%(fout.GetName()))
				m[i].Write(m[i].GetName(),TH1.kOverwrite)
				gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))
	
	fout.Write()
	fin.Close()

##################################################
def getDistMaps(opts,fout):
	fin = TFile(opts.fdistmaps,"read")
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"DistMaps/")

	fin.cd()
	m = {}
	for i in opts.samples:
		gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))
		for j in gDirectory.GetListOfKeys():
			#print i,j.GetName()
			if '%s-Num'%i in j.GetName(): 
				try: cat = re.search("(mvaNOMC|CAT)([0-9]{1})",j.GetName()).group(2)
				except: cat = "N"
				#print cat
				m[i] = fin.Get("2DMaps/%s/%s"%(i,j.GetName()))
				m[i].Scale(1./m[i].Integral())
				m[i].SetName("DistributionMap_%s_C%s"%(i,cat))
				gDirectory.cd("%s:/DistMaps/"%(fout.GetName()))
				m[i].Write(m[i].GetName(),TH1.kOverwrite)
				gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))

	fout.Write()
	fin.Close()
	print

##################################################
def getConvolutions(opts,fout):
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"ScaleFactors/")

	sfmaps = {}
	for i in ['JetMon','QCD']:#,'JetMon-QCD']:
		sfmaps[i] = fout.Get("2DMaps/ScaleFactorMap_%s"%i)

	integral = ROOT.Double(0.0)
	error    = ROOT.Double(0.0)

	eff = {}
	efferr = {}

	gDirectory.cd("%s:/Uncertainties/"%(fout.GetName()))
	for i in opts.samples:
		for c in ["N"]+["%d"%x for x in range(5)]:
			distmap = fout.Get("DistMaps/DistributionMap_%s_C%s"%(i,c))
			if not distmap: continue
			for j in ['JetMon','QCD']:#,'JetMon-QCD']:
				convolution = distmap.Clone("convolution")
				#convolution.Scale(1./convolution.Integral())
				convolution.Multiply(sfmaps[j])
				integral = convolution.IntegralAndError(0,convolution.GetNbinsX(),0,convolution.GetNbinsY(),error)
				eff[(i,j,c)] = integral
				efferr[(i,j,c)] = error
				print "%30s: %.2f +- %.2f"%("(%12s,%12s,%3s)"%(i,j,c),eff[(i,j,c)],efferr[(i,j,c)])
	
	print

	sf = {}
	sferr = {}
	sfplots = {}
	sfplot_labels = ["CAT0","CAT1","CAT2","CAT3","CAT4","ALL"]

	for i in opts.samples:
		sfplots[i] = TH2F("ScaleFactors_%s"%i,"ScaleFactors_%s"%i,6,0,6,1,0,1)
		for j in range(sfplots[i].GetNbinsX()): sfplots[i].GetXaxis().SetBinLabel(j+1,sfplot_labels[j])
		for c in ["N"]+["%d"%x for x in range(5)]:
			if not (i,"JetMon",c) in eff.keys(): continue
			d  = eff[(i,"JetMon",c)]
			q  = eff[(i,"QCD",c)]
			ed = efferr[(i,"JetMon",c)]
			eq = efferr[(i,"QCD",c)]
			sf    = 100 *  d / q
			sferr = 100 * sqrt( (ed*ed/q/q) + (d*d*eq*eq/q/q/q/q) )
			print "%20s: %.1f +- %.1f %%"%("%12s, %3s"%(i,c),sf,sferr)
			sfplots[i].SetBinContent(int(c)+1 if not c=="N" else 6,1,sf)
			sfplots[i].SetBinError(int(c)+1 if not c=="N" else 6,1,sferr)
		fout.cd()
		gDirectory.cd("%s:/ScaleFactors/"%(fout.GetName()))
		sfplots[i].Write(sfplots[i].GetName(),TH1.kOverwrite)

	print

##################################################
def getCanvases(opts,fout):
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"Canvases/")
	makeDirs("plots/%s/TriggerUncertainty/"%(os.path.split(fout.GetName()))[1][:-5])

	gROOT.SetBatch(1)
	gStyle.SetOptStat(0)
	gStyle.SetPaintTextFormat(".2f")

	gDirectory.cd("%s:/ScaleFactors"%fout.GetName())
	c = TCanvas("c","",1800,1200)
	for i in gDirectory.GetListOfKeys():
		h = fout.Get("ScaleFactors/%s"%(i.GetName()))
		h.GetYaxis().SetNdivisions(0)
		h.GetYaxis().SetBinLabel(1,"")
		h.GetYaxis().SetTitle("Trigger Scale Factor")
		h.GetYaxis().SetTitleOffset(0.5)
		h.GetZaxis().SetRangeUser(70,90)
		c.SetName(h.GetName())
		c.cd()
		h.Draw("colz,error,text")
		gPad.Update()
		line = TLine(5.0,0.0,5.0,1.0)
		line.SetLineWidth(4)
		line.Draw("same")
		gPad.Update()
		gDirectory.cd("%s:/Canvases"%(fout.GetName()))
		c.Update()
		c.Write(c.GetName(),TH1.kOverwrite)
		c.SaveAs("plots/%s/TriggerUncertainty/%s.pdf"%(os.path.split(fout.GetName())[1][:-5],c.GetName()))
		c.SaveAs("plots/%s/TriggerUncertainty/%s.png"%(os.path.split(fout.GetName())[1][:-5],c.GetName()))
		c.Update()
	c.Close()
		
####################################################################################################
def mkTriggerUncertainties():
	## init main (including option parsing)
	#opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())
	mp = parser()
	opts,args = mp.parse_args()

	fout = TFile(opts.outputfile,"update")

	getTwoDMaps(opts,fout)
	getDistMaps(opts,fout)
	getConvolutions(opts,fout)
	getCanvases(opts,fout)

	fout.Close()

if __name__=='__main__':
	mkTriggerUncertainties()
