#!/usr/bin/env python

import sys,os,json,re
from optparse import OptionParser,OptionGroup
from array import array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from main import main

# OPTION PARSER ##################################################################################
##
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mpTransfer = OptionGroup(mp,cyan+"Transfer function options"+plain)
	mpTransfer.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)
	mpTransfer.add_option('--catTags',help='tags for categories',type='str',action='callback',callback=optsplit,default=[])
	mpTransfer.add_option('--fBound',help='fit MIN and MAX',type='str',action='callback',callback=optsplit,default=['80','200'])	
	mpTransfer.add_option('--scale',help='transfer function scale factors',type='str',action='callback',callback=TFscale,default=None)	
	mpTransfer.add_option('--scaledBand',help='which band to print POL(1,2,3)',type='int',default=3)
	mp.add_option_group(mpTransfer)
	return mp

####################################################################################################

def TFscale(option,opt,value,parser):
	fitTag = ['_POL1','_POL2','_POL3']
	sd = {}
	for i,vi in enumerate(value.split(',')):
		for j,vj in enumerate(vi.split(';')):
			sd[(j,fitTag[i])] = float(vj)
	setattr(parser.values, option.dest, sd)

####################################################################################################

def INTERNALprepare(opts):
	if '/' in opts.fout: makeDirs(os.path.split(opts.fout)[0])
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
	for v in opts.mvaBins:
			jsons['vars']['variables'][v]['nbins_x'] = opts.mvaBins[v][0]
			jsons['vars']['variables'][v]['xs'] = array('f',[round(float(x),4) for x in opts.mvaBins[v][1]])
			jsons['vars']['variables'][v]['xmin'] = opts.mvaBins[v][1][0]
			jsons['vars']['variables'][v]['xmax'] = opts.mvaBins[v][1][-1]
	return jsons

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
	
	markers = [20, 21, 20 , 23]
	#colours = [kBlack,kBlue,kRed,kGreen+2] 
	colours = [TColor.GetColorBright(kGray+2),TColor.GetColorBright(kBlue),TColor.GetColorBright(kRed)]
	return markers, colours

####################################################################################################

def INTERNALstyleHist(h,i,markers,colour): #s):
	h.Sumw2()
	h.SetMarkerStyle(markers[i])
	h.SetMarkerColor(kBlack)#colours[i])
	h.SetMarkerSize(1.0)
	h.SetLineColor(kBlack)#s[i])
	h.GetXaxis().SetTitle("M_{bb} (GeV)")
	h.GetYaxis().SetTitle("PDF")
	h.GetYaxis().SetNdivisions(505)
	h.SetMaximum(0.25)
	return h

####################################################################################################

def INTERNALhistograms(opts):
	hDat = {}
	hRat = {}
	fFit = {}
	gUnc = {}
	gUncScaled = {}
	fitter = {}
	covariant = {}
	for iTag,Tag in enumerate(opts.catTags):
		for iCat,Cat in enumerate(opts.mvaBins[opts.mvaBins.keys()[iTag]]):
			hDat[(Tag,iCat)] = None
			for fitTag in ['_POL1','_POL2','_POL3']: 
				hRat[(Tag,iCat,fitTag)]       = None
				fFit[(Tag,iCat,fitTag)]       = None
				gUnc[(Tag,iCat,fitTag)]       = None
				gUncScaled[(Tag,iCat,fitTag)] = None
	for fitTag in ['_POL1','_POL2','_POL3']:
		fitter[fitTag]    = None
		covariant[fitTag] = None
	return hDat, hRat, fFit, gUnc, gUncScaled, fitter, covariant

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

def INTERNALpave():
	pave = TPaveText(0.2,0.8,0.5,0.9,"NDC")
	pave.SetFillColor(0)
	pave.SetBorderSize(0)
	pave.SetTextFont(42)
	pave.SetTextSize(0.05)
	return pave

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
def INTERNALlegendB():
	leg = TLegend(0.20,0.10,0.55,0.38)
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
	ln.SetMinimum(0.7)
	ln.SetMaximum(1.3)
	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
	ln.GetYaxis().SetTitle("Signal / Control")
	return ln

####################################################################################################

def INTERNALgraph(r,f,c): #ratio, function, covariant
	nBins = 200
	order = c.GetNrows()
	dx = (r.GetBinLowEdge(r.GetNbinsX()+1)-r.GetBinLowEdge(1))/float(nBins)
	vx = array('f',[r.GetBinLowEdge(1)+(i+1)*dx for i in range(nBins)])
	vy = array('f',[f.Eval(vx[i]) for i in range(nBins)])
	vex = array('f',[0.0]*nBins)
	vey = array('f',[0.0]*nBins)
	for i in range(nBins):
		for j in range(order):
			for k in range(order):
				vey[i] += pow(vx[i],j)*pow(vx[i],k)*c(j,k)
		vey[i] = sqrt(vey[i])
	g = TGraphErrors(nBins,vx,vy,vex,vey)
	return g

