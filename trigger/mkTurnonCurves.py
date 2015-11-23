#!/usr/bin/env python

import sys,os,json,re,math
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

import main
from optparse import OptionParser,OptionGroup
from copy import deepcopy as dc
from toolkit import *
from dependencyFactory import *
from write_cuts import *
from array import array

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mgtc = OptionGroup(mp,cyan+"Turnon Curve settings"+plain)
	mgtc.add_option('--fill',help='Fill histograms and write to root file.',action='store_true',default=False)
	mgtc.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
	mgtc.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mgtc.add_option('--drawstack',help='Draw histogram (stacked) from root file (fill if not present).',action='store_true',default=False)
	mgtc.add_option('--redrawstack',help='Draw histogram (stacked) from root file (refill in all cases).',action='store_true',default=False)
	mgtc.add_option('--closure',help='Run also without reference trigger and add curve to plots.',action='store_true',default=False)
	mgtc.add_option('--overlay',help='Draw both corrected and uncorrected curves.',action='store_true',default=False)
	mgtc.add_option('--shade',help='Shade selected areas.',action='store_true',default=False)

	mp.add_option_group(mgtc)
	return mp


# CONTAINER ########################################################################################
class TEffiType():
	def __init__(self,v):
		self.v = v
		self.h = {}
		self.s = {}
		for tag in ['Num','Den']:
			self.h[tag] = {}
			self.s[tag] = None
		self.s['Rat'] = None
	
	def fill(self,spointer,sample,tag,names,cuts):
		self.h[tag][sample] = TH1F(names['hist'],names['hist-title'],int(self.v['nbins_x']),float(self.v['xmin']),float(self.v['xmax']))
		self.h[tag][sample].Sumw2()
		inroot('%s.draw("%s","%s","%s");'%(spointer,self.h[tag][sample].GetName(),self.v['root'],cuts))
		self.fillstack(sample,tag,names)
	
	def fillstack(self,sample,tag,names):
		print red+"Filling %s %s %s"%(sample,tag,names['stack'])+plain
		if not self.s[tag]: self.s[tag] = THStack(names['stack'],names['stack-title'])
		self.s[tag].Add(self.h[tag][sample])
		self.s[tag].GetStack()

	def get(self,sample,tag,fullpath,names):
		if not gDirectory.Get(fullpath): return 
		self.h[tag][sample] = TH1F(gDirectory.Get(fullpath))
		self.fillstack(sample,tag,names)

	def effi(self,names,mColor,mStyle):
		self.e = TEfficiency(names['stack'],names['stack-title'],int(self.v['nbins_x']),float(self.v['xmin']),float(self.v['xmax']))
		#print Blue+names['stack']+plain
		#print blue+"Num: ",self.s['Num'].GetStack().Last().GetEntries(),plain
		#print blue+"Den: ",self.s['Den'].GetStack().Last().GetEntries(),plain
		self.e.SetPassedHistogram(self.s['Num'].GetStack().Last(),'f')
		self.e.SetTotalHistogram(self.s['Den'].GetStack().Last(),'f')
		self.e.SetLineColor(mColor)
		self.e.SetMarkerStyle(mStyle)
		self.e.SetMarkerColorAlpha(mColor,1.0 if not (mStyle==33 or (mStyle==22 and not 'NoCor' in names['stack'])) else 0.85)
		self.e.SetMarkerSize(1.8 if not any([x in names['hist'] for x in ['Data','JetMon']]) else 1.50) #1.75
		if mStyle==21: self.e.SetMarkerSize(2.0)
		if mStyle==33: self.e.SetMarkerSize(2.3)
		self.e.Paint("")
		self.e.GetPaintedGraph().GetXaxis().SetTitle(names['stack-title'].split(';')[1])
		self.e.GetPaintedGraph().GetYaxis().SetTitle(names['stack-title'].split(';')[2])
	
	def write(self,fout,path):
		gDirectory.cd('%s:/'%fout.GetName())
		makeDirsRoot(fout,path)
		for js in self.h.itervalues():
			for ks in js.itervalues():
				if ks==None: continue
				gDirectory.cd(path)
				ks.Write(ks.GetName(),TH1.kOverwrite)
				gDirectory.cd('%s:/'%fout.GetName())
		gDirectory.cd(path)
		self.e.Write(self.e.GetName(),TH1.kOverwrite)
		gDirectory.cd('%s:/'%fout.GetName())

	def delete(self):
		for js in self.s.itervalues(): 
			if js: js.Delete()
		for ih in self.h.itervalues():
			for jh in ih.itervalues():
				if jh: jh.Delete()
		self.e.Delete()


