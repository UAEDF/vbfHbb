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
from math import *
from optparse import OptionParser,OptionGroup
from copy import deepcopy as dc
from toolkit import *
from dependencyFactory import *
from write_cuts import *
from array import array

global paves
paves = []

####################################################################################################
def axisupdate(h):
    ax = h.GetXaxis()
    ax.SetTitleFont(42)
    ax.SetTitleSize(0.05)
    ax.SetTitleOffset(1.00)
    ax.SetLabelFont(42)
    ax.SetLabelSize(0.05)
    ax.SetLabelOffset(0.005)
#
    ax = h.GetYaxis()
    ax.SetTitleFont(42)
    ax.SetTitleSize(0.05)
    ax.SetTitleOffset(1.2)
    ax.SetLabelFont(42)
    ax.SetLabelSize(0.04)
    ax.SetLabelOffset(0.005)
#
    return h

####################################################################################################
def putLine(x1,y1,x2,y2,style=kDashed,color=kGray+2,width=1):
    global paves
    l = TLine(x1,y1,x2,y2)
    l.SetLineStyle(style)
    l.SetLineColor(color)
    l.SetLineWidth(width)
    l.Draw()
    paves += [l]

####################################################################################################
def putPave(text,x1,y1,align=12,font=42,size=0.045,color=kBlack,ndc=1):
    global paves
    l = TLatex(x1,y1,text)
    l.SetNDC(1)
    l.SetTextFont(font)
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.SetTextAlign(align)
    l.Draw()
    paves += [l]

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
	mgtc.add_option('-b','--categoryboundaries',help=blue+'Boundaries for categories.'+plain,dest='categoryboundaries',type="str",default=[-1.0,-0.6,0.0,0.70,0.84,1.001],action='callback',callback=optsplit) #],[-1.0,-0.1,0.40,0.80,1.001]
	mgtc.add_option('--notext',help='No right margin legends.',default=False,action='store_true')

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
				try: cat = re.search('(mvaVBFC|mvaNOMC|CAT)([0-9]{1})',j.GetName()).group(2)
				except: cat = "N"
				if opts.categories and not cat in opts.categories: continue
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
	j = 4 if 'VBF' in '-'.join(info[3]) else 0 
	#sfplot_labels = ["CAT%d (%.2f,%.2f)"%(x,y,z) for (x,y,z) in [(i-1+j if not (i==0 and j==4) else -2,float(opts.categoryboundaries[i]),float(opts.categoryboundaries[i+1])) for i in range(len(opts.categoryboundaries)-1)]]+["ALL"] #["CAT0","CAT1","CAT2","CAT3","CAT4","ALL"]
	sfplot_labels = ["CAT%d"%x for x in [i-1+j if not (i==0 and j==4) else -2 for i in range(len(opts.categoryboundaries)-1)]]+["ALL"] #["CAT0","CAT1","CAT2","CAT3","CAT4","ALL"]

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
	numbers = {}

	gROOT.SetBatch(1)
	gStyle.SetOptStat(0)
	gStyle.SetPaintTextFormat(".3f")
        gROOT.ProcessLineSync('.x ../common/styleCMSTDR.C')
        gStyle.SetPadTopMargin(0.07)
        gStyle.SetPadRightMargin(0.04)
        gStyle.SetPadBottomMargin(0.09)
        gStyle.SetPadLeftMargin(0.14)

	gDirectory.cd("%s:/ScaleFactors"%fout.GetName())
	c = TCanvas("c","",1800 if not opts.notext else 1600,1200)
	for i in gDirectory.GetListOfKeys():
		gPad.SetRightMargin(0.25)
		text = printText(opts,1-0.1,1-0.15,i.GetName().split('_')[1],"Set A" if "NOM_" in fout.GetName() else ("Set B" if "VBF" in fout.GetName() else "???"),info[4])#,0.020,kBlue-2)
		h = fout.Get("ScaleFactors/%s"%(i.GetName()))
		h.SetTitle("")
		#h.GetXaxis().SetLabelSize(0.032)
		#h.GetXaxis().SetLabelSize(0.05)
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
		pave = None
		if th2f: h.Draw("colz,error,text")
		else: 
			gPad.SetRightMargin(0.20 if not opts.notext else 0.04)
			text.SetX1(text.GetX1()-0.04)
			selleg.SetX1(selleg.GetX1()-0.04)
			#h.GetXaxis().SetTitleSize(0.06)
			#h.GetYaxis().SetTitleSize(0.06)
			#h.GetXaxis().SetLabelSize(0.06)
			#h.GetYaxis().SetLabelSize(0.05)
			#h.GetXaxis().SetLabelOffset(h.GetXaxis().GetLabelOffset()*1.1)
			#h.GetYaxis().SetLabelOffset(h.GetYaxis().GetLabelOffset()*1.3)
			#h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()/1.1)
                        h = axisupdate(h)
			h.GetXaxis().SetDecimals(kTRUE)
			h.GetYaxis().SetDecimals(kTRUE)
			h.GetYaxis().SetRangeUser(0,1.2)#round(h.GetMaximum()*1.5,1))
			h.SetLineWidth(3)
                        h.DrawCopy("axis")
                        tb = TBox(h.GetBinLowEdge(1),0,h.GetBinLowEdge(2),1.2)
                        tb.SetLineColor(kGray)
                        tb.SetFillColor(kGray)
                        tb.SetFillStyle(1001)
                        tb.Draw("same")
			h.DrawCopy("hist,same")
			h.SetMarkerSize(1.5)
			h.SetFillColor(kBlue)
			h.SetFillStyle(3018)#3018)
			h.Draw("e2same,text70")
			gPad.Update()
                        gPad.RedrawAxis()
			error=[None]*h.GetNbinsX()
			for i in range(1,h.GetNbinsX()+1): 
				if not 'ALL' in h.GetXaxis().GetBinLabel(i) and float(re.search('([A-Z]*)([0-9+-]*)',h.GetXaxis().GetBinLabel(i)).group(2))<0:
						ctr = h.GetXaxis().GetBinCenter(i)
						wid = h.GetXaxis().GetBinWidth(i)
						pave = TPave(ctr-wid/2.,gPad.GetUymin(),ctr+wid/2.,gPad.GetUymax())
						pave.SetFillColor(kGray)
						pave.SetFillStyle(1001)
						#pave.Draw("same")
				if h.GetBinContent(i)==0: continue
				error[i-1] = extraText(i-h.GetBinWidth(i)/2.,h.GetBinContent(i),"#pm %.3f"%h.GetBinError(i))
				error[i-1].Draw("same")
	#			print error[i-1].Print()
	#			print "%10s %10s    %12.3f / %12.3f   =  %12.6f"%(h.GetName(), h.GetXaxis().GetBinLabel(i), h.GetBinContent(i), h.GetBinError(i), h.GetBinError(i)/h.GetBinContent(i))
				if not 'ALL' in h.GetXaxis().GetBinLabel(i): 
					numbers[(h.GetName().split('_')[1],re.search("([A-Z]*)([0-9\-+]{1,2})",h.GetXaxis().GetBinLabel(i)).group(2))] = h.GetBinError(i)/h.GetBinContent(i)
	#		print
		gPad.Update()
		line = TLine(h.GetNbinsX()-1,0.0,h.GetNbinsX()-1,gPad.GetUymax())
		line.SetLineWidth(4)
		line.Draw("same")
		#text.Draw("same")
		#if not opts.notext: selleg.Draw("same")
                samplenames = {"GF":"GF","Tall": "Top", "ZJets":"Z+jets","QCD":"QCD","VBF125":"VBF"}
                for lline in text.GetListOfLines():
                    if "sample" in lline.GetTitle():
                        sample = re.search("sample: (.*)",lline.GetTitle()).group(1)
                        if not sample in samplenames: continue
                        putPave(samplenames[sample]+" sample",0.5,gStyle.GetPadBottomMargin()+0.08,align=22,font=62,size=0.036)
                        print sample
                        print

                pcms1 = TPaveText(gPad.GetLeftMargin(),1.-gPad.GetTopMargin(),0.3,1.,"NDC")
                pcms1.SetTextAlign(12)
                pcms1.SetTextFont(62)
                pcms1.SetTextSize(gPad.GetTopMargin()*2.5/4.0)
                pcms1.SetFillStyle(-1)
                pcms1.SetBorderSize(0)
                pcms1.AddText("CMS")
                #pcms1.Draw()
                
                pcms2 = TPaveText(0.6,1.-gPad.GetTopMargin(),1.-gPad.GetRightMargin()+0.015,1.,"NDC")
                pcms2.SetTextAlign(32)
                pcms2.SetTextFont(62)
                pcms2.SetTextSize(gPad.GetTopMargin()*2.5/4.0)
                pcms2.SetFillStyle(-1)
                pcms2.SetBorderSize(0)
                pcms2.AddText("%.1f fb^{-1} (8 TeV)"%(19.8 if 'NOM' in fout.GetName() else 18.3))
                #pcms2.Draw()

                gStyle.SetPaintTextFormat(".3g")
                putPave("Set %s selection"%("A" if 'NOM_' in fout.GetName() else "B"),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),align=12,font=62)
                putPave("%.1f fb^{-1} (8 TeV)"%(19.8 if 'NOM_' in fout.GetName() else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),align=32,font=42)
		gPad.Update()
		gDirectory.cd("%s:/Canvases"%(fout.GetName()))
		c.Update()
		c.Write(c.GetName(),TH1.kOverwrite)
                gPad.RedrawAxis()
		c.SaveAs("plots/%s/TriggerUncertainty/%s%s.pdf"%(os.path.split(fout.GetName())[1][:-5],c.GetName(),'' if not opts.notext else '_noleg'))
		c.SaveAs("plots/%s/TriggerUncertainty/%s%s.png"%(os.path.split(fout.GetName())[1][:-5],c.GetName(),'' if not opts.notext else '_noleg'))
		c.Update()

	print purple+"Scale factor plots at: plots/%s/TriggerUncertainty/*ScaleFactor*.png"%(os.path.split(fout.GetName())[1][:-5])+plain

	# table
	labels = ['Category']+list(set([x for (x,y) in numbers.iterkeys() if not x in ['VBF115','VBF120','VBF130','VBF135','WJets']]))
	print "\\begin{table}[htbf]\n\t\\caption{Relative uncertainties for trigger scale factors per category.} \\small \\centering \n\t\\begin{tabular}{|*{%d}{c|}} \\hline"%(len(labels))  
	print "\t",
	for il,l in enumerate(sorted(labels,key=lambda x:('Category' in x,'VBF125' in x,'GF' in x,'QCD' in x,'ZJets' in x,'Tall' in x),reverse=True)):
		print "%20s%s"%("\makebox[1.8cm]{%s}"%l.replace('Tall','Top').replace('GF','GF125')," &" if il<len(labels)-1 else ""),
	print "\\\\ \\hline \\hline"
	for ic,cat in enumerate(sorted([y for (x,y) in numbers.iterkeys() if x==labels[-1]])):
		print "%20s &"%cat,
		for il,l in enumerate(sorted(list(set(labels)-set(['Category'])),key=lambda x:('Category' in x, 'VBF125' in x,'GF' in x,'QCD' in x,'ZJets' in x,'Tall' in x),reverse=True)):
			print "%20.4f%s"%(numbers[(l,cat)]," &" if not l=="Tall" else ""),
		print "\\\\ \\hline",
		if not 'VBF' in fout.GetName() and ic==len([y for (x,y) in numbers.iterkeys() if x==labels[-1]])-1: print " \\hline"
		else: print ""
	print "\t\\end{tabular}\n\\end{table}"
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

