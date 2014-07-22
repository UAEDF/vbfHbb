#!/usr/bin/env python

import os,re,sys
from optparse import OptionParser
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *

##################################################
def parser():
	mp = OptionParser()
	mp.add_option('-o','--fout',help='Input/Output filename.',type='str')
	return mp

##################################################
def twopad(c):
	c.cd()
	p1 = TPad("p1","p1",0.0,0.37,1.0,1.0)
	p2 = TPad("p2","p2",0.0,0.0,1.0,0.4)
	p1.SetBottomMargin(0.05)
	p1.SetRightMargin(0.2)
	p2.SetTopMargin(0)
	p2.SetRightMargin(0.2)
	p2.SetFillStyle(0)
	p1.SetTicks(1,1)
	p2.SetTicks(1,1)
	c.Update()
	p1.Draw()
	c.Update()
	p2.Draw()
	c.Update()
	return p1,p2

##################################################
def divide(hnum,hden):
	hrat = hnum.Clone("%s_rel"%hnum.GetName())
	hrat.Divide(hden)
	eps = 1e-3
	hrat.GetYaxis().SetRangeUser(0.85+eps,1.15-eps)
	hrat.SetTitle("")
	return hrat

##################################################
def legend(left,bottom,right,top,title,size=0.025):
	l = TLegend(left,bottom,right,top,title)
	l.SetTextSize(size)
	l.SetTextColor(kBlack)
	l.SetFillColor(0)
	l.SetFillStyle(0)
	return l

##################################################
def mkUncPDFhistos():
	mp = parser()
	opts,args = mp.parse_args()

	l1("Loading from %s"%opts.fout)
	f = TFile.Open(opts.fout,'update')

	gStyle.SetOptStat(0)
	gStyle.SetPadBorderMode(0)
	gStyle.SetCanvasBorderMode(0)
	#gROOT.SetBatch(1)

	keys = [k.GetName() for k in f.GetListOfKeys() if not '_' in k.GetName()]

	for k in keys: 
# base tag
		base = k
# to save in
		makeDirsRoot(f,base+"_canvases")
# get histo names
		gDirectory.cd(base+"_results")
		resultkeys = sorted([h.GetName() for h in gDirectory.GetListOfKeys()])
		gDirectory.cd("/")
# variable list & pdf list
		variables = []
		pdfs = []
		for h in resultkeys:
			variables += [h.split('-')[0]]
			pdfs += [h.split('_')[2]]
		l2("Variables:")
		variables = list(set(variables))
		for v in variables: l3("variable: %s"%v)
		pdfs = list(set(pdfs))
		l2("PDFs:")
		for pdf in pdfs: l3("pdf: %s"%pdf)

	makeDirs("plots")
	ds = []
	rs = []
	ls = [None]*4
	for v in variables:
		c = TCanvas("%s_UncPDF"%v,"%s_UncPDF"%v,2400,2400)
		c.Divide(2,2)
		n = 0
		for ip,p in enumerate(['CT10','MSTW','NNPDF','all']):
			l2("Running for %s"%p)
			cp = c.GetPad(ip+1)
			p1,p2 = twopad(cp)
			ls[ip] = legend(0.8,0.85,0.98,0.90,"pdfsets-%s"%p)
			l = ls[ip]

			href = None
			for h in resultkeys:
				if 'cl' in h and v in h and 'CT10' in h: 
					href = h
					rref = f.Get("%s_results/%s"%(base,href))
					break
			n = 0
			for h in resultkeys:
				if v in h and (p in h or p=='all'):
					r = f.Get("%s_results/%s"%(base,h))
					r2 = r.Clone("%s2"%r.GetName()) 
					rs += [r2]
					p2.cd()
					d = divide(r,rref)
					ds += [d]
					d.Draw("" if n==0 else "same")
					p1.cd()
					if n==0: 
						r2.GetXaxis().SetLabelSize(0)
						r2.GetXaxis().SetTitleSize(0)
					r2.Draw("" if n==0 else "same")
					l.AddEntry(r,'_'.join(r.GetName().split('_')[2:3]),"L")
					n += 1
			cp.Update()
			c.WaitPrimitive()
			c.Update()
			l.SetY1(0.90-n*0.035)
			l.Draw("same")
			c.WaitPrimitive()
			c.Update()

		c.Update()
		c.SaveAs("plots/%s.png"%c.GetName())
		c.Close()

	f.Close()

##################################################
if __name__=='__main__':
	mkUncPDFhistos()

##################################################
