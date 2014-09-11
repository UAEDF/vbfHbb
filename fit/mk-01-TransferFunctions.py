#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
import main

# OPTION PARSER ##################################################################################
##
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mp.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)
	mp.add_option('--catTags',help='tags for categories',type='str',action='callback',callback='optsplit',default=[])
	mp.add_option('--fBound',help='fit MIN and MAX',type='str',action='callback',callback='optsplit',default=['90','200'])	
    return mp

####################################################################################################
def INTERNALprepare(opts):
	lhapdf.setVerbosity(opts.verbosity)
	makeDirs(os.path.split(opts.fout)[0])
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonpdfs = json.loads(filecontent(opts.jsonpdfs))
	jsons = {'samp':jsonsamp,'vars':jsonvars,'info':jsoninfo,'pdfs':jsonpdfs}
	# fix binning
	if opts.binning:
		for v in opts.binning:
			#print v
			jsons['vars']['variables'][v[0]]['nbins_x'] = v[1]
			jsons['vars']['variables'][v[0]]['xmin'] = v[2]
			jsons['vars']['variables'][v[0]]['xmax'] = v[3]
	for v in opts.mvaBins:
			jsons['vars']['variables'][v[0]]['nbins_x'] = opts.mvaBins[v['var']][0]
			jsons['vars']['variables'][v[0]]['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v['var']][1]])
			jsons['vars']['variables'][v[0]]['xmin'] = opts.mvaBins[v['var']][1][0]
			jsons['vars']['variables'][v[0]]['xmax'] = opts.mvaBins[v['var']][1][-1]
	return jsons

####################################################################################################

def INTERNALstyle():
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")
	
	markers = [20, 20 , 23, 21]
	colours = [kBlack,kBlue,kRed,kGreen+2] 
	return markers, colours

####################################################################################################

def INTERNALstyleHist(h,i,markers,colours):
	h.SetMarkerStyle(markers[i])
	h.SetMarkerColor(colours[i])
	h.SetLineColor(colours[i])

####################################################################################################

def INTERNALhistograms(opts):
	hDat = {}
	hRat = {}
	fFit = {}
	gUnc = {}
	for iTag,Tag in enumerate(opts.catTags):
		for iCat,Cat in enumerate(opts.mvaBins[opts.mvaBins.keys(iTag)]):
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
	c = {}
	for iTag,Tag in enumerate(opts.catTags):
		c1[Tag] = None
		c2[Tag] = None
		c[Tag] = None
	return c1, c2, c

####################################################################################################

def INTERNALlegend(Tag):
	leg = new TLegend(0.6,0.6,0.9,0.9)
	leg.SetHeader("%s selection"%Tag)
	leg.SetFillColor(0)
	leg.SetBorderSize(0)
	leg.SetTextFont(42)
	leg.SetTextSize(0.05)

####################################################################################################

def INTERNALline(fun, min, max):
	ln = TF1("line",fun,min,max)
	ln.SetLineColor(kBlack)
	ln.SetLineWidth(1)
	ln.SetLineStyle(2)
	ln.SetMinimum(0.7)
	ln.SetMaximum(1.3)
	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
	ln.GetYaxis().SetTitle("Signal/Control")
	return ln

####################################################################################################

def mkTemplateFunctions():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()

	hDat, hRat, fFit, gUnc, fitter, covariant = INTERNALhistograms()
	c1, c2, c = INTERNALcanvases()

	ln = INTERNALline("1",opts.fBounds[0],opts.fBounds[1])

	for iTag,Tag in enumerate(opts.catTags):
		nCat = opts.mvaBins(opts.mvaBins.keys(iTag))
		fin = TFile.Open('flat/fitFlatTree_%s.root'%Tag)
		l1('Running for %s --> %s'%(Tag,fin.GetName()))
		tin = fin.Get("Hbb/events")
		
		c2[Tag] = TCanvas('transfer_sel%s'%Tag,'transfer_sel%s'%Tag,600*nCat,600)
		c2[Tag].Divide(nCat-1,1)

		leg = INTERNALlegend(Tag)
		
		for iCat in range(nCat):
#			v = jsons['vars']['variables'][opts.variables[opts.variables.keys()[iTag]][0]]

# regular hists
#			if v['xs']: hData[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,iCat),'hDat_sel%s_CAT%d'%(Tag,iCat),int(v['nbins_x']),v['xs'])
#			else: hData[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,iCat),'hDat_sel%s_CAT%d'%(Tag,iCat),int(v['nbins_x']),int(v['xmin']),int(v['xmax']))
			hData[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,iCat),'hDat_sel%s_CAT%d'%(Tag,iCat),10,opts.fBounds[0],opts.fBounds[1])
			h = hData[(Tag,iCat)]
			INTERNALstyleHist(h)
			
