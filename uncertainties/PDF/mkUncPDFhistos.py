#!/usr/bin/env python

import os,re,sys,itertools
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
	mp.add_option('-s','--skip',help='Skip stuff not matching this.',type='str')
	mp.add_option('--noleg',help='No side legend.',action='store_true',default=False)
	mp.add_option('--plotmax',help='Set plot scale for rel/abs plots.',type='float',default=0.055)
	return mp

##################################################
class mycanvas():
	def __init__(self,opts,base,var,pdf,suff):
		self.cb = TCanvas("%s_%s_%s_UncPDF_relative"%(var,pdf,base),"%s_%s_%s_UncPDF_relative"%(var,pdf,base),1600,1200)
		self.ct = TCanvas("%s_%s_%s_UncPDF_absolute"%(var,pdf,base),"%s_%s_%s_UncPDF_absolute"%(var,pdf,base),1600,1200)
		onepad(opts,self.cb)
		onepad(opts,self.ct)
		self.c = TCanvas("%s_%s_%s_UncPDF"%(var,pdf,base),"%s_%s_%s_UncPDF"%(var,pdf,base),1600,1200)
		self.p1,self.p2 = twopad(opts,self.c)
		self.l = legend(0.75,0.5,0.99,0.95,"pdfset-%s (%s)"%(pdf,suff))
		if not opts.noleg:
			self.lt = legend(0.75,0.5,0.99,0.95,"pdfset-%s (%s) (frac)"%(pdf,suff))
			self.lb = legend(0.75,0.5,0.99,0.95,"pdfset-%s (%s) (rel)"%(pdf,suff))
		else:
			self.lt = legend(0.75,0.5,0.99,0.95)
			self.lb = legend(0.75,0.5,0.99,0.95)

	def Close(self):
		self.c.Close()
		self.cb.Close()
		self.ct.Close()
		
##################################################
def onepad(opts,c):
	c.cd()
	c.SetTopMargin(0.05)
	c.SetLeftMargin(0.12)
	if not opts.noleg: c.SetRightMargin(0.26)
	else: c.SetRightMargin(0.05)
	c.SetBottomMargin(0.10)
	c.SetFillStyle(0)
	c.SetTicks(1,1)
	c.Update()

##################################################
def twopad(opts,c):
	c.cd()
	p1 = TPad("p1","p1",0.0,0.37,1.0,1.0)
	p2 = TPad("p2","p2",0.0,0.0,1.0,0.4)
	p1.SetTopMargin(0.05)
	p1.SetBottomMargin(0.04)
	p1.SetLeftMargin(0.12)
	#if not opts.noleg: p1.SetRightMargin(0.26)
	#else: p1.SetRightMargin(0.12)
	p1.SetRightMargin(0.26)
	p2.SetTopMargin(0)
	p2.SetLeftMargin(0.12)
	#if not opts.noleg: p2.SetRightMargin(0.26)
	#else: p2.SetRightMargin(0.12)
	p2.SetRightMargin(0.26)
	p2.SetBottomMargin(0.25)
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
def legend(left,bottom,right,top,title="",size=0.025):
	l = TLegend(left,bottom,right,top)
	if not title=="":
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
def GFromH(a,h,hp,hm,p):
	gPad.Update()
	colours = {'MSTW':kYellow, 'CT10':kGreen+2, 'NNPDF':kRed}
	lcolours = {'MSTW':kBlack, 'CT10':kGreen+2, 'NNPDF':kRed}
	hatches = {'MSTW':1001, 'CT10':3345, 'NNPDF':3359}
	p = [x for x in colours.keys() if x in p][0]

	g = TGraphAsymmErrors(h.GetNbinsX())

	g.GetXaxis().SetTitle(a.GetXaxis().GetTitle())
	g.GetYaxis().SetTitle(a.GetYaxis().GetTitle())

	g.GetXaxis().SetTitleOffset(1./(gPad.GetHNDC()))
	g.GetYaxis().SetTitleOffset(1./(gPad.GetWNDC()))
	g.GetXaxis().SetLabelOffset(0.005/(gPad.GetHNDC()))
	g.GetYaxis().SetLabelOffset(0.005/(gPad.GetWNDC()))

	g.SetLineColor(h.GetLineColor())
	g.SetLineWidth(2)
	g.SetFillColor(colours[p] if p in colours else kBlack)
	g.SetFillStyle(hatches[p] if p in hatches else 3003)

	h.SetLineColor(lcolours[p] if p in lcolours else kBlack)
	hp.SetLineColor(lcolours[p] if p in lcolours else kBlack)
	hm.SetLineColor(lcolours[p] if p in lcolours else kBlack)
	h.SetLineWidth(3)
	hp.SetLineWidth(2)
	hm.SetLineWidth(2)
	h.SetLineStyle(9)
	hp.SetLineStyle(0)
	hm.SetLineStyle(0)

	g.GetXaxis().SetLimits(h.GetBinLowEdge(1),h.GetBinLowEdge(h.GetNbinsX()+1))

	g.SetTitle("")

	g.GetXaxis().SetTitleSize(0.035)
	g.GetXaxis().SetLabelSize(0.030)

	for iBin in range(1,h.GetNbinsX()+1):
		x = h.GetBinCenter(iBin)
		y = h.GetBinContent(iBin)
		xp = h.GetBinWidth(iBin)/2.
		xm = h.GetBinWidth(iBin)/2.
		yp = hp.GetBinContent(iBin) - y
		ym = y - hm.GetBinContent(iBin)
		g.SetPoint(iBin-1,x,y)
		g.SetPointError(iBin-1,xm,xp,ym,yp)


	return g

