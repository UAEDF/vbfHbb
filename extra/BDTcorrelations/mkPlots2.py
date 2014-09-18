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

from write_cuts import *
from toolkit import *
from main import main

# OPTION PARSER ##################################################################################
##
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mpExtra = OptionGroup(mp,cyan+"Extra options"+plain)
	mpExtra.add_option('--mvaBins',help='mva bins: var#3#1;3;6;9,...',type='str',action='callback',callback=optsplitdict)#,default={'mvaNOM':['4',['-0.6','0.0','0.7','0.84','1.0']],'mvaVBF':['3',['-0.1','0.4','0.8','1.0']]})
	mpExtra.add_option('--complexWghts',help='Wght info.',type='str',action='callback',callback=optsplitmore,default=[])
	mpExtra.add_option('--read',help='Read h\'s from file.',action='store_true',default=False)
	mp.add_option_group(mpExtra)
	return mp

####################################################################################################
def INTERNALprepare(opts):
	makeDirs(os.path.split(opts.fout)[0])
	makeDirs('plots')
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))
	jsons = {'samp':jsonsamp,'vars':jsonvars,'info':jsoninfo,'cuts':jsoncuts}
	# fix binning
	if opts.binning:
		for v in opts.binning:
			#print v
			jsons['vars']['variables'][v[0]]['nbins_x'] = v[1]
			jsons['vars']['variables'][v[0]]['xmin'] = v[2]
			jsons['vars']['variables'][v[0]]['xmax'] = v[3]
	if opts.mvaBins:
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
	gStyle.SetPadLeftMargin(0.18)
	gStyle.SetPadRightMargin(0.04)
	gStyle.SetStripDecimals(0)
	
	markers = [20, 21, 20 , 23]
	colours = [kBlack,kBlue,kRed,kGreen+2] 
	return markers, colours

####################################################################################################

#def INTERNALstyleHist(h,i,markers,colours):
#	h.Sumw2()
#	h.SetMarkerStyle(markers[i])
#	h.SetMarkerColor(colours[i])
#	h.SetMarkerSize(1.2)
#	h.SetLineColor(colours[i])
#	h.GetXaxis().SetTitle("M_{bb} (GeV)")
#	h.GetYaxis().SetTitle("PDF")
#	h.GetYaxis().SetNdivisions(505)
#	h.SetMaximum(0.25)
#	return h

####################################################################################################

def INTERNALgraph(h):
	g = TGraphErrors(h.GetNbinsX())
	for ibin in range(1,h.GetNbinsX()+1):
		x = h.GetBinCenter(ibin)
		y = h.GetBinContent(ibin)
		ex = h.GetBinWidth(ibin)/2.
		ey = h.GetBinError(ibin)

		g.SetPoint(ibin-1,x,y)
		g.SetPointError(ibin-1,ex,ey)
	return g

####################################################################################################

def INTERNALhistograms(opts,sels,jsons):
	hProf = {}
	vars = jsons['vars']['variables']
	for s in sels:
		for v in opts.variable:
			vroot = vars[v]['root']
			if s=='NOM' and '[2]' in vroot: continue
			if s=='VBF' and '[1]' in vroot: continue
			if 'mva' in v and not s in v: continue

			for tag in ['QCD','DAT']:
				vy = 'BDT'
				vy2 = 'mva%s'%s
				if tag=='QCD': hProf[(s,v,vy,tag)] = TProfile("h%s_sel%s_%s_%s"%(tag,s,v,vy),"h%s_sel%s_%s_%s;%s;<%s>%s"%(tag,s,v,vy,'BDT output',vars[v]['title_x'].replace(' (GeV)','')," (GeV)" if 'GeV' in vars[v]['title_x'] else ""),int(int(vars[vy2]['nbins_x'])/(2 if not ('mbb' in v or 'cos' in v) else 4)),float(vars[vy2]['xmin']),float(vars[vy2]['xmax']))
				else: hProf[(s,v,vy,tag)] = TProfile("h%s_sel%s_%s_%s"%(tag,s,v,vy),"h%s_sel%s_%s_%s;%s;<%s>%s"%(tag,s,v,vy,'BDT output',vars[v]['title_x'].replace(' (GeV)','')," (GeV)" if 'GeV' in vars[v]['title_x'] else ""),int(vars[vy2]['nbins_x']),float(vars[vy2]['xmin']),float(vars[vy2]['xmax']))
				hProf[(s,v,vy,tag)].Sumw2()
				if 'mbbReg' in v: continue
				vy = 'mbbReg'
				vy2 = 'mbbReg[%d]'%(1 if s=='NOM' else 2)
				if tag=='QCD': hProf[(s,v,vy,tag)] = TProfile("h%s_sel%s_%s_%s"%(tag,s,v,vy),"h%s_sel%s_%s_%s;%s;<%s>%s"%(tag,s,v,vy,'regressed M_{bb} (GeV)',vars[v]['title_x'].replace(' (GeV)','')," (GeV)" if 'GeV' in vars[v]['title_x'] else ""),int(48/(2 if not ('cos' in v) else 4)),80.,200.)
				else: hProf[(s,v,vy,tag)] = TProfile("h%s_sel%s_%s_%s"%(tag,s,v,vy),"h%s_sel%s_%s_%s;%s;<%s>%s"%(tag,s,v,vy,'regressed M_{bb} (GeV)',vars[v]['title_x'].replace(' (GeV)','')," (GeV)" if 'GeV' in vars[v]['title_x'] else ""),48,80.,200.)
				hProf[(s,v,vy,tag)].Sumw2()
	return hProf

