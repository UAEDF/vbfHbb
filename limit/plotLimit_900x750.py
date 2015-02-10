#!/usr/bin/env python
import ROOT
from ROOT import *
from optparse import OptionParser
from copy import deepcopy as dc
import os,sys,re
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
	lp.add_option('-t','--tag',help='Name tag.',default="")
	return lp

def main(opts,limnames):
	cwd = os.getcwd()
	path = os.path.split(limnames[0])[0]
	os.chdir(path)
	print os.getcwd()

	gROOT.ProcessLine(".x /afs/cern.ch/work/s/salderwe/private/2014/vbfHbb/kostas/../common/styleCMSTDR.C")
	gROOT.ProcessLine('gROOT->ForceStyle();')
	gStyle.SetPadLeftMargin(0.12)
	gStyle.SetPadRightMargin(0.04)
	gStyle.SetPadTopMargin(0.06)
	gStyle.SetStripDecimals(0)
	gStyle.SetTitleOffset(0.8,"Y")
	gROOT.SetBatch(1)

	limfiles = []
	limits = []
	print "Limit files:"
	for limname in [os.path.split(x)[1] for x in limnames]:
		if limname == '': sys.exit('No useable root file given. Exiting.')
		if not os.path.exists(limname): sys.exit('Specified root file doesn\'t exist. Exiting.')
#		print red+limname+plain
		limfiles.append(TFile.Open(limname))
		limfile = limfiles[-1]
		print "\t - %s"%limname
#		limfile.ls()
#		print
		limits.append(limfile.Get('limit'))
		limit = limits[-1]
#		limit.Print()
#		print
#		limit.Scan('*')
#		print
	
	lists = {'aMass':[],'ExpLimit95D':[],'ExpLimit68D':[],'ExpLimitMed':[],'ExpLimit68U':[],'ExpLimit95U':[],'ObsLimit':[],'InjLimit':[],'aMassErr':[],'Exp68U':[],'Exp68D':[],'Exp95U':[],'Exp95D':[]}
	positions = {0:'ExpLimit95D',1:'ExpLimit68D',2:'ExpLimitMed',3:'ExpLimit68U',4:'ExpLimit95U'}
	
	for ilimit, limit in enumerate(limits):
		nentries = limit.GetEntries()
		lm, mh = treeAccess(limit)
		for ientry in range(nentries):
			limit.GetEntry(ientry)
			if ientry<5 and not 'Inj' in limnames[ilimit]: lists[positions[ientry]].append(dc(lm))
			elif ientry >= 5 and 'Inj' in limnames[ilimit]: lists['InjLimit'].append(dc(lm))
			elif ientry >= 5: lists['ObsLimit'].append(dc(lm))
			elif ientry<5: continue
			else: print "unknown case!", ientry, lm, mh
		lists['Exp68U'].append(lists['ExpLimit68U'][-1] - lists['ExpLimitMed'][-1])
		lists['Exp68D'].append(lists['ExpLimitMed'][-1] - lists['ExpLimit68D'][-1])
		lists['Exp95U'].append(lists['ExpLimit95U'][-1] - lists['ExpLimitMed'][-1])
		lists['Exp95D'].append(lists['ExpLimitMed'][-1] - lists['ExpLimit95D'][-1])
		if not 'Inj' in limnames[ilimit]: 
			lists['aMass'].append(dc(mh))
			lists['aMassErr'].append(0.)
		if not any(['Inj' in x for x in limnames]):
			lists['InjLimit'].append(0.)

	print
	arrays = dict([(k,array('d',v)) for (k,v) in lists.iteritems()])

	c = TCanvas('c','c',900,750)
	c.cd()
	nMass = len(arrays['aMass'])
	limitplotband95 = TGraphAsymmErrors(nMass, arrays['aMass'], arrays['ExpLimitMed'],arrays['aMassErr'],arrays['aMassErr'],arrays['Exp95D'],arrays['Exp95U']) 
	limitplotband68 = TGraphAsymmErrors(nMass, arrays['aMass'], arrays['ExpLimitMed'],arrays['aMassErr'],arrays['aMassErr'],arrays['Exp68D'],arrays['Exp68U']) 
	limitplotexp    = TGraph           (nMass, arrays['aMass'], arrays['ExpLimitMed']) 
	limitplotobs    = TGraph           (nMass, arrays['aMass'], arrays['ObsLimit'])
	limitplotinj    = TGraph           (nMass, arrays['aMass'], arrays['InjLimit'])

	print limitplotband95.Print()
	print limitplotband68.Print()
	print limitplotexp.Print()
	print limitplotobs.Print()
	print limitplotinj.Print()
	
	maxplot = int(max(arrays['ExpLimit95U'])*1.2)
	if maxplot<10: maxplot=10

	limitplotexp.GetYaxis().SetRangeUser(0.0,maxplot)
	limitplotband95.SetFillColor(kYellow)#90)
	limitplotband95.SetLineColor(kYellow)#90)
	#limitplotband95.GetXaxis().SetRangeUser(arrays[-1][0],arrays[-1][-1])
	#limitplotband95.GetYaxis().SetRangeUser(0.0,12.0)
	limitplotband68.SetFillColor(kGreen)#211)
	limitplotband68.SetLineColor(kGreen)#211)

	gPad.SetTicks(1)
	#limitplotexp.GetXaxis().SetTicks("+")
	#limitplotexp.GetYaxis().SetTicks("-")
	limitplotexp.GetXaxis().SetTickLength(0.03)
	limitplotexp.GetYaxis().SetTickLength(0.03)
	limitplotexp.GetYaxis().SetNdivisions(310)
	limitplotexp.SetLineStyle(1)#7)#9)
	limitplotexp.SetLineWidth(2)
	limitplotexp.SetLineColor(kBlack)#kBlue
	limitplotexp.GetXaxis().SetTitle("Higgs Mass (GeV)")
	limitplotexp.GetYaxis().SetTitle("95% Asymptotic CL Limit on #sigma/#sigma_{SM}")