def ratio(eff1,eff2):
	N = eff1.GetTotalHistogram().GetNbinsX()+1
	vx = array('f',N*[0])
	vy = array('f',N*[0])
	vexl = array('f',N*[0])
	vexh = array('f',N*[0])
	veyl = array('f',N*[0])
	veyh = array('f',N*[0])
	for i in range(N):
		vx[i]    = eff1.GetTotalHistogram().GetBinCenter(i)
		vexl [i] = 0
		vexh[i]  = 0
		y1    = eff1.GetEfficiency(i)
		e1l   = eff1.GetEfficiencyErrorLow(i)
		e1h   = eff1.GetEfficiencyErrorUp(i)
		y2    = eff2.GetEfficiency(i)
		e2l   = eff2.GetEfficiencyErrorLow(i)
		e2h   = eff2.GetEfficiencyErrorUp(i)
		vy[i]   = 0
		veyl[i] = 0
		veyh[i] = 0
		if (y1>0 and y2>0):
			vy[i]   = y1/y2
			veyl[i] = vy[i]*math.sqrt(e1l*e1l/y1/y1 + e2l*e2l/y2/y2)
			veyh[i] = vy[i]*math.sqrt(e1h*e1h/y1/y1 + e2h*e2h/y2/y2)
	g = TGraphAsymmErrors(N,vx,vy,vexl,vexh,veyl,veyh)
	g.SetTitle("")
	g.GetXaxis().SetTitle(eff1.GetPaintedGraph().GetXaxis().GetTitle())
	g.GetYaxis().SetTitle("Data / MC")
	g.GetYaxis().SetRangeUser(0.65,1.35) #0.6,1.4 #0.0,2.0
	g.GetYaxis().SetNdivisions(505)
	g.GetXaxis().SetTickLength(0.025)
	g.GetYaxis().SetTickLength(0.082)
#	g.SetMarkerStyle(20)
#	g.SetMarkerColor(kBlack)
	g.SetMarkerSize(2.3 if markerStyle==33 else (1.8 if not g.GetMarkerStyle()==22 else 1.6)) #1.25
	g.SetLineColor(g.GetMarkerColor()) #1.25
	return g

def markerStyle(tag,smarker,opts):
	if 'NoRef' in tag: return 21
	elif 'QCD' in tag and 'NoCor' in tag: return 22#26
	elif 'QCD' in tag: return 22 if opts.closure else 33
	elif 'VBF' in tag and 'NoCor' in tag: return 27
	elif 'VBF' in tag: return 33
	else: return smarker

def markerColour(tag,scolour,opts):
	if 'NoRef' in tag: return kOrange+1
	elif 'NoCor' in tag: return TColor.GetColorDark(kAzure-3)#kRed+1#kGreen-3
	elif 'QCD' in tag: return TColor.GetColorDark(kAzure-3) if opts.closure else TColor.GetColorDark(kGreen-3)
	else: return TColor.GetColorDark(scolour)

# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,ref,KFWght=None,skipWght=None):
	# info
	l2("Filling for %s"%v['var'])
	# containers
	cuts = {}
	cutlabels = {}
	names = {}
	canvas = TCanvas("cfill","cfill",1200,1000)
	# trg
	trg, trg_orig = trigData(opts,s,trg)
	# names
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	names['global'] = getNames(opts,s,v,sel,trg_orig,ref)
	keepMapInfo = None
	if skipWght==True:
		keepMapInfo = [x for x in opts.weight[1] if (x[0:3]=='MAP' or x[0:3]=='FUN' or x[0:3]=='COR')]
		opts.weight[1] = [dc(x) for x in opts.weight[1] if not (x[0:3]=='MAP' or x[0:3] == 'FUN' or x[0:3]=='COR')]
	wpars = weightInfo(opts.weight,KFWght)

	# TEffi object
	TEffi = TEffiType(v)

	# looping over different tags
	for tag in ['Num','Den']:
		# cuts
		cuts[tag],cutlabels[tag] = write_cuts(sel,trg if tag=='Num' else ['None'],reftrig=ref,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,varskip=opts.skip+[v['root']],trigequal=trigTruth(opts.usebool))
		if opts.debug: l3("Cut %s: %s%s%s: %s"%(tag,blue,cutlabels[tag],plain,cuts[tag]))

		# loading/filling
		names[tag] = getNames(opts,s,v,sel,trg_orig if tag=='Num' else ['None'],ref,tag)
		if not s['tag'] in TEffi.h[tag] or TEffi.h[tag][s['tag']]==None:
			fout.Delete(names[tag]['hist'])
			TEffi.fill(s['pointer'],s['tag'],tag,names[tag],cuts[tag])
			if opts.debug: l3("%sFilled: %40s(N=%9d, Int=%9d)%s"%(yellow,TEffi.h[tag][s['tag']].GetName(),TEffi.h[tag][s['tag']].GetEntries(),TEffi.h[tag][s['tag']].Integral(),plain))
	
	# consider ratio
	tag = 'Rat'
	names[tag]  = getNames(opts,s,v,sel,trg_orig,ref,tag)
	TEffi.effi(names[tag],jsoninfo['colours'][s['tag']],markerStyle(s['tag'],jsoninfo['markers'][s['tag']],opts))

	# write histogram to file			
	path = "%s/%s/%s"%('turnonCurves',wpars,names['global']['path-turnon'])
	TEffi.write(fout,path)

	# clean
	#TEffi.delete()
	canvas.Close()
	trg = dc(trg_orig)
	if skipWght==True:
		opts.weight[1] += keepMapInfo


