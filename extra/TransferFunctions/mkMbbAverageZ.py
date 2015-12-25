#!/usr/bin/env python

import sys,os,json,re,glob
from optparse import OptionParser,OptionGroup
from array import array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from write_cuts import *
from toolkit import *
from main import main
from math import *

global paves
paves = []

# OPTION PARSER ##################################################################################
##
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mpTransfer = OptionGroup(mp,cyan+"Transfer function options"+plain)
	mpTransfer.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)
	mpTransfer.add_option('--catTags',help='tags for categories',type='str',action='callback',callback=optsplit,default=[])
	mpTransfer.add_option('--fBound',help='fit MIN and MAX',type='str',action='callback',callback=optsplit,default=['90','200'])	
	mpTransfer.add_option('--complexWghts',help='Wght info.',type='str',action='callback',callback=optsplitmore,default=[])
	mpTransfer.add_option('--typetag',help='Type tag (Dat,QCD,Z,T).',type='str',default='Data')
	mpTransfer.add_option('--unblind',help='No blind window.',action='store_true',default=False)
	mpTransfer.add_option('--merge',help='Merge higher CATs.',action='store_true',default=False)
	mp.add_option_group(mpTransfer)
	return mp

####################################################################################################
def INTERNALprepare(opts):
	makeDirs(os.path.split(opts.fout)[0])
	makeDirs('plots/transfer')
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsons = {'samp':jsonsamp,'vars':jsonvars,'info':jsoninfo}
	# fix binning
	if opts.binning:
		for v in opts.binning:
			#print v
			jsons['vars']['variables'][v[0]]['nbins_x'] = v[1]
			jsons['vars']['variables'][v[0]]['xmin'] = v[2]
			jsons['vars']['variables'][v[0]]['xmax'] = v[3]
	for v in opts.mvaBins:
			jsons['vars']['variables'][v]['nbins_x'] = opts.mvaBins[v][0]
			jsons['vars']['variables'][v]['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v][1]])
			jsons['vars']['variables'][v]['xmin'] = opts.mvaBins[v][1][0]
			jsons['vars']['variables'][v]['xmax'] = opts.mvaBins[v][1][-1]
	return jsons

####################################################################################################

def INTERNALblind(h,min,max):
	for ix in range(1,h.GetNbinsX()+1):
		x = h.GetBinCenter(ix)
		if x>=min and x<=max:
			h.SetBinContent(ix,0)
			h.SetBinError(ix,0)
	return h

####################################################################################################

def INTERNALstyle():
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")
	gROOT.ProcessLine(".x %s/styleCMSTDR.C++"%basepath)
	gROOT.ProcessLine('gROOT->ForceStyle();')
	gStyle.SetStripDecimals(0)
        gStyle.SetLineScalePS(1.8)
        gStyle.SetPadRightMargin(0.04)
        gStyle.SetPadLeftMargin(0.14)
        gStyle.SetPadTopMargin(0.07)
        gStyle.SetPadBottomMargin(0.12)
        gStyle.SetTitleSize(0.05,"XY")
        gStyle.SetLabelSize(0.04,"XY")
        gStyle.SetGridColor(17)

	
	markers = [20, 21, 20 , 23]
	colours = [kBlack,kBlue,kRed,kGreen+2] 
	return markers, colours

####################################################################################################

def INTERNALstyleHist(h,i,markers,colours,TYPE):
	h.Sumw2()
	h.SetMarkerStyle(25)#markers[i])
	h.SetMarkerColor(kBlue)#colours[i])
	h.SetLineColor(kBlue)#colours[i])
	h.SetMarkerSize(0.8 if not "QCD" in h.GetName() else 0.0)
	h.SetLineColor(colours[i])
	h.GetXaxis().SetTitle("Z discriminant output")
	h.GetYaxis().SetTitle("< m_{b#bar{b}} > (GeV)")
	h.GetXaxis().SetNdivisions(506)
	h.GetYaxis().SetNdivisions(506)
	h.GetYaxis().SetRangeUser(70.01,170.02)
	return h

####################################################################################################

def INTERNALhistograms(opts):
	hDat = {}
	for iTag,Tag in enumerate(opts.catTags):
		hDat[Tag] = None
	return hDat

####################################################################################################

def INTERNALcanvases(opts):
	c1 = {}
	c2 = {}
	c = None
	for iTag,Tag in enumerate(opts.catTags):
		c1[Tag] = None
		c2[Tag] = None
	return c1, c2, c

####################################################################################################

def INTERNALpave():
	pave = TPaveText(0.2,0.8,0.5,0.9,"NDC")
	pave.SetFillColor(0)
	pave.SetBorderSize(0)
	pave.SetTextFont(42)
	pave.SetTextSize(0.05)
	return pave

####################################################################################################

def INTERNALlegend(Tag):
	leg = TLegend(0.6,0.62,0.95,0.92)
	leg.SetHeader("%s selection"%Tag)
	leg.SetFillColor(0)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.05)
	return leg

####################################################################################################

def INTERNALline(fun, min, max):
	ln = TF1("line",fun,min,max)
	ln.SetLineColor(kBlack)
	ln.SetLineWidth(1)
	ln.SetLineStyle(2)
	ln.SetMinimum(0.0)
	ln.SetMaximum(2.0)
	ln.GetXaxis().SetTitle("m_{b#bar{b}} (GeV)")
	ln.GetYaxis().SetTitle("Signal / Control (QCD)")
	return ln

