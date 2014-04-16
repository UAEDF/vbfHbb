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
	mgm.add_option('-o','--outputfile',help=blue+"Name of output file."+plain,dest='outputfile',default="%s/../trigger/rootfiles/vbfHbb.root"%basepath)

	mgtc = OptionGroup(mp,cyan+"Trigger uncertainty settings"+plain)
#	mgtc.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
#	mgtc.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mgtc.add_option('--ftwodmaps',help=blue+'Filename for twodmaps.'+plain,dest='ftwodmaps',default="",type="str")
	mgtc.add_option('--fdistmaps',help=blue+'Filename for distmaps.'+plain,dest='fdistmaps',default="",type="str")
	mgtc.add_option('-s','--samples',help=blue+'List of samples (distmap).'+plain,dest='samples',type="str",default=[],action='callback',callback=optsplit)
	mgtc.add_option('-c','--categories',help=blue+'Pick for categories.'+plain,dest='categories',type="str",default=[],action='callback',callback=optsplit)
	mgtc.add_option('-b','--categoryboundaries',help=blue+'Boundaries for categories.'+plain,dest='categoryboundaries',type="str",default=[0.0,0.25,0.70,0.88,1.001],action='callback',callback=optsplit)

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
	info = None
	for i in opts.samples:
		gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))
		for j in gDirectory.GetListOfKeys():
			if info==None: info = [x.split("-") for x in re.search("_s(.*)-t(.*)-r(.*)-d(.*)_(.*)",j.GetName()).groups()]
			if '%s-Num'%i in j.GetName(): 
				try: cat = re.search("(mvaNOMC|CAT)([0-9]{1})",j.GetName()).group(2)
				except: cat = "N"
				if opts.categories and not cat in opts.categories: continue
				#print cat
				m[i] = fin.Get("2DMaps/%s/%s"%(i,j.GetName()))
				#print m[i].Integral()
				if not m[i].Integral() == 0: m[i].Scale(1./m[i].Integral())
				m[i].SetName("DistributionMap_%s_C%s"%(i,cat))
				gDirectory.cd("%s:/DistMaps/"%(fout.GetName()))
				m[i].Write(m[i].GetName(),TH1.kOverwrite)
				gDirectory.cd("%s:/2DMaps/%s/"%(fin.GetName(),i))

	for i in info[0]: 
		if 'mva' in i: del info[0][info[0].index(i)]
	
	fout.Write()
	fin.Close()
	print
	return info