#	limitplotexp.GetXaxis().SetLimits(114,136)
	limitplotexp.GetXaxis().SetLimits(99,151)

	gStyle.SetLineStyleString(11,"24 24")
	limitplotinj.SetLineStyle(11)
	limitplotinj.SetLineWidth(2)
	limitplotinj.SetLineColor(kBlue)

	limitplotobs.SetLineStyle(1)
	limitplotobs.SetLineWidth(2)
	limitplotobs.SetLineColor(kBlack)
	limitplotobs.SetMarkerStyle(20)
	limitplotobs.SetMarkerColor(kBlack)
	limitplotobs.SetMarkerSize(1.7)

	#line = TF1("line","1.0",114,136)
	line = TF1("line","1.0",99,151)
	line.SetLineColor(kGray+2)#+kRed)#kBlack)
	line.SetLineStyle(3)#2
	line.SetLineWidth(1)

	pave = TPaveText(0.16,0.7,0.25,0.91,"NDC")
	pave.SetTextFont(62)
	pave.SetTextSize(gStyle.GetPadTopMargin()*3./4.)
	pave.SetBorderSize(0)
	pave.SetFillStyle(-1)
#	pave.SetFillColor(kRed)
	pave.SetTextAlign(12)
	pave.AddText("CMS")
	#l = pave.AddText("Preliminary")
	#l.SetTextFont(52)
#	pave.AddText("#sqrt{s} = 8 TeV")
#	pave.AddText("L = 19 fb^{-1}")
#	pave.AddText("VBF H#rightarrow b#bar{b}")
	pave.Draw()
	gPad.Update()
	pave.SetY1NDC(pave.GetY2NDC()-len(pave.GetListOfLines())*gStyle.GetPadTopMargin())

	pave2 = TPaveText(0.5,0.94,0.98,1.00,"NDC")
	pave2.SetTextFont(42)
	pave2.SetTextSize(0.04)
	pave2.SetBorderSize(0)
	pave2.SetFillStyle(-1)
	#pave2.SetFillColor(kRed)
	pave2.SetTextAlign(32)
	pave2.AddText("19.8 fb^{-1} (8TeV)")#+ 18.2 

	tag=""
	if 'CATveto' in limnames[ilimit]:
		if '0123' in limnames[ilimit]:
			tag="PRK"
		elif '456' in limnames[ilimit]:
			tag="NOM"
		else: 
			tag = re.search('.*CATveto([0-9]*)\..*',limnames[ilimit]).group(1)

	pave3 = TPaveText(0.72,0.7,0.92,0.90,"NDC")
	pave3.SetTextFont(62)
	pave3.SetTextSize(0.045)
	pave3.SetBorderSize(0)
	pave3.SetFillStyle(-1)
	pave3.SetTextAlign(32)
	if tag=="": pass 
	elif len(tag)<3: pave3.AddText("veto CAT%s"%tag)
	else: pave3.AddText(tag)
	pave3.Draw()
	gPad.Update()
	pave3.SetY1NDC(pave3.GetY2NDC()-len(pave3.GetListOfLines())*0.055)

	leg = TLegend(0.38,0.92-0.04*4,0.62,0.90)
	leg.SetTextFont(42)
	leg.SetTextSize(0.042)
	leg.SetBorderSize(0)
	leg.SetFillStyle(-1)

	leg.AddEntry(limitplotobs,"CL_{S} Observed^{ }","LP")
	leg.AddEntry(limitplotexp,"CL_{S} Expected^{ }","L")
	if any(['Inj' in x for x in limnames]): leg.AddEntry(limitplotinj,"CL_{S} H(125) Injected^{ }","L")
	leg.AddEntry(limitplotband68,"CL_{S} Expected (68%)^{ }","F")
	leg.AddEntry(limitplotband95,"CL_{S} Expected (95%)^{ }","F")
	leg.SetY1(leg.GetY2()-(leg.GetNRows())*0.052)

	limitplotexp.Draw("axisl")
	limitplotband95.Draw("same3")
	limitplotband68.Draw("same3")
	limitplotexp.Draw("samel")
	if not opts.blind: limitplotobs.Draw("samelp")
	if any(['Inj' in x for x in limnames]): limitplotinj.Draw("samel")
	line.Draw("same")
	leg.Draw("same")
	pave.Draw("same")
	pave2.Draw("same")
	if 'CATveto' in limnames[ilimit]: pave3.Draw("same")

	os.chdir(cwd)

	print os.getcwd()
	c.SaveAs('limit%s.png'%opts.tag)
	c.SaveAs('limit%s.pdf'%opts.tag)
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