def do_drawstack(opts,fout,samples,v,sel,trg,ref,KFWght=None):
	# names
	namesGlobal = getNames(opts,None,v,sel,trg,ref)
	wpars = weightInfo(opts.weight,KFWght)
	wparsover = None
	if any([('MAP'==x[0:3] or 'FUN'==x[0:3] or x[0:3]=='COR') for x in opts.weight[1]]):
		weightsover = dc(opts.weight)
		weightsover[1] = [dc(x) for x in opts.weight[1] if not (x[0:3]=='MAP' or x[0:3]=='FUN' or x[0:3]=='COR')]
		wparsover = weightInfo(weightsover,KFWght)
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawstack','cdrawstack',1200 if not opts.notext else 1000,1000)
	canvas.cd()

	# legend
	columns = 1 #ceil(len(samples)/4.)
	rows = 0
	for y in samples:
		ytag = y['tag']
		for x in ['Jetmon','QCD','VBF']:
			if x in ytag and opts.overlay: rows += 1
			elif x in ytag and opts.closure: rows += 1
			elif x in ytag: rows += 1

	#left    = gPad.GetLeftMargin()+0.02
	#bottom  = 1-gPad.GetTopMargin()-0.02 - (0.05*rows) # n rows sized 0.04
	#right   = gPad.GetLeftMargin()+0.02 + (0.20*columns) # n columns width 0.12
	#top     = 1-gPad.GetTopMargin()-0.02
	left    = 1 + 0.01 - gPad.GetRightMargin()
	right   = 1 - 0.02
	bottom  = 1 - gPad.GetTopMargin() - 0.25 - 0.02 - (0.045*rows) 
	top     = 1 - gPad.GetTopMargin() - 0.25 - 0.02 
	legend  = getTLegend(left,bottom,right,top,columns,"%s cut trigger efficiency"%("(N-1)" if not ('mbb' in v['bare'] or 'mva' in v['bare'] or not (any([v['bare'] in x for x in sel]) or ('jetBtag' in v['bare'] and any(['Btag' in x for x in sel])))) else "N"),0,1,0.030) #3001
        legend.SetFillStyle(-1)
        legend.SetBorderSize(0)
	if opts.notext: 
