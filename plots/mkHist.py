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
from copy import deepcopy as dc





# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mga = OptionGroup(mp,cyan+"action settings"+plain)
	mga.add_option('--fill',help='Fill histograms and write to root file.',action='store_true',default=False)
	mga.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
	mga.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mga.add_option('--drawstack',help='Draw histograms from root file (stack samples, fill if not present).',action='store_true',default=False)
	mga.add_option('--redrawstack',help='Draw histograms from root file (stack samples, refill in all cases).',action='store_true',default=False)
	mga.add_option('--drawnormalized',help='Draw histograms from root file (stack samples, normalized).',action='store_true',default=False)
	mga.add_option('--redrawnormalized',help='Draw histograms from root file (stack samples, normalized, refill in all cases).',action='store_true',default=False)

	mp.add_option_group(mga)
	return mp





# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg,ref,KFWght=None):
	trg,trg_orig = trigData(opts,s,trg)
	# cut
	cut,cutlabel = write_cuts(sel,trg,reftrig=ref,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool))
	if opts.debug: l3("Cut: %s%s%s: %s"%(blue,cutlabel,plain,cut))

	# names
	sample = s['pointer']
	names  = getNames(opts,s,v,sel,trg_orig,ref)
	wpars  = weightInfo(opts.weight,KFWght)

	# containers
	canvas = TCanvas("cfill","cfill",1200,800)
	fout.Delete(names['hist'])
	h      = TH1F(names['hist'],names['hist-title'],int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
	h.Sumw2()
	
	# do actual filling
	inroot('%s.draw("%s","%s","%s")'%(sample,h.GetName(),v['root'],cut))
	if opts.debug: l3("%sFilled: %40s(N=%9d, Int=%9d)%s"%(yellow,h.GetName(),h.GetEntries(),h.Integral(),plain))
	
	# write histogram to file
	gDirectory.cd('%s:/'%fout.GetName())
	path = "%s/%s/%s"%('plots',wpars,names['path-hist'])
	makeDirsRoot(fout,path)
	gDirectory.cd(path)
	h.Write(h.GetName(),TH1.kOverwrite)
	gDirectory.cd('%s:/'%fout.GetName())

	# clean
	h.Delete()
	canvas.Close()
	trg = dc(trg_orig)

########################################
def do_draw(opts,fout,s,v,sel,trg,ref,KFWght=None):
	# names
	trg,trg_orig = trigData(opts,s,trg)
	names  = getNames(opts,s,v,sel,trg_orig,ref)
	wpars  = weightInfo(opts.weight,KFWght)
	
	# load
	gDirectory.cd('%s:/'%fout.GetName())
	path = '%s/%s/%s/%s;1'%('plots',wpars,names['path-hist'],names['hist'])
	hload = gDirectory.Get(path)
	# fill if needed/wanted
	if (not hload) or opts.redraw:
		l2("Sample: %s"%(names['tag']))
		print
		if not opts.redraw: l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
		else: l3("Redrawing %s%s first.%s"%(red,path,plain))
		do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
		hload = gDirectory.Get(path)
	if opts.debug: l3("%sLoaded: %30s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
	
	# containers
	canvas = TCanvas("cdraw","cdraw",1200,800)

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
	rows   = sum([not opts.weight==[[''],['']],sum([x in opts.weight[1] for x in ['KFAC','LUMI']]+[(x[0:2]=='PU' or x[0:3] in ['MAP','COR']) for x in opts.weight[1]])]) # counting lines about weights + 1 for vbfHbb tag 
	left   = 1-gPad.GetRightMargin()-0.02 - (0.3) # width 0.3
	right  = 1-gPad.GetRightMargin()-0.02
	top    = 1-gPad.GetTopMargin()
	bottom = 1-gPad.GetTopMargin() - (0.04*rows) # n rows size 0.04
	text = getTPave(left,bottom,right,top)
	text.AddText("VBF H #rightarrow b#bar{b}: #sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'PU'  in [x[0:2] for x in opts.weight[1]]: text.AddText("PU reweighted")
	if not opts.weight==[[''],['']] and 'COR' in [x[0:3] for x in opts.weight[1]]: text.AddText("1DMap reweighted")#\n (%s,%s)"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	if not opts.weight==[[''],['']] and 'MAP' in [x[0:3] for x in opts.weight[1]]: text.AddText("2DMap(%s,%s) reweighted"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	
	# selection legend
	rows = 2+sum([1 for x in sel])
	left   = 1-gPad.GetRightMargin()+0.01
	right  = 1-0.02
	top    = 1-gPad.GetTopMargin()-0.80
	bottom = 1-gPad.GetTopMargin()-0.80 - (0.03*rows) # n rows size 0.03
	selleg = getSelLegend(left,bottom,right,top)
	for iline,line in enumerate(sorted([x.strip() for x in sel])): selleg.AddText('%s %s'%('sel:' if iline==0 else ' '*4,line))
	selleg.AddText('trg: %s (MC)'%(','.join(trg)))
	selleg.AddText('     %s (data)'%(','.join(opts.datatrigger[opts.trigger.index(trg)])))
	selleg.AddText('ref: %s'%(','.join(ref)))

	text.Draw()
	selleg.Draw()

	# write
	path = "%s/%s/%s/%s"%('plots',os.path.split(fout.GetName())[1][:-5],wpars,names['path-hist'])
	makeDirs(path)
	canvas.SetName("c%s"%hload.GetName()[1:])
	canvas.SetTitle(canvas.GetName())
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	canvas.SaveAs('%s/%s.pdf'%(path, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: eog %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	# clean
	canvas.Close()
	trg = dc(trg_orig)

########################################
def do_drawstack(opts,fout,samples,v,sel,trg,ref,KFWght=None):
	# names
	namesGlobal = getNames(opts,None,v,sel,trg,ref)
	wpars = weightInfo(opts.weight,KFWght)
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawstack','cdrawstack',1200,800)
	canvas.cd()
	sigStack = THStack(namesGlobal['stack-sig'],namesGlobal['stack-sig-title'])
	datStack = THStack(namesGlobal['stack-dat'],namesGlobal['stack-dat-title'])
	bkgStack = THStack(namesGlobal['stack-bkg'],namesGlobal['stack-bkg-title'])
	sigHistos = []
	datHistos = []
	bkgHistos = []	
	totHist = None

	groups = list(set([jsoninfo['groups'][s['tag']] for s in samples]))
	groupsInLegend = []

	# legend
#	columns = ceil(len(samples)/6.)
#	rows    = ceil(len(samples)/columns)
#	left    = gPad.GetLeftMargin()+0.02
#	bottom  = 1-gPad.GetTopMargin()-0.02 - (0.03*rows) # n rows sized 0.035
#	right   = gPad.GetLeftMargin()+0.02 + (0.15*columns) # n columns width 0.12
#	top     = 1-gPad.GetTopMargin()-0.02
#	legend  = getTLegend(left,bottom,right,top,columns,None,3001,1,0.035)
	columns = 1
	rows 	= len(groups)+1+1 #(samples + header + MC uncertainty)
	left    = 1-gPad.GetRightMargin()+0.01
	right   = 1-0.02
	bottom  = 1-gPad.GetTopMargin() - 0.24 - (0.031*rows) # n rows sized 0.035
	top     = 1-gPad.GetTopMargin() - 0.24
	legend  = getTLegendRight(left,bottom,right,top,columns,"Presel. & Trigger",3001,1,0.025)

	# info text
	rows   = sum([not opts.weight==[[''],['']],sum([(x[0:2]=='PU' or x[0:3] in ['MAP','COR']) for x in opts.weight[1]])])+2 # counting lines about weights + 2 for vbfHbb tag #(LUMI,KFAC in array)
	if any([x[0:3]=='MAP' for x in opts.weight[1]]): rows += 1
	rows += 1 #LUMI
#old#	left   = 1-gPad.GetRightMargin()-0.02 - (0.3) # width 0.3
#old#	right  = 1-gPad.GetRightMargin()-0.02
#old#	top    = 1-gPad.GetTopMargin()
#old#	bottom = 1-gPad.GetTopMargin() - (0.04*rows) # n rows size 0.04
	left    = 1-gPad.GetRightMargin()+0.01
	right   = 1-0.02
	bottom  = 1-gPad.GetTopMargin() -0.0 - (0.030*rows) # n rows sized 0.035
	top     = 1-gPad.GetTopMargin() -0.0
	text = getTPave(left,bottom,right,top,None,0,0,1,0.027)
	t0 = text.AddText("CMS VBF H #rightarrow b#bar{b}:")
	t0.SetTextFont(62)
	text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000. if len(opts.weight)>0 else 0.0))
	text.AddText("#sqrt{s} = 8 TeV (2012)")
	#if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	#if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'PU'  in [x[0:2] for x in opts.weight[1]]: text.AddText("PU reweighted")
	if not opts.weight==[[''],['']] and 'COR' in [x[0:3] for x in opts.weight[1]]: text.AddText("1DMap reweighted")#\n (%s,%s)"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	if not opts.weight==[[''],['']] and 'MAP' in [x[0:3] for x in opts.weight[1]]: 
		text.AddText("2DMap reweighted") 
		text.AddText("(%s,%s)"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	# layout scaling
	ymin=0
	ymax=0

	# selection legend
	rows = 2+sum([1 for x in sel])
	left   = 1-gPad.GetRightMargin()+0.01
	right  = 1-0.02
	top    = 1-gPad.GetTopMargin()-0.58
	bottom = 1-gPad.GetTopMargin()-0.58 - (0.03*rows) # n rows size 0.03
	selleg = getSelLegend(left,bottom,right,top)
	for iline,line in enumerate(sorted([x.strip() for x in sel])): selleg.AddText('%s %s'%('sel:' if iline==0 else ' '*4,line))
	selleg.AddText('trg: %s (MC)'%(','.join(trg)))
	selleg.AddText('     %s (data)'%(','.join(opts.datatrigger[opts.trigger.index(trg)] if opts.datatrigger else trg)))

	sprev = None
	### LOOP over all samples
	for s in sorted(samples,key=lambda x:('QCD' in x['tag'],not 'WJets' in x['tag'],jsoninfo['crosssections'][x['tag']])):
		# names
		trg,trg_orig = trigData(opts,s,trg)
		names  = getNames(opts,s,v,sel,trg_orig,ref)
		# get histogram
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s/%s/%s;1'%('plots',wpars,names['path-hist'],names['hist'])
		hload = gDirectory.Get(path)
		# fill if needed/wanted 
		if (not hload) or opts.redrawstack:
			l2("Sample: %s"%(names['tag']))
			print
			if not opts.redrawstack: l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
			else: l3("Redrawing %s%s first.%s"%(red,path,plain))
			do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
			hload = gDirectory.Get(path)
		if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
		# sort
### DATA
		if names['group']=='Data' or names['group']=='DataV':
			datHistos += [hload]
			setStyleTH1F(datHistos[-1],jsoninfo['colours'][names['tag']],1,jsoninfo['colours'][names['tag']],0,1,20,0,1)
			datStack.Add(datHistos[-1])
			#legend.AddEntry(datHistos[-1],names['tag'],'P')
			if not jsoninfo['groups'][s['tag']] in [x for (x,y) in groupsInLegend]: 
				groupsInLegend += [(jsoninfo['groups'][s['tag']],datHistos[-1])]
			ymin, ymax = getRangeTH1F(datHistos[-1],ymin,ymax)
### SIGNAL
		elif names['group']=='VBF' or names['group']=='GF':
			sigHistos += [hload]
			setStyleTH1F(sigHistos[-1],jsoninfo['colours'][names['tag']],1,jsoninfo['colours'][names['tag']],0,0,0,3,0)
			sigStack.Add(sigHistos[-1])
			#legend.AddEntry(sigHistos[-1],names['tag'],'L')
			if not jsoninfo['groups'][s['tag']] in [x for (x,y) in groupsInLegend]: 
				groupsInLegend += [(jsoninfo['groups'][s['tag']],sigHistos[-1])]
			ymin, ymax = getRangeTH1F(sigHistos[-1],ymin,ymax)
### QCD
		else:
			# for MC band
			if not totHist: totHist = hload.Clone("totHist")
			else: totHist.Add(hload)
			# rest
			scurr = jsoninfo['groups'][s['tag']]
			if scurr==sprev and len(bkgHistos)>0: 
				bkgHistos[-1].Add(hload)
			else:
				bkgHistos += [hload]
				setStyleTH1F(bkgHistos[-1],1,1,jsoninfo['colours'][names['tag']],1001,0,0,1,0)
			if not scurr==sprev:
				bkgStack.Add(bkgHistos[-1])
			#legend.AddEntry(bkgHistos[-1],names['tag'],'F')
			if not jsoninfo['groups'][s['tag']] in [x for (x,y) in groupsInLegend]: 
				groupsInLegend += [(jsoninfo['groups'][s['tag']],bkgHistos[-1])]
			sprev = scurr
			ymin, ymax = getRangeTH1F(bkgHistos[-1],ymin,ymax)
		mcErrorUp = totHist.Clone("mcErrorUp")
		for i in range(mcErrorUp.GetNbinsX()): 
			mcErrorUp.SetBinContent(i,totHist.GetBinError(i)/totHist.GetBinContent(i) if not totHist.GetBinContent(i)==0 else 0.0)
			mcErrorUp.SetBinError(i,0.0)
		mcErrorUp.SetLineColor(kBlue)
		mcErrorUp.SetLineWidth(1)
		mcErrorUp.SetFillColor(kBlue)
		mcErrorUp.SetFillStyle(3003)
		mcErrorUp.SetMarkerStyle(0)
		mcErrorDown = mcErrorUp.Clone("mcErrorDown")
		mcErrorDown.Scale(-1)

		# clean
		trg = dc(trg_orig)
	
	for g,h in sorted(groupsInLegend,key=lambda (x,y):('Data' in x, 'QCD' in x, 'Z' in x, 'TT' in x, 'T' in x, 'W' in x,'VBF' in x, 'G' in x),reverse=True):
		nicetext = {"ZJets":"Z+jets","WJets":"W+jets","TTJets":"t#bar{t}","singleT":"single top"}
		gstyled = nicetext[g] if g in nicetext.keys() else g
		if 'Data' in g: legend.AddEntry(h,gstyled + ' (%.1f fb^{-1})'%(float(opts.weight[0][0])/1000.) if opts.weight[0] and opts.weight[0][0] else 0.0,'P')
		elif 'VBF' in g or 'G' in g: legend.AddEntry(h,gstyled + ' H(125) #rightarrow b#bar{b}','L')
		elif 'QCD' in g: legend.AddEntry(h,gstyled + ' (x %.2f)'%(KFWght) if KFWght else '','F')
		else: legend.AddEntry(h,gstyled,'F')
	legend.AddEntry(mcErrorUp,"MC uncertainty",'F')

### RATIO plot if Data is plotted
	if not (datHistos == [] or bkgHistos == []):
		ratio = datStack.GetStack().Last().Clone('data')
		ratio.Divide(datStack.GetStack().Last(),bkgStack.GetStack().Last())
	elif not (datHistos == [] or sigHistos == []):
		ratio = datStack.GetStack().Last().Clone('data')
		ratio.Divide(datStack.GetStack().Last(),sigStack.GetStack().Last())
	else:
		ratio = None
	### END LOOP over samples

	canvas.SetLogy(1)
	if bkgStack.GetStack(): setRangeTH1F(bkgStack,ymin,ymax)
	if sigStack.GetStack(): setRangeTH1F(sigStack,ymin,ymax)
	if datStack.GetStack(): setRangeTH1F(datStack,ymin,ymax)
	if bkgStack.GetStack(): 
		bkgStack.SetTitle('%s;%s;%s'%('','',bkgHistos[0].GetYaxis().GetTitle().replace('N /','Events /'))) #bkgStack.SetTitle(namesGlobal['hist-title'])#"stack_%s;%s;%s"%(bkgStack.GetName()[5:],bkgStack.GetStack().Last().GetXaxis().GetTitle(),bkgStack.GetStack().Last().GetYaxis().GetTitle()))

	if not ratio==None:
		# containers
		c1,c2 = getRatioPlotCanvas(canvas)
		c1.SetLogy(1)
		# draw (top)
		c1.cd()
		if not bkgHistos == []: 
			setStyleTHStack(bkgStack)
			bkgStack.Draw("hist")
		if not sigHistos == []: sigStack.Draw("nostack,hist"+(",same" if not bkgHistos == [] else ""))
		if not datHistos == []: datStack.GetStack().Last().Draw("same" if not (bkgHistos == [] and sigHistos == []) else "")
		# draw (bottom)
		c2.cd()
		ratioshifted = ratio.Clone("ratioshifted")
		for i in range(ratioshifted.GetNbinsX()): ratioshifted.SetBinContent(i,-1.0)
		ratioshifted.Add(ratio,1.0)
		setStyleTH1Fratio(ratioshifted)
		ratioshifted.Draw('e')
		gPad.Update()
		mcErrorUp.Draw("same,hist")
		mcErrorDown.Draw("same,hist")
		# line through y=1
		gPad.Update()
		line = TLine(gPad.GetUxmin(),0.0,gPad.GetUxmax(),0.0)
		line.SetLineWidth(2)
		line.SetLineColor(kBlack)
		line.Draw("same")
		c2.RedrawAxis()
		c1.cd()
	else:
		canvas.cd()
		# draw (top only)
		if not bkgHistos == []: bkgStack.Draw("hist")
		if not sigHistos == []: sigStack.Draw("nostack,hist"+(",same" if not bkgHistos == [] else ""))
		if not datHistos == []: 
			datStack.GetStack().Last().Draw("same" if not (bkgHistos == [] and sigHistos == []) else "")
	# draw legend/textinfo
	canvas.cd()
	legend.Draw()
	text.Draw()
	selleg.Draw()

#	# save
#	gDirectory.cd('%s:/'%fout.GetName())
#	path = '%s/%s/%s/%s'%('plots',wpars,'stack',namesGlobal['path-hist'])
#	makeDirsRoot(fout,path)
#	gDirectory.cd(path)
#	canvas.Write(canvas.GetName(),TH1.kOverwrite)
	
	# update
	canvas.SetName("c%s"%bkgStack.GetName()[4:])
	canvas.SetTitle(canvas.GetName())
	canvas.Update()

	# var2: strip off the path and the suffix, keep the basename
	path = '%s/../plots/%s/%s/%s/%s/%s'%(basepath,'plots',os.path.split(fout.GetName())[1][:-5],wpars,'stack',namesGlobal['path-hist'])
	makeDirs(path)

	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	canvas.SaveAs('%s/%s.pdf'%(path, canvas.GetName()))
	print
	if opts.debug: l3("%sWritten plots to: eog %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()


########################################
def do_drawnormalized(opts,fout,samples,v,sel,trg,ref,KFWght=None):
	# names
	namesGlobal = getNames(opts,None,v,sel,trg,ref)
	wpars = weightInfo(opts.weight,KFWght)
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	# containers
	canvas = TCanvas('cdrawnormalized','cdrawnormalized',1200,800)
	canvas.cd()
	sigStack = THStack(namesGlobal['stack-sig'],namesGlobal['stack-sig-title'])
	datStack = THStack(namesGlobal['stack-dat'],namesGlobal['stack-dat-title'])
	bkgStack = THStack(namesGlobal['stack-bkg'],namesGlobal['stack-bkg-title'])
	sigHistos = []
	datHistos = []
	bkgHistos = []	

	# legend
	print samples
	columns = ceil(len(samples)/4.)
	rows    = ceil(len(samples)/columns)
	left    = gPad.GetLeftMargin()+0.02
	bottom  = 1-gPad.GetTopMargin()-0.02 - (0.04*rows) # n rows sized 0.04
	right   = gPad.GetLeftMargin()+0.02 + (0.12*columns) # n columns width 0.12
	top     = 1-gPad.GetTopMargin()-0.02
	legend  = getTLegend(left,bottom,right,top,columns)

	# info text
	rows   = sum([not opts.weight==[[''],['']],sum([x in opts.weight[1] for x in ['KFAC','LUMI']]+[(x[0:2]=='PU' or x[0:3] in ['MAP','COR']) for x in opts.weight[1]])]) # counting lines about weights + 1 for vbfHbb tag 
	left   = 1-gPad.GetRightMargin()-0.02 - (0.3) # width 0.3
	right  = 1-gPad.GetRightMargin()-0.02
	top    = 1-gPad.GetTopMargin()
	bottom = 1-gPad.GetTopMargin() - (0.035*rows) # n rows size 0.035
	text = getTPave(left,bottom,right,top)
	text.AddText("VBF H #rightarrow b#bar{b}: #sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']] and 'LUMI' in opts.weight[1]: text.AddText("L = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = %s"%("%.3f"%KFWght if not KFWght==None else 'default'))
	if not opts.weight==[[''],['']] and 'PU'  in [x[0:2] for x in opts.weight[1]]: text.AddText("PU reweighted")
	if not opts.weight==[[''],['']] and 'COR' in [x[0:3] for x in opts.weight[1]]: text.AddText("1DMap reweighted")#\n (%s,%s)"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	if not opts.weight==[[''],['']] and 'MAP' in [x[0:3] for x in opts.weight[1]]: text.AddText("2DMap(%s,%s) reweighted"%([x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[1],[x for x in opts.weight[1] if x[0:3]=='MAP'][0].split('#')[2]))
	# layout scaling
	ymin=0
	ymax=0
	
	# selection legend
	rows = 2+sum([1 for x in sel])
	left   = 1-gPad.GetRightMargin()+0.01
	right  = 1-0.02
	top    = 1-gPad.GetTopMargin()-0.80
	bottom = 1-gPad.GetTopMargin()-0.80 - (0.03*rows) # n rows size 0.03
	selleg = getSelLegend(left,bottom,right,top)
	for iline,line in enumerate(sorted([x.strip() for x in sel])): selleg.AddText('%s %s'%('sel:' if iline==0 else ' '*4,line))
	selleg.AddText('trg: %s (MC)'%(','.join(trg)))
	selleg.AddText('     %s (data)'%(','.join(opts.datatrigger[opts.trigger.index(trg)])))

	### LOOP over all samples
	for s in sorted(samples,key=lambda x:('QCD' in x['tag'],not 'WJets' in x['tag'],jsoninfo['crosssections'][x['tag']])):
		# names
		trg,trg_orig = trigData(opts,s,trg)
		names = getNames(opts,s,v,sel,trg_orig,ref)
		# get histogram
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/%s/%s/%s/%s;1'%('plots',wpars,names['hist-path'],names['hist'])
		hload = gDirectory.Get(path)
		# fill if needed/wanted 
		if (not hload) or opts.redrawnormalized:
			l2("Sample: %s"%(names['tag']))
			print
			if not opts.redrawnormalized: l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
			else: l3("Redrawing %s%s first.%s"%(red,path,plain))
			do_fill(opts,fout,s,v,sel,trg_orig,ref,KFWght)
			hload = gDirectory.Get(path)
		if opts.debug: l3("%sLoaded: %40s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
		# sort
### DATA
		if names['group']=='Data' or names['group']=='DataV':
			datHistos += [hload]
			setStyleTH1F(datHistos[-1],jsoninfo['colours'][names['tag']],1,jsoninfo['colours'][names['tag']],0,1,20,0,2)
			datStack.Add(datHistos[-1])
			legend.AddEntry(datHistos[-1],names['tag'],'P')
#			ymin, ymax = getRangeTH1F(datHistos[-1],ymin,ymax)
### SIGNAL
		elif names['group']=='VBF' or names['group']=='GluGlu':
			sigHistos += [hload]
			setStyleTH1F(sigHistos[-1],jsoninfo['colours'][names['tag']],1,jsoninfo['colours'][names['tag']],0,0,0,3,0)
			sigStack.Add(sigHistos[-1])
			legend.AddEntry(sigHistos[-1],names['tag'],'L')
#			ymin, ymax = getRangeTH1F(sigHistos[-1],ymin,ymax)
### QCD
		else:
			bkgHistos += [hload]
			setStyleTH1F(bkgHistos[-1],1,1,jsoninfo['colours'][names['tag']],1,0,0,1,0)
			bkgStack.Add(bkgHistos[-1])
			legend.AddEntry(bkgHistos[-1],names['tag'],'F')
#			ymin, ymax = getRangeTH1F(bkgHistos[-1],ymin,ymax)
		# clean
		trg = dc(trg_orig)

### USE just Data stack, all others
	data = None
	histos = []
	ratios = []
	if not datHistos == []:
		data = datStack.GetStack().Last().Clone('data')
		data.Scale(1./data.Integral())
		ymin,ymax = getRangeTH1F(data,ymin,ymax)
		for ih,h in enumerate(sigHistos + bkgHistos):
			histos += [dc(h)]
			histos[-1].Scale(1./histos[-1].Integral())
			ymin,ymax = getRangeTH1F(histos[-1],ymin,ymax)
			ratios += [data.Clone('ratio%i'%ih)]
			ratios[-1].Divide(data,histos[-1])

	canvas.SetLogy(0)
	if not (data==None or histos==[] or ratios==[]):
		# containers
		c1,c2 = getRatioPlotCanvas(canvas)
		c1.SetLogy(0)
		# draw (top)
		c1.cd()
		print ymin,ymax
		setRangeTH1F(data,ymin,ymax,False)
		data.SetTitle("")
		data.Draw()
		for h in histos:
			h.Draw("histsame")
		# draw (bottom)
		c2.cd()
		for ir,r in enumerate(ratios):
			setStyleTH1Fratio(r)
			r.GetYaxis().SetNdivisions(603)
			r.SetLineWidth(2)
			r.GetYaxis().SetRangeUser(0.0,min(round(r.GetBinContent(r.GetMaximumBin())*1.2,0),5))
			if ir==0: r.Draw('hist')
			r.Draw('histsame')
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
		setRangeTH1F(data,ymin,ymax,False)
		data.Draw()
		for h in histos:
			h.Draw("same")
	# draw legend/textinfo
	legend.Draw()
	text.Draw()
	selleg.Draw()

#	# save
#	gDirectory.cd('%s:/'%fout.GetName())
#	path = '%s/%s/%s/%s'%('plots',wpars,'normalized',namesGlobal['hist-path'])
#	makeDirsRoot(fout,path)
#	gDirectory.cd(path)
	
	# var2: strip off the path and the suffix, keep the basename
	path = '%s/%s/%s/%s/%s'%('plots',os.path.split(fout.GetName())[1][:-5],wpars,'normalized',namesGlobal['hist-path'])
	makeDirs(path)

	canvas.SetName("c%s"%bkgStack.GetName()[4:])
	canvas.SetTitle(canvas.GetName())
	canvas.Update()
	canvas.SaveAs('%s/%s.png'%(path, canvas.GetName()))
	canvas.SaveAs('%s/%s.pdf'%(path, canvas.GetName()))
	print
	if opts.debug: l3("%sWritten plots to: eog %s%s"%(yellow,'%s/%s.png'%(path, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())
	canvas.Close()





# MAIN FUNCTION ####################################################################################
def mkHist():
	# init main (including option parsing)
	opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack or opts.drawnormalized or opts.redrawnormalized): sys.exit(red+"Specify either fill, draw, redraw, drawstack, redrawstack, drawnormalized or redrawnormalized option to run. Exiting."+plain) 
	
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			for ref in opts.reftrig:
				KFWght = KFWghts[('-'.join(sorted(sel)),'-'.join(trg))] 
				for v in variables.itervalues():
					if not v['var'] in opts.variable: continue
					if v['var'] in opts.novariable: continue
					l2("Var: %s"%v['var'])
					for s in sorted(loadedSamples):
						if opts.fill or opts.draw or opts.redraw: l2("Sample: %s"%(s['tag']))
						if opts.fill: do_fill(opts,fout,s,v,sel,trg,ref,KFWght)
						if opts.draw or opts.redraw: do_draw(opts,fout,s,v,sel,trg,ref,KFWght)
						if opts.fill or opts.draw or opts.redraw: print
					if opts.drawstack or opts.redrawstack: 
						do_drawstack(opts,fout,loadedSamples,v,sel,trg,ref,KFWght)
						print 
					if opts.drawnormalized or opts.redrawnormalized:
						do_drawnormalized(opts,fout,loadedSamples,v,sel,trg,ref,KFWght)
						print
					### END LOOP over samples
				### END LOOP over variables
			### END LOOP over ref triggers
		### END LOOP over selections
	### END LOOP over triggers

	# try to clean up 
	#main.dumpSamples(loadedSamples)	
	fout.Close()





####################################################################################################
if __name__=='__main__':
	mkHist()
