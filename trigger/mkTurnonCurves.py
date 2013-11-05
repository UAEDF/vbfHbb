#!/usr/bin/env python

import sys,os,json,re
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
		if not self.s[tag]: self.s[tag] = THStack(names['stack'],names['stack-title'])
		self.s[tag].Add(self.h[tag][sample])

	def get(self,sample,tag,fullpath,names):
		if not gDirectory.Get(fullpath): return
		self.h[tag][sample] = TH1F(gDirectory.Get(fullpath).GetStack().Last())
		self.fillstack(sample,tag,names)

	def effi(self,names,mColor,mStyle):
		self.e  = TEfficiency(names['stack'],names['stack-title'],int(self.v['nbins_x']),float(self.v['xmin']),float(self.v['xmax']))
		self.e.SetPassedHistogram(self.s['Num'].GetStack().Last(),'f')
		self.e.SetTotalHistogram(self.s['Den'].GetStack().Last(),'f')
		self.e.SetMarkerStyle(mStyle)
		self.e.SetMarkerColor(mColor)
		self.e.SetMarkerSize(2.75 if not any([x in names['hist'] for x in ['Data','JetMon']]) else 2)
		self.e.Paint("")
		self.e.GetPaintedGraph().GetXaxis().SetTitle(names['stack-title'].split(';')[1])
		self.e.GetPaintedGraph().GetYaxis().SetTitle(names['stack-title'].split(';')[2])
	
	def write(self,fout,path):
		gDirectory.cd('%s:/'%fout.GetName())
		makeDirsRoot(fout,path)
		for js in self.s.itervalues():
			if js==None: continue
			gDirectory.cd(path)
			js.Write(js.GetName(),TH1.kOverwrite)
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
	N = eff1.GetTotalHistogram().GetNbinsX()
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
			veyl[i] = vy[i]*sqrt(e1l*e1l/y1/y1 + e2l*e2l/y2/y2)
			veyh[i] = vy[i]*sqrt(e1h*e1h/y1/y1 + e2h*e2h/y2/y2)
	g = TGraphAsymmErrors(N,vx,vy,vexl,vexh,veyl,veyh)
	g.SetTitle("")
	g.GetXaxis().SetTitle(eff1.GetPaintedGraph().GetXaxis().GetTitle())
	g.GetYaxis().SetTitle("Data / MC")
	g.GetYaxis().SetRangeUser(0.25,1.25)
	g.GetYaxis().SetNdivisions(505)
	g.SetMarkerStyle(20)
	g.SetMarkerColor(kBlack)
	g.SetMarkerSize(1.8)
	return g


# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,ref,KFWght=None):
	# info
	l2("Filling for %s"%v['var'])
	# containers
	cuts = {}
	cutlabels = {}
	names = {}
	canvas = TCanvas("cfill","cfill",2400,1800)
	# trg
	trg, trg_orig = trigData(opts,s,trg)
	# names
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	names['global'] = getNames(opts,s,v,sel,trg_orig,ref)
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
	TEffi.effi(names[tag],jsoninfo['colours'][s['tag']],20 if any([x in s['tag'] for x in ['Data','JetMon']]) else (22 if not 'NoRef' in names[tag]['hist'] else 26))

	# write histogram to file			
	path = "%s/%s/%s"%('turnonCurves',wpars,names['global']['path-turnon'])
	TEffi.write(fout,path)

	# clean
	TEffi.delete()
	canvas.Close()
	trg = dc(trg_orig)


