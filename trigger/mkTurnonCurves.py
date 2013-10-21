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





# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,ref,KFWght=None):
	# info
	l2("Filling for %s"%v['var'])
	# containers
	histos = {}
	cuts = {}
	cutlabels = {}
	names = {}
	canvas = TCanvas("cfill","cfill",2400,1800)
	# trg
	trg, trg_orig = trigData(opts,s,trg)
	# names
	names['global'] = getNames(opts,s,v,sel,trg_orig,ref)
	wpars = weightInfo(opts.weight,KFWght)

	# looping over different tags
	for tag in ['Num','Den']:
		# cuts
		locweight = dc(opts.weight)
		if tag=='Den' and 'MAP' in [x[:3] for x in opts.weight[1]]: locweight[1] = [x for x in opts.weight[1] if not x[:3]=='MAP']
		cuts[tag],cutlabels[tag] = write_cuts(sel,trg if tag=='Num' else ['None'],reftrig=ref,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=locweight,KFWght=KFWght,varskip=opts.skip+[v['root']],trigequal=trigTruth(opts.usebool))
		if opts.debug: l3("Cut %s: %s%s%s: %s"%(tag,blue,cutlabels[tag],plain,cuts[tag]))

		# loading/filling
		sample     = s['pointer']
		names[tag] = getNames(opts,s,v,sel,trg_orig if tag=='Num' else ['None'],ref,tag)