###		legend.SetTextSize(0.028)
###		legend.SetX1(0.15)
###		legend.SetX2(0.15+0.3)
###		legend.SetY1(0.77)
###		legend.SetY2(0.90)
		legend.SetFillStyle(1000)
		legend.SetFillColor(kWhite)
		legend.SetTextSize(2.0/4.0*gStyle.GetPadTopMargin())
		legend.SetX1(gStyle.GetPadLeftMargin()+0.015)
		legend.SetX2(0.55)
		legend.SetY1(0.0)

	# info text
	rows   = sum([not opts.weight==[[''],['']],sum([x in opts.weight[1] for x in ['KFAC','LUMI']]),sum([(x[0:2]=='PU' or x[0:3] in ['MAP','COR']) for x in opts.weight[1]]),1]) # counting lines about weights + 1 for vbfHbb tag 
	#left   = 1-gPad.GetRightMargin()-0.02 - (0.25) # width 0.3
	#right  = 1-gPad.GetRightMargin()-0.02
	#top    = 1-gPad.GetTopMargin()
	#bottom = 1-gPad.GetTopMargin() - (0.05*rows) # n rows size 0.04
	left   = 1 - gPad.GetRightMargin() + 0.01 
	right  = 1 - 0.02
	bottom = 1 - gPad.GetTopMargin() - 0.02 - (0.05*rows) 
	top = 1 - gPad.GetTopMargin() - 0.02 
	text = getTPave(left,bottom,right,top,None,0,0,1,0.030)
	text.AddText("VBF H #rightarrow b#bar{b}:") 
	text.AddText("#sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'PU'  in [x[0:2] for x in opts.weight[1]]: text.AddText("PU reweighted")
	if not opts.weight==[[''],['']] and 'COR' in [x[0:3] for x in opts.weight[1]]: text.AddText("1DMap reweighted")
	if not opts.weight==[[''],['']] and 'MAP' in [x[0:3] for x in opts.weight[1]]: text.AddText("2DMap reweighted")
	textaltpad = TPave(gPad.GetLeftMargin()+0.015,0.0,0.55,1.-gPad.GetTopMargin()-0.015)
        textaltpad.SetFillColor(kWhite)
        textaltpad.SetFillStyle(1000)
        textaltpad.SetBorderSize(0)
###	textalt = getTPave(0.14,0.91,0.46,0.92,None,0,0,1,0.028)
	textalt = getTPave(gPad.GetLeftMargin()+0.006,0.0,0.55,1.-gPad.GetTopMargin()-0.015,None,0,0,1,2.2/4.0*gStyle.GetPadTopMargin())
        textalt.SetTextAlign(12)
	textalt.SetFillStyle(3000)
	textalt.SetFillColor(kWhite)
	l = textalt.AddText("%s selection      "%('Set A' if any(['NOM' in x for x in trg]) else ('Set B' if any(['VBF' in x for x in trg]) else '???')))
	l.SetTextFont(62)
        textalt.Draw()
        gPad.Update()
        textalt.SetY1NDC(textalt.GetY2NDC()-textalt.GetListOfLines().GetSize()*2.4/4.*gStyle.GetPadTopMargin())
        textaltpad.SetY1(textalt.GetY1NDC()-0.01)
        if opts.notext:
		legend.SetY2(textalt.GetY1NDC()-0.005)
	# layout scaling
	ymin=0
	ymax=0

	# selection legend
	rows = 2+sum([1 for x in sel])
	left   = 1 - gPad.GetRightMargin() + 0.01
	right  = 1 - 0.02
	top    = 1 - gPad.GetTopMargin() -0.02 - 0.55
	bottom = 1 - gPad.GetTopMargin() -0.02 - 0.55 - (0.03*rows) # n rows size 0.03
	selleg = getSelLegend(left,bottom,right,top)
	for iline,line in enumerate(sorted([x.strip() for x in sel],key=lambda x:x.lower())): selleg.AddText('%s %s'%('sel:' if iline==0 else ' '*4,line))
	selleg.AddText('trg: %s (MC)'%(','.join(trg)))
	selleg.AddText('     %s (data)'%(','.join(opts.datatrigger[opts.trigger.index(trg)] if opts.datatrigger else trg)))
	selleg.AddText('ref: %s '%(','.join(ref)))

	# containers
	stacks = {}

	### LOOP over all samples
	for s in sorted(samples,key=lambda x:('QCD' in x['tag'],-jsoninfo['crosssections'][x['tag']])):
		# trg
		trg,trg_orig = trigData(opts,s,trg)
		# names
		sample = s['pointer']
		names = {}
		names['global'] = getNames(opts,s,v,sel,trg_orig,ref)
		for tag in ['Num','Den','Rat']:
			names[tag] = getNames(opts,s,v,sel,trg_orig if not tag=='Den' else ['None'],ref,tag)
		# info	
		l3("%sStack group: %s (sample: %s)%s"%(blue,names['global']['group'],s['tag'],plain))

		group = names['global']['group']
		if not group in stacks:
			stacks[group] = {}
			stacks[group]['effis']    = TEffiType(v) 
			stacks[group]['names']    = names
			stacks[group]['colours']  = jsoninfo['colours'][s['tag']]
			stacks[group]['markers']  = jsoninfo['markers'][s['tag']]

		# load histograms from file
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
		# fill if needed/wanted 
		for tag in ['Num','Den']:
			fullpath = path+names[tag]['hist']+';1'
			if not (opts.redraw or opts.redrawstack): stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
			if (not s['tag'] in stacks[group]['effis'].h[tag]) or opts.redrawstack:
				if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
				elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
				else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
				if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
				stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
			if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,stacks[group]['effis'].h[tag][s['tag']].GetName(),stacks[group]['effis'].h[tag][s['tag']].GetEntries(),stacks[group]['effis'].h[tag][s['tag']].Integral(),plain))
			setStyleTH1F(stacks[group]['effis'].h[tag][s['tag']],stacks[group]['colours'],1,stacks[group]['colours'],0,1,20,0,1)
		print
		trg = dc(trg_orig)


	if opts.closure:
		### LOOP over all samples (again, without reference trigger)
		for s in sorted(samples,key=lambda x:('QCD' in x['tag'],-jsoninfo['crosssections'][x['tag']])):
			if any([x in s['tag'] for x in ['Data','JetMon']]): continue
			# trg
			trg,trg_orig = trigData(opts,s,trg)
			# names
			sample = s['pointer']
			names = {}
			names['global'] = getNames(opts,s,v,sel,trg_orig,['None'])
			for tag in ['Num','Den','Rat']:
				names[tag] = getNames(opts,s,v,sel,trg_orig if not tag=='Den' else ['None'],['None'],tag)
			# info	
			group = names['global']['group'] + '_NoRef'
			l3("%sStack group: %s (sample: %s)%s"%(blue,group,s['tag'],plain))
	
			if not group in stacks:
				#print group
				stacks[group] = {}
				stacks[group]['effis']    = TEffiType(v) 
				stacks[group]['names']    = names
				stacks[group]['colours']  = jsoninfo['colours'][s['tag']]
				stacks[group]['markers']  = jsoninfo['markers'][s['tag']]
	
			# load histograms from file
			gDirectory.cd('%s:/'%fout.GetName())
			path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
			# fill if needed/wanted 
			for tag in ['Num','Den']:
				fullpath = path+names[tag]['hist']+';1'
				if not (opts.redraw or opts.redrawstack): stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
				if (not s['tag'] in stacks[group]['effis'].h[tag]) or opts.redrawstack:
					if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
					elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
					else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
					if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,['None'],KFWght)
					stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
				if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,stacks[group]['effis'].h[tag][s['tag']].GetName(),stacks[group]['effis'].h[tag][s['tag']].GetEntries(),stacks[group]['effis'].h[tag][s['tag']].Integral(),plain))
				setStyleTH1F(stacks[group]['effis'].h[tag][s['tag']],stacks[group]['colours'],1,stacks[group]['colours'],0,1,26,0,1)
			print
			trg = dc(trg_orig)

	
	if opts.overlay and any([('MAP'==x[0:3] or 'FUN'==x[0:3] or x[0:3]=='COR') for x in opts.weight[1]]):
		### LOOP over all samples (again, without map correction)
		for s in sorted(samples,key=lambda x:('QCD' in x['tag'],-jsoninfo['crosssections'][x['tag']])):
			if any([x in s['tag'] for x in ['Data','JetMon']]): continue
			# trg
			trg,trg_orig = trigData(opts,s,trg)
			# names
			sample = s['pointer']
			names = {}
			names['global'] = getNames(opts,s,v,sel,trg_orig,ref)
			for tag in ['Num','Den','Rat']:
				names[tag] = getNames(opts,s,v,sel,trg_orig if not tag=='Den' else ['None'],ref,tag)
			# info	
			group = names['global']['group'] + '_NoCor'
			l3("%sStack group: %s (sample: %s)%s"%(blue,group,s['tag'],plain))
	
			if not group in stacks:
				stacks[group] = {}
				stacks[group]['effis']    = TEffiType(v) 
				stacks[group]['names']    = names
				stacks[group]['colours']  = jsoninfo['colours'][s['tag']]
				stacks[group]['markers']  = jsoninfo['markers'][s['tag']] if not 'NoRef' in group else 21 
	
			# load histograms from file
			gDirectory.cd('%s:/'%fout.GetName())
			path = '/%s/%s/%s/'%('turnonCurves',wparsover,names['global']['path-turnon'])
			# fill if needed/wanted 
			for tag in ['Num','Den']:
				fullpath = path+names[tag]['hist']+';1'
				if not (opts.redraw or opts.redrawstack): stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
				if (not s['tag'] in stacks[group]['effis'].h[tag]) or opts.redrawstack:
					if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
					elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
					else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
					if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght,True)
					stacks[group]['effis'].get(s['tag'],tag,fullpath,names[tag])
				if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,stacks[group]['effis'].h[tag][s['tag']].GetName(),stacks[group]['effis'].h[tag][s['tag']].GetEntries(),stacks[group]['effis'].h[tag][s['tag']].Integral(),plain))
				setStyleTH1F(stacks[group]['effis'].h[tag][s['tag']],stacks[group]['colours'],1,stacks[group]['colours'],0,1,26,0,1)
			print
			trg = dc(trg_orig)

	istack=0
	for group,g in sorted(stacks.iteritems(),key=lambda (x,y):(not 'JetMon' in x, not 'NoRef' in x, not 'NoCor' in x)):
		# get ratio
		tag = 'Rat'
		g['effis'].effi(g['names'][tag],markerColour(group,g['colours'],opts),markerStyle(group,g['markers'],opts))