##################################################
##################################################
def mkUncPDFhistos():
	mp = parser()
	opts,args = mp.parse_args()

	l1("Loading from %s"%opts.fout)
	f = TFile.Open(opts.fout,'update')
	fname = opts.fout.split('/')[-1].replace('.root','')
	makeDirs("plots/%s"%fname)

	gStyle.SetOptStat(0)
	gStyle.SetTitleFont(43)
	gStyle.SetLabelFont(43)
	gStyle.SetTitleSize(0.035,"XYZT")
	gStyle.SetLabelSize(0.030,"XYZT")
	gROOT.ProcessLine("gErrorIgnoreLevel = kWarning;")
	gROOT.SetBatch(1)

	keys = [k.GetName() for k in f.GetListOfKeys() if not '_' in k.GetName()]
	axistitles = {'mvaNOM': 'mva set A', 'mvaVBF': 'mva set B', 'mbbReg1': 'regressed m_{b#bar{b}}', 'mbbReg2': 'regressed m_{b#bar{b}}'}


	for k in keys: 
		archive = {}
# base tag
		base = k
		if opts.skip and not opts.skip in base: continue
		for suff in ['','_acc']:
# to save in
			makeDirs("plots/%s/%s"%(fname,'yield' if suff=='' else 'acceptance'))
			makeDirsRoot(f,base+"_canvases%s"%suff)
# get histo names
			res = "results"+suff
			if not any(["%s_%s"%(base,res) in x.GetName() for x in f.GetListOfKeys()]): continue

			gDirectory.cd(base+"_%s"%res)
			resultkeys = sorted([h.GetName() for h in gDirectory.GetListOfKeys()])
			gDirectory.cd("/")
# variable list & pdf list
			variables = []
			pdfs = []
			for h in resultkeys:
		#		if 'band' in h: continue
				variables += [h.split('-')[0]]
				pdfs += [h.split('_')[2]]
			l1("Filling plots for %s (%s):"%(base,'yield' if suff=='' else 'acceptance'))
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
						archive[hv][pdfshort][tag] = f.Get("%s_%s/%s"%(base,res,h))
	
