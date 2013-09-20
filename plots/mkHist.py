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
from operator import itemgetter
from toolkit import *
from dependencyFactory import *
from write_cuts import *
import datetime
today=datetime.date.today().strftime('%Y%m%d')





# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mga = OptionGroup(mp,cyan+"action settings"+plain)
	mga.add_option('--fill',help='Fill histograms and write to root file.',action='store_true',default=False)
	mga.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
	mga.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mga.add_option('--drawstack',help='Draw histograms from root file (stack samples, fill if not present).',action='store_true',default=False)
	mga.add_option('--redrawstack',help='Draw histograms from root file (stack samples, refill in all cases).',action='store_true',default=False)

	mp.add_option_group(mga)
	return mp





# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,KFWght=None):
	# cut
	cut,cutlabel = write_cuts(sel,trg,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght)
	if opts.debug: l3("Cut: %s%s%s: %s"%(blue,cutlabel,plain,cut))

	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
	if not opts.weight == [[''],['']]: weightpars = ('-'.join(sorted(opts.weight[1]))+'/').replace('KFAC','KFAC%s'%("%.2f"%KFWght if KFWght else 'def'))
	else: weightpars = 'NONE/'

	# containers
	canvas = TCanvas("cfill","cfill",2400,1800)
	fout.Delete(hname)
	h      = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
	h.Sumw2()
	
	# do actual filling
	inroot('%s.draw("%s","%s","%s")'%(sample,h.GetName(),v['root'],cut))
	if opts.debug: l3("%sFilled: %40s(N=%9d, Int=%9d)%s"%(yellow,h.GetName(),h.GetEntries(),h.Integral(),plain))
	
	# write histogram to file
	gDirectory.cd('%s:/'%fout.GetName())
	path = "%s/%s%s/%s_%s"%('plots',weightpars,s['tag'],selname,trgname)
	makeDirsRoot(fout,path)
	gDirectory.cd(path)
	h.Write(h.GetName(),TH1.kOverwrite)
	gDirectory.cd('%s:/'%fout.GetName())

	# clean
	h.Delete()
	canvas.Close()