#g['markers'] if (not 'NoRef' in group and not 'NoCor' in group) else (21 if not ('NoCor' in group) else (26 if 'QCD' in group else 27)))#25 26 27 #if not 'NoRef' in group else kOrange+1 ## 22 an 33
		legentry = ""
		if 'JetMon' in group: legentry = 'Data'
		elif 'QCD' in group:
			if 'NoRef' in group: legentry = 'QCD (without reference trigger)'
			elif 'NoCor' in group: legentry = 'QCD (no correction)'
			else: 
				if any(['NoRef' in x for x in stacks.iterkeys()]): legentry = 'QCD (with reference trigger)'
				else: legentry = 'QCD (corrected)'
		else: legentry = group
		legend.AddEntry(g['effis'].e,legentry,'LP')

	# Data / MC ratio
	ratioplots = {}
	if 'JetMon' in stacks.keys():
		for group,g in sorted(stacks.iteritems()):
			if group=='JetMon': continue
			#if 'NoCor' in group or 'NoRef' in group: continue
			ratioplots[group] = ratio(stacks['JetMon']['effis'].e,stacks[group]['effis'].e)
			ratioplots[group].SetMarkerStyle(markerStyle(group,stacks[group]['markers'],opts))
			ratioplots[group].SetMarkerColorAlpha(markerColour(group,stacks[group]['colours'],opts),1.0 if not (ratioplots[group].GetMarkerStyle()==33 or (ratioplots[group].GetMarkerStyle==22 and opts.closure)) else 0.85)
			ratioplots[group].SetMarkerSize(1.8 if not ratioplots[group].GetMarkerStyle()==33 else 2.3)
			ratioplots[group].SetLineColor(markerColour(group,stacks[group]['colours'],opts))
			
	cutsjson = json.loads(filecontent(opts.jsoncuts))
	if not ratioplots=={}:
		# containers
