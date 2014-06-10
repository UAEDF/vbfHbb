#!/usr/bin/env python

import sys,os,re

from ROOT import *
import ROOT

def do(string):
	gROOT.ProcessLine(string)

def fitTF1(h,hscale,xmin,xmax):
	RooMsgService.instance().setSilentMode(kTRUE)
	for i in range(2): RooMsgService.instance().setStreamStatus(i,kFALSE)
	
	w = RooWorkspace("w","workspace")

	do('RooRealVar x("mbbReg","mbbReg",%.16f,%.16f)'%(xmin,xmax))
	do('RooRealVar kJES("CMS_scale_j","CMS_scale_j",1,0.9,1.1)')
	do('RooRealVar kJER("CMS_res_j","CMS_res_j",1,0.8,1.2)')
	ROOT.kJES.setConstant(kTRUE)
	ROOT.kJER.setConstant(kTRUE)

	hname = h.GetName()
	do('TString hname("%s")'%hname)
	h.Scale(1./hscale)

	RooHistFit = RooDataHist("fit_"+hname,"fit_"+hname,RooArgList(ROOT.x),h)

	do('RooRealVar m("mean_%s","mean_%s",125,100,150)'%(hname,hname))
	do('RooRealVar s("sigma_%s","sigma_%s",12,3,30)'%(hname,hname))
	do('RooFormulaVar mShift("mShift_%s","@0*@1",RooArgList(m,kJES))'%(hname))
	do('RooFormulaVar sShift("sShift_%s","@0*@1",RooArgList(m,kJER))'%(hname))
	do('RooRealVar a("alpha_%s","alpha_%s",1,-10,10)'%(hname,hname))
	do('RooRealVar n("exp_%s","exp_%s",1,0,100)'%(hname,hname))
	do('RooRealVar b0("b0_"+hname,"b0_"+hname,0.5,0.,1.)')
	do('RooRealVar b1("b1_"+hname,"b1_"+hname,0.5,0.,1.)')
	do('RooRealVar b2("b2_"+hname,"b2_"+hname,0.5,0.,1.)')
	do('RooRealVar b3("b3_"+hname,"b3_"+hname,0.5,0.,1.)')
	do('RooBernstein bkg("signal_bkg_%s","signal_bkg_%s",x,RooArgSet(b0,b1,b2))'%(hname,hname))
	do('RooRealVar fsig("fsig_%s","fsig_%s",0.7,0.0,1.0)'%(hname,hname))
	do('RooCBShape sig("signal_gauss_%s","signal_gauss_%s",x,mShift,sShift,a,n)'%(hname,hname))
	#bkg    = RooBernstein("signal_bkg_"+hname,"signal_bkg_"+hname,ROOT.x,RooArgSet(b0,b1,b2))
	#fsig   = RooRealVar("fsig_"+hname,"fsig_"+hname,0.7,0.0,1.0)
	#sig    = RooCBShape("signal_gauss_"+hname,"signal_gauss_"+hname,x,mShift,sShift,a,n)
	
	model = RooAddPdf("signal_model_"+hname,"signal_model_"+hname,RooArgList(ROOT.sig,ROOT.bkg),RooArgList(ROOT.fsig))
	
	res = model.fitTo(RooHistFit,RooFit.Save(),RooFit.SumW2Error(kFALSE))
	
	frame = ROOT.x.frame()
	RooHistFit.plotOn(frame)
	model.plotOn(frame)
	#model.plotOn(frame,RooFit.Components(ROOT.bkg),RooFit.LineColor(kBlue),RooFit.LineWidth(2),RooFit.LineStyle(kDashed))
	frame.Draw()
	h.Draw("hist,same")
	frame.Draw("same")
	gPad.RedrawAxis()

	tf1 = model.asTF(RooArgList(ROOT.x),RooArgList(ROOT.fsig),RooArgSet(ROOT.x))
	
	return tf1


