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
	if opts.mvaBins:
		for v in opts.mvaBins:
			jsons['vars']['variables'][v]['nbins_x'] = opts.mvaBins[v][0]
			jsons['vars']['variables'][v]['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v][1]])
			jsons['vars']['variables'][v]['xmin'] = opts.mvaBins[v][1][0]
			jsons['vars']['variables'][v]['xmax'] = opts.mvaBins[v][1][-1]
	return jsons

####################################################################################################

def INTERNALgraph(h):
	g = TGraphErrors(h.GetNbinsX())
	for ibin in range(1,h.GetNbinsX()+1):
		x = h.GetBinCenter(ibin)
		y = h.GetBinContent(ibin)
		ex = h.GetBinWidth(ibin)/2.
		ey = h.GetBinError(ibin)

		g.SetPoint(ibin-1,x,y)
		g.SetPointError(ibin-1,ex,ey)
	return g

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
	gStyle.SetOptFit(0)
	gStyle.SetOptStat(0)
	gStyle.SetPadLeftMargin(0.18)
	gStyle.SetPadRightMargin(0.04)
	
	markers = [20, 21, 20 , 23]
	colours = [kBlack,kBlue,kRed,kGreen+2] 
	return markers, colours

####################################################################################################

def INTERNALstyleHist(h,i,markers,colours,TYPE):
	h.Sumw2()
	h.SetMarkerStyle(markers[i])
	h.SetMarkerColor(colours[i])
	h.SetMarkerSize(1.2)
	h.SetLineColor(colours[i])
	h.GetXaxis().SetTitle("M_{bb} (GeV)")
	h.GetYaxis().SetTitle("PDF (%s)"%TYPE)
	h.GetYaxis().SetNdivisions(505)
	h.SetMaximum(0.25)
	return h

####################################################################################################

def INTERNALhistograms(opts):
	hDat = {}
	hRat = {}
	fFit = {}
	gUnc = {}
	for iTag,Tag in enumerate(opts.catTags):
		for iCat,Cat in enumerate(opts.mvaBins[opts.mvaBins.keys()[iTag]]):
			hDat[(Tag,iCat)] = None
			hRat[(Tag,iCat)] = None
			fFit[(Tag,iCat)] = None
			gUnc[(Tag,iCat)] = None
	fitter = None
	covariant = None
	return hDat, hRat, fFit, gUnc, fitter, covariant

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
	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
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
		s['tfile'] = TFile.Open('../../fit/flat/' + s['fname'])
		s['incarnation'] = 'NOM' if 'NOM' in s['tag'] else 'VBF'
		l2('%-15s: %-50s(%s)'%(s['tag'],s['fname'],s['tfile']))
	return selsamples

####################################################################################################

def mkTemplateFunctions():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()

	splitkeys = []
	keys = fout.GetListOfKeys()
	for k in keys:
		splitkeys += [k.GetName().split('_')]
		
	SELS = list(set([x[1] for x in splitkeys]))
	CATS = list(set([x[2] for x in splitkeys]))
	
	graphs = []
	bands = []

	for SEL in SELS:
		can = TCanvas("hTransfer_%s"%SEL,"hTransfer_%s"%SEL,50+900*(4 if 'NOM' in SEL else 3),900)
		can.Divide(4 if 'NOM' in SEL else 3,1)

		leg = []

		counterCAT = -1
		for iCAT,CAT in enumerate(sorted(CATS,key=lambda x:int(x.replace('CAT','')))):
			leg += [TLegend(0.45,0.6,0.9,0.92,"%s selection"%SEL.replace('sel',''))]
			leg[counterCAT+1].SetTextFont(42)
			leg[counterCAT+1].SetTextSize(0.045)
			leg[counterCAT+1].SetBorderSize(0)
			leg[counterCAT+1].SetFillStyle(-1)
			can.cd(counterCAT+2)
			todraw = []
			for iTYPE,TYPE in enumerate(['Data','QCD']):
				if ['hRat',SEL,CAT,TYPE] in splitkeys:
					h = fout.Get('_'.join(['hRat',SEL,CAT,TYPE]))
					b = fout.Get('_'.join(['gRat',SEL,CAT,TYPE]))
					if TYPE=='Data': h = INTERNALblind(h,110,150)
					if iTYPE==0: 
						h.GetYaxis().SetRangeUser(0.5 if 'VBF' in SEL else 0.4,1.7)#0.4,1.6)
						h.GetYaxis().SetTitle("Signal / Control")
						h.Draw("AXIS")
						#todraw += [[h,"AXIS"]]
						counterCAT += 1	
					f = h.GetListOfFunctions()[0]
					g = INTERNALgraph(h)
					graphs += [g]
					bands += [b]
					if TYPE=='QCD': 
						g.SetMarkerStyle(25)
						g.SetMarkerColor(kBlue)
						g.SetLineColor(kBlue)
						g.SetLineStyle(1)
						f.SetLineColor(kBlue)
						f.SetLineWidth(1)
						f.SetLineStyle(2)
						b.SetFillColor(TColor.GetColorBright(kBlue))
						b.SetFillStyle(3004)
					else:
						g.SetMarkerStyle(20)
						g.SetMarkerColor(kBlack)
						g.SetLineColor(kBlack)
						f.SetLineColor(kBlack)
						f.SetLineStyle(1)
						f.SetLineWidth(1)
						b.SetFillColor(kBlack)
						b.SetFillStyle(3005)
					g.Draw("same PZ")
					f.Draw("same")
					b.Draw("same E3")
					#todraw += [[g,"same pz"]]
					#todraw += [[f,"same"]]
					#todraw += [[b,"same e3"]]
					thisl = leg[counterCAT].AddEntry(g,"%s CAT%d/CAT%d"%(TYPE,int(CAT.replace('CAT','')),0 if 'NOM' in SEL else 4),'LP')
					thisl.SetTextColor(kBlue if TYPE=='QCD' else kBlack)
			
			#if len(todraw)>0: todraw[0][0].Draw(todraw[0][1])
			#for x in range(len(todraw)-1,0,-1):
			#	todraw[x][0].Draw(todraw[x][1])

			leg[counterCAT].SetY1(leg[counterCAT].GetY2()-(leg[counterCAT].GetNRows()+1)*0.05)
			leg[counterCAT].Draw()
		
		can.SaveAs('plots/%s.png'%can.GetName())
		can.SaveAs('plots/%s.pdf'%can.GetName())
		can.Close()

# clean
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkTemplateFunctions()
