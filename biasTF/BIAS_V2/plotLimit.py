#!/usr/bin/env python
import ROOT
from ROOT import *
from optparse import OptionParser
from copy import deepcopy as dc
import os,sys
import numpy
from array import *

red = '\033[0;31m'
plain = '\033[m'

def treeAccess(tree):
	tree.SetBranchStatus('*',0)

	_lm = numpy.array(1,'d')
	_mh = numpy.array(1,'d')

	tree.SetBranchStatus('limit',1)
	tree.SetBranchStatus('mh'   ,1)
	tree.SetBranchAddress('limit',_lm)
	tree.SetBranchAddress('mh',   _mh)

	return _lm, _mh

def localParser():
	lp = OptionParser()
	#lp.add_option('-f','--filename',help='Name of limit root file to plot from.',default='',dest='limname',type='str')
	lp.add_option('-b','--blind',help='Without observed.',default=False,action='store_true')
	return lp

#def main(limname):
#	if limname == '':
#		sys.exit('No useable root file given. Exiting.')
#	if not os.path.exists(limname):
#		sys.exit('Specified root file doesn\'t exist. Exiting.')
def main(opts,limnames):
	gROOT.ProcessLine(".x /afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/kostas/../common/styleCMSTDR.C")
	gROOT.ProcessLine('gROOT->ForceStyle();')
	gStyle.SetPadLeftMargin(0.12)
	gStyle.SetPadRightMargin(0.04)
	gStyle.SetStripDecimals(0)
	gStyle.SetTitleOffset(0.8,"Y")
	gROOT.SetBatch(1)

	limfiles = []
	limits = []
	for limname in limnames:
		if limname == '':
			sys.exit('No useable root file given. Exiting.')
		if not os.path.exists(limname):
			sys.exit('Specified root file doesn\'t exist. Exiting.')
#		print red+limname+plain
		limfiles.append(TFile.Open(limname))
		limfile = limfiles[-1]
#		limfile.ls()
#		print
		limits.append(limfile.Get('limit'))
		limit = limits[-1]
#		limit.Print()
#		print
#		limit.Scan('*')
#		print
	
	aMass = []
	aObsLimit = []
	aMeanExpLimit = []
	aMedExpLimit = []
	aExpLimit68D = []
	aExpLimit68U = []
	aExpLimit95D = []
	aExpLimit95U = []
	if not opts.blind:
		arrays = [aExpLimit95D, aExpLimit68D, aMedExpLimit, aExpLimit68U, aExpLimit95U, aObsLimit, aMass]
		names = ['ExpLimit95D','ExpLimit68D','ExpLimitMed','ExpLimit68U','ExpLimit95U','ObsLimit','Mass']
	else:
		arrays = [aExpLimit95D, aExpLimit68D, aMedExpLimit, aExpLimit68U, aExpLimit95U, aMass]
		names = ['ExpLimit95D','ExpLimit68D','ExpLimitMed','ExpLimit68U','ExpLimit95U','Mass']
	
	for ilimit, limit in enumerate(limits):
		nentries = limit.GetEntries()
		lm, mh = treeAccess(limit)
		for ientry in range(nentries):
			limit.GetEntry(ientry)
			if ientry > len(arrays):
				sys.exit('Too many entries in limit tree. Exiting.')
			arrays[ientry].append(dc(lm))
		arrays[ientry+1].append(dc(mh))
#	for ia,a in enumerate(arrays):
#		print names[ia], a