#			for k,v in archive.iteritems():
#				print k
#				for k2,v2 in v.iteritems():
#					print '\t',k2
#					for k3,v3 in v2.iteritems():
#						print '\t\t',k3,v3
#		sys.exit()
#
#		if 1==1:

			# container
			canvases = {}
			ratios = {}
			gs = []
			for v in archive.keys():
				canvases[v] = {}
				ratios[v] = {}
				for p in archive[v].keys()+['all']:
					canvases[v][p] = mycanvas(opts,base,v,p,'yield' if suff=='' else 'acceptance')
					ratios[v][p] = {}

			# drawing
			for v in archive.keys():

				for p in archive[v].keys()+['all']:
					c = canvases[v][p]
					l2("Running for %s -- %s"%(v,p))
					c.l.SetY1(0.95-0.032*(len(archive[v][p]) if not p=='all' else sum([len(archive[v][p2]) for p2 in archive[v].keys()]))-0.032*6/5)
					if 'all' in p:
						c.lt.SetY1(0.95-0.032*(len([x for x in list(itertools.chain(*[archive[v][p2].keys() for p2 in archive[v].keys()])) if 'cl' in x]))-0.032*6/5)
						c.lb.SetY1(0.95-0.032*(len([x for x in list(itertools.chain(*[archive[v][p2].keys() for p2 in archive[v].keys()])) if 'cl' in x])+1)-0.032*6/5)
						if opts.noleg:
							c.lt.SetX1(0.15)
							c.lt.SetX2(0.40)
							c.lt.SetY1(0.15)
							c.lt.SetY2(0.15+0.032*(len([x for x in list(itertools.chain(*[archive[v][p2].keys() for p2 in archive[v].keys()])) if 'cl' in x])))#+0.032*6/5)
							c.lb.SetX1(0.15)
							c.lb.SetX2(0.40)
							c.lb.SetY1(0.15)
							c.lb.SetY2(0.15+0.032*(len([x for x in list(itertools.chain(*[archive[v][p2].keys() for p2 in archive[v].keys()])) if 'cl' in x])+1))#+0.032*6/5)
				
					c.p1.cd()
					haxisp1 = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp1")
					haxisp1.GetXaxis().SetTitleSize(0)
					haxisp1.GetXaxis().SetLabelSize(0)
					haxisp1.GetYaxis().SetTitleOffset(haxisp1.GetYaxis().GetTitleOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					haxisp1.GetYaxis().SetLabelOffset(haxisp1.GetYaxis().GetLabelOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					haxisp1.GetYaxis().SetTitle("N")
					gPad.Update()
					#if suff=='': 
					haxisp1.GetYaxis().SetRangeUser(0.,round(haxisp1.GetBinContent(haxisp1.GetMaximumBin())*1.2,2))
					#else:        haxisp1.GetYaxis().SetRangeUser(0.90,1.10)
					if v=='plain': haxisp1.GetXaxis().SetNdivisions(101)
					haxisp1.Draw("AXIS")
					c.p2.cd()
					eps = 1e-4
					haxisp2 = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp2")
					haxisp2.GetXaxis().SetTitle("%s"%axistitles[v] if not v=='plain' else "")
					haxisp2.GetYaxis().SetTitle("other / central - 1")
					if suff=='': 
						plotmax = 0.075 if not 'GF' in base else 0.1
						haxisp2.GetYaxis().SetRangeUser(-plotmax+eps,plotmax-eps)
					else:        
						haxisp2.GetYaxis().SetRangeUser(-opts.plotmax+eps,opts.plotmax-eps)
						haxisp2.GetYaxis().SetNdivisions(506)
					haxisp2.GetXaxis().SetLabelOffset(haxisp2.GetXaxis().GetLabelOffset()/(gPad.GetHNDC()))
					haxisp2.GetXaxis().SetTitleOffset(haxisp2.GetXaxis().GetTitleOffset()/(gPad.GetHNDC()))
					haxisp2.GetYaxis().SetLabelOffset(haxisp2.GetYaxis().GetLabelOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					haxisp2.GetYaxis().SetTitleOffset(haxisp2.GetYaxis().GetTitleOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					if v=='plain': 
						haxisp2.SetNdivisions(101)
						haxisp2.GetXaxis().SetBinLabel(1,'ALL')
					haxisp2.Draw("AXIS")
					hone = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axisp1")
					for iBin in range(0,hone.GetNbinsX()+2): 
						hone.SetBinContent(iBin,1.0)
						hone.SetBinError(iBin,0.0)

					c.cb.cd()
					gPad.Update()
					haxispb = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axispb")
					haxispb.GetXaxis().SetTitle("%s"%axistitles[v] if not v=='plain' else "")
					haxispb.GetYaxis().SetTitle("Fractional uncertainty, relative to CT10(0) NLO (68% C.L.)")
					if suff=='': 
						plotmax = 0.06 if not 'GF' in base else 0.1
						haxispb.GetYaxis().SetRangeUser(-plotmax+eps,plotmax-eps)
					else:        
						haxispb.GetYaxis().SetRangeUser(-opts.plotmax+eps,opts.plotmax-eps)
						haxispb.GetYaxis().SetNdivisions(506)
					haxispb.GetXaxis().SetLabelOffset(haxispb.GetXaxis().GetLabelOffset()/(gPad.GetHNDC()))
					haxispb.GetXaxis().SetTitleOffset(haxispb.GetXaxis().GetTitleOffset()/(gPad.GetHNDC()))
					haxispb.GetYaxis().SetLabelOffset(haxispb.GetYaxis().GetLabelOffset()/(gPad.GetWNDC())*1.1)
					haxispb.GetYaxis().SetTitleOffset(haxispb.GetYaxis().GetTitleOffset()/(gPad.GetWNDC())*1.1)
					if v=='plain': 
						haxispb.SetNdivisions(101)
						haxispb.GetXaxis().SetBinLabel(1,'ALL')
					haxispb.Draw("AXIS")
	
					c.ct.cd()
					gPad.Update()
					haxispt = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axispt")
					haxispt.GetYaxis().SetTitleOffset(haxispt.GetYaxis().GetTitleOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					haxispt.GetYaxis().SetLabelOffset(haxispt.GetYaxis().GetLabelOffset()/(1.-gPad.GetRightMargin()-gPad.GetLeftMargin()))
					haxispt.GetYaxis().SetTitle("N")
					#print suff
					if suff=='': haxispt.GetYaxis().SetRangeUser(0.,round(haxispt.GetBinContent(haxispt.GetMaximumBin())*1.2,1))
					else:        haxispt.GetYaxis().SetRangeUser(0.90,1.10)
					if v=='plain': 
						haxispt.SetNdivisions(101)
						haxispt.GetXaxis().SetBinLabel(1,'ALL')
					haxispt = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("axispt")
					haxispt.GetXaxis().SetTitle("%s"%axistitles[v] if not v=='plain' else "")
					haxispt.GetYaxis().SetTitle("Fractional uncertainty (68% C.L.)")
					if suff=='': 
						plotmax = 0.04 if not 'GF' in base else 0.06
						haxispt.GetYaxis().SetRangeUser(-plotmax+eps,plotmax-eps)
					else:        
						haxispt.GetYaxis().SetRangeUser(-opts.plotmax+eps,opts.plotmax-eps)
						haxispt.GetYaxis().SetNdivisions(506)
					haxispt.GetXaxis().SetLabelOffset(haxispt.GetXaxis().GetLabelOffset()/(gPad.GetHNDC()))
					haxispt.GetXaxis().SetTitleOffset(haxispt.GetXaxis().GetTitleOffset()/(gPad.GetHNDC()))
					haxispt.GetYaxis().SetLabelOffset(haxispt.GetYaxis().GetLabelOffset()/(gPad.GetWNDC())*1.1)
					haxispt.GetYaxis().SetTitleOffset(haxispt.GetYaxis().GetTitleOffset()/(gPad.GetWNDC())*1.1)
					if v=='plain': 
						haxispt.SetNdivisions(101)
						haxispt.GetXaxis().SetBinLabel(1,'ALL')
					haxispt.Draw("AXIS")

					href = archive[v][p if not p=='all' else 'CT10']['cl' if not p=='band' else 'M'].Clone("ref")
					archiveall = {}
					prevp = ""
					if p=='all':
						keys = [] 
						for x in [[("%s-%s"%(p2,t2),v2) for t2,v2 in archive[v][p2].iteritems()] for p2 in archive[v].keys()]: keys += x 
						archiveall = dict(keys)
					np = 0
					lines = []
					for it,(t,h) in enumerate(sorted(archive[v][p].iteritems() if not p=='all' else archiveall.iteritems(),key=lambda (x,y):(not 'band' in x,x.split('-')[0] if len(x.split('-'))>1 else 1.,['U','M','L','upcb','up','upas','cl','dnas','dn','dncb'].index(y.GetName().split('_')[-1])))):
						if p=='all': palt,talt = t.split('-')
						else: palt,talt = p,t	

						r2s = []
						r3s = []

						# top pad
						c.p1.cd()
						h.Draw("same")
						# bottom pad
						c.p2.cd()
						ratios[v][p][t] = h.Clone(("r%s"%h.GetName()).replace(palt,'all' if 'all' in p else p))
						r = ratios[v][p][t]
						r.Divide(href)
						r.Add(hone,-1)
						if 'cl' in t and ('CT10' in p or 'CT10' in t): r.SetLineWidth(4)
						#if 'cb' in t: 
						#	r.SetFillStyle(3003)
						#	r.SetFillColor(r.GetLineColor())
						if 'band' in h.GetName() and not 'M' in t: 
							r.SetFillStyle(3003)
							r.SetFillColor(TColor.GetColorBright(kCyan))
						r.Draw("samehiste0")
						# legend
						legentry = c.l.AddEntry(r,t.replace("as"," #alpha_{s}").replace("cb"," combined") + ("" if not 'plain' in h.GetName() else " (%+.2f%%)"%(r.GetBinContent(1)*100)),"L" if not ('band' in h.GetName() and not 'M' in t) else "LF")
						if 'cl' in t: 
							legentry.SetTextFont(72)
						c.p1.cd()
						if (p=='all' and (((not prevp=="") and (not prevp==palt)))) or (np==0): 
							line = TLine(0.75,0.95-0.032*np-0.034,0.99,0.95-0.032*np-0.034)
							line.SetNDC(1)
							line.SetLineColor(kBlack)
							line.SetLineWidth(1)
							lines += [line]
						if p=='all': np += 1
						prevp = palt
					
					counter = 0
					for it,(t,h) in enumerate(sorted(archive[v][p].iteritems() if not p=='all' else archiveall.iteritems(),key=lambda (x,y):(not 'MSTW' in x,not 'band' in x,x.split('-')[0] if len(x.split('-'))>1 else 1.,['U','M','L','upcb','up','upas','cl','dnas','dn','dncb'].index(y.GetName().split('_')[-1])))):
						if p=='all': palt,talt = t.split('-')
						else: palt,talt = p,t	
						
						total = len([x for x in list(itertools.chain(*[archive[v][p2].keys() for p2 in archive[v].keys()])) if 'cl' in x])-1
						if 'all' in p and 'cl' in t:
							r    = ratios[v][palt][talt].Clone()
							rp   = ratios[v][palt]['upcb'].Clone()
							rm   = ratios[v][palt]['dncb'].Clone()

							if counter==total:
								mm   = ratios[v]['all']['band-U'].Clone()
								ml   = ratios[v]['all']['band-L'].Clone()
								mm.SetFillStyle(0)
								mm.SetLineColor(kBlue+1)
								mm.SetLineStyle(7)
								mm.SetLineWidth(3)
								ml.SetFillStyle(0)
								ml.SetLineColor(kBlue+1)
								ml.SetLineStyle(7)
								ml.SetLineWidth(3)

							rabs  = ratios[v][p][t].Clone()
							rpabs = ratios[v][p][palt+'-upcb'].Clone()	
							rmabs = ratios[v][p][palt+'-dncb'].Clone()	
							
##							# bottom copy
							c.cb.cd()
							if counter==0: haxispb.Draw("axis") 
							grabs = GFromH(haxispb,rabs,rpabs,rmabs,palt)
							grabs.Draw("p2same")
							rabs.Draw("samehist")
							rpabs.Draw("samehist")
							rmabs.Draw("samehist")
							grabs.SetLineColor(rabs.GetLineColor())
							#grabs.SetLineStyle(rabs.GetLineStyle())
							c.lb.AddEntry(grabs,palt,"LF")
							if counter==total:
								mm.Draw("samehist")
								ml.Draw("samehist")
								c.lb.AddEntry(mm,'Full uncertainty',"L")
							gPad.RedrawAxis()
							gs += [grabs,rabs,rpabs,rmabs]
							if counter==total: gs += [mm,ml]

##							# top copy
							c.ct.cd()
							if counter==0: haxispt.Draw("axis") 
							gr = GFromH(haxispb,r,rp,rm,palt)
							gr.Draw("p2same")
							r.Draw("samehist")
							rp.Draw("samehist")
							rm.Draw("samehist")
							gr.SetLineColor(r.GetLineColor())
							#gr.SetLineStyle(r.GetLineStyle())
							c.lt.AddEntry(gr,palt,"LF")
							gPad.RedrawAxis()
							gs += [gr,r,rp,rm]

							if counter==total:
								print "%8s |"%"bin",
								for iBin in range(1,r.GetNbinsX()+1): print " %8d |"%iBin,
								print
								print "-"*((r.GetNbinsX()+1)*12)
								print "%8s |"%"low",
								for iBin in range(1,r.GetNbinsX()+1): print " %8.4f |"%ml.GetBinContent(iBin),
								print
								print "%8s |"%"high",
								for iBin in range(1,r.GetNbinsX()+1): print " %8.4f |"%mm.GetBinContent(iBin),
								print
								print

							counter += 1

					c.p1.cd()
					gPad.Update()
					c.l.Draw()
					for l in lines: l.Draw()

					c.ct.cd()
					c.lt.Draw()

					c.cb.cd()
					c.lb.Draw()
		# saving
					c.c.Update()
					c.c.SaveAs("plots/%s/%s/%s.png"%(fname,'yield' if suff=='' else 'acceptance',c.c.GetName()))
					c.c.SaveAs("plots/%s/%s/%s.pdf"%(fname,'yield' if suff=='' else 'acceptance',c.c.GetName()))
					if 'all' in p:
						c.cb.Update()
						c.cb.SaveAs("plots/%s/%s/%s%s.png"%(fname,'yield' if suff=='' else 'acceptance',c.cb.GetName(),"_noleg" if opts.noleg else ""))
						c.cb.SaveAs("plots/%s/%s/%s%s.pdf"%(fname,'yield' if suff=='' else 'acceptance',c.cb.GetName(),"_noleg" if opts.noleg else ""))
						c.ct.Update()
						c.ct.SaveAs("plots/%s/%s/%s%s.png"%(fname,'yield' if suff=='' else 'acceptance',c.ct.GetName(),"_noleg" if opts.noleg else ""))
						c.ct.SaveAs("plots/%s/%s/%s%s.pdf"%(fname,'yield' if suff=='' else 'acceptance',c.ct.GetName(),"_noleg" if opts.noleg else ""))
					gDirectory.cd("%s:/%s_canvases%s"%(f.GetName(),base,suff))
					c.c.Write("%s"%(c.c.GetName()),TH1.kOverwrite)
					gDirectory.cd("%s:/"%(f.GetName()))
					c.Close()

			
	f.Close()

##################################################
if __name__=='__main__':
	mkUncPDFhistos()

##################################################