###		c1,c2 = getRatioPlotCanvas(canvas)
                c1 = TPad("c1","c1",0.0,0.0,1.0,1.0)
                c2 = TPad("c2","c2",0.0,0.0,1.0,1.0)
                c2.SetFillStyle(-1)
                c1.Draw()
                c2.Draw()
                canvas.Update()
                canvas.Modified()
                c1.SetBottomMargin(0.3)
                c2.SetTopMargin(1-0.29)
                canvas.Update()
                canvas.Modified()
		# draw (top)
		c1.cd()
		#gPad.SetLeftMargin(0.08)
		#gPad.SetRightMargin(0.03)
		plotcut = None
		for istack,tagNstack in enumerate([(g,stacks[g]['effis']) for g in stacks.keys()]):
			tag = tagNstack[0]
			stack = tagNstack[1]
			if any(['NOM' in x for x in trg]): ymax = 0.65 if not any([x in stack.e.GetPaintedGraph().GetXaxis().GetTitle() for x in ['mva','Bjet']]) else 0.70 #0.14
			elif any(['VBF' in x for x in trg]): ymax = 1.2 if not any([x in stack.e.GetPaintedGraph().GetXaxis().GetTitle() for x in ['ptAve','jet3']]) else 1.3
			else: ymax = 1.0
			#stack.e.SetTitle(namesGlobal['turnon-title'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon-title'])
			stack.e.SetTitle(";;Efficiency curves")
			stack.e.GetPaintedGraph().SetTitle(";;Efficiency curves")
			stack.e.GetPaintedGraph().GetXaxis().SetLimits(float(v['xmin']),float(v['xmax']))
			stack.e.GetPaintedGraph().GetXaxis().SetLabelColor(0);
			stack.e.GetPaintedGraph().GetXaxis().SetTitleColor(0);
			stack.e.GetPaintedGraph().GetYaxis().SetRangeUser(0.0,ymax)
			stack.e.GetPaintedGraph().GetXaxis().SetNdivisions(808)
			#stack.e.GetPaintedGraph().GetYaxis().SetRangeUser(0.0,1.4)#5*stack.e.GetPaintedGraph().GetHistogram().GetMaximum())
			stack.e.GetPaintedGraph().GetYaxis().SetTitleOffset(1.10 if not opts.notext else 1.25)
			stack.e.GetPaintedGraph().GetXaxis().SetTickLength(0.025)
			stack.e.GetPaintedGraph().GetYaxis().SetTickLength(0.025)
			stack.e.GetPaintedGraph().GetYaxis().SetLabelSize(stack.e.GetPaintedGraph().GetYaxis().GetLabelSize()*(1.2 if not opts.notext else 1.1))
			stack.e.GetPaintedGraph().GetYaxis().SetLabelOffset(stack.e.GetPaintedGraph().GetYaxis().GetLabelOffset()/(1.4 if not opts.notext else 1.2))
			stack.e.GetPaintedGraph().GetYaxis().SetDecimals(kTRUE)
			if istack==0: stack.e.GetPaintedGraph().Draw("ap")
			stack.e.GetPaintedGraph().Draw("e,p,same")
			c1.Modified()
			if istack==0: 
		#		ymax = 0
		#		for st in [stacks[g]['effis'] for g in stacks.keys()]:
		#			for i in range(st.e.GetPaintedGraph().GetN()):
		#				x = ROOT.Double(0.0)
		#				y = ROOT.Double(0.0)
		#				st.e.GetPaintedGraph().GetPoint(i,x,y)
		#				if y>ymax: 
		#					ymax = dc(y)
		#		ymax = 1.0#max(ymax,0.7/1.4)
				vlines = []
				vboxes = []
				plotcuts = []
				plotcutdirections = []
				for isel in sel:
					if v['root'] in cutsjson['sel'][isel]: 
						gPad.Update()
						gPad.Modified()
						for i in range(len(cutsjson['sel'][isel][v['root']])/2):
							plotcuts += [float(cutsjson['sel'][isel][v['root']][2*i+1])]
							plotcutdirections += [1 if cutsjson['sel'][isel][v['root']][2*i]=='>' else -1]
							vlines += [getTLine(plotcuts[-1],gPad.GetUymin(),plotcuts[-1],gPad.GetUymax(),kRed,3,9)]
							vlines[-1].Draw("same")
						for i in range(len(plotcuts)):
							if opts.shade:
								vboxes += [TBox(gPad.GetUxmin() if plotcutdirections[i]==1 else plotcuts[i],gPad.GetUymin(),plotcuts[i] if plotcutdirections[i]==1 else gPad.GetUxmax(),gPad.GetUymax())]
								vboxes[-1].SetFillColor(kGray)
								vboxes[-1].SetFillStyle(3001)
								vboxes[-1].Draw("same")
						gPad.Update()
						gPad.Modified()
						