#		h          = fout.FindObjectAny(names[tag]['hist'])
		h = None
		if not h:
			fout.Delete(names[tag]['hist'])
			h = TH1F(names[tag]['hist'],names[tag]['hist-title'],int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
			h.Sumw2()
			inroot('%s.draw("%s","%s","%s");'%(sample,h.GetName(),v['root'],cuts[tag]))
			if opts.debug: l3("%sFilled: %40s(N=%9d, Int=%9d)%s"%(yellow,h.GetName(),h.GetEntries(),h.Integral(),plain))
#		else: 
#			if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,h.GetName(),h.GetEntries(),h.Integral(),plain))
		histos[tag] = dc(h)

		# write histogram to file			
		gDirectory.cd('%s:/'%fout.GetName())
		path = "%s/%s/%s"%('turnonCurves',wpars,names['global']['path-turnon'])
		makeDirsRoot(fout,path)
		gDirectory.cd(path)
		h.Write(h.GetName(),TH1.kOverwrite)
		gDirectory.cd('%s:/'%fout.GetName())

		# clean
		if h: h.Delete()
	
	# consider ratio
	tag = 'Rat'
	names[tag]  = getNames(opts,s,v,sel,trg_orig,ref,tag)
	histos[tag] = histos['Num'].Clone(names[tag]['hist'])
	histos[tag].SetTitle(names[tag]['hist-title'])
	histos[tag].GetYaxis().SetTitle('Trigger Efficiency (N-1 Cuts)')
	histos[tag].Divide(histos['Num'],histos['Den'],1.0,1.0,"B")

	# write histogram to file
	gDirectory.cd('%s:/'%fout.GetName())
	path = "%s/%s/%s"%('turnonCurves',wpars,names['global']['path-turnon'])
	makeDirsRoot(fout,path)
	gDirectory.cd(path)
	histos['Rat'].Write(histos['Rat'].GetName(),TH1.kOverwrite)
	gDirectory.cd('%s:/'%fout.GetName())

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
			stacks[group]['stack']    = {}
			stacks[group]['histos']   = {}
			stacks[group]['names']    = names
			stacks[group]['colours']  = jsoninfo['colours'][s['tag']]

			for tag in ['Num','Den']:
				stacks[group]['stack'][tag]  = THStack(names[tag]['stack'],names[tag]['stack-title'])
				stacks[group]['histos'][tag] = []

		# load histograms from file
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
		# fill if needed/wanted 
		for tag in ['Num','Den']:
			fullpath  = path+names[tag]['hist']+';1'
			hload     = gDirectory.Get(fullpath) 
			if (not hload) or opts.redrawstack:
				if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
				elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
				else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
				if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
				hload = gDirectory.Get(fullpath)
			if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
			stacks[group]['histos'][tag] += [dc(hload)]
			setStyleTH1F(stacks[group]['histos'][tag][-1],stacks[group]['colours'],1,stacks[group]['colours'],0,1,20)
			stacks[group]['stack'][tag].Add(stacks[group]['histos'][tag][-1])
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
				stacks[group]['stack']    = {}
				stacks[group]['histos']   = {}
				stacks[group]['names']    = names
				stacks[group]['colours']  = jsoninfo['colours'][s['tag']]
	
				for tag in ['Num','Den']:
					stacks[group]['stack'][tag]  = THStack(names[tag]['stack'],names[tag]['stack-title'])
					stacks[group]['histos'][tag] = []
	
			# load histograms from file
			gDirectory.cd('%s:/'%fout.GetName())
			path = '/%s/%s/%s/'%('turnonCurves',wpars,names['global']['path-turnon'])
			# fill if needed/wanted 
			for tag in ['Num','Den']:
				fullpath  = path+names[tag]['hist']+';1'
				hload     = gDirectory.Get(fullpath) 
				if (not hload) or opts.redrawstack:
					if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
					elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
					else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
					if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg_orig,['None'],KFWght)
					hload = gDirectory.Get(fullpath)
				if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
				stacks[group]['histos'][tag] += [dc(hload)]
				setStyleTH1F(stacks[group]['histos'][tag][-1],stacks[group]['colours'],1,stacks[group]['colours'],0,1,26)
				stacks[group]['stack'][tag].Add(stacks[group]['histos'][tag][-1])
			print
			trg = dc(trg_orig)

	istack=0
	for group,g in stacks.iteritems():
		# get ratio
		tag = 'Rat'
		g['stack'][tag] = TH1F(g['names'][tag]['turnon'],g['names'][tag]['turnon-title'],int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
		g['stack'][tag].Divide(g['stack']['Num'].GetStack().Last(),g['stack']['Den'].GetStack().Last(),1.0,1.0,'B')
		setStyleTH1F(g['stack'][tag],g['colours'],1,g['colours'],0,g['colours'],20 if not 'NoRef' in group else 26)
		print 
		ymin, ymax = getRangeTH1F(g['stack'][tag],ymin,ymax)
		setRangeTH1F(g['stack'][tag],0.0,1.2,False)
		legend.AddEntry(g['stack'][tag],group,'LP')

		# write histogram to file
		gDirectory.cd('%s:/'%fout.GetName())
		path = "%s/%s/%s"%('turnonCurves',wpars,g['names']['global']['path-turnon'])
		makeDirsRoot(fout,path)
		gDirectory.cd(path)
		g['stack'][tag].Write(g['stack'][tag].GetName(),TH1.kOverwrite)
		gDirectory.cd('%s:/'%fout.GetName())
	
	# Data / MC ratio
	if 'JetMon' in stacks.keys() and 'QCD' in stacks.keys():
		ratioplot = stacks['JetMon']['stack']['Rat'].Clone('Data / MC')
		ratioplot.SetTitle('Data / MC')
		ratioplot.Divide(stacks['JetMon']['stack']['Rat'],stacks['QCD']['stack']['Rat'])
	else: ratioplot=None

	cutsjson = json.loads(filecontent(opts.jsoncuts))
	if not ratioplot==None:
		# containers
		c1,c2 = getRatioPlotCanvas(canvas)
		# draw (top)
		c1.cd()
		plotcut = None
		for istack,stack in enumerate([stacks[g]['stack'] for g in stacks.keys()]):
			stack['Rat'].Draw("" if istack==0 else "same")
			if istack==0: 
				stack['Rat'].SetTitle(namesGlobal['turnon-title'] if len(stacks.keys())>1 else stacks[stacks.keys()[0]]['names']['global']['turnon-title'])
				for isel in sel:
					if v['root'] in cutsjson['sel'][isel]: 
						gPad.Update()
						plotcut = float(cutsjson['sel'][isel][v['root']][1])
						vline1 = getTLine(plotcut,stack['Rat'].GetMinimum(),plotcut,stack['Rat'].GetMaximum(),kMagenta,5,9)
						vline1.Draw("same")
		# draw (bottom)
		c2.cd()
		setStyleTH1Fratio(ratioplot)
		ratioplot.SetTitleOffset(5.5,'X')
		ratioplot.SetLabelOffset(0.035,'X')
		ratioplot.Draw('e0')
		ratioplot.Draw('psame')
		# line at cut
		if plotcut:
			gPad.Update()
			vline2 = getTLine(plotcut,ratioplot.GetMinimum(),plotcut,ratioplot.GetMaximum(),kMagenta,5,9)
			vline2.Draw("same")
			plotcut = None
		# line through y=1
		gPad.Update()
		line = getTLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0,kBlack,2,1)
		line.Draw("same")
		c1.cd()
	else:
		canvas.cd()
		for istack,stack in enumerate([stacks[g]['stack'] for g in stacks.keys()]):
			stack['Rat'].Draw("" if istack==0 else "same")

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
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s.{png,pdf}'%(path, canvas.GetName()),plain))
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
					for s in sorted(loadedSamples):
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