####################################################################################################
def INTERNALpicksamples(opts,jsons):
	l1("Global path: %s"%opts.globalpath)
	l1("Using input samples:")
	allsamples = jsons['samp']['files']
	selsamples = []
	for s in allsamples.itervalues():
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in s['tag']) for x in opts.sample]): continue
	    # veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in s['tag']) for x in opts.nosample]): continue
		selsamples += [s]
	for s in sorted(selsamples,key=lambda x:(x['tag'][:3],int(re.findall('[0-9]+',x['tag'])[0]) if len(re.findall('[0-9]+',x['tag']))>0 else 1.,not 'NOM' in x['fname'])):
		s['tfile'] = TFile.Open(opts.globalpath + "/" + s['fname'])
		s['incarnation'] = 'NOM' if 'NOM' in s['tag'] else 'VBF'
		l2('%-15s: %-50s(%s)'%(s['tag'],s['fname'],s['tfile']))
	return selsamples

####################################################################################################

def mkTemplateFunctions():
        global paves
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()

	TYPE = opts.typetag
	samples = INTERNALpicksamples(opts,jsons)

	hDat  = INTERNALhistograms(opts)
	hQcd  = INTERNALhistograms(opts)
	can = TCanvas('profiles','profiles',900,750)
	#can.Divide(2,1)

	ln = INTERNALline("1",float(opts.fBound[0]),float(opts.fBound[1]))

	for iTag,Tag in enumerate(opts.catTags):
		selsamples = [s for s in samples if s['incarnation']==Tag] 
		fins = [x['tfile'] for x in selsamples]
		l1('Running for %s'%Tag)
		
                can.cd(1 if 'NOM' in Tag else 2)
                leg = TLegend(0.75,0.5,1.-gPad.GetRightMargin()-0.05,1.-gPad.GetTopMargin()-0.015)
                leg.SetFillStyle(0)
                leg.SetBorderSize(0)
                leg.SetTextSize(0.045)
                leg.SetTextFont(42)
                leg.SetY1(leg.GetY2()-2*leg.GetTextSize()*1.25)
		
                l2("Running for <mbbReg>")
                fout.cd()
                hQcd[Tag] = TProfile("hProf_sel%s_%s"%(Tag,TYPE),"hProf_sel%s_%s"%(Tag,TYPE),25,-0.15,0.15)
                hDat[Tag] = TProfile("hProf_sel%s_%s"%(Tag,"Data"),"hProf_sel%s_%s"%(Tag,"Data"),50,-0.15,0.15)
                h = hDat[Tag]
		h = INTERNALstyleHist(h,0,markers,colours,TYPE)
                h = hQcd[Tag]
		h = INTERNALstyleHist(h,0,markers,colours,TYPE)
		can.cd()
		for ifin,fin in enumerate(fins):
                    if "QCD" in fin.GetName(): 
                        h = hQcd[Tag]
                    else: 
                        h = hDat[Tag]
                    if "VBF" in fin.GetName(): continue
                    fout.cd()
                    can.cd(1 if 'NOM' in Tag else 2)
		    l4('Sample: %s'%fin.GetName())
                    CUT1 = "mbbReg[%d] > %.1f && mbbReg[%d] < %.1f"%(1 if 'NOM' in Tag else 2,60,1 if 'NOM' in Tag else 2,170)
		    CUT2,cutlabel = write_cuts(["None"],["None"],reftrig=["None"],sample=jsons['samp']['files'][os.path.split(fin.GetName())[1]]['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.complexWghts[(Tag,'old')],trigequal=trigTruth(opts.usebool))
		    l4('Cutting with: (%s)*%s'%(CUT1,CUT2))
		    tin = fin.Get("Hbb/events")
    	            l3('Drawing mbbReg[%d] --> %s'%(1 if 'NOM' in Tag else 2,h.GetName()))
                    tin.Draw("mbbReg[%d]:%s>>+%s"%(1 if 'NOM' in Tag else 2,"mvaZ" if 'NOM' in Tag else "mvaVBF",h.GetName()),TCut(CUT1)*TCut(CUT2),"prof")

	            h.Write(h.GetTitle(),TH1.kOverwrite)

                gPad.SetGrid(0,1)
                gPad.RedrawAxis()
                hQcd[Tag].SetMarkerSize(1.0)
                hQcd[Tag].SetMarkerStyle(20)
                hQcd[Tag].SetMarkerColor(kBlack)
                hDat[Tag].GetXaxis().SetTitleOffset(1.1)
                hDat[Tag].DrawCopy()
                hQcd[Tag].DrawCopy("same")
                epave("Z selection",gPad.GetLeftMargin()+0.01,1.-0.5*gPad.GetTopMargin(),"left",1,0.048)
                epave("%.1f fb^{-1} (8 TeV)"%(19.8 if 'NOM' in Tag else 18.3),1.-gPad.GetRightMargin()-0.01,1.-0.5*gPad.GetTopMargin(),"right",0,0.048)
                line = -0.6 if 'NOM' in Tag else -0.1
                tl = TLine(line,70,line,170)
                tl.SetLineStyle(kDashed)
                tl.SetLineColor(kGray+2)
                tl.Draw()
                paves += [tl]
                leg.Clear()
                a = leg.AddEntry(hDat[Tag],"Data","PL")
                a.SetTextColor(kBlue+2)
                a = leg.AddEntry(hQcd[Tag],"QCD","PL")
                a.SetTextColor(kBlack)
                leg.Draw()
                paves += [leg]
                gPad.RedrawAxis()
                can.SaveAs("mbbRegProfileZ.pdf")


# clean
	for f in samples: 
            if f['tfile']: f['tfile'].Close()
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkTemplateFunctions()