####################################################################################################

#def INTERNALcanvases(opts):
#	return None 

####################################################################################################

#def INTERNALlegend(Tag):
#	leg = TLegend(0.6,0.62,0.95,0.92)
#	leg.SetHeader("%s selection"%Tag)
#	leg.SetFillColor(0)
#	leg.SetBorderSize(0)
#	leg.SetTextFont(42)
#	leg.SetTextSize(0.05)
#	return leg

####################################################################################################

#def INTERNALline(fun, min, max):
#	ln = TF1("line",fun,min,max)
#	ln.SetLineColor(kBlack)
#	ln.SetLineWidth(1)
#	ln.SetLineStyle(2)
#	ln.SetMinimum(0.7)
#	ln.SetMaximum(1.3)
#	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
#	ln.GetYaxis().SetTitle("Signal / Control")
#	return ln

####################################################################################################

def INTERNALpicksamples(opts,jsons):
	l1("Global path: %s"%opts.globalpath)
	l1("Using input samples:")
	allsamples = jsons['samp']['files']
	selsamples = []
	for s in allsamples.itervalues():
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in s['tag']) for x in opts.sample]): continue
	    # veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in s['tag']) for x in opts.nosample]): continue
		selsamples += [s]
	for s in sorted(selsamples,key=lambda x:(x['tag'][:3],int(re.findall('[0-9]+',x['tag'])[0]) if len(re.findall('[0-9]+',x['tag']))>0 else 1.,not 'NOM' in x['fname'])):
		s['tfile'] = TFile.Open(opts.globalpath + s['fname'])
		s['tree'] = s['tfile'].Get("Hbb/events")
		s['incarnation'] = 'NOM' if 'NOM' in s['tag'] else 'VBF'
		l2('%-15s: %-50s(%s)'%(s['tag'],s['fname'],s['tfile']))
	return selsamples

####################################################################################################

def mkBDTcorrelations():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	sels = ['NOM','VBF']
	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()

	selsamples = INTERNALpicksamples(opts,jsons)

	can = TCanvas("main","main",650,600)
	hProf = INTERNALhistograms(opts,sels,jsons)
	#INTERNALcanvases(opts)

	l1("Creating profiles")
	if not opts.read:
		for isel,sel in enumerate(sels):
			ssel = [s for s in selsamples if sel in s['fname']]
	
			for s in ssel:
				l2("Running for %s"%s['tag'])
	
				cut,cutlabel = write_cuts(["None"],["None"],reftrig=["None"],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.complexWghts[(sel,'old')],trigequal=trigTruth(opts.usebool))
				#cut = re.findall('\*.*',cut)[0][2:-1].replace('pu','ev.pu').replace('trig','ev.trig')
				if opts.debug: l3("Cut %s: \n\t\t\t%s%s%s: \n\t\t\t%s"%(s['tag'],blue,cutlabel,plain,cut))
				
				cutextra = "mbbReg[%d]>=80. && mbbReg[%d]<=200."%(1 if sel=='NOM' else 2, 1 if sel=='NOM' else 2)

				for v in [jsons['vars']['variables'][vv] for vv in opts.variable]:
					if sel=='NOM' and '[2]' in v['root']: continue
					if sel=='VBF' and '[1]' in v['root']: continue
					if 'mva' in v and not sel in v: continue

					s['tree'].Draw("%s:%s>>+%s"%(v['root'],"mva%s"%sel,hProf[(sel,v['var'],'BDT','QCD' if 'QCD' in s['fname'] else 'DAT')].GetName()),TCut(cutextra)*TCut(cut),"prof")
					if 'mbbReg' in v['var']: continue
					s['tree'].Draw("%s:%s>>+%s"%(v['root'],"mbbReg[%d]"%(1 if sel=='NOM' else 2),hProf[(sel,v['var'],'mbbReg','QCD' if 'QCD' in s['fname'] else 'DAT')].GetName()),TCut(cutextra)*TCut(cut),"prof")

	else:
		for k in hProf.iterkeys():
			hProf[k] = fout.Get("h%s_sel%s_%s_%s"%(k[3],k[0],k[1],k[2]))
			
	k = list(set([x[0:3] for x in hProf.iterkeys()])) 
	for ik in k:
		low = min(hProf[(ik[0],ik[1],ik[2],'QCD')].GetBinContent(hProf[(ik[0],ik[1],ik[2],'QCD')].GetMinimumBin()),hProf[(ik[0],ik[1],ik[2],'DAT')].GetBinContent(hProf[(ik[0],ik[1],ik[2],'DAT')].GetMinimumBin()))
		hig = max(hProf[(ik[0],ik[1],ik[2],'QCD')].GetBinContent(hProf[(ik[0],ik[1],ik[2],'QCD')].GetMaximumBin()),hProf[(ik[0],ik[1],ik[2],'DAT')].GetBinContent(hProf[(ik[0],ik[1],ik[2],'DAT')].GetMaximumBin()))
		med = hProf[(ik[0],ik[1],ik[2],'DAT')].GetMean(2)
		dif = hig-low
		setlow = med - 1.6*dif
		sethig = med + 1.6*dif
		if not 'cos' in ik[1]: 
			setlow = max(setlow,0)

		limits = {'dEtaqq1':[2,7,2,7],'dPhiqq1':[0,3,0,3],'jetBtag00':[0.5,1.2,0.8,1.0],'jetBtag01':[0.0,1.2,0.55,0.75],'jetQGLNOM0':[0,1,0.5,0.65],'jetQGLNOM1':[0,1,0.35,0.55],'jetQGLNOM2':[0,1,0.5,0.7],'jetQGLNOM3':[0,1,0.5,0.7],'mqq1':[0,2500,500,800],'mbbReg1':[115,145,115,145],'cosTheta1':[-0.35,0.35,-0.2,0.2],'jetQGLVBF0':[0,1,0.4,0.55],'jetQGLVBF1':[0,1,0.3,0.5],'jetQGLVBF2':[0,1,0.55,0.75],'jetQGLVBF3':[0,1,0.5,0.7],'mqq2':[0,2500,1000,1300],'mbbReg2':[115,145,115,145],'cosTheta2':[-0.35,0.35,-0.2,0.2],'dEtaqq2':[2,7,2,7],'dPhiqq2':[0,3,0,3],'softHt':[0,100,25,50],'softN2':[0,10,4,7]} #[3,7,4,6], [0,3,1,2] [0,3,1.5,2.5]
		if ik[1] in limits:
			if ik[2]=='BDT':
				setlow = limits[ik[1]][0]
				sethig = limits[ik[1]][1]
			else:
				setlow = limits[ik[1]][0]#2]
				sethig = limits[ik[1]][1]#3]
