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
	
	markers = [20, 21, 20 , 23]
	colours = [kBlack,kBlue,kRed,kGreen+2] 
	return markers, colours

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

def INTERNALhistograms(opts,sels,jsons):
	hProf = {}
	vars = jsons['vars']['variables']
	for s in sels:
		for v in opts.variable:
			if '1' in v and not s=='NOM' and not 'Btag' in v and not 'QGL' in v: continue
			if '2' in v and not s=='VBF' and not 'Btag' in v and not 'QGL' in v: continue
			if 'mva' in v and not s in v: continue
			for tag in ['QCD','DAT']:
				if tag=='QCD': hProf[(s,v,tag)] = TProfile("h%s_sel%s_%s"%(tag,s,v),"h%s_sel%s_%s;%s;<%s>"%(tag,s,v,'mva%s'%s,vars[v]['title_x']),int(int(vars['mva%s'%s]['nbins_x'])/2),float(vars['mva%s'%s]['xmin']),float(vars['mva%s'%s]['xmax']))
				else: hProf[(s,v,tag)] = TProfile("h%s_sel%s_%s"%(tag,s,v),"h%s_sel%s_%s;%s;<%s>"%(tag,s,v,'mva%s'%s,vars[v]['title_x']),int(vars['mva%s'%s]['nbins_x']),float(vars['mva%s'%s]['xmin']),float(vars['mva%s'%s]['xmax']))
	return hProf

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
	ln.GetXaxis().SetTitle("M_{bb} (GeV)")
	ln.GetYaxis().SetTitle("Signal / Control")
	return ln

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

def mkTemplateFunctions():
	mp = parser()
	opts,fout,samples = main(mp,False,False,True)

	sels = ['NOM','VBF']
	jsons = INTERNALprepare(opts)
	markers, colours = INTERNALstyle()

	selsamples = INTERNALpicksamples(opts,jsons)

	can = TCanvas("main","main")
	hProf = INTERNALhistograms(opts,sels,jsons)
	#INTERNALcanvases(opts)

	l1("Creating profiles")
	if not opts.read:
		for isel,sel in enumerate(sels):
			ssel = [s for s in selsamples if sel in s['fname']]
	
			for s in ssel:
				l2("Running for %s"%s['tag'])
	
				cut,cutlabel = write_cuts(["None"],["None"],reftrig=["None"],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.complexWghts[(sel,'old')],trigequal=trigTruth(opts.usebool))
				cut = re.findall('\*.*',cut)[0][2:-1].replace('pu','ev.pu').replace('trig','ev.trig')
				if opts.debug: l3("Cut %s: \n\t\t\t%s%s%s: \n\t\t\t%s"%(s['tag'],blue,cutlabel,plain,cut))
				
				nevents = s['tree'].GetEntries()
	
				for iev,ev in enumerate(s['tree']):
					if iev%int(nevents/5)==0: l3("%10s/%10s"%(iev,nevents))
					wght = eval(cut)
					mva = ev.mvaNOM if sel=='NOM' else ev.mvaVBF
					mbb = ev.mbbReg[1] if sel=='NOM' else ev.mbbReg[2]
					if sel=='NOM':
						if mva<-0.6: continue
						if mbb<80. or mbb>200.: continue
					if sel=='VBF':
						if mva<-0.1: continue
						if mbb<80. or mbb>200.: continue

					for v in opts.variable:
						if '1' in v and not sel=='NOM' and not 'Btag' in v and not 'QGL' in v: continue
						if '2' in v and not sel=='VBF' and not 'Btag' in v and not 'QGL' in v: continue
						if 'mva' in v and not sel in v: continue
	
						v = jsons['vars']['variables'][v]
	
						h = hProf[(sel,v['var'],'QCD' if 'QCD' in s['fname'] else 'DAT')]
						h.Fill(mva,eval("ev.%s"%(v['root'] if not '[btag' in v['root'] else v['root'].replace('[btag','[ev.btag'))),wght)
	else:
		for k in hProf.iterkeys():
			hProf[k] = fout.Get("h%s_sel%s_%s"%(k[2],k[0],k[1]))
			
	k = list(set([x[0:2] for x in hProf.iterkeys()])) 
	for ik in k:
		low = min(hProf[(ik[0],ik[1],'QCD')].GetBinContent(hProf[(ik[0],ik[1],'QCD')].GetMinimumBin()),hProf[(ik[0],ik[1],'DAT')].GetBinContent(hProf[(ik[0],ik[1],'DAT')].GetMinimumBin()))
		hig = max(hProf[(ik[0],ik[1],'QCD')].GetBinContent(hProf[(ik[0],ik[1],'QCD')].GetMaximumBin()),hProf[(ik[0],ik[1],'DAT')].GetBinContent(hProf[(ik[0],ik[1],'DAT')].GetMaximumBin()))
		med = hProf[(ik[0],ik[1],'DAT')].GetMean(2)
		dif = hig-low
		setlow = med - 2*dif
		sethig = med + 2*dif
		if 'mbb' in ik[1]: setlow=110
		if 'mbb' in ik[1]: sethig=160

		hProf[(ik[0],ik[1],'DAT')].GetYaxis().SetRangeUser(setlow,sethig)
		hProf[(ik[0],ik[1],'DAT')].Draw()
		hProf[(ik[0],ik[1],'QCD')].SetMarkerStyle(25)
		hProf[(ik[0],ik[1],'QCD')].SetMarkerColor(kBlue)
		#for ibin in range(1,hProf[(ik[0],ik[1],'QCD')].GetNbinsX()+1): hProf[(ik[0],ik[1],'QCD')].
		hProf[(ik[0],ik[1],'QCD')].Draw("same L")

		leg = TLegend(0.6,0.6,0.9,0.9,"%s selection"%(ik[0].strip('sel')))
		leg.SetFillStyle(-1)
		leg.SetBorderSize(0)
		leg.SetTextFont(42)
		leg.SetTextSize(0.045)
		leg.AddEntry(hProf[(ik[0],ik[1],'DAT')],'Data')
		leg.AddEntry(hProf[(ik[0],ik[1],'QCD')],'QCD')
		leg.SetY1(leg.GetY2()-(leg.GetNRows()+1)*0.05)
		leg.Draw()

		can.SaveAs("plots/%s.png"%hProf[(ik[0],ik[1],'DAT')].GetName().replace('hDAT','h'))

	fout.cd()
	for h in hProf.itervalues():
		h.Write(h.GetName(),TH1.kOverwrite)

# clean
	fout.Close()

####################################################################################################

if __name__=='__main__':
	mkTemplateFunctions()