def do_drawstack(opts,fout,samples,v,sel,trg,ref,KFWght=None):
	# names
	namesGlobal = getNames(opts,None,v,sel,trg,ref)
	wpars = weightInfo(opts.weight,KFWght)
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawstack','cdrawstack',2400,1800)
	canvas.cd()

	# legend
	columns = 1 #ceil(len(samples)/4.)
	rows    = 2 #ceil(len(samples)/columns)
	left    = gPad.GetLeftMargin()+0.02
	bottom  = 1-gPad.GetTopMargin()-0.02 - (0.05*rows) # n rows sized 0.05
	right   = gPad.GetLeftMargin()+0.02 + (0.12*columns) # n columns width 0.12
	top     = 1-gPad.GetTopMargin()-0.02
	legend  = getTLegend(left,bottom,right,top,columns,None,0,1,0.035)

	# info text
	rows   = sum([not opts.weight==[[''],['']],sum([x in opts.weight[1] for x in ['KFAC','PU','BMAP','LUMI','MAP']])]) # counting lines about weights + 1 for vbfHbb tag 
	left   = 1-gPad.GetRightMargin()-0.02 - (0.3) # width 0.3
	right  = 1-gPad.GetRightMargin()-0.02
	top    = 1-gPad.GetTopMargin()
	bottom = 1-gPad.GetTopMargin() - (0.05*rows) # n rows size 0.05
	text = getTPave(left,bottom,right,top,None,0,0,1,0.035)
	text.AddText("VBF H #rightarrow b#bar{b}: #sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'BMAP' in opts.weight[1]: text.AddText("BMAP reweighted")
	if not opts.weight==[[''],['']] and 'PU' in opts.weight[1]: text.AddText("PU reweighted")
	# layout scaling
	ymin=0
	ymax=0

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

		# load histograms from file
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
		# fill if needed/wanted 
		for tag in ['Num','Den']:
			fullpath = path+names[tag]['stack']+';1'
			stacks[group]['effis'].get(s['tag'],tag,fullpath,stacks[group]['names'][tag])
			if (not s['tag'] in stacks[group]['effis'].h[tag]) or opts.redrawstack:
				if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
				elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
				else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
				if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
				stacks[group]['effis'].get(s['tag'],tag,fullpath,stacks[group]['names'][tag])
			if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,stacks[group]['effis'].h[tag][s['tag']].GetName(),stacks[group]['effis'].h[tag][s['tag']].GetEntries(),stacks[group]['effis'].h[tag][s['tag']].Integral(),plain))
			setStyleTH1F(stacks[group]['effis'].h[tag][s['tag']],stacks[group]['colours'],1,stacks[group]['colours'],0,1,20)
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
			l3("%sStack group: %s (sample: %s)%s"%(blue,names['global']['group'],s['tag'],plain))
	
			group = names['global']['group'] + '_NoRef'
			if not group in stacks:
				stacks[group] = {}
				stacks[group]['effis']    = TEffiType(v) 
				stacks[group]['names']    = names
				stacks[group]['colours']  = jsoninfo['colours'][s['tag']]
	
			# load histograms from file
			gDirectory.cd('%s:/'%fout.GetName())
			path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
			# fill if needed/wanted 
			for tag in ['Num','Den']:
				fullpath  = path+names[tag]['stack']+';1'
				stacks[group]['effis'].get(s['tag'],tag,fullpath,stacks[group]['names'][tag])
				if (not s['tag'] in stacks[group]['effis'].h[tag]) or opts.redrawstack:
					if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
					elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
					else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
					if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,['None'],KFWght)
					stacks[group]['effis'].get(s['tag'],tag,fullpath,stacks[group]['names'][tag])
				if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,stacks[group]['effis'].h[tag][s['tag']].GetName(),stacks[group]['effis'].h[tag][s['tag']].GetEntries(),stacks[group]['effis'].h[tag][s['tag']].Integral(),plain))
				setStyleTH1F(stacks[group]['effis'].h[tag][s['tag']],stacks[group]['colours'],1,stacks[group]['colours'],0,1,26)
			print
			trg = dc(trg_orig)

	istack=0
	for group,g in stacks.iteritems():
		# get ratio
		tag = 'Rat'
		g['effis'].effi(g['names'][tag],g['colours'],20 if any([x in group for x in ['Data','JetMon']]) else (22 if not 'NoRef' in group else 26))
		print 
#		ymin, ymax = getRangeTH1F(g['teffis'].h[tag],ymin,ymax)
#		setRangeTH1F(g['teffis'].h[tag],0.0,1.2,False)
		legend.AddEntry(g['effis'].e,group,'LP')

		# write histogram to file
		gDirectory.cd('%s:/'%fout.GetName())
		path = "%s/%s/%s"%('turnonCurves',wpars,g['names']['global']['path-turnon'])
		makeDirsRoot(fout,path)
		g['effis'].write(fout,path)
	
	# Data / MC ratio
	if 'JetMon' in stacks.keys() and 'QCD' in stacks.keys():
		ratioplot = ratio(stacks['JetMon']['effis'].e,stacks['QCD']['effis'].e)