#			stack.e.GetPaintedGraph().GetYaxis().SetRangeUser(0.0,round(ymax*1.4,1))
#			stack.e.GetPaintedGraph().GetYaxis().SetLabelSize(stack.e.GetPaintedGraph().GetYaxis().GetLabelSize()*1.2)
#			stack.e.GetPaintedGraph().GetYaxis().SetLabelOffset(stack.e.GetPaintedGraph().GetYaxis().GetLabelOffset()/1.4)
#			gPad.Update()
#			gPad.Modified()
#			stack.e.Paint("")
#			gPad.Update()
#			gPad.Modified()
#			stack.e.GetPaintedGraph().Draw("epsame")
#			gPad.Update()
#			gPad.Modified()
		# draw (bottom)
		c2.cd()
#		gPad.SetLeftMargin(0.08)
#		gPad.SetRightMargin(0.03)
#		gPad.SetBottomMargin(0.32)
		for iratioplot,ratioplot in enumerate(ratioplots.itervalues()):
			ratioplot.GetYaxis().SetNdivisions(505)
			ratioplot.GetXaxis().SetLimits(float(v['xmin']),float(v['xmax']))
			ratioplot.GetXaxis().SetNdivisions(808)
###			ratioplot.GetXaxis().SetTitleOffset(3.5)
			ratioplot.GetXaxis().SetTitleOffset(1.02)
			ratioplot.GetYaxis().SetTitleOffset(1.20 if not opts.notext else 1.40)
			ratioplot.GetYaxis().SetTitleSize(ratioplot.GetYaxis().GetTitleSize()*0.9)
			ratioplot.GetYaxis().SetLabelSize(ratioplot.GetYaxis().GetLabelSize()*(1.0 if not opts.notext else 0.95))
			ratioplot.GetYaxis().SetDecimals(kTRUE)
###			if opts.notext:
###				c2.SetLeftMargin(0.13)
###				c2.SetRightMargin(0.07)
			gPad.SetGridy(1)
			if iratioplot==0: 
				ratioplot.Draw('e')
				ratioplot.Draw('a,p,same')
			else: 
				ratioplot.Draw('p,e,same')
			
