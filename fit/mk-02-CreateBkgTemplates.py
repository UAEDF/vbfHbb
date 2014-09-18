#!/usr/bin/env python

import sys,os,json,re
from optparse import OptionParser,OptionGroup
from array import array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

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
	mpBkgTemp = OptionGroup(mp,cyan+"Background template options"+plain)
	mpBkgTemp.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)
#	mpBkgTemp.add_option('--catTags',help='tags for categories',type='str',action='callback',callback=optsplit,default=[])
	mpBkgTemp.add_option('--fBound',help='fit MIN and MAX',type='str',action='callback',callback=optsplit,default=['80','200'])	
	complexWght
	mp.add_option_group(mpBkgTemp)
	return mp

####################################################################################################
def INTERNALprepare(opts):
	makeDirs(os.path.split(opts.fout)[0])
	makeDirs('plots/bkgTemplates')
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
	
#	markers = [20, 21, 20 , 23]
#	colours = [kBlack,kBlue,kRed,kGreen+2] 
#	return markers, colours

####################################################################################################

def INTERNALstyleHist(h,i,markers,colours):
	h.Sumw2()
	h.SetMarkerStyle(markers[i])
	h.SetMarkerColor(colours[i])
	h.SetMarkerSize(1.2)
	h.SetLineColor(colours[i])
	h.GetXaxis().SetTitle("M_{bb} (GeV)")
	h.GetYaxis().SetTitle("PDF")
	h.GetYaxis().SetNdivisions(505)
	h.SetMaximum(0.25)
	return h

####################################################################################################

def INTERNALhistograms(opts):
	hMbb = {}
	hMbbYield = {}
	hZ = None
	hW = None
	hTT = None
	hST = None
	hTop = None
	hZYield = None
	hWYield = None
	hTTYield = None
	hSTYield = None
	hTopYield = None

	return hMbb, hMbbYield, hZ, hW, hTT, hST, hTop, hZYield, hWYield, hTTYield, hSTYield, hTopYield

####################################################################################################

def INTERNALcanvases(opts):
	return None 

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

def INTERNALline(fun, min, max):
	ln = TF1("line",fun,min,max)
	ln.SetLineColor(kBlack)
	ln.SetLineWidth(1)
	ln.SetLineStyle(2)
	ln.SetMinimum(0.7)
	ln.SetMaximum(1.3)
#	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
#	ln.GetYaxis().SetTitle("Signal / Control")
	return ln

####################################################################################################