##################################################
def getConvolutions(opts,fout,info):
	print Blue+"Determining scale factors + errors: %s (%s)\n"%('-'.join(info[3]),','.join(info[4]))+plain
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"Convolutions/")
	makeDirsRoot(fout,"ScaleFactors/")

	sfmaps = {}
	for i in ['JetMon','QCD']:#,'JetMon-QCD']:
		sfmaps[i] = fout.Get("2DMaps/ScaleFactorMap_%s"%i)

	eff = {}
	efferr = {}

	gDirectory.cd("%s:/Convolutions/"%(fout.GetName()))
	for i in opts.samples:
		for c in ["N"]+["%d"%x for x in range(len(opts.categoryboundaries)-1)]:
			if opts.categories and not c in opts.categories: continue
			distmap = fout.Get("DistMaps/DistributionMap_%s_C%s"%(i,c))
			if not distmap: continue
			for j in ['JetMon','QCD']:#,'JetMon-QCD']:
				convolution = distmap.Clone("Convolution_%s_%s_C%s"%(i,j,c))
				#convolution.Scale(1./convolution.Integral())
				convolution.Multiply(sfmaps[j])
				convolution.Write(convolution.GetName(),TH1.kOverwrite)
				integral = ROOT.Double(0.0)
				error    = ROOT.Double(0.0)
				integral = convolution.IntegralAndError(0,convolution.GetNbinsX(),0,convolution.GetNbinsY(),error)
				eff[(i,j,c)] = integral
				efferr[(i,j,c)] = error


	print "%12s |"%"E",
	for c in ["N"]+["%d"%x for x in range(len(opts.categoryboundaries)-1)]:
		for j in ['JetMon','QCD']:
			print "%14s |"%("%s CAT%s"%(j,c)),
	print
	print "-"*(14 + 17*2*(len(opts.categoryboundaries)))
	for i in opts.samples:
		print "%12s |"%i,
		for c in ["N"]+["%d"%x for x in range(len(opts.categoryboundaries)-1)]:
			for j in ['JetMon','QCD']:
				print "%14s |"%("%.2f +- %.3f"%(eff[(i,j,c)],efferr[(i,j,c)])),
		print
	print

	sf = {}
	sferr = {}
	sfplots = {}
	sfplots1d = {}
	sfplot_labels = ["CAT%d"%x for x in range(len(opts.categoryboundaries)-1)]+["ALL"] #["CAT0","CAT1","CAT2","CAT3","CAT4","ALL"]

	print "%12s |"%"E(data/mc)",
	for c in ["N"]+["%d"%x for x in range(len(opts.categoryboundaries)-1)]:
		print "%17s |"%("CAT%s"%(c)),
	print
	print "-"*(14 + 20*(len(opts.categoryboundaries)))

	gDirectory.cd("%s:/ScaleFactors/"%(fout.GetName()))
	for i in opts.samples:
		print "%12s |"%i,
		# 2D
		#binsx = array('f',opts.categoryboundaries+[1.2])
		#binsy = array('f',[0,1])
		nbins = len(opts.categoryboundaries)
		sfplots[i] = TH2F("ScaleFactors_%s"%i,"ScaleFactors_%s"%i,nbins,0,nbins,1,0,1)#len(binsx)-1,binsx,len(binsy)-1,binsy)
		sfplots1d[i] = TH1F("ScaleFactors1D_%s"%i,"ScaleFactors1D_%s"%i,nbins,0,nbins)#len(binsx)-1,binsx)
		for j in range(sfplots[i].GetNbinsX()): sfplots[i].GetXaxis().SetBinLabel(j+1,sfplot_labels[j])
		for j in range(sfplots[i].GetNbinsX()): sfplots1d[i].GetXaxis().SetBinLabel(j+1,sfplot_labels[j])
		#sfplots[i].GetXaxis().SetTickLength(0)
		for c in ["N"]+["%d"%x for x in range(nbins-1)]:
			if opts.categories and not c in opts.categories: continue
			if not (i,"JetMon",c) in eff.keys(): continue
			d  = eff[(i,"JetMon",c)]
			q  = eff[(i,"QCD",c)]
			ed = efferr[(i,"JetMon",c)]
			eq = efferr[(i,"QCD",c)]
			#print d,q,ed,eq
			if not q==0:
				sf    = d / q
				sferr = sqrt( (ed*ed/q/q) + (d*d*eq*eq/q/q/q/q) )
			else: 
				sf = 0
				sferr = 0
			print "%17s |"%("%.3f +- %.3f %%"%(sf,sferr)),
			thisbin = int(c)+1 if not c=="N" else nbins
			sfplots[i].SetBinContent(thisbin,1,sf)
			sfplots[i].SetBinError(thisbin,1,sferr)
			sfplots1d[i].SetBinContent(thisbin,sf)
			sfplots1d[i].SetBinError(thisbin,sferr)
		print
		fout.cd()
		gDirectory.cd("%s:/ScaleFactors/"%(fout.GetName()))
		sfplots[i].Write(sfplots[i].GetName(),TH1.kOverwrite)
		sfplots1d[i].Write(sfplots1d[i].GetName(),TH1.kOverwrite)

	print