#			gStyle.SetOptFit(0)
#			fit = TF1("fitline","[0]",max([float(v['xmin'])]+[x for (ix,x) in enumerate(plotcuts) if plotcutdirections[ix]==1]),min([float(v['xmax'])]+[x for (ix,x) in enumerate(plotcuts) if plotcutdirections[ix]==-1]))
#			ratioplot.Fit("fitline","QR")
#			av = fit.GetParameter(0)
#			avtext = getTPave(0.85,0.75,0.99,0.85,None,0,0,1,0.08)
#			avtext.AddText("average: %.2f"%av)
#			avtext.Draw()

		# line at cut
		if len(plotcuts)>0:
			gPad.Update()
			vlines2 = []
			rvboxes = []
			for plotcut in plotcuts: 
				plotcutdirection = plotcutdirections[plotcuts.index(plotcut)]
				vlines2 += [getTLine(plotcut,gPad.GetUymin(),plotcut,gPad.GetUymax(),kRed,3,9)]
				vlines2[-1].Draw("same")
				if opts.shade:
					rvboxes += [TBox(gPad.GetUxmin() if plotcutdirection==1 else plotcut,gPad.GetUymin(),plotcut if plotcutdirection==1 else gPad.GetUxmax(),gPad.GetUymax())]
					rvboxes[-1].SetFillColor(kGray)
					rvboxes[-1].SetFillStyle(3001)
					rvboxes[-1].Draw("same")
		# line through y=1
		gPad.Modified()
		gPad.Update()
		line = getTLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0,kBlack,2,1)
		line.Draw("same")
		c1.cd()
	else:
		canvas.cd()
		for istack,stack in enumerate([stacks[g]['effis'] for g in stacks.keys()]):
			stack.e.GetPaintedGraph().Draw("" if istack==0 else "same")
	c1.cd()
	gPad.RedrawAxis()

	# write plot to file
	canvas.cd()
        textaltpad.Draw()
	legend.Draw()
        legend.SetY1(legend.GetY2()-(legend.GetNRows()+1)*2.15/4.0*gStyle.GetPadTopMargin())
	if not opts.notext: 
		text.Draw()
		selleg.Draw()
	else:
		textalt.Draw()

        pcms1 = TPaveText(gPad.GetLeftMargin(),1.-gPad.GetTopMargin(),0.4,1.,"NDC")
        pcms1.SetTextAlign(12)
        pcms1.SetTextFont(62)
        pcms1.SetTextSize(gPad.GetTopMargin()*2.5/4.)
        pcms1.SetFillStyle(-1)
        pcms1.SetBorderSize(0)
        pcms1.AddText("CMS")
        pcms1.Draw()

        pcms2 = TPaveText(0.5,1.-gPad.GetTopMargin(),1.-gPad.GetRightMargin()+0.02,1.,"NDC")
        pcms2.SetTextAlign(32)
        pcms2.SetTextFont(62)
        pcms2.SetTextSize(gPad.GetTopMargin()*2.5/4.)
        pcms2.SetFillStyle(-1)
        pcms2.SetBorderSize(0)
        pcms2.AddText("%.1f fb^{-1} (8 TeV)"%(float(opts.weight[0][0])/1000.))
        pcms2.Draw()

	gPad.RedrawAxis()
	path = '%s/../trigger/%s/%s/%s/%s/%s'%(basepath,'plots',os.path.split(fout.GetName())[1][:-5],wpars,'turnonCurves',namesGlobal['path-turnon'])
	makeDirs(path)
	canvas.SetName(namesGlobal['turnon'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon'])
	canvas.SetTitle(namesGlobal['turnon-title'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon-title'])
	canvas.Update()
	canvas.SaveAs('%s/%s%s.png'%(path, canvas.GetName(),'' if not opts.notext else "_noleg"))
	canvas.SaveAs('%s/%s%s.pdf'%(path, canvas.GetName(),'' if not opts.notext else "_noleg"))
	print
	if opts.debug: l3("%sWritten plots to: (eog %s)%s"%(yellow,'%s/%s%s.png'%(path, canvas.GetName(),'' if not opts.notext else '_noleg'),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()





####################################################################################################
def mkTurnonCurves():
	# init main (including option parsing)
	opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser(),False,None,None)

        # ROOT
        gROOT.SetBatch(1)
        gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
        gStyle.SetDrawBorder(0)
        gStyle.SetCanvasBorderMode(0)
        gStyle.SetCanvasBorderSize(0)
        gStyle.SetPadBorderMode(1)
        gStyle.SetLineScalePS(2.2)
        gStyle.SetPadTopMargin(0.06)
        gStyle.SetPadBottomMargin(0.12)
        gStyle.SetPadRightMargin(0.04)
        gStyle.SetTextFont(42)
        gStyle.SetTitleFont(42,"XYZT")
        gStyle.SetLabelFont(42,"XYZT")
        gStyle.SetTextSize(0.04)
        gStyle.SetTitleSize(0.05,"XYZT")
        gStyle.SetLabelSize(0.04,"XYZT")
        gStyle.SetLabelOffset(0.01,"Y")

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack): sys.exit(red+"Specify either fill, draw, redraw, drawstack or redrawstack option to run. Exiting."+plain) 

	#if opts.KFWght or len(opts.weight)==4: l1("Including KFWght calculations or manual KFWght.")
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			for ref in opts.reftrig:
				KFWght = KFWghts[('-'.join(sorted(sel)),'-'.join(trg))]
				for v in variables.itervalues():
					if not v['var'] in opts.variable: continue
					if v['var'] in opts.novariable: continue
					for s in sorted(loadedSamples, key=lambda x:(not 'QCD' in x['tag'], len(x['tag']), x['tag'])):
						if opts.fill or opts.draw or opts.redraw: 
							print
							l2("Sample: %s"%s['tag'])
						if opts.fill: 
							do_fill(opts,fout,s,v,sel,trg,ref,KFWght)
							if opts.closure: do_fill(opts,fout,s,v,sel,trg,['None'],KFWght)
					if opts.drawstack or opts.redrawstack: 
						do_drawstack(opts,fout,loadedSamples,v,sel,trg,ref,KFWght)
						print 
					### END LOOP over samples
				### END LOOP over variables
			### END LOOP over reference triggers
		### END LOOP over selections
	### END LOOP over triggers

	# try to clean up 
	#main.dumpSamples(loadedSamples)	
		
	
	

if __name__=='__main__':
	mkTurnonCurves()
