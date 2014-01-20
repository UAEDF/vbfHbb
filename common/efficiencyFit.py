#!/usr/bin/env python

import sys,os
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from copy import deepcopy as dc
from array import array
from optparse import OptionParser,OptionGroup
from toolkit import *
from random import random
import main

####################################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mp.usage += '''
%s
fitting a combination of a AV40 and AV80 map for data and qcd:
%s
efficiencyFit.py -o rootfiles/vbfHbb_2DMaps_corrections_mqq2-ht.root -p "dEtaqq2;jetPt1;run194270,dEtaqq2;jetPt1;run194270" -t "VBF" --datatrigger "VBFOR" -r "AV40,AV80" --mergetag="HT400AV40AV80" --correctiontag="mqq2-ht" --cutoff='y,400'
%s
	'''%("\033[1;4;36m",cyan,plain)
	mg1 = OptionGroup(mp,"%sefficiency fit settings%s"%(cyan,plain))
	mg1.add_option("--cutoff",help="Cutoff x or y for histogram combining. Syntax: 'x,xval'",default="",type=str,action="callback",callback=optsplit)
	mg1.add_option("--correctiontag",help="Tag for correction used. Syntax: 'mqq2-ht'",default="",type=str)
	mg1.add_option("--mergetag",help="Tag for merge performed. Syntax: 'HT400AV40AV80'",default="",type=str)
	mg1.add_option("--addlinear",help="Add extra linear component above x=1000.",action="store_true",default=False)
	mg1.add_option("--lin",help="Use y linear component.",action="store_true",default=False)
	mp.add_option_group(mg1)
	return mp

# FIT FUNCTIONS ####################################################################################
def fefficiency(x,par):
	f0 = par[0] / (1.+TMath.Exp(-(x[0]-par[3])/par[1])) / (1.+TMath.Exp(-(x[1]-par[4])/par[2]))
	return f0

def fefficiency_lin(x,par):
	f1 = par[0] / (1. + TMath.Exp(-(x[0]-par[1])/par[2]))
	f2 = 1. - par[3]*(1. - ((x[0]-2000)/par[4]))*(x[1]-3.5) if x[1]>=3.5 else 0.
	return f1 * f2

def fefficiency_pluslinear(x,par):
	f0 = par[0] / (1.+TMath.Exp(-(x[0]-par[3])/par[1])) / (1.+TMath.Exp(-(x[1]-par[4])/par[2]))
	f1 = 0.0 if not (x[0]>999. and x[1]>499.) else par[5]*(x[0]-999)
	f2 = 0.0 if not (x[0]>999. and x[1]>499.) else par[6]*(x[1]-499)
	return f0 + f1 + f2

def fefficiency_ratio(x,par):
	f0 = par[0] / (1.+TMath.Exp(-(x[0]-par[3])/par[1])) / (1.+TMath.Exp(-(x[1]-par[4])/par[2]))
	f1 = par[5] / (1.+TMath.Exp(-(x[0]-par[8])/par[6])) / (1.+TMath.Exp(-(x[1]-par[9])/par[7]))
	return (f0) / (f1)

def fefficiency_lin_ratio(x,par):
	f1 = par[0] / (1. + TMath.Exp(-(x[0]-par[1])/par[2]))
	f2 = 1. - par[3]*(1. - ((x[0]-2000)/par[4]))*(x[1]-3.5) if x[1]>=3.5 else 0.
	f3 = par[5] / (1. + TMath.Exp(-(x[0]-par[6])/par[7]))
	f4 = 1. - par[8]*(1. - ((x[0]-2000)/par[9]))*(x[1]-3.5) if x[1]>=3.5 else 0.
	f = (f1*f2) / (f3*f4) if not f3*f4==0 else 0.
	return f 

def fefficiency_ratio_pluslinear(x,par):
	f0 = par[0] / (1.+TMath.Exp(-(x[0]-par[3])/par[1])) / (1.+TMath.Exp(-(x[1]-par[4])/par[2]))
	f1 = 0.0 if (x[0]>999. and x[1]>499.) else par[5]*(x[0]-999)
	f2 = 0.0 if not (x[0]>999. and x[1]>499.) else par[6]*(x[1]-499)
	f3 = par[7] / (1.+TMath.Exp(-(x[0]-par[10])/par[8])) / (1.+TMath.Exp(-(x[1]-par[11])/par[9]))
	f4 = 0.0 if not (x[0]>999. and x[1]>499.) else par[12]*(x[0]-999)
	f5 = 0.0 if not (x[0]>999. and x[1]>499.) else par[13]*(x[1]-499)
	return (f0 + f1 + f2) / (f3 + f4 + f5)

# HELPER FUNCTIONS #################################################################################
def hf_difference(hdiff,hdiffabs,h1,f1,title="",titleabs=""):
	for i in range(hdiff.GetNbinsX()+1):
		for j in range(hdiff.GetNbinsY()+1):
			cx = h1.GetXaxis().GetBinCenter(i)
			cy = h1.GetYaxis().GetBinCenter(j)
			hxy = h1.GetBinContent(i,j)
			hexy = h1.GetBinError(i,j)
			fxy = f1.Eval(cx,cy)
			hdiff.SetBinContent(i,j,(hxy-fxy))
			hdiff.SetBinError(i,j,0)
			hdiffabs.SetBinContent(i,j,(hxy-fxy)/hexy if not hexy==0. else -999.)
			hdiffabs.SetBinError(i,j,0)
	hdiff.SetTitle("%s;%s;%s;"%(title,h1.GetXaxis().GetTitle(),h1.GetYaxis().GetTitle()))
	hdiffabs.SetTitle("%s;%s;%s;"%(titleabs,h1.GetXaxis().GetTitle(),h1.GetYaxis().GetTitle()))
	return hdiff,hdiffabs

def ShiftTitles(h,xtimes=1.,ytimes=1.):
	h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*xtimes)
	h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()*ytimes)

def MovePalette(c,h):
	c.Update()
	pal = h.GetListOfFunctions().FindObject("palette")
	pal.SetX1NDC(0.89)
	pal.SetX2NDC(0.92)
	pal.SetY1NDC(0.1)
	pal.SetY2NDC(0.9)
	c.Modified()
	c.Update()

# FIT CLASS ########################################################################################
class efficiency_fit():
	def __init__(self,opts,hsigs,hbkgs,hrats,limits,cutoffx=None,cutoffy=None):
		self.xmin = limits[0] 
		self.xmax = limits[1] 
		self.ymin = limits[2] 
		self.ymax = limits[3] 
		
		self.hsigs = hsigs
		self.hbkgs = hbkgs
		self.hrats = hrats
		if len(hsigs)==2: self.hsig = self.hist_combine(hsigs[0],hsigs[1],cutoffx,cutoffy)
		elif len(hsigs)==1: self.hsig = hsigs[0]
		else: sys.exit("%shsig histogram insufficient.%s"%(red,plain))
		if len(hbkgs)==2: self.hbkg = self.hist_combine(hbkgs[0],hbkgs[1],cutoffx,cutoffy)
		elif len(hbkgs)==1: self.hbkg = hbkgs[0]
		else: sys.exit("%shbkg histogram insufficient.%s"%(red,plain))
		if len(hrats)==2: self.hrat = self.hist_combine(hrats[0],hrats[1],cutoffx,cutoffy)
		elif len(hrats)==1: self.hrat = hrats[0]
		else: sys.exit("%shrat histogram insufficient.%s"%(red,plain))
		
		self.fsig = self.efficiency(opts,"fsig")
		self.fbkg = self.efficiency(opts,"fbkg")
		self.fsob = None
	
	def compare(self):
		self.dsig = self.hsig.Clone("dsig")
		self.dsig_abs= self.hsig.Clone("dsig_abs")
		self.dsig,self.dsig_abs = hf_difference(self.dsig,self.dsig_abs,self.hsig,self.fsig,"data - fit(data)","(data - fit(data))/ #sigma(data)")

		self.dbkg = self.hbkg.Clone("dbkg")
		self.dbkg_abs = self.hbkg.Clone("dbkg_abs")
		self.dbkg,self.dbkg_abs = hf_difference(self.dbkg,self.dbkg_abs,self.hbkg,self.fbkg,"qcd - fit(qcd)","(qcd - fit(qcd)) / #sigma(qcd)")

		self.dsig.GetZaxis().SetRangeUser(-0.15,0.15)
		self.dbkg.GetZaxis().SetRangeUser(-0.15,0.15)
		self.dsig_abs.GetZaxis().SetRangeUser(-25,25)
		self.dbkg_abs.GetZaxis().SetRangeUser(-250,250)

	def fit(self,opts,psig,pbkg):
		if opts.addlinear: npar=7
		elif opts.lin: npar=5
		else: npar=5
		self.fit_setPars(self.fsig,psig[:npar])
		self.fit_setPars(self.fbkg,pbkg[:npar])
		
		#oldscale = self.hsig.GetBinContent(self.hsig.GetNbinsX(),self.hsig.GetNbinsY())
		#self.hsig.Smooth()
		#newscale = self.hsig.GetBinContent(self.hsig.GetNbinsX(),self.hsig.GetNbinsY())
		##print oldscale,newscale
		#self.hsig.Scale(oldscale/newscale)
		#oldscale = self.hbkg.GetBinContent(self.hbkg.GetNbinsX(),self.hbkg.GetNbinsY())
		#self.hbkg.Smooth()
		#newscale = self.hbkg.GetBinContent(self.hbkg.GetNbinsX(),self.hbkg.GetNbinsY())
		##print oldscale,newscale
		#self.hbkg.Scale(oldscale/newscale)
		
		#self.fit_setLims(self.fsig,0,0,1)
		self.fit_setLims(self.fsig,5,0,1)
		self.fit_setLims(self.fsig,6,0,1)
		#self.fit_setLims(self.fbkg,0,0,1)
		self.fit_setLims(self.fbkg,5,0,1)
		self.fit_setLims(self.fbkg,6,0,1)
		if opts.lin:
			self.fit_setLims(self.fsig,0,0.6,1.0)
			self.fit_setLims(self.fbkg,0,0.6,1.0)
			self.fit_setLims(self.fsig,3,0.05,0.15)
			self.fit_setLims(self.fbkg,3,0.05,0.15)
		#	for iv,v in enumerate([1.0,700,50,0.1,1500]):
		#		self.fsig.FixParameter(iv,v)
		#		self.fbkg.FixParameter(iv,v*(1.+random()/10.))

		self.fsig.SetRange(self.xmin,self.ymin,self.xmax,self.ymax)
		self.fbkg.SetRange(self.xmin,self.ymin,self.xmax,self.ymax)
		
		self.hsig.Fit(self.fsig,"RNBM") #WL")
		self.hbkg.Fit(self.fbkg,"RNBM") #WL")
		
		self.fsig.SetMinimum(0.0)
		self.fsig.SetMaximum(1.0)
		self.fbkg.SetMinimum(0.0)
		self.fbkg.SetMaximum(1.0)
#		self.hsig.GetXaxis().SetRangeUser(self.xmin,self.xmax)
#		self.hsig.GetYaxis().SetRangeUser(self.ymin,self.ymax)
#		self.hbkg.GetXaxis().SetRangeUser(self.xmin,self.xmax)
#		self.hbkg.GetYaxis().SetRangeUser(self.ymin,self.ymax)

		self.hsig.GetZaxis().SetRangeUser(0.0,1.0)
		self.hbkg.GetZaxis().SetRangeUser(0.0,1.0)
		self.hrat.GetZaxis().SetRangeUser(0.0,1.4)

		self.efficiency_ratio(opts,"fsob",self.fsig,self.fbkg)
		self.fsob.SetMinimum(0.0)
		self.fsob.SetMaximum(1.4)
		self.fsob.SetRange(self.xmin,self.ymin,self.xmax,self.ymax)

		self.compare()
	
	def drawplain(self,opts,r):
		folder = 'plots/Fits/%s/%s'%(opts.fout.split('/')[-1][:-5],r)
		makeDirs(folder)

		c0 = TCanvas("c0","c0",1500,1000)
		self.hsig.Draw("lego2z")
		c0.Update()
		c0.SaveAs("%s/hsig3D.pdf"%(folder))
		self.hbkg.Draw("lego2z")
		c0.Update()
		c0.SaveAs("%s/hbkg3D.pdf"%(folder))
		self.hsig.SetMarkerSize(self.hsig.GetMarkerSize()*0.8)
		self.hsig.Draw("colz,text45,error")
		c0.Update()
		c0.SaveAs("%s/hsig.pdf"%(folder))
		self.hbkg.SetMarkerSize(self.hbkg.GetMarkerSize()*0.8)
		self.hbkg.Draw("colz,text45,error")
		c0.Update()
		c0.SaveAs("%s/hbkg.pdf"%(folder))
		
		self.hrat.Draw("lego2z,hist")
		c0.Update()
		c0.SaveAs("%s/h3D.pdf"%(folder))
		self.hrat.Draw("colz,text")
		c0.Update()
		c0.SaveAs("%s/h2D.pdf"%(folder))
		
		c0.Close()

	def draw(self,opts,r=""):
		folder = 'plots/Fits/%s%s'%(opts.fout.split('/')[-1][:-5],"/%s"%r if not r=="" else "")
		makeDirs(folder)

		c = TCanvas("c","c",1500,1000)
		c.Divide(2,3)
		c.cd(1)
		self.hsig.Draw("lego,hist")
		self.fsig.Draw("lego,same")
		c.cd(2)
		self.hbkg.Draw("lego,hist")
		self.fbkg.Draw("lego,same")
		c.cd(3)
		self.dsig.Draw("colz,text")
		c.cd(4)
		self.dbkg.Draw("colz,text")
		c.cd(5)
		self.dsig_abs.Draw("colz,text")
		c.cd(6)
		self.dbkg_abs.Draw("colz,text")
		c.Update()
		c.WaitPrimitive()
		c.SaveAs("%s/effi3D.pdf"%(folder))
		
		c.Clear()
		c.Divide(2,2)
		c.cd(1)
		self.hrat.Draw("lego2z,hist")
		c.cd(2)
		self.hrat.Draw("colz,text")
		c.cd(3)
		self.fsob.SetNpx(20)
		self.fsob.SetNpy(20)
		self.fsob.Draw("lego2z,hist")
		c.cd(4)
		fsob2 = self.fsob.Clone()
		fsob2.SetNpx(10)
		fsob2.SetNpy(10)
		fsob2.Draw("colz,text")
		c.Update()
		c.WaitPrimitive()
		c.SaveAs("%s/sf2D3D.pdf"%(folder))

		c.Close()

		c0 = TCanvas("c0","c0",1500,1000)
		c0.cd()
		gPad.SetRightMargin(gPad.GetRightMargin()*1.2)
		ShiftTitles(self.hsig,2,2)
		self.hsig.Draw("lego,hist")
		self.fsig.Draw("lego,same")
		c0.Update()
		c0.SaveAs("%s/hsigfsig.pdf"%(folder))
		ShiftTitles(self.hbkg,2,2)
		self.hbkg.Draw("lego,hist")
		self.fbkg.Draw("lego,same")
		c0.Update()
		c0.SaveAs("%s/hbkgfbkg.pdf"%(folder))
		ShiftTitles(self.dsig,1.3,1.3)
		self.dsig.Draw("colz")
		MovePalette(c0,self.dsig)
		c0.Update()
		c0.SaveAs("%s/hsigfsigdiff.pdf"%(folder))
		ShiftTitles(self.dbkg,1.3,1.3)
		self.dbkg.Draw("colz")
		MovePalette(c0,self.dbkg)
		c0.Update()
		c0.SaveAs("%s/hbkgfbkgdiff.pdf"%(folder))
		ShiftTitles(self.dsig_abs,1.3,1.3)
		self.dsig_abs.Draw("colz")
		MovePalette(c0,self.dsig_abs)
		c0.Update()
		c0.SaveAs("%s/hsigfsigdiffabs.pdf"%(folder))
		ShiftTitles(self.dbkg_abs,1.3,1.3)
		self.dbkg_abs.Draw("colz")
		MovePalette(c0,self.dbkg_abs)
		c0.Update()
		c0.SaveAs("%s/hbkgfbkgdiffabs.pdf"%(folder))
		ShiftTitles(self.hsig,0.75,0.75)
		self.hsig.SetMarkerSize(self.hsig.GetMarkerSize()*0.5)
		self.hsig.Draw("colz,text90,error")
		MovePalette(c0,self.hsig)
		c0.Update()
		c0.SaveAs("%s/hsig.pdf"%(folder))
		ShiftTitles(self.hbkg,0.75,0.75)
		self.hbkg.SetMarkerSize(self.hbkg.GetMarkerSize()*0.5)
		self.hbkg.Draw("colz,text90,error")
		MovePalette(c0,self.hbkg)
		c0.Update()
		c0.SaveAs("%s/hbkg.pdf"%(folder))
		
		ShiftTitles(self.hrat,2.0,2.0)
		self.hrat.Draw("lego2z,hist")
		c0.Update()
		c0.SaveAs("%s/h3D.pdf"%(folder))
		ShiftTitles(self.hrat,0.75,0.75)
		self.hrat.Draw("colz,text")
		c0.Update()
		c0.SaveAs("%s/h2D.pdf"%(folder))
		self.fsob.SetNpx(20)
		self.fsob.SetNpy(20)
		hfsob = self.fsob.GetHistogram()
		hfsob.SetTitle("fit(data)/fit(qcd);%s;%s;"%(self.hrat.GetXaxis().GetTitle(),self.hrat.GetYaxis().GetTitle()))
		ShiftTitles(hfsob,2.0,2.0)
		hfsob.Draw("lego2z,hist")
		MovePalette(c0,hfsob)
		c0.Update()
		c0.SaveAs("%s/r3D.pdf"%(folder))
		self.fsob.SetNpx(10)
		self.fsob.SetNpy(10)
		hfsob = self.fsob.GetHistogram()
		hfsob.SetTitle("fit(data)/fit(qcd);%s;%s;"%(self.hrat.GetXaxis().GetTitle(),self.hrat.GetYaxis().GetTitle()))
		ShiftTitles(hfsob,1.2,1.2)
		hfsob.Draw("colz,text")
		MovePalette(c0,hfsob)
		c0.Update()
		c0.SaveAs("%s/r2D.pdf"%(folder))
		
		c0.Close()
		
	def save(self,opts,fopen):
		fopen.cd("/")
		makeDirsRoot(fopen,"2DFits")
		gDirectory.cd("2DFits")
		self.fsig2 = TF2("fsig2","[0] / (1 + TMath::Exp(-(x - [3])/[1])) / (1 + TMath::Exp(-(y - [4])/[2]))")
		pars = self.fsig.GetParameters()
		self.fsig2.SetParameters(pars)
		self.fbkg2 = TF2("fbkg2","[0] / (1 + TMath::Exp(-(x - [3])/[1])) / (1 + TMath::Exp(-(y - [4])/[2]))")
		pars = self.fbkg.GetParameters()
		self.fbkg2.SetParameters(pars)
		self.fsob2 = TF2("fsob2","([0] / (1 + TMath::Exp(-(x - [3])/[1])) / (1 + TMath::Exp(-(y - [4])/[2]))) / ([5] / (1 + TMath::Exp(-(x - [8])/[6])) / (1 + TMath::Exp(-(y - [9])/[7])))")
		pars = self.fsob.GetParameters()
		self.fsob2.SetParameters(pars)
		print
		print self.fsig.Eval(1500,500)
		print self.fsig.Eval(2500,1500)
		print
		print self.fsig2.Eval(1500,500)
		print self.fsig2.Eval(2500,1500)
		print
		self.fsig2.SetName(self.hsigs[0].GetName().replace("2DMap","2DFun")+("_%s"%opts.mergetag if opts.mergetag else ""))
		self.fbkg2.SetName(self.hbkgs[0].GetName().replace("2DMap","2DFun")+("_%s"%opts.mergetag if opts.mergetag else ""))
		self.fsob2.SetName(self.hrats[0].GetName().replace("2DMap","2DFun")+("_%s"%opts.mergetag if opts.mergetag else ""))
		self.fsig2.Write(self.fsig2.GetName(),TH1.kOverwrite)
		self.fbkg2.Write(self.fbkg2.GetName(),TH1.kOverwrite)
		self.fsob2.Write(self.fsob2.GetName(),TH1.kOverwrite)
		self.fsig2.GetHistogram().Write("H"+self.fsig2.GetName(),TH1.kOverwrite)
		self.fbkg2.GetHistogram().Write("H"+self.fbkg2.GetName(),TH1.kOverwrite)
		self.fsob2.GetHistogram().Write("H"+self.fsob2.GetName(),TH1.kOverwrite)

		gDirectory.cd("/")
		
##################################################
	def efficiency(self,opts,fname):
		###f = TF2(fname,"([0]/(1.+TMath::Exp(-(x-[3])/[1]))/(1.+TMath::Exp(-(y-[4])/[2])))+()",self.xmin,self.xmax,self.ymin,self.ymax)
		if opts.addlinear: f = TF2(fname,fefficiency_pluslinear,self.xmin,self.xmax,self.ymin,self.ymax,7)
		elif opts.lin: f = TF2(fname,fefficiency_lin,self.xmin,self.xmax,self.ymin,self.ymax,5)
		else: f = TF2(fname,fefficiency,self.xmin,self.xmax,self.ymin,self.ymax,5)
		return f

	def efficiency_ratio(self,opts,fname,f1,f2):
		###self.fsob = TF2(fname,"([0]/(1.+TMath::Exp(-(x-[3])/[1]))/(1.+TMath::Exp(-(y-[4])/[2]))) / ([5]/(1.+TMath::Exp(-(x-[8])/[6]))/(1.+TMath::Exp(-(y-[9])/[7])))",self.xmin,self.xmax,self.ymin,self.ymax)
		if opts.addlinear: 
			npar = 7 
			self.fsob = TF2(fname,fefficiency_ratio_pluslinear,self.xmin,self.xmax,self.ymin,self.ymax,npar*2)
		elif opts.lin: 
			npar = 5 
			self.fsob = TF2(fname,fefficiency_lin_ratio,self.xmin,self.xmax,self.ymin,self.ymax,npar*2)
		else: 
			npar = 5
			self.fsob = TF2(fname,fefficiency_ratio,self.xmin,self.xmax,self.ymin,self.ymax,npar*2)
		for i in range(npar):
			self.fsob.SetParameter(i,      f1.GetParameter(i))
			self.fsob.SetParameter(i+npar, f2.GetParameter(i))
		return self.fsob

##################################################
	def fit_setLims(self,f,i,lo,up): f.SetParLimits(i,lo,up)

	def fit_setPars(self,f,pars,fmin=0.0,fmax=1.0):
		for i,ipar in enumerate(pars): f.SetParameter(i,ipar)
		f.SetMinimum(fmin)
		f.SetMaximum(fmax)

##################################################
	def hist_combine(self,h1,h2,cutoffx=None,cutoffy=None):
		x1 = [h1.GetXaxis().GetBinUpEdge(xi) for xi in range(h1.GetNbinsX()+1)]
		y1 = [h1.GetYaxis().GetBinUpEdge(yi) for yi in range(h1.GetNbinsY()+1)]
		x2 = [h2.GetXaxis().GetBinUpEdge(xi) for xi in range(h2.GetNbinsX()+1)]
		y2 = [h2.GetYaxis().GetBinUpEdge(yi) for yi in range(h2.GetNbinsY()+1)]
		x = array('f',sorted(list(set(x1+x2))))
		y = array('f',sorted(list(set(y1+y2))))
		h = TH2F(h1.GetName(),"%s;%s;%s"%(h1.GetName(),h1.GetXaxis().GetTitle(),h1.GetYaxis().GetTitle()),int(len(x)-1),x,int(len(y)-1),y)
		h.Sumw2()
		for ix in range(h1.GetNbinsX()+1):
			for iy in range(h1.GetNbinsY()+1):
				cx = h1.GetXaxis().GetBinCenter(ix)
				cy = h1.GetYaxis().GetBinCenter(iy)
				if not cutoffx==None:
				    if cx > cutoffx: break
				if not cutoffy==None:
				    if cy > cutoffy: break
				h.SetBinContent(h.GetXaxis().FindBin(cx),h.GetYaxis().FindBin(cy),h1.GetBinContent(ix,iy))
				h.SetBinError(h.GetXaxis().FindBin(cx),h.GetYaxis().FindBin(cy),h1.GetBinError(ix,iy))
		for ix in range(h2.GetNbinsX()+1):
			for iy in range(h2.GetNbinsY()+1):
				cx = h2.GetXaxis().GetBinCenter(ix)
				cy = h2.GetYaxis().GetBinCenter(iy)
				if not cutoffx==None:
					if cx < cutoffx: continue
				if not cutoffy==None:
					if cy < cutoffy: continue
				h.SetBinContent(h.GetXaxis().FindBin(cx),h.GetYaxis().FindBin(cy),h2.GetBinContent(ix,iy))
				h.SetBinError(h.GetXaxis().FindBin(cx),h.GetYaxis().FindBin(cy),h1.GetBinError(ix,iy))
		return h

###################################################################################################
def efficiencyFit():
	gROOT.SetBatch(0)
	gStyle.SetOptStat(0)
	
	mp = parser(main.parser())	
	opts,args = mp.parse_args()

	fopen = TFile.Open(opts.fout,"update") 
	
	nsigs = []
	nbkgs = []
	nrats = []
	print "%sHistgrams added in order: %s%s"%(Blue,','.join(['-'.join(ref) for ref in opts.reftrig]),plain)
	for ir,r in enumerate(sorted(['-'.join(ref) for ref in opts.reftrig])):
		nsigs += ["2DMaps/JetMon/2DMap_JetMon-Rat_s%s-t%s-r%s-d%s%s"%('-'.join(sorted(opts.selection[ir])),'-'.join(opts.trigger[0]),r,'-'.join(opts.datatrigger[0]),"_"+opts.correctiontag if not opts.correctiontag=="" else "")]
		nbkgs += ["2DMaps/QCD/2DMap_QCD-Rat_s%s-t%s-r%s-d%s%s"%('-'.join(sorted(opts.selection[ir])),'-'.join(opts.trigger[0]),r,'-'.join(opts.datatrigger[0]),"_"+opts.correctiontag if not opts.correctiontag=="" else "")]
		nrats += ["2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_s%s-t%s-r%s-d%s%s"%('-'.join(sorted(opts.selection[ir])),'-'.join(opts.trigger[0]),r,'-'.join(opts.datatrigger[0]),"_"+opts.correctiontag if not opts.correctiontag=="" else "")]

	for n in nsigs: print n
	hsigs = []
	hbkgs = []
	hrats = []
	for n in nsigs: hsigs += [fopen.Get(n)]
	for n in nbkgs: hbkgs += [fopen.Get(n)]
	for n in nrats: hrats += [fopen.Get(n)]

	if not opts.cutoff=='':
		e = efficiency_fit(opts,hsigs,hbkgs,hrats,[300,2000,0,1200],float(opts.cutoff[1]) if opts.cutoff[0]=='x' else None,float(opts.cutoff[1]) if opts.cutoff[0]=='y' else None)
		e.fit(opts,[0.7,50,50,700,400,2e-5,1e-5],[0.7,50,50,700,400,1e-5,1e-5])
		e.draw(opts)
		e.save(opts,fopen)
	else:
		e = {}
		for ir,r in enumerate(sorted(['-'.join(ref) for ref in opts.reftrig])):
			if not ir==1: continue
			print "%sEfficiencies for ref %s%s"%(Blue,r,plain)
			e[r] = efficiency_fit(opts,hsigs[ir:ir+1],hbkgs[ir:ir+1],hrats[ir:ir+1],[300,2000,2.5,7],None,None)
			e[r].drawplain(opts,r)
			e[r].fit(opts,[0.8,700,50,0.1,1500],[0.8,700,50,0.1,1500])
			e[r].draw(opts,r)
			e[r].save(opts,fopen)

	fopen.Close()

if __name__=='__main__':
	efficiencyFit()
