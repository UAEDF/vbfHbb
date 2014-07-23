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
class mycanvas():
	def __init__(self,base,var,pdf):
		self.c = TCanvas("%s_%s_%s_UncPDF"%(var,pdf,base),"%s_%s_%s_UncPDF"%(var,pdf,base),1600,1200)
		self.p1,self.p2 = twopad(self.c)
		self.l = legend(0.81,0.5,0.99,0.9,"pdfset-%s"%pdf)
		
##################################################
def twopad(c):
	c.cd()
	p1 = TPad("p1","p1",0.0,0.37,1.0,1.0)
	p2 = TPad("p2","p2",0.0,0.0,1.0,0.4)
	p1.SetBottomMargin(0.04)
	p1.SetLeftMargin(0.12)
	p1.SetRightMargin(0.2)
	p2.SetTopMargin(0)
	p2.SetLeftMargin(0.12)
	p2.SetRightMargin(0.2)
	p2.SetBottomMargin(0.2)
	p2.SetFillStyle(0)
	p1.SetTicks(1,1)
	p2.SetTicks(1,1)
	c.Update()
	p1.Draw()
	c.Update()
	p2.Draw()
	c.Update()
	return p1,p2

####################################################
##def divide(hnum,hden):
##	hrat = hnum.Clone("%s_rel"%hnum.GetName())
##	hrat.Divide(hden)
##	eps = 1e-3
##	hrat.GetYaxis().SetRangeUser(0.85+eps,1.15-eps)
##	hrat.SetTitle("")
##	return hrat

##################################################
def legend(left,bottom,right,top,title,size=0.025):
	l = TLegend(left,bottom,right,top)
	l.SetTextSize(size*6/5)
	l.SetTextFont(62)
	l.SetHeader(title)
	l.SetTextFont(42)
	l.SetTextSize(size)
	l.SetTextColor(kBlack)
	l.SetFillColor(TColor.GetColorBright(kGray))
	l.SetFillStyle(1001)
	return l

##################################################
def mkUncPDFhistos():
	mp = parser()
	opts,args = mp.parse_args()

	l1("Loading from %s"%opts.fout)
	f = TFile.Open(opts.fout,'update')
	makeDirs("plots")

	gStyle.SetOptStat(0)
	gStyle.SetTitleFont(43)
	gStyle.SetLabelFont(43)
	gStyle.SetTitleSize(0.035,"XYZT")
	gStyle.SetLabelSize(0.030,"XYZT")
	gROOT.ProcessLine("gErrorIgnoreLevel = kWarning;")
	gROOT.SetBatch(1)

	keys = [k.GetName() for k in f.GetListOfKeys() if not '_' in k.GetName()]
	axistitles = {'mvaNOM': 'mva set A', 'mvaVBF': 'mva set B', 'mbbReg1': 'regressed m_{b#bar{b}}', 'mbbReg2': 'regressed m_{b#bar{b}}'}

	archive = {}

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
	#		if 'band' in h: continue
			variables += [h.split('-')[0]]
			pdfs += [h.split('_')[2]]
		l2("Variables:")
		variables = list(set(variables))
		for v in variables: 
			l3("variable: %s"%v)
		# sort by variable
			if not v in archive: archive[v] = {}
		pdfs = list(set(pdfs))
		l2("PDFs:")
		for pdf in pdfs: 
			l3("pdf: %s"%pdf)
			pdfshort = pdf.split('as')[0]

			for h in resultkeys:
				if any([x in h for x in ['denv','dpm','rpm']]): continue
				hv = h.split('-')[0]
				if pdf in h: 
		# sort by pdf
					if not pdfshort in archive[hv]: archive[hv][pdfshort] = {}
		# sort by tag
					tag = h.split('_')[-1]
					archive[hv][pdfshort][tag] = f.Get("%s_results/%s"%(base,h))
	
