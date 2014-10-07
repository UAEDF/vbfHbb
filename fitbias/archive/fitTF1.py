#!/usr/bin/env python

import sys,os,re

from ROOT import *
import ROOT

def fitTF1(canvas,h,xmin,xmax,dx,params,color):
	canvas.cd()
	RooMsgService.instance().setSilentMode(kTRUE)
	for i in range(2): RooMsgService.instance().setStreamStatus(i,kFALSE)
	
	w = RooWorkspace("w","workspace")

	x = RooRealVar("mbb","mbb",xmin,xmax)
	kJES = RooRealVar("CMS_scale_j","CMS_scale_j",1,0.9,1.1)
	kJER = RooRealVar("CMS_res_j","CMS_res_j",1,0.8,1.2)
	kJES.setConstant(kTRUE)
	kJER.setConstant(kTRUE)

	hname = h.GetName()

	RooHistFit = RooDataHist("fit_"+hname,"fit_"+hname,RooArgList(x),h)
	YieldVBF = RooRealVar("yield_"+hname,"yield_"+hname,h.Integral());

	m = RooRealVar("mean_"+hname,"mean_"+hname,125,100,150)
	s = RooRealVar("sigma_"+hname,"sigma_"+hname,12,3,30)
	
	mShift = RooFormulaVar("mShift_"+hname,"@0*@1",RooArgList(m,kJES))
	sShift = RooFormulaVar("sShift_"+hname,"@0*@1",RooArgList(s,kJER))

	a = RooRealVar("alpha_"+hname,"alpha_"+hname,1,-10,10)
	n = RooRealVar("exp_"+hname,"exp_"+hname,1,0,100)
	b0 = RooRealVar("b0_"+hname,"b0_"+hname,0.5,0.,1.)
	b1 = RooRealVar("b1_"+hname,"b1_"+hname,0.5,0.,1.)
	b2 = RooRealVar("b2_"+hname,"b2_"+hname,0.5,0.,1.)
	b3 = RooRealVar("b3_"+hname,"b3_"+hname,0.5,0.,1.)
	b4 = RooRealVar("b4_"+hname,"b3_"+hname,0.5,0.,1.)

	bSet = RooArgList(b0,b1,b2,b3)

	bkg  = RooBernstein("signal_bkg_"+hname,"signal_bkg_"+hname,x,bSet)
	fsig = RooRealVar("fsig_"+hname,"fsig_"+hname,0.7,0.0,1.0)
	sig  = RooCBShape("signal_gauss_"+hname,"signal_gauss_"+hname,x,mShift,sShift,a,n)
	
	model = RooAddPdf("signal_model_"+hname,"signal_model_"+hname,RooArgList(sig,bkg),RooArgList(fsig))
	
	model.fitTo(RooHistFit,RooFit.Save(),RooFit.SumW2Error(kFALSE))#.Print()
	
	frame = x.frame()
	frame.GetXaxis().SetLimits(50,200);
	RooHistFit.plotOn(frame)
	model.plotOn(frame,RooFit.LineColor(color),RooFit.LineWidth(2))
	bkgSet = RooArgSet(bkg)
	model.plotOn(frame,RooFit.Components(bkgSet),RooFit.LineColor(color),RooFit.LineWidth(2),RooFit.LineStyle(kDashed))
	frame.Draw()
	h.Draw("hist,same")
	frame.Draw("same")
	gPad.RedrawAxis()

	canvas.Update()

	tf1 = model.asTF(RooArgList(x),RooArgList(fsig),RooArgSet(x))

	y0_ = tf1.GetMaximum();
	x0_ = tf1.GetMaximumX();
	x1_ = tf1.GetX(y0_/2.,xmin,x0_);
	x2_ = tf1.GetX(y0_/2.,x0_,xmax);
	FWHM_ = x2_-x1_;
	INT_ = tf1.Integral(xmin,xmax);
	YIELD_= YieldVBF.getVal();
	y1_ = dx*0.5*y0_*(YieldVBF.getVal()/tf1.Integral(xmin,xmax));

	params[0] = x0_;
	params[1] = x1_;
	params[2] = x2_;
	params[3] = y0_;
	params[4] = y1_;
	params[5] = FWHM_;
	params[6] = INT_;
	params[7] = YIELD_;
	params[8] = s.getVal(); 

	ln = TLine(x1_,y1_,x2_,y1_);
	#ln.SetLineColor(kMagenta+3);
	ln.SetLineColor(color);
	ln.SetLineStyle(7);
	ln.SetLineWidth(2);
	ln.Draw();
	
	canvas.Update();
	#canvas.SaveAs("testPy.png");
	
#def run():
#	f = 'plainHisto.root'
#	tf = TFile(f,"read")
#	h = tf.Get("mbbReg")
#	c = TCanvas("c1","c1")
#	params = [0]*8
#	fitTF1(c,h,50,200,2.5,params,kBlack)
#	tf.Close()
#
#if __name__=='__main__':
#	run()
#