####################################################################################################

def INTERNALgraphScaled(r,f,c,s): #ratio, function, covariant, scale
	nBins = 200
	order = c.GetNrows()
	dx = (r.GetBinLowEdge(r.GetNbinsX()+1)-r.GetBinLowEdge(1))/float(nBins)
	vx = array('f',[r.GetBinLowEdge(1)+(i+1)*dx for i in range(nBins)])
	vy = array('f',[f.Eval(vx[i]) for i in range(nBins)])
	vex = array('f',[0.0]*nBins)
	vey = array('f',[0.0]*nBins)
	for i in range(nBins):
		for j in range(order):
			vey[i] += pow(s,2)*pow(vx[i],2*j)*c(j,j)
		vey[i] = sqrt(vey[i])
	g = TGraphErrors(nBins,vx,vy,vex,vey)
	return g

####################################################################################################

def mkTemplateFunctions():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()
	paves = []

	hDat, hRat, fFit, gUnc, gUncScaled, fitter, covariant = INTERNALhistograms(opts)
	c1, c2, c = INTERNALcanvases(opts)
	can = TCanvas("main","main")

	ln = INTERNALline("1",float(opts.fBound[0]),float(opts.fBound[1]))

	for iTag,Tag in enumerate(opts.catTags):
		nCat = int(opts.mvaBins['mva%s'%Tag][0])-1
		rCat = 0 if Tag=='NOM' else 4
		fin = TFile.Open('flat/fitFlatTree_Data_%s.root'%Tag)
		l1('Running for %s --> %s'%(Tag,fin.GetName()))
		tin = fin.Get("Hbb/events")
		
		c2[Tag] = TCanvas('transfer_sel%s'%Tag,'transfer_sel%s'%Tag,600*(nCat-1),500*3)
		c2[Tag].Divide(nCat-1,3)

		leg = INTERNALlegend(Tag)
		leg.SetX1(0.7)
		lleg = dict(((Tag,iCat+1),INTERNALlegend(Tag)) for iCat in range(nCat-1))
		llegB = dict(((Tag,iCat+1),INTERNALlegendB()) for iCat in range(nCat-1))

		
		for iCat in range(nCat):
			jCat = iCat + rCat
			l2('Running for CAT%d'%jCat)

# regular hists
			hDat[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,jCat),'hDat_sel%s_CAT%d'%(Tag,jCat),int(float(opts.fBound[1]) - float(opts.fBound[0]))/5,float(opts.fBound[0]),float(opts.fBound[1]))
			h = hDat[(Tag,iCat)]
			h = INTERNALstyleHist(h,iCat,markers,colours[0])
			can.cd()
# cut
			CUT = TCut("mva%s>%.2f && mva%s<=%.2f"%(Tag,float(opts.mvaBins["mva%s"%Tag][1][iCat+1]),Tag,float(opts.mvaBins["mva%s"%Tag][1][iCat+2])))
			l3('Cutting with: %s'%CUT)

# drawing
			l3('Drawing mbbReg[%d] --> %s'%(1 if 'NOM' in Tag else 2,h.GetName()))
			tin.Draw("mbbReg[%d]>>%s"%(1 if 'NOM' in Tag else 2,h.GetName()),CUT)
			h = INTERNALblind(h,100.,150.)
			h.Scale(1./h.Integral())
			h.SetDirectory(0)

# fit
			fitFunction = {'_POL1':'pol1', '_POL2':'pol2', '_POL3':'pol3'}
			for ifitTag,fitTag in enumerate(['_POL1','_POL2','_POL3']):
# ratio hist
				hRat[(Tag,iCat,fitTag)] = h.Clone(h.GetName().replace('hDat','hRat'))
				r = hRat[(Tag,iCat,fitTag)]
				r = INTERNALstyleHist(r,iCat,markers,colours[0])
	