# cut
			CUT = TCut("mva%s>%.2f && mva%s<=.2f"%(Tag,opts.mvaBins[opts.mvaBins.keys()[iTag]]['xs'][iCat],opts.mvaBins[opts.mvaBins.keys()[iTag]]['xs'][iCat+1]))
			l2('Cutting with: %s'%CUT)

# drawing
			l2('Drawing mbbReg[%d] --> %s'%(1 if 'NOM' in Tag else 2,h.GetName())
			tin.Draw("mbbReg[%d]>>%s"%(1 if 'NOM' in Tag else 2,h.GetName()),CUT)
			h.Scale(1./h.Integral())
			h.SetDirectory(0)

# ratio hist
			hRat[(Tag,iCat)] = h.Clone(h.GetName().replace('hDat','hRat'))
			r = hRat[(Tag,iCat)]
			INTERNALstyleHist(r)

# dividing by control CAt
			r.Divide(hData[(Tag,0)])
			r.SetDirectory(0)
			
# fit
			fFit[(Tag,iCat)] = TF1(h.GetName().replace('hDat','fitRatio'),'pol1',float(opts.fBound[0]),float(opts.fBound[1]))
			f = fFit[(Tag,iCat)]
			f.SetLineColor(colours[iCat])

			if not iCat==0:
				r.Fit(f,"RQ")
				fitter = TVirtualFitter.GetFitter()
				covariant = TMatrixDSym.Use(fitter.GetNumberTotalParameters(),fitter.GetCovarianceMatrix())
				nBins = 200
				dx = (r.GetBinLowEdge(r.GetNbinsX()+1)-r.GetBinLowEdge(1))/float(nBins)
				vx = array('f',[r.GetBinLowEdge(1)+(i+1)*dx for i in range(nBins)])
				vy = array('f',[f.Eval(vx[i]) for i in range(nBins)])
				vex = array('f',[0.0]*nBins)
				vey = array('f',[sqrt(pow(vx[i],2)*covariant(1,1)+covariant(0,0)) for i in range(nBins)])

				gUnc[(Tag,iCat)] = TGraphErrors(nBins,vx,vy,vex,vey)
				g = gUnc[(Tag,iCat)]
				g.SetFillColor(colours[iCat])
				g.SetFillStyle(3004)
				
				c1[Tag].cd()
				h.Draw('same E')
				leg.AddEntry(h,'CAT%d'%iCat,'P')
				c2[Tag].cd(iCat)
				ln.Draw()
				g.Draw('same E3')
				r.Draw('same')
			else:
				c1[Tag] = TCanvas('MbbShape_sel%s'%Tag,'MbbShape_sel%s'%Tag,1200,800)
				c1[Tag].cd()
				h.SetFillColor(kGray)
				h.Draw('hist')
				leg.AddEntry(h,'CAT%d'%iCat,'F')

			fout.cd()
			f.Write()

		c1[Tag].cd()
		leg.Draw()
		c1[Tag].SaveAs('plots/transfer/%s.png'%c1[Tag].GetName())
		c2[Tag].SaveAs('plots/transfer/%s.png'%c2[Tag].GetName())

	c.SaveAs('plots/transfer/%s.png'%c.GetName())

# clean
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkTemplateFunctions()