#	for k,v in archive.iteritems():
#		print k
#		for k2,v2 in v.iteritems():
#			print '\t',k2
#			for k3,v3 in v2.iteritems():
#				print '\t\t',k3,v3
#	sys.exit()

		# container
		canvases = {}
		ratios = {}
		for v in archive.keys():
			canvases[v] = {}
			ratios[v] = {}
			for p in archive[v].keys()+['all']:
				canvases[v][p] = mycanvas(base,v,p)
				ratios[v][p] = {}

		# drawing
		l1("Filling plots for %s:"%base)
		for v in archive.keys():
			for p in archive[v].keys()+['all']:
				c = canvases[v][p]
				l2("Running for %s -- %s"%(v,p))
				c.l.SetY1(0.9-0.032*(len(archive[v][p]) if not p=='all' else sum([len(archive[v][p2]) for p2 in archive[v].keys()]))-0.032*6/5)
				
				c.p1.cd()
				haxisp1 = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp1")
				haxisp1.GetXaxis().SetTitleSize(0)
				haxisp1.GetXaxis().SetLabelSize(0)
				haxisp1.GetYaxis().SetTitleOffset(haxisp1.GetYaxis().GetTitleOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
				haxisp1.GetYaxis().SetLabelOffset(haxisp1.GetYaxis().GetLabelOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
				haxisp1.GetYaxis().SetTitle("N")
				haxisp1.GetYaxis().SetRangeUser(0.,round(haxisp1.GetBinContent(haxisp1.GetMaximumBin())*1.1,1))
				if v=='plain': haxisp1.SetNdivisions(101)
				haxisp1.Draw("AXIS")
				c.p2.cd()
				eps = 1e-3
				haxisp2 = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp2")
				haxisp2.GetXaxis().SetTitle("%s"%axistitles[v] if not v=='plain' else "")
				haxisp2.GetYaxis().SetTitle("other / central - 1")
				haxisp2.GetYaxis().SetRangeUser(-0.15+eps,0.15-eps)
				haxisp2.GetXaxis().SetLabelOffset(haxisp2.GetXaxis().GetLabelOffset()/(gPad.GetHNDC()))
				haxisp2.GetXaxis().SetTitleOffset(haxisp2.GetXaxis().GetTitleOffset()/(gPad.GetHNDC()))
				haxisp2.GetYaxis().SetLabelOffset(haxisp2.GetYaxis().GetLabelOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
				haxisp2.GetYaxis().SetTitleOffset(haxisp2.GetYaxis().GetTitleOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
				if v=='plain': 
					haxisp2.SetNdivisions(101)
					haxisp2.GetXaxis().SetBinLabel(1,'ALL')
				haxisp2.Draw("AXIS")
				hone = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp1")
				for iBin in range(0,hone.GetNbinsX()+2): hone.SetBinContent(iBin,1.0)

				href = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("ref")
				archiveall = {}
				prevp = ""
				if p=='all':
					keys = [] 
					for x in [[("%s-%s"%(p2,t2),v2) for t2,v2 in archive[v][p2].iteritems()] for p2 in archive[v].keys()]: keys += x 
					archiveall = dict(keys)
				np = 0
				lines = []
				for t,h in sorted(archive[v][p].iteritems() if not p=='all' else archiveall.iteritems(),key=lambda (x,y):(not 'band' in x,x.split('-')[0] if len(x.split('-'))>1 else 1.,['U','M','L','upcb','up','upas','cl','dnas','dn','dncb'].index(y.GetName().split('_')[-1]))):
					if p=='all': palt,talt = t.split('-')
					else: palt,talt = p,t	
					# top pad
					c.p1.cd()
					h.Draw("same")
					# bottom pad
					c.p2.cd()
					ratios[v][palt][talt] = h.Clone("r%s"%h.GetName())
					r = ratios[v][palt][talt]
					r.Divide(href)
					r.Add(hone,-1)
					if 'cl' in t and ('CT10' in p or 'CT10' in t): r.SetLineWidth(4)
					#if 'cb' in t: 
					#	r.SetFillStyle(3003)
					#	r.SetFillColor(r.GetLineColor())
					if 'band' in h.GetName() and not 'M' in t: 
						r.SetFillStyle(3003)
						r.SetFillColor(TColor.GetColorBright(kCyan))
					r.Draw("same")
					# legend
					legentry = c.l.AddEntry(r,t.replace("as"," #alpha_{s}").replace("cb"," combined"),"L" if not ('band' in h.GetName() and not 'M' in t) else "LF")
					if 'cl' in t: 
						legentry.SetTextFont(72)
					c.p1.cd()
					if (p=='all' and (((not prevp=="") and (not prevp==palt)))) or (np==0): 
						line = TLine(0.81,0.9-0.032*np-0.034,0.99,0.9-0.032*np-0.034)
						line.SetNDC(1)
						line.SetLineColor(kBlack)
						line.SetLineWidth(1)
						lines += [line]
					if p=='all': np += 1
					prevp = palt
				c.p1.cd()
				gPad.Update()
				c.l.Draw()
				for l in lines: l.Draw()
		# saving
				c.c.Update()
				c.c.SaveAs("plots/%s.png"%(c.c.GetName()))
				gDirectory.cd("%s:/%s_canvases"%(f.GetName(),base))
				c.c.Write("%s"%(c.c.GetName()))
				gDirectory.cd("%s:/"%(f.GetName()))
				c.c.Close()
			
	f.Close()

##################################################
if __name__=='__main__':
	mkUncPDFhistos()

##################################################