# dividing by control CAT
				##print "Divide: ", hDat[(Tag,0)].GetName()
				r.Divide(hDat[(Tag,0)])
				r.SetDirectory(0)
				
				fFit[(Tag,iCat,fitTag)] = TF1(h.GetName().replace('hDat','fitRatio'),fitFunction[fitTag],float(opts.fBound[0]),float(opts.fBound[1]))
				f = fFit[(Tag,iCat,fitTag)]
				f.SetLineColor(colours[ifitTag])
				f.SetLineWidth(2)

				if not iCat==0:
					r.Fit(f,"RQBN")
					fitter[fitTag]    = TVirtualFitter.GetFitter()
					covariant[fitTag] = TMatrixDSym()
					covariant[fitTag].Use(fitter[fitTag].GetNumberTotalParameters(),fitter[fitTag].GetCovarianceMatrix())
	
					gUnc[(Tag,iCat,fitTag)] = INTERNALgraph(r,f,covariant[fitTag])
					gUncScaled[(Tag,iCat,fitTag)] = INTERNALgraphScaled(r,f,covariant[fitTag],opts.scale[(jCat,fitTag)])
					g = gUnc[(Tag,iCat,fitTag)]
					g.SetFillColor(colours[ifitTag])
					fills = [3765,3775,3785,3756,3757,3758]
					g.SetFillStyle(fills[ifitTag])
					gS = gUncScaled[(Tag,iCat,fitTag)]
					gS.SetFillColor(TColor.GetColorBright(kGreen+2))
					gS.SetFillStyle(3002)#fills[ifitTag+3])
								
					if ifitTag==0:
						c1[Tag].cd()
						h.Draw('same E')
						hDat[(Tag,0)].GetYaxis().SetRangeUser(0.0,max(h.GetMaximum(),hDat[(Tag,0)].GetMaximum())*1.02)
						leg.AddEntry(h,'CAT%d'%jCat,'P')
						gPad.Update()

					for ci in range(3):
						c2[Tag].cd(iCat+ci*(nCat-1))
						if ifitTag==0:
							ln.Draw()
						g.Draw('same E3')
						if ifitTag==2: gUncScaled[(Tag,iCat,'_POL%d'%(ci+1))].Draw('same E3')
						r.Draw('same')	
						f.Draw('same')

						llB = llegB[(Tag,iCat)]
						if ifitTag==0 and ci==0: llB.SetHeader("                      %8s    %8s"%("PROB","#chi^{2}/NDF"))
						if ci==0: llB.AddEntry(f,'%6s %8.2f   %8.2f'%(fitTag[1:],f.GetProb(),f.GetChisquare()/f.GetNDF()),'LF')
						if ifitTag==2:
							llB.SetTextSize(0.03)
							llB.SetY1(llB.GetY2()-(llB.GetNRows()+1)*0.035)
							llB.Draw()
							pave = TPaveText(llB.GetX1(),llB.GetY1()-0.05,llB.GetX2(),llB.GetY1()-0.01,"NDC")
							pave.SetFillStyle(-1)
							pave.SetBorderSize(0)
							pave.SetTextAlign(11)
							pave.SetTextSize(0.035)
							pave.SetTextFont(42)
							pave.AddText("Scale Factor band: %.3f"%opts.scale[(jCat,'_POL%d'%(ci+1))])
							pave.Draw()
							paves += [pave]
					
					if ifitTag==0:
						ll = lleg[(Tag,iCat)] 
						ll.AddEntry(h,'CAT%d / CAT%d'%(jCat,rCat),'P')
						ll.SetY1(ll.GetY2()-ll.GetNRows()*0.06)
						ll.SetTextSize(0.04)
						ll.Draw()

				else:
					if ifitTag==0:
						c1[Tag] = TCanvas('MbbShape_sel%s'%Tag,'MbbShape_sel%s'%Tag,900,600)
						c1[Tag].cd()
						gPad.SetLeftMargin(0.12)
						gPad.SetRightMargin(0.03)
						h.GetYaxis().SetTitleOffset(0.8)
						h.SetFillColor(kGray)
						h.Draw('hist')
						leg.AddEntry(h,'CAT%d'%jCat,'F')

				fout.cd()
				f.Write(f.GetName(),TH1.kOverwrite)

		c1[Tag].cd()
		leg.SetY1(leg.GetY2()-leg.GetNRows()*0.06)
		leg.Draw()
		c1[Tag].SaveAs('plots/transfer/%s.png'%c1[Tag].GetName())
		c1[Tag].SaveAs('plots/transfer/%s.pdf'%c1[Tag].GetName())
		c2[Tag].SaveAs('plots/transfer/%s.png'%c2[Tag].GetName())
		c2[Tag].SaveAs('plots/transfer/%s.pdf'%c2[Tag].GetName())

	#c.SaveAs('plots/transfer/%s.png'%c.GetName())

# clean
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkTemplateFunctions()