##################################################
def getCanvases(opts,fout,info):
	fout.cd()
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,"Canvases/")
	makeDirs("plots/%s/TriggerUncertainty/"%(os.path.split(fout.GetName()))[1][:-5])

	gROOT.SetBatch(1)
	gStyle.SetOptStat(0)
	gStyle.SetPaintTextFormat(".3f")

	gDirectory.cd("%s:/ScaleFactors"%fout.GetName())
	c = TCanvas("c","",1800,1200)
	for i in gDirectory.GetListOfKeys():
		gPad.SetRightMargin(0.25)
		text = printText(1-0.1,1-0.15,i.GetName().split('_')[1],"NOM" if "NOM_" in fout.GetName() else ("VBF" if "VBF" in fout.GetName() else "???"),info[4])#,0.020,kBlue-2)
		h = fout.Get("ScaleFactors/%s"%(i.GetName()))
		h.SetTitle("")
		th2f = (h.IsA().GetName() == "TH2F")
		if th2f and 'ScaleFactor' in h.GetName():
			h.GetYaxis().SetNdivisions(0)
			h.GetYaxis().SetBinLabel(1,"")
			h.GetZaxis().SetRangeUser(0.70,0.90)
		if 'ScaleFactor' in h.GetName():
			h.GetYaxis().SetTitle("Trigger Scale Factor")
			h.GetYaxis().SetTitleOffset(0.5 if th2f else 1.0)
		c.SetName(h.GetName())
		c.cd()
		selleg = printSelleg(text.GetY1()-0.1,1-0.15,info[0],info[1])
		if th2f: h.Draw("colz,error,text")
		else: 
			gPad.SetRightMargin(0.20)
			text.SetX1(text.GetX1()-0.04)
			selleg.SetX1(selleg.GetX1()-0.04)
			h.GetYaxis().SetRangeUser(0,1.2)#round(h.GetMaximum()*1.5,1))
			h.SetLineWidth(3)
			h.DrawCopy("hist")
			h.SetMarkerSize(1.5)
			h.SetFillColor(kBlue)
			h.SetFillStyle(3018)#3018)
			h.Draw("e2same,text70")
			error=[None]*h.GetNbinsX()
			for i in range(1,h.GetNbinsX()+1): 
				if h.GetBinContent(i)==0: continue
				error[i-1] = extraText(i-h.GetBinWidth(i)/2.,h.GetBinContent(i),"#pm %.3f"%h.GetBinError(i))
				error[i-1].Draw("same")
	#			print error[i-1].Print()
		gPad.Update()
		line = TLine(h.GetNbinsX()-1,0.0,h.GetNbinsX()-1,gPad.GetUymax())
		line.SetLineWidth(4)
		line.Draw("same")
		text.Draw("same")
		selleg.Draw("same")
		gPad.Update()
		gDirectory.cd("%s:/Canvases"%(fout.GetName()))
		c.Update()
		c.Write(c.GetName(),TH1.kOverwrite)
		c.SaveAs("plots/%s/TriggerUncertainty/%s.pdf"%(os.path.split(fout.GetName())[1][:-5],c.GetName()))
		c.SaveAs("plots/%s/TriggerUncertainty/%s.png"%(os.path.split(fout.GetName())[1][:-5],c.GetName()))
		c.Update()
	print purple+"Scale factor plots at: plots/%s/TriggerUncertainty/*ScaleFactor*.png"%(os.path.split(fout.GetName())[1][:-5])+plain
	c.Close()
		
####################################################################################################
def extraText(hcenter,vcenter,line,fontSize=0.027,fontColor=kBlack):
	text = TPaveText(hcenter-0.2+0.17,vcenter-0.2+0.07,hcenter+0.2+0.17,vcenter+0.2+0.07)
	text.SetTextAlign(22)
	text.SetTextSize(fontSize)
	text.SetTextColor(fontColor)
	text.SetFillStyle(0)
	text.SetBorderSize(0)
	theline = text.AddText(line)
	theline.SetTextAngle(70)
	return text

def printText(top,left,sample,selection,mapvars,fontSize=0.020,fontColor=kBlack):
	nlines = 6
	right = left + 0.13
	bottom = top - nlines*(fontSize+0.018)
	text = TPaveText(left,bottom,right,top,"NDC")
	text.SetFillColor(0)
	text.SetFillStyle(0)
	text.SetBorderSize(0)
	text.SetTextSize(fontSize)
	text.SetTextColor(fontColor)
	text.SetTextAlign(11)
	text.AddText("CMS preliminary")
	text.AddText("VBF H#rightarrow b#bar{b}")
	text.AddText("L = %.1f fb^{-1}"%(19800./1000. if selection=="NOM" else 18300./1000. if selection=="VBF" else "???"))
	text.AddText("%s selection"%selection)
	text.AddText("sample: %s"%sample)
	text.AddText("2D map: %s"%(' & '.join(mapvars)))
	thisline = text.AddText("#varepsilon = #frac{#varepsilon_{%s #times data}}{#varepsilon_{%s #times qcd}}"%(sample,sample))
	thisline.SetTextAlign(13)
	return text

def printSelleg(top,left,selection,trigger,fontSize=0.020,fontColor=kBlack):
	rows = sum([1 for x in selection])+1
	selleg = getSelLegend(left,top - rows*(0.030),1-0.02,top,None,0,0,1,0.018)
	for iline,line in enumerate(sorted([x.strip() for x in selection])): selleg.AddText('%s %s'%('sel:' if iline==0 else ' '*4,line))
	selleg.AddText('trg: %s (MC)'%(','.join(trigger)))
	#selleg.AddText('     %s (data)'%(','.join(datatrigger)))
	return selleg

####################################################################################################
def mkTriggerUncertainties():
	## init main (including option parsing)
	#opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())
	mp = parser()
	opts,args = mp.parse_args()

	fout = TFile(opts.outputfile,"recreate")
	gROOT.ProcessLine("gErrorIgnoreLevel = kWarning;")

	getTwoDMaps(opts,fout)
	info = getDistMaps(opts,fout)
	getConvolutions(opts,fout,info)
	getCanvases(opts,fout,info)

	fout.Close()

if __name__=='__main__':
	mkTriggerUncertainties()