########################################
def do_draw(opts,fout,s,v,sel,trg,KFWght=None):
	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
	if not opts.weight == [[''],['']]: weightpars = ('-'.join(sorted(opts.weight[1]))+'/').replace('KFAC','KFAC%s'%("%.2f"%KFWght if KFWght else 'def'))
	else: weightpars = 'NONE/'
	
	# load
	gDirectory.cd('%s:/'%fout.GetName())
	path = '%s/%s%s/%s_%s/%s;1'%('plots',weightpars,s['tag'], selname, trgname, hname)
	hload = gDirectory.Get(path)
	# fill if needed/wanted
	if (not hload) or opts.redraw:
		hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
		hnew.SetTitle(hname)
		print
		if not opts.redraw: l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
		else: l3("Redrawing %s%s first.%s"%(red,path,plain))
		do_fill(opts,fout,s,v,sel,trg,KFWght)
		hload = gDirectory.Get(path)
	if opts.debug: l3("%sLoaded: %30s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
	
	# containers
	canvas = TCanvas("cdraw","cdraw",2400,1800)

	# draw
	hload.Draw()	
	left   = gPad.GetLeftMargin()+0.02
	bottom = 1-gPad.GetTopMargin()-0.02 - (0.04) # one line sized 0.04
	right  = gPad.GetLeftMargin()+0.02 + (0.2) # width 0.2
	top    = 1-gPad.GetTopMargin()-0.02
	legend = getTLegend(left,bottom,right,top)
	legend.AddEntry(hload,s['tag'],'LP')
	legend.Draw()
	
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
	text.Draw()

	# write
	path = "%s/%s/%s%s/%s_%s"%('plots',os.path.split(fout.GetName())[1][:-5],weightpars,s['tag'],selname,trgname)
	makeDirs(path)
	canvas.SetName("c%s"%hload.GetName()[1:])
	canvas.SetTitle(canvas.GetName())
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()

########################################
def do_drawstack(opts,fout,samples,v,sel,trg,KFWght=None):
	# names
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	if not opts.weight == [[''],['']]: weightpars = ('-'.join(sorted(opts.weight[1]))+'/').replace('KFAC','KFAC%s'%("%.2f"%KFWght if KFWght else 'def'))
	else: weightpars = 'NONE/'
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawstack','cdrawstack',2400,1800)
	canvas.cd()
	sigStackname = '_'.join(['ssig',v['var'],selname,trgname])
	datStackname = '_'.join(['sdat',v['var'],selname,trgname])
	bkgStackname = '_'.join(['sbkg',v['var'],selname,trgname])
	sigStack = THStack(sigStackname,"%s;%s;%s"%(sigStackname,v['title_x'],v['title_y']))
	datStack = THStack(datStackname,"%s;%s;%s"%(datStackname,v['title_x'],v['title_y']))
	bkgStack = THStack(bkgStackname,"%s;%s;%s"%(bkgStackname,v['title_x'],v['title_y']))
	sigHistos = []
	datHistos = []
	bkgHistos = []	

	# legend
	columns = ceil(len(samples)/4.)
	rows    = ceil(len(samples)/columns)
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

	### LOOP over all samples
	for s in sorted(samples,key=lambda x:('QCD' in x['tag'],jsoninfo['crosssections'][x['tag']])):
		# names
		sname = s['pointer']
		group = jsoninfo['groups'][s['tag']]
		hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
		# get histogram
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s%s/%s_%s/%s;1'%('plots',weightpars,s['tag'], selname, trgname, hname)
		hload = gDirectory.Get(path)
		# fill if needed/wanted 
		if (not hload) or opts.redrawstack:
			hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
			hnew.SetTitle(hname)
			print
			if not opts.redraw: l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
			else: l3("Redrawing %s%s first.%s"%(red,path,plain))
			do_fill(opts,fout,s,v,sel,trg,KFWght)
			hload = gDirectory.Get(path)
		if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
		# sort
# setStyleTH1F : f(histo, lineColor, lineStyle, fillColor, fillStyle, markerColor, markerStyle)
# getRangeTH1F : ymin, ymax = f(histo, ymin, ymax)
### DATA
		if group=='Data':
			datHistos += [hload]
			setStyleTH1F(datHistos[-1],jsoninfo['colours'][s['tag']],1,jsoninfo['colours'][s['tag']],0,1,20)
			datStack.Add(datHistos[-1])
			legend.AddEntry(datHistos[-1],s['tag'],'P')
			ymin, ymax = getRangeTH1F(datHistos[-1],ymin,ymax)
### SIGNAL
		elif group=='VBF' or group=='GluGlu':
			sigHistos += [hload]
			setStyleTH1F(sigHistos[-1],jsoninfo['colours'][s['tag']],1,jsoninfo['colours'][s['tag']],0,0,0)
			sigStack.Add(sigHistos[-1])
			legend.AddEntry(sigHistos[-1],s['tag'],'L')
			ymin, ymax = getRangeTH1F(sigHistos[-1],ymin,ymax)
### QCD
		else:
			bkgHistos += [hload]
			setStyleTH1F(bkgHistos[-1],jsoninfo['colours'][s['tag']],1,jsoninfo['colours'][s['tag']],1,0,0)
			bkgStack.Add(bkgHistos[-1])
			legend.AddEntry(bkgHistos[-1],s['tag'],'F')
			ymin, ymax = getRangeTH1F(bkgHistos[-1],ymin,ymax)

### RATIO plot if Data is plotted
	if not (datHistos == [] or bkgHistos == []):
		ratio = datStack.GetStack().Last().Clone('data')
		ratio.Divide(datStack.GetStack().Last(),bkgStack.GetStack().Last())
	### END LOOP over samples

	canvas.SetLogy(1)
	setRangeTH1F(bkgStack,ymin,ymax)
	bkgStack.SetTitle("stack_%s;%s;%s"%(bkgStack.GetName()[5:],bkgStack.GetStack().Last().GetXaxis().GetTitle(),bkgStack.GetStack().Last().GetYaxis().GetTitle()))

	if ratio:
		# containers
		c1,c2 = getRatioPlotCanvas(canvas)
		c1.SetLogy()
		# draw (top)
		c1.cd()
		bkgStack.Draw("hist")
		sigStack.Draw("nostack,hist,same")
		datStack.Draw("same")
		# draw (bottom)
		c2.cd()
		setStyleTH1Fratio(ratio)
		ratio.Draw('histe0')
#		ratio.Draw('psame')
		# line through y=1
		gPad.Update()
		line = TLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0)
		line.SetLineWidth(2)
		line.SetLineColor(kBlack)
		line.Draw("same")
		c1.cd()
	else:
		canvas.cd()
		# draw (top only)
		bkgStack.Draw("hist")
		sigStack.Draw("nostack,hist,same")
		datStack.Draw("same")
	# draw legend/textinfo
	legend.Draw()
	text.Draw()

	# save
	gDirectory.cd('%s:/'%fout.GetName())
	path = '%s/%s%s/%s_%s'%('plots',weightpars,'stack',selname,trgname)
	makeDirsRoot(fout,path)
	gDirectory.cd(path)
	
	# var2: strip off the path and the suffix, keep the basename
	path = '%s/%s/%s%s/%s_%s'%('plots',os.path.split(fout.GetName())[1][:-5],weightpars,'stack',selname,trgname)
	makeDirs(path)

	canvas.SetName("c%s"%bkgStack.GetName()[4:])
	canvas.SetTitle(canvas.GetName())
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	print
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()





# MAIN FUNCTION ####################################################################################
def mkHist():
	# init main (including option parsing)
	opts,samples,variables,loadedSamples,fout = main.main(parser())

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack): sys.exit(red+"Specify either fill, draw, redraw, drawstack or redrawstack option to run. Exiting."+plain) 
	
	if opts.KFWght or len(opts.weight)==4: l1("Including KFWght calculations or manual KFWght.")
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			if opts.KFWght: KFWght = getKFWght(opts,loadedSamples,sel,trg)
			elif len(opts.weight)==4: KFWght = float(opts.weight[3][0])
			else: KFWght = None
			for v in variables.itervalues():
				if not v['var'] in opts.variable: continue
				if v['var'] in opts.novariable: continue
				for s in sorted(loadedSamples):
					if opts.fill: do_fill(opts,fout,s,v,sel,trg,KFWght)
					if opts.draw or opts.redraw: do_draw(opts,fout,s,v,sel,trg,KFWght)
					if opts.fill or opts.draw or opts.redraw: print
				if opts.drawstack or opts.redrawstack: 
					do_drawstack(opts,fout,loadedSamples,v,sel,trg,KFWght)
					print 
				### END LOOP over samples
			### END LOOP over variables
		### END LOOP over selections
	### END LOOP over triggers

	# try to clean up 
	main.dumpSamples(loadedSamples)	
	fout.Close()





####################################################################################################
if __name__=='__main__':
	mkHist()