def printText(opts,top,left,sample,selection,mapvars,fontSize=0.020,fontColor=kBlack):
	varnames = {'jetBtag00':'bjet0 CSV','jetBtag10':'bjet1 CSV','mqq1':'m_{q#bar{q}}','mqq2':'m_{q#bar{q}}','dEtaqq1':'#Delta#eta_{q#bar{q}}','dEtaqq2':'#Delta#eta_{q#bar{q}}'}
	nlines = 6 if not opts.notext else 3
	if opts.notext: 
		left = 0.33
		top = 0.30
		fontSize = fontSize*1.4
	right = left + 0.13
	###bottom = top - nlines*(fontSize+0.018)
	bottom = top - nlines*(0.05)
	text = TPaveText(left,bottom,right,top,"NDC")
	text.SetFillColor(0)
	text.SetFillStyle(0)
	text.SetBorderSize(0)
	text.SetTextFont(62)
	###text.SetTextSize(fontSize)
	text.SetTextSize(0.04)
	text.SetTextColor(fontColor)
	text.SetTextAlign(11)
	if not opts.notext:
		text.AddText("CMS preliminary")
		text.AddText("VBF H#rightarrow b#bar{b}")
		text.AddText("%.1f fb^{-1}"%(19800./1000. if selection=="Set A" else 18300./1000. if selection=="Set B" else "???")) # NOM VBF
	text.AddText("%s selection"%selection.replace('VBF','Set B').replace('NOM','Set A'))
	text.AddText("sample: %s"%sample)
	text.AddText("2D map: %s"%(' & '.join([(varnames[x] if x in varnames else x) for x in mapvars])))
	if not opts.notext: 
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
        global paves
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
