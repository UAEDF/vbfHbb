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

	mp.add_option_group(mgtc)
	return mp





# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,reftrig,KFWght=None):
	# info
	l2("Filling for %s"%v['var'])
	# containers
	histos = {}
	cuts = {}
	canvas = TCanvas("cfill","cfill",2400,1800)
	# cut
	cuts['Num'],cutlabelnum = write_cuts(sel,trg,reftrig=reftrig,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,varskip=v['root'],trigequal=('49' if not opts.usebool else '1'))
	if opts.debug: l3("Cut numerator: %s%s%s: %s"%(blue,cutlabelnum,plain,cuts['Num']))
	cuts['Den'],cutlabelden = write_cuts(sel,reftrig=reftrig,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,varskip=v['root'],trigequal=('49' if not opts.usebool else '1'))
	if opts.debug: l3("Cut denominator: %s%s%s: %s"%(blue,cutlabelden,plain,cuts['Den']))

	for itag,icut,isel,itrg in [('Num',cuts['Num'],sel,trg),('Den',cuts['Den'],sel,['None'])]:
		# names
		sample   = s['pointer']
		selname  = 's'+'-'.join(isel)
		trgname  = 't'+'-'.join(itrg)
		refname  = 'r'+'-'.join(reftrig)
		hname    = '_'.join(['h',v['var'],s['tag'],selname,trgname,refname])
		hnamenew = 'h'+itag+hname[1:]
		if not opts.weight == [[''],['']]: weightpars = ('-'.join(sorted(opts.weight[1]))+'/').replace('KFAC','KFAC%s'%("%.2f"%KFWght if KFWght else 'def'))
		else: weightpars = 'NONE/'
		h = fout.FindObjectAny(hname)
		if h: 
			hnew = h.Clone(hnamenew)
			hnew.SetTitle(hnamenew+';%s;%s'%(v['title_x'],v['title_y']))
			if opts.debug: l3("%sCloned: %40s(N=%9d, Int=%9d)%s"%(yellow,hnew.GetName(),hnew.GetEntries(),hnew.Integral(),plain))
		else:
			fout.Delete(hnamenew)
			hnew = TH1F(hnamenew,';'.join([hnamenew,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
			hnew.Sumw2()
			inroot('%s.draw("%s","%s","%s");'%(sample,hnew.GetName(),v['root'],icut))
			if opts.debug: l3("%sFilled: %40s(N=%9d, Int=%9d)%s"%(yellow,hnew.GetName(),hnew.GetEntries(),hnew.Integral(),plain))
		histos[itag] = dc(hnew)

		# write histogram to file
		gDirectory.cd('%s:/'%fout.GetName())
		path = "%s/%s%s"%('turnonCurves',weightpars,s['tag'])
		makeDirsRoot(fout,path)
		gDirectory.cd(path)
		hnew.Write(hnew.GetName(),TH1.kOverwrite)
		gDirectory.cd('%s:/'%fout.GetName())
	
		# clean
		if h: h.Delete()
		if hnew: hnew.Delete()
	
	histos['Rat'] = histos['Num'].Clone(histos['Num'].GetName().replace('hNum','hRat'))
	histos['Rat'].SetTitle(histos['Rat'].GetName()+';%s;%s'%(v['title_x'],'Trigger Efficiency (N-1 Cuts)'))
	histos['Rat'].Divide(histos['Num'],histos['Den'],1.0,1.0,"B")
	# write histogram to file
	gDirectory.cd('%s:/'%fout.GetName())
	path = "%s/%s%s"%('turnonCurves',weightpars,s['tag'])
	makeDirsRoot(fout,path)
	gDirectory.cd(path)
	histos['Rat'].Write(histos['Rat'].GetName(),TH1.kOverwrite)
	gDirectory.cd('%s:/'%fout.GetName())

	canvas.Close()
	
def do_drawstack(opts,fout,samples,v,sel,trg,reftrg,KFWght=None):
	# names
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	refname = 'r'+'-'.join(reftrg)
	if not opts.weight == [[''],['']]: weightpars = ('-'.join(sorted(opts.weight[1]))+'/').replace('KFAC','KFAC%s'%("%.2f"%KFWght if KFWght else 'def'))
	else: weightpars = 'NONE/'
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawstack','cdrawstack',2400,1800)
	canvas.cd()

	# legend
	columns = 1 #ceil(len(samples)/4.)
	rows    = 1 #ceil(len(samples)/columns)
	left    = gPad.GetLeftMargin()+0.02
	bottom  = 1-gPad.GetTopMargin()-0.02 - (0.04*rows) # n rows sized 0.04
	right   = gPad.GetLeftMargin()+0.02 + (0.12*columns) # n columns width 0.12
	top     = 1-gPad.GetTopMargin()-0.02
	legend  = getTLegend(left,bottom,right,top,columns)

	# info text
	rows   = sum([not opts.weight==[[''],['']],sum([x in opts.weight[1] for x in ['KFAC','PU','BMAP','LUMI']])]) # counting lines about weights + 1 for vbfHbb tag 
	left   = 1-gPad.GetRightMargin()-0.02 - (0.3) # width 0.3
	right  = 1-gPad.GetRightMargin()-0.02
	top    = 1-gPad.GetTopMargin()
	bottom = 1-gPad.GetTopMargin() - (0.04*rows) # n rows size 0.04
	text = getTPave(left,bottom,right,top)
	text.AddText("VBF H #rightarrow b#bar{b}: #sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'BMAP' in opts.weight[1]: text.AddText("BMAP reweighted")
	if not opts.weight==[[''],['']] and 'PU' in opts.weight[1]: text.AddText("PU reweighted")
	# layout scaling
	ymin=0
	ymax=0

	# containers
	allstacknames = {}
	allstacks = {}
	allcolours = {}

	### LOOP over all samples
	for s in sorted(samples,key=lambda x:('QCD' in x['tag'],jsoninfo['crosssections'][x['tag']])):
		# names
		sname = s['pointer']
		group = jsoninfo['groups'][s['tag']]
		print
		l3("%sStack group: %s%s"%(blue,group,plain))

		if not group in allstacks:
			stackname = {}
			stack = {}
			stackname['Num'] = '_'.join(['turnonCurveNum',v['var'],group,selname,trgname,refname])
			stack['Num'] = THStack(stackname['Num'],"%s;%s;%s"%(stackname['Num'],v['title_x'],v['title_y']))
			stackname['Den'] = '_'.join(['turnonCurveDen',v['var'],group,selname,trgname,refname])
			stack['Den'] = THStack(stackname['Den'],"%s;%s;%s"%(stackname['Den'],v['title_x'],v['title_y']))
			histos = {'Num': [], 'Den': []}
			allcolours[group] = jsoninfo['colours'][s['tag']]

		hload = {}
		hname = {}
		hname['Num'] = '_'.join(['hNum',v['var'],s['tag'],selname,trgname,refname])
		hname['Den'] = '_'.join(['hDen',v['var'],s['tag'],selname,'tNone',refname])
		hname['Rat'] = '_'.join(['hRat',v['var'],group,selname,trgname,refname])
		allstacknames[group] = dc(hname)
		allstacks[group] = {}
		# get histograms
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s%s/'%('turnonCurves',weightpars,s['tag'])
		# fill if needed/wanted 
		for tag in ['Num','Den']:
			fullpath = path+hname[tag]+';1'
			hload[tag] = gDirectory.Get(fullpath) 
			if (not hload[tag]) or opts.redrawstack:
				hnew = TH1F(hname[tag],';'.join([hname[tag],v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
				hnew.SetTitle(';'.join([hname[tag],v['title_x'],v['title_y']]))
				print Green, opts.redraw, opts.redrawstack, tag, plain
				if not (opts.redraw or opts.redrawstack): l3("%s%s doesn\'t exist. Filling first.%s"%(red,fullpath,plain))
				elif (opts.redraw or opts.redrawstack) and tag=='Den': l3("%sLoading %s since it was redrawn with 'Num'.%s"%(red,fullpath,plain))
				else: l3("%sRedrawing %s first.%s"%(red,fullpath,plain))
				if not ((opts.redraw or opts.redrawstack) and tag=='Den'): do_fill(opts,fout,s,v,sel,trg,reftrg,KFWght)
				#print Red+"fout:"+plain
				#fout.ls()
				#print Red+"gDirectory:"+plain
				#gDirectory.ls()
				hload[tag] = gDirectory.Get(fullpath)
			if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload[tag].GetName(),hload[tag].GetEntries(),hload[tag].Integral(),plain))
			histos[tag] += [hload[tag]]
			setStyleTH1F(histos[tag][-1],jsoninfo['colours'][s['tag']],1,jsoninfo['colours'][s['tag']],0,1,20)
			stack[tag].Add(histos[tag][-1])
			#legend.AddEntry(histos[tag][-1],s['tag'],'L')
			allstacks[group][tag] = dc(stack[tag])

	istack=0
	ratio = {}
	for kstack,stack in allstacks.iteritems():
		print kstack,stack
		print stack['Num'].GetStack().Last().GetEntries()
		print stack['Den'].GetStack().Last().GetEntries()
		# get ratios
		ratio[kstack] = TH1F(allstacknames[kstack]['Rat'],';'.join([allstacknames[kstack]['Rat'],v['title_x'],'Trigger Efficiency (N-1 Cuts)']),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
		ratio[kstack].Divide(stack['Num'].GetStack().Last(),stack['Den'].GetStack().Last(),1.0,1.0,'B')
		setStyleTH1F(ratio[kstack],allcolours[kstack],1,allcolours[kstack],0,allcolours[kstack],20)
		print 
		#ymin, ymax = getRangeTH1F(ratio[kstack],ymin,ymax)
		#setRangeTH1F(ratio[kstack],ymin,ymax,False)
		setRangeTH1F(ratio[kstack],0,0.15/1.3,False)
		legend.AddEntry(ratio[kstack],kstack,'L')
		canvas.cd()
		ratio[kstack].Draw("" if istack==0 else "same")
		istack += 1

		# write histogram to file
		gDirectory.cd('%s:/'%fout.GetName())
		path = "%s/%s%s"%('turnonCurvePlots',weightpars,group)
		makeDirsRoot(fout,path)
		gDirectory.cd(path)
		ratio[kstack].Write(ratio[kstack].GetName(),TH1.kOverwrite)
		gDirectory.cd('%s:/'%fout.GetName())

	# write plot to file
	legend.Draw()
	text.Draw()
	path = '%s/%s/%s%s'%('plots',os.path.split(fout.GetName())[1][:-5],weightpars,'turnonCurves')
	makeDirs(path)
	canvas.SetName("c%s"%ratio[kstack].GetName()[4:].replace(kstack+'_',''))
	canvas.SetTitle(ratio[kstack].GetName().replace(kstack+'_',''))
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	print
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()





####################################################################################################
def mkTurnonCurves():
	# init main (including option parsing)
	opts,samples,variables,loadedSamples,fout = main.main(parser())

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack): sys.exit(red+"Specify either fill, draw, redraw, drawstack or redrawstack option to run. Exiting."+plain) 

	if opts.KFWght or len(opts.weight)==4: l1("Including KFWght calculations or manual KFWght.")
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			for reftrg in opts.reftrig:
				if opts.KFWght: KFWght = getKFWght(opts,loadedSamples,sel,trg)
				elif len(opts.weight)==4: KFWght = float(opts.weight[3][0])
				else: KFWght = None
				for v in variables.itervalues():
					if not v['var'] in opts.variable: continue
					if v['var'] in opts.novariable: continue
					for s in sorted(loadedSamples):
						if opts.fill or opts.draw or opts.redraw: 
							print
							l2("Sample: %s"%s['tag'])
						if opts.fill: do_fill(opts,fout,s,v,sel,trg,reftrg,KFWght)
					if opts.drawstack or opts.redrawstack: 
						do_drawstack(opts,fout,loadedSamples,v,sel,trg,reftrg,KFWght)
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