#		if 'jetBtag01' in ik[1] and ik[0]=='VBF' and ik[2]=='mbbReg':
#			setlow = 0.4
#			sethig = 0.55

		hProf[(ik[0],ik[1],ik[2],'DAT')].GetYaxis().SetRangeUser(setlow,sethig)
		hProf[(ik[0],ik[1],ik[2],'DAT')].GetYaxis().SetTitleOffset(1.4)
		hProf[(ik[0],ik[1],ik[2],'DAT')].GetXaxis().SetTitleOffset(1.0)
		hProf[(ik[0],ik[1],ik[2],'DAT')].GetYaxis().SetNdivisions(507)
		hProf[(ik[0],ik[1],ik[2],'DAT')].GetXaxis().SetNdivisions(507)
		hProf[(ik[0],ik[1],ik[2],'DAT')].Draw("axis")
		h = INTERNALgraph(hProf[(ik[0],ik[1],ik[2],'DAT')])
		h.SetMarkerStyle(20)
		h.SetMarkerSize(0.8)
		h.SetMarkerColor(kBlack)
		h.SetLineColor(kBlack)
		h.SetFillStyle(0)
		h.Draw("same pz")
		g = INTERNALgraph(hProf[(ik[0],ik[1],ik[2],'QCD')])
#		hProf[(ik[0],ik[1],ik[2],'QCD')].SetMarkerStyle(25)
#		hProf[(ik[0],ik[1],ik[2],'QCD')].SetMarkerColor(kBlue)
#		hProf[(ik[0],ik[1],ik[2],'QCD')].Draw("same e")
		g.SetMarkerStyle(25)
		g.SetMarkerColor(kBlue)
		g.SetLineColor(kBlue)
		g.SetFillStyle(0)
		g.Draw("same pz")

		leg = TLegend(0.62,0.75,0.9,0.92,"%s selection"%(ik[0].strip('sel')))
		leg.SetFillStyle(-1)
		leg.SetBorderSize(0)
		leg.SetTextFont(42)
		leg.SetTextSize(0.045)
		#leg.AddEntry(hProf[(ik[0],ik[1],ik[2],'DAT')],'Data')
		#leg.AddEntry(hProf[(ik[0],ik[1],ik[2],'QCD')],'QCD')
		leg.AddEntry(h,'Data','LP')
		leg.AddEntry(g,'QCD','LP')
		leg.SetY1(leg.GetY2()-(leg.GetNRows()+1)*0.05)
		leg.Draw()

		can.SaveAs("plots/%s.png"%hProf[(ik[0],ik[1],ik[2],'DAT')].GetName().replace('hDAT','h'))
		can.SaveAs("plots/%s.pdf"%hProf[(ik[0],ik[1],ik[2],'DAT')].GetName().replace('hDAT','h'))

	fout.cd()
	for h in hProf.itervalues():
		h.Write(h.GetName(),TH1.kOverwrite)

# clean
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkBDTcorrelations()