#	for a in arrays:
#		for e in a:
#			print e,
#		print

	c = TCanvas('c','c',900,750)
	c.cd()
	nMass = len(arrays[0])
	limitplotband95 = TGraphAsymmErrors(nMass, array('d',arrays[6 if not opts.blind else 5]), array('d',arrays[2]), array('d',[0.]*nMass), array('d',[0.]*nMass), array('d',[arrays[2][i]-arrays[0][i] for i in range(nMass)]), array('d',[arrays[4][i]-arrays[2][i] for i in range(nMass)])) 
	limitplotband68 = TGraphAsymmErrors(nMass, array('d',arrays[6 if not opts.blind else 5]), array('d',arrays[2]), array('d',[0.]*nMass), array('d',[0.]*nMass), array('d',[arrays[2][i]-arrays[1][i] for i in range(nMass)]), array('d',[arrays[3][i]-arrays[2][i] for i in range(nMass)])) 
	limitplotexp = TGraph(nMass,array('d',arrays[6 if not opts.blind else 5]),array('d',arrays[2]))
	if not opts.blind: limitplotobs = TGraph(nMass,array('d',arrays[6]),array('d',arrays[5]))

	print limitplotband95.Print()
	print limitplotband68.Print()
	print limitplotexp.Print()
	if not opts.blind: limitplotobs.Print()
	
	maxplot = int(max(arrays[4])*1.2)

	limitplotexp.GetYaxis().SetRangeUser(0.0,maxplot)
	limitplotband95.SetFillColor(90)
	#limitplotband95.GetXaxis().SetRangeUser(arrays[-1][0],arrays[-1][-1])
	#limitplotband95.GetYaxis().SetRangeUser(0.0,12.0)
	limitplotband68.SetFillColor(211)

	gPad.SetTicks(1)
	#limitplotexp.GetXaxis().SetTicks("+")
	#limitplotexp.GetYaxis().SetTicks("-")
	limitplotexp.GetXaxis().SetTickLength(0.02)
	limitplotexp.GetYaxis().SetTickLength(0.03)
	limitplotexp.SetLineStyle(7)#9)
	limitplotexp.SetLineWidth(2)
	limitplotexp.SetLineColor(kBlue)#kBlack
	limitplotexp.GetXaxis().SetTitle("Higgs Mass (GeV)")
	limitplotexp.GetYaxis().SetTitle("95% Asymptotic CL Limit on #sigma/#sigma_{SM}")
	limitplotexp.GetXaxis().SetLimits(114.5,135.5)

	limitplotobs.SetLineStyle(1)
	limitplotobs.SetLineWidth(2)
	limitplotobs.SetMarkerStyle(20)
	limitplotobs.SetMarkerColor(1)

	line = TF1("line","1.0",113,137)
	line.SetLineColor(kRed)#kBlack)
	line.SetLineStyle(3)

	pave = TPaveText(0.15,0.7,0.35,0.92,"NDC")
	pave.SetTextFont(62)
	pave.SetTextSize(0.045)
	pave.SetBorderSize(0)
	pave.SetFillStyle(-1)
	pave.SetTextAlign(11)
	pave.AddText("CMS")
	pave.AddText("#sqrt{s} = 8 TeV")
	pave.AddText("L = 19 fb^{-1}")
	pave.AddText("VBF H#rightarrow b#bar{b}")
	pave.SetY1NDC(pave.GetY1NDC()-(len(pave.GetListOfLines())-1)*0.045)

	leg = TLegend(0.38,0.92-0.04*4,0.68,0.92)
	leg.SetTextFont(42)
	leg.SetTextSize(0.035)
	leg.SetBorderSize(0)
	leg.SetFillStyle(-1)

	leg.AddEntry(limitplotobs,"CL_{S} Observed","LP")
	leg.AddEntry(limitplotexp,"CL_{S} Expected","L")
	leg.AddEntry(limitplotband68,"CL_{S} Expected #pm 1#sigma","F")
	leg.AddEntry(limitplotband95,"CL_{S} Expected #pm 2#sigma","F")
	leg.SetY1(leg.GetY2()-(leg.GetNRows())*0.05)

	limitplotexp.Draw("axisl")
	limitplotband95.Draw("same3")
	limitplotband68.Draw("same3")
	limitplotexp.Draw("samel")
	limitplotobs.Draw("samelp")
	line.Draw("same")
	leg.Draw("same")
	pave.Draw("same")

	c.SaveAs('limit.png')
	c.SaveAs('limit.pdf')
	c.Close()

#		ExpBand95->SetFillColor(90);
#        ExpBand95->GetYaxis()->SetRangeUser(0.,50);
#        ExpBand95->GetXaxis()->SetRangeUser(x1,x2);
#        ExpBand95->GetXaxis()->SetTitle("Higgs mass [GeV/c^{2}]");
#        ExpBand95->GetYaxis()->SetTitle("95% Limit on #sigma/#sigma_{SM} ");
#        ExpBand95->Draw("A3");
#        ExpBand95->GetYaxis()->SetRangeUser(0.,50);
#        ExpBand95->Draw("A3");
#	    ExpBand68 = new TGraphAsymmErrors((signed) vMass.size(),x,y,ex,ex,yd68,yu68);
#        ExpBand68->SetFillColor(211);
#        ExpBand68->Draw("3");
#        ExpLim = new TGraph((signed) vMass.size(),x,y);
#        ExpLim->SetLineWidth(2);
#        ExpLim->SetLineStyle(2);
#        ExpLim->Draw("l");
	
	for limfile in limfiles:
		limfile.Close()

if __name__=='__main__':
	lp = localParser()
	opts,args = lp.parse_args()

#	main(options.limname)
	main(opts,args)