def INTERNALpicksamples(opts,jsons):
	l1("Global path: %s"%opts.globalpath)
	l1("Using input samples:")
	allsamples = jsonsamp['files']
	selsamples = []
	for s in allsamples.itervalues():
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in s['tag']) for x in opts.sample]): continue
	    # veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in s['tag']) for x in opts.nosample]): continue
		selsamples += [s]
	for s in selsamples:
		s['tfile'] = TFile.Open(opts.globalpath + s['fname'])
		l2('%s: %s(%s)'%(s['tag'],s['fname'],s['tfile'])
	return selsamples
	
####################################################################################################

def mkBkgTemplates():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	jsons = INTERNALprepare(opts)
	INTERNALstyle()

	hMbb, hMbbYield, hZ, hW, hTT, hST, hTop, hZYield, hWYield, hTTYield, hSTYield, hTopYield = INTERNALhistograms(opts)
	#INTERNALcanvases(opts)
	
	samples = INTERNALpicksamples(opts,jsons)

	ln = INTERNALline("1",float(opts.fBound[0]),float(opts.fBound[1]))

	for iTag,Tag in enumerate(opts.catTags):
		nCat = int(opts.mvaBins['mva%s'%Tag][0])-1
		rCat = 0 if Tag=='NOM' else 4

		
	

		fin = TFile.Open('flat/fitFlatTree_Data_%s.root'%Tag)
		l1('Running for %s --> %s'%(Tag,fin.GetName()))
		tin = fin.Get("Hbb/events")
		
		c2[Tag] = TCanvas('transfer_sel%s'%Tag,'transfer_sel%s'%Tag,600*(nCat-1),600)
		c2[Tag].Divide(nCat-1,1)

		leg = INTERNALlegend(Tag)
		leg.SetX1(0.7)
		lleg = dict(((Tag,iCat+1),INTERNALlegend(Tag)) for iCat in range(nCat-1))
		
		for iCat in range(nCat):
			jCat = iCat + rCat
			l2('Running for CAT%d'%jCat)
#			v = jsons['vars']['variables'][opts.variables[opts.variables.keys()[iTag]][0]]

# regular hists
#			if v['xs']: hDat[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,iCat),'hDat_sel%s_CAT%d'%(Tag,iCat),int(v['nbins_x']),v['xs'])
#			else: hDat[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,iCat),'hDat_sel%s_CAT%d'%(Tag,iCat),int(v['nbins_x']),int(v['xmin']),int(v['xmax']))
			hDat[(Tag,iCat)] = TH1F('hDat_sel%s_CAT%d'%(Tag,jCat),'hDat_sel%s_CAT%d'%(Tag,jCat),int(float(opts.fBound[1]) - float(opts.fBound[0]))/10,float(opts.fBound[0]),float(opts.fBound[1]))
			h = hDat[(Tag,iCat)]
			h = INTERNALstyleHist(h,iCat,markers,colours)
			can.cd()
# cut
			CUT = TCut("mva%s>%.2f && mva%s<=%.2f"%(Tag,float(opts.mvaBins["mva%s"%Tag][1][iCat+1]),Tag,float(opts.mvaBins["mva%s"%Tag][1][iCat+2])))
			###CUT = TCut("mvaNOM>%.2f && mvaNOM<=%.2f"%(float(opts.mvaBins["mva%s"%Tag][1][iCat+1]),float(opts.mvaBins["mva%s"%Tag][1][iCat+2])))
			l3('Cutting with: %s'%CUT)

# drawing
			l3('Drawing mbbReg[%d] --> %s'%(1 if 'NOM' in Tag else 2,h.GetName()))
			tin.Draw("mbbReg[%d]>>%s"%(1 if 'NOM' in Tag else 2,h.GetName()),CUT)
			###tin.Draw("mbbReg[1]>>%s"%(h.GetName()),CUT)
			h = INTERNALblind(h,100.,150.)
			h.Scale(1./h.Integral())
			h.SetDirectory(0)

# ratio hist
			hRat[(Tag,iCat)] = h.Clone(h.GetName().replace('hDat','hRat'))
			r = hRat[(Tag,iCat)]
			r = INTERNALstyleHist(r,iCat,markers,colours)

# dividing by control CAT
			##print "Divide: ", hDat[(Tag,0)].GetName()
			r.Divide(hDat[(Tag,0)])
			r.SetDirectory(0)
			
# fit
			fFit[(Tag,iCat)] = TF1(h.GetName().replace('hDat','fitRatio'),'pol1',float(opts.fBound[0]),float(opts.fBound[1]))
			f = fFit[(Tag,iCat)]
			f.SetLineColor(colours[iCat])

			if not iCat==0:
				r.Fit(f,"RQ")
				fitter = TVirtualFitter.GetFitter()
				covariant = TMatrixDSym()
				covariant.Use(fitter.GetNumberTotalParameters(),fitter.GetCovarianceMatrix())
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
				hDat[(Tag,0)].GetYaxis().SetRangeUser(0.0,max(h.GetMaximum(),hDat[(Tag,0)].GetMaximum())*1.02)
				gPad.Update()
				leg.AddEntry(h,'CAT%d'%jCat,'P')
				c2[Tag].cd(iCat)
				ln.Draw()
				g.Draw('same E3')
				r.Draw('same')
				ll = lleg[(Tag,iCat)] 
				ll.AddEntry(h,'CAT%d / CAT%d'%(jCat,rCat),'P')
				ll.SetY1(ll.GetY2()-ll.GetNRows()*0.06)
				ll.SetTextSize(0.04)
				ll.Draw()
			else:
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