#		ratioplot = stacks['JetMon']['effis'].h['Rat']['JetMonA'].Clone('Data / MC')
#		ratioplot.SetTitle('Data / MC')
#		ratioplot.Divide(stacks['JetMon']['teffis'].h['Rat'].GetStack().Last(),stacks['QCD']['teffis'].h['Rat'].GetStack().Last())
	else: ratioplot=None

	cutsjson = json.loads(filecontent(opts.jsoncuts))
	if not ratioplot==None:
		# containers
		c1,c2 = getRatioPlotCanvas(canvas)
		# draw (top)
		c1.cd()
		plotcut = None
		for istack,stack in enumerate([stacks[g]['effis'] for g in stacks.keys()]):
			if istack==0: 
				stack.e.SetTitle(namesGlobal['turnon-title'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon-title'])
				stack.e.GetPaintedGraph().GetXaxis().SetLimits(float(v['xmin']),float(v['xmax']))
				stack.e.GetPaintedGraph().GetYaxis().SetRangeUser(0.0,1.3)
				stack.e.GetPaintedGraph().GetYaxis().SetTitleOffset(1.4)
				stack.e.GetPaintedGraph().Draw("ap")
				vlines = []
				plotcuts = []
				for isel in sel:
					if v['root'] in cutsjson['sel'][isel]: 
						gPad.Update()
						gPad.Modified()
						for i in range(len(cutsjson['sel'][isel][v['root']])/2):
							plotcuts += [float(cutsjson['sel'][isel][v['root']][2*i+1])]
							vlines += [getTLine(plotcuts[-1],gPad.GetUymin(),plotcuts[-1],gPad.GetUymax(),kMagenta,5,9)]
							vlines[-1].Draw("same")
			stack.e.Draw("same")
		# draw (bottom)
		c2.cd()
		#setStyleTH1Fratio(ratioplot)
		ratioplot.Draw()
		ratioplot.GetYaxis().SetNdivisions(505)
		ratioplot.GetXaxis().SetLimits(float(v['xmin']),float(v['xmax']))
		ratioplot.GetXaxis().SetTitleOffset(4.7)
		ratioplot.Draw('e0')
		ratioplot.Draw('apsame')
		# line at cut
		if len(plotcuts)>0:
			gPad.Update()
			vlines2 = []
			for plotcut in plotcuts: 
				vlines2 += [getTLine(plotcut,gPad.GetUymin(),plotcut,gPad.GetUymax(),kMagenta,5,9)]
				vlines2[-1].Draw("same")
		# line through y=1
		gPad.Modified()
		gPad.Update()
		line = getTLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0,kBlack,2,1)
		line.Draw("same")
		c1.cd()
	else:
		canvas.cd()
		for istack,stack in enumerate([stacks[g]['effis'] for g in stacks.keys()]):
			stack.e.Draw("" if istack==0 else "same")

	# write plot to file
	legend.Draw()
	text.Draw()
	path = '%s/%s/%s/%s/%s'%('plots',os.path.split(fout.GetName())[1][:-5],wpars,'turnonCurves',namesGlobal['path-turnon'])
	makeDirs(path)
	canvas.SetName(namesGlobal['turnon'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon'])
	canvas.SetTitle(namesGlobal['turnon-title'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon-title'])
	canvas.Update()
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	canvas.SaveAs('%s/%s.pdf'%(path, canvas.GetName()))
	print
	if opts.debug: l3("%sWritten plots to: (eog %s)%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()





####################################################################################################
def mkTurnonCurves():
	# init main (including option parsing)
	opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack): sys.exit(red+"Specify either fill, draw, redraw, drawstack or redrawstack option to run. Exiting."+plain) 

	#if opts.KFWght or len(opts.weight)==4: l1("Including KFWght calculations or manual KFWght.")
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			for ref in opts.reftrig:
				KFWght = KFWghts[('-'.join(sel),'-'.join(trg))]
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
	main.dumpSamples(loadedSamples)	
		
	
	

if __name__=='__main__':
	mkTurnonCurves()
