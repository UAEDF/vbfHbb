#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from optparse import OptionParser,OptionGroup
from operator import itemgetter
from toolkit import *
from write_cuts import *
import datetime
today=datetime.date.today().strftime('%Y%m%d')





# OPTION PARSER ####################################################################################
def parser():
	mp = OptionParser()

	mga = OptionGroup(mp,cyan+"action settings"+plain)
	mga.add_option('--fill',help='Fill histograms and write to root file.',action='store_true',default=False)
	mga.add_option('--draw',help='Draw histograms from root file (fill if not present).',action='store_true',default=False)
	mga.add_option('--redraw',help='Draw histogram from root file (refill in all cases).',action='store_true',default=False)
	mga.add_option('--drawstack',help='Draw histograms from root file (stack samples, fill if not present).',action='store_true',default=False)
	mga.add_option('--redrawstack',help='Draw histograms from root file (stack samples, refill in all cases).',action='store_true',default=False)

	mgj = OptionGroup(mp,cyan+"json settings"+plain)
	mgj.add_option('-S','--jsonsamp',help="File name for json with sample info.",dest='jsonsamp',default="%s/../common/vbfHbb_samples_%s.json"%(basepath,today),type='str')
	mgj.add_option('-V','--jsonvars',help="File name for json with variable info.",dest='jsonvars',default="%s/../common/vbfHbb_variables_%s.json"%(basepath,today),type='str')
	mgj.add_option('-C','--jsoncuts',help="File name for json with cut info.",dest='jsoncuts',default="%s/../common/vbfHbb_cuts_%s.json"%(basepath,today),type='str')
	mgj.add_option('-I','--jsoninfo',help="File name for json with general info.",dest='jsoninfo',default="vbfHbb_info.json",type='str')

	mgr = OptionGroup(mp,cyan+"root settings"+plain)
	mgr.add_option('-o','--fout',help="File name for output file.",dest='fout',default='rootfiles/vbfHbb.root',type='str')
	mgr.add_option('-b','--batch',help="Set batch mode for ROOT.",action='store_true',default=False)

	mgd = OptionGroup(mp,cyan+"detail settings"+plain)
	mgd.add_option('-d','--debug',help="Write extra printout statements.",action='store_true',default=False)
	mgd.add_option('-R','--reformat',help="Reformat all trees, even when present allready.",action='store_true',default=False)

	mgst = OptionGroup(mp,cyan+"Run for subselection determined by variable, sample and/or selection/trigger"+plain)
	mgst.add_option('-v','--variable',help=purple+"Run only for these variables (comma separated)."+plain,dest='variable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-s','--sample',help=purple+"Run only for these samples (comma separated)."+plain,dest='sample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-t','--trigger',help=purple+"Run only for these triggers (comma and colon separated)."+plain,dest='trigger',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-p','--selection',help=purple+"Run only for these selections (comma and colon separated)."+plain,dest='selection',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-r','--reftrig',help=purple+"Add reference trigger to selection."+plain,action='store_true',default=False)
	mgst.add_option('-w','--weight',help=purple+"Put this weight (\"lumi,weight1;weight2;...\")"+plain,dest='weight',default=[[''],['']],type='str',action='callback',callback=optsplitlist)
	
	mp.add_option_group(mga)
	mp.add_option_group(mgj)
	mp.add_option_group(mgr)
	mp.add_option_group(mgd)
	mp.add_option_group(mgst)
	return mp





# LOADING SAMPLES ##################################################################################
def loadSamples(opts,samples):
	samplesroot = [] 
	for isample,sample in enumerate(sorted(samples.itervalues())): 
		# follow regex in opts FOR samples
		if not opts.sample==[] and not any([(x in sample['tag']) for x in opts.sample]): continue
		inroot('sample mysample%i = sample("%s_reformatted.root","Hbb/events",variables);'%(isample,sample['fname'][:-5]))
		samplesroot.append({'pointer':'mysample%i'%isample, 'fname':sample['fname'], 'tag':sample['tag'], 'colour':sample['colour']})
		l2(samplesroot[-1])
	return samplesroot

# CLEANING SAMPLES #################################################################################
def dumpSamples(samplesroot):
	for sample in samplesroot:
		inroot("%s.getf()->cd();"%sample['pointer'])
		inroot("%s.delt();"%sample['pointer'])
		inroot("%s.delf();"%sample['pointer'])





# FUNCTIONS FOR FILLING AND DRAWING HISTOGRAMS #####################################################
def do_fill(opts,fout,s,v,sel,trg):
	# cut
	cut,cutlabel = write_cuts(sel,trg,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight)
	if opts.debug: l3("Cut: %s%s%s: %s"%(blue,cutlabel,plain,cut))

	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])

	# containers
	canvas = TCanvas("cfill","cfill",2400,1800)
	h      = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
	h.Sumw2()
	
	# bMapWght
	if not opts.weight == [[''],['']] and 'BMAP' in opts.weight[1]: 
		if not len(opts.weight)>2 or not os.path.exists(opts.weight[2][0]): sys.exit(red+"Check bMapWght file path. Exiting."+plain)
		gROOT.ProcessLineSync('TFile *fmap = TFile::Open("%s");'%opts.weight[2][0])
		gROOT.ProcessLineSync('gDirectory->cd("%s:/")'%fout.GetName())
		gROOT.ProcessLineSync('TH2F *bMap = (TH2F*)fmap->Get("bMap;1").Clone();')
		print ROOT.bMap
		gROOT.ProcessLineSync('fmap->Close();')
		print ROOT.bMap
		fout.cd()

	# do actual filling
	inroot('%s.draw("%s","%s","%s")'%(sample,h.GetName(),v['root'],cut))
	if opts.debug: l3("%sFilled: %30s(N=%9d, Int=%9d)%s"%(yellow,h.GetName(),h.GetEntries(),h.Integral(),plain))
	
	# write histogram to file
	gDirectory.cd('%s:/'%fout.GetName())
	ndir = 'plots'
	if not gDirectory.GetDirectory('/%s'%(ndir)): gDirectory.mkdir('%s'%(ndir))
	if not gDirectory.GetDirectory('/%s/%s'%(ndir, s['tag'])): gDirectory.mkdir('%s/%s'%(ndir, s['tag']))
	if not gDirectory.GetDirectory('/%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname)): gDirectory.mkdir('%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname))
	gDirectory.cd('%s:/%s/%s/%s_%s'%(fout.GetName(), ndir, s['tag'], selname, trgname))
	h.Write(h.GetName(),TH1.kOverwrite)
	gDirectory.cd('%s:/'%fout.GetName())

	h.Delete()
	canvas.Close()

def do_draw(opts,fout,s,v,sel,trg):
	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
	gDirectory.cd('%s:/'%fout.GetName())
	path = '/plots/%s/%s_%s/%s;1'%(s['tag'], selname, trgname, hname)
	hload = gDirectory.Get(path)
	if (not hload) or opts.redraw:
		hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
		hnew.SetTitle(hname)
		l3("%s%s doesn\'t exist. Filling first.%s"%(red,path,plain))
		do_fill(opts,fout,s,v,sel,trg)
		hload = gDirectory.Get(path)
	if opts.debug: l3("%sLoaded: %30s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
	canvas = TCanvas("cdraw","cdraw",2400,1800)
	hload.Draw()	
	legend = TLegend(gPad.GetLeftMargin()+0.02,1-gPad.GetTopMargin()-0.04-0.02,gPad.GetLeftMargin()+0.22,1-gPad.GetTopMargin()-0.02)
	legend.SetFillStyle(0)
  	legend.SetTextColor(kBlue-2)
	legend.SetTextSize(0.025)
	legend.AddEntry(hload,s['tag'],'LP')
	legend.Draw()
	ndir = 'plots/%s'%(os.path.split(fout.GetName())[1][:-5]) # strip off the path and the suffix, keep the basename
	if not os.path.exists('%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname)): os.makedirs('%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname))
	canvas.SetName("c%s"%hload.GetName()[1:])
	canvas.SetTitle(canvas.GetName())
	canvas.SaveAs('%s/%s/%s_%s/%s.png'%(ndir, s['tag'], selname, trgname, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s/%s_%s/%s.png'%(ndir, s['tag'], selname, trgname, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())

def do_drawstack(opts,fout,samples,v,sel,trg):
	# names
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)

	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

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
	legend = TLegend(gPad.GetLeftMargin()+0.02,1-gPad.GetTopMargin()-(0.04*ceil(len(samples)/ceil(len(samples)/4.)))-0.04-0.02,gPad.GetLeftMargin()+(0.12*ceil(len(samples)/4.))+0.02,1-gPad.GetTopMargin()-0.02)
	legend.SetFillStyle(0)
  	legend.SetTextColor(kBlue-2)
	legend.SetTextSize(0.025)
	legend.SetNColumns(int(ceil(len(samples)/4.)))
	text = TPaveText(1-gPad.GetRightMargin()-0.3,1-gPad.GetTopMargin()-(0.06*sum([x for x in [not opts.weight==[[''],['']], 'KFAC' in opts.weight[1], True] if x])),1-gPad.GetRightMargin(),1-gPad.GetTopMargin(),"NDC")
	text.SetFillColor(kWhite)
	text.SetFillStyle(0)
	text.SetBorderSize(0)
	text.SetTextSize(0.030)
	text.SetTextAlign(13)
	text.AddText("VBF H #rightarrow b#bar{b}: #sqrt{s} = 8 TeV (2012)")
	if not opts.weight==[[''],['']]: text.AddText("#sigma = %.1f fb^{-1}"%(float(opts.weight[0][0])/1000.))
	if not opts.weight==[[''],['']] and 'KFAC' in opts.weight[1]: text.AddText("k-factor = 1.3")
	if not opts.weight==[[''],['']] and 'BMAP' in opts.weight[1]: text.AddText("BMAP reweighted")
	if not opts.weight==[[''],['']] and 'PU' in opts.weight[1]: text.AddText("PU reweighted")
	ymin=0
	ymax=0

	for s in samples:
		# names
		sname = s['pointer']
		group = jsoninfo['groups'][s['tag']]
		hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
		# get histogram
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/plots/%s/%s_%s/%s;1'%(s['tag'], selname, trgname, hname)
		hload = gDirectory.Get(path)
		if (not hload) or opts.redrawstack:
			hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
			hnew.SetTitle(hname)
			l3("%s doesn\'t exist. Filling first."%(path))
			do_fill(opts,fout,s,v,sel,trg)
			hload = gDirectory.Get(path)
		if opts.debug: l3("%sLoaded: %30s(N=%9d, Int=%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),hload.Integral(),plain))
		# sort
		if group=='Data':
			datHistos += [hload]
			datHistos[-1].SetLineColor(jsoninfo['colours'][s['tag']])
			datHistos[-1].SetLineStyle(1)
			datHistos[-1].SetFillColor(jsoninfo['colours'][s['tag']])
			datHistos[-1].SetFillStyle(0)
			datHistos[-1].SetMarkerStyle(20)
			datStack.Add(datHistos[-1])
			legend.AddEntry(datHistos[-1],s['tag'],'P')
			if datHistos[-1].GetMaximum() > ymax: ymax = datHistos[-1].GetMaximum()
			if datHistos[-1].GetMinimum() < ymin: ymin = datHistos[-1].GetMinimum()
		elif group=='VBF' or group=='GluGlu':
			sigHistos += [hload]
			sigHistos[-1].SetLineColor(jsoninfo['colours'][s['tag']])
			sigHistos[-1].SetLineStyle(1)
			sigHistos[-1].SetFillColor(jsoninfo['colours'][s['tag']])
			sigHistos[-1].SetFillStyle(0)
			sigHistos[-1].SetMarkerStyle(0)
			sigStack.Add(sigHistos[-1])
			legend.AddEntry(sigHistos[-1],s['tag'],'L')
			if sigHistos[-1].GetMaximum() > ymax: ymax = sigHistos[-1].GetMaximum()
			if sigHistos[-1].GetMinimum() < ymin: ymin = sigHistos[-1].GetMinimum()
		else:
			bkgHistos += [hload]
			bkgHistos[-1].SetLineColor(jsoninfo['colours'][s['tag']])
			bkgHistos[-1].SetLineStyle(1)
			bkgHistos[-1].SetFillColor(jsoninfo['colours'][s['tag']])
			bkgHistos[-1].SetFillStyle(1)
			bkgHistos[-1].SetMarkerStyle(0)
			bkgStack.Add(bkgHistos[-1])
			legend.AddEntry(bkgHistos[-1],s['tag'],'F')
			if bkgHistos[-1].GetMaximum() > ymax: ymax = bkgHistos[-1].GetMaximum()
			if bkgHistos[-1].GetMinimum() < ymin: ymin = bkgHistos[-1].GetMinimum()

	if not (datHistos == [] or bkgHistos == []):
		ratio = datStack.GetStack().Last().Clone('data')
		#ratio.SetTitle("%s;%s;%s"%(datHistos[-1].GetTitle,datHistos[-1].GetXaxis().GetTitle(),datHistos[-1].GetYaxis().GetTitle()))
		ratio.Divide(datStack.GetStack().Last(),bkgStack.GetStack().Last())

	canvas.SetLogy(1)
	bkgStack.SetMinimum(float("1e%i"%log10(ymin+0.1)))
	bkgStack.SetMaximum(float("1e%i"%(log10(ymax)+3)))
	bkgStack.SetTitle("stack_%s;%s;%s"%(bkgStack.GetName()[5:],bkgStack.GetStack().Last().GetXaxis().GetTitle(),bkgStack.GetStack().Last().GetYaxis().GetTitle()))
	if ratio:
		c1 = TPad('c1','c1',0,0.3,1,1)
		c2 = TPad('c2','c2',0,0,1,0.3)
		c1.SetBottomMargin(0.0)
		c2.SetTopMargin(0.0)
		c2.SetBottomMargin(c2.GetBottomMargin()+0.075)
		c1.Draw()
		c2.Draw()
		canvas.Update()
		c1.cd()
		c1.SetLogy()
#		bkgStack.GetStack().Last().SetLabelSize(bkgStack.GetStack().Last().GetLabelSize()/0.7,'XYZT')
		bkgStack.Draw("hist")
		sigStack.Draw("nostack,hist,same")
		datStack.Draw("same")
		c2.cd()
		ratio.SetTitle("")
		ratio.GetYaxis().SetTitle('Data / MC')
		ratio.GetYaxis().SetRangeUser(0.0,2.0)
		ratio.SetLabelFont(42,'XYZT')
		ratio.SetLabelSize(0.070,'XYZT')
		ratio.SetTitleFont(42,'XYZT')
		ratio.SetTitleSize(0.070,'XYZT')
		ratio.SetTitleOffset(1.20,'X')
		ratio.SetTitleOffset(0.7,'Y')
		ratio.SetFillColor(kGray)
		ratio.SetFillStyle(1)
		ratio.Draw('hist')
		ratio.Draw('psame')
		gPad.Update()
		line = TLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0)
		line.SetLineWidth(2)
		line.SetLineColor(kBlack)
		line.Draw("same")
		c1.cd()
	else:
		canvas.cd()
		bkgStack.Draw("hist")
		sigStack.Draw("nostack,hist,same")
		datStack.Draw("same")

	legend.Draw()
	text.Draw()

#	gPad.Update()
#	# change the title background to nothing
#	bkgS#titlebox = gPad.GetPrimitive("title")
#	#titlebox.SetFillStyle(0)
#	gPad.Update()

	ndir = 'plots'
	if not gDirectory.GetDirectory('/%s'%(ndir)): gDirectory.mkdir('%s'%(ndir))
	if not gDirectory.GetDirectory('/%s/%s'%(ndir, 'stack')): gDirectory.mkdir('%s/%s'%(ndir, 'stack'))
	if not gDirectory.GetDirectory('/%s/%s/%s_%s'%(ndir, 'stack', selname, trgname)): gDirectory.mkdir('%s/%s/%s_%s'%(ndir, 'stack', selname, trgname))
	gDirectory.cd('%s:/%s/%s/%s_%s'%(fout.GetName(), ndir, 'stack', selname, trgname))
	
	ndir = 'plots/%s'%(os.path.split(fout.GetName())[1][:-5]) # strip off the path and the suffix, keep the basename
	if not os.path.exists('%s/%s/%s_%s'%(ndir, 'stack', selname, trgname)): os.makedirs('%s/%s/%s_%s'%(ndir, 'stack', selname, trgname))
#	#gPad.SetRightMargin(0.14)
#	#gPad.Update()
	canvas.SetName("c%s"%bkgStack.GetName()[4:])
	canvas.SetTitle(canvas.GetName())
	#canvas.Write(canvas.GetName(),TH1.kOverwrite)
	canvas.SaveAs('%s/%s/%s_%s/%s.png'%(ndir, 'stack', selname, trgname, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'%s/%s/%s_%s/%s.png'%(ndir, 'stack', selname, trgname, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())





# MAIN FUNCTION ####################################################################################
def main():
	# parse options
	mp = parser()
	opts,args = mp.parse_args()

	# check actions
	if not (opts.fill or opts.draw or opts.redraw or opts.drawstack or opts.redrawstack): sys.exit(red+"Specify either fill, draw, redraw, drawstack or redrawstack option to run. Exiting."+plain) 
	
	# decide batch mode
	if opts.batch: gROOT.SetBatch(1)
	# suppress blabla messages (... has been created)
	ROOT.gErrorIgnoreLevel = kWarning # or 1001 
	
	# load C++ modules
	inroot('.L ../common/sample.C+')
	inroot('.L ../common/reformat.C+')
	inroot('.L ../common/bMapWght.C+')
	# load style
	inroot('.x ../common/styleCMS.C+')
	inroot('gROOT->ForceStyle();')

	# load sample info
	samplesfull = json.loads(filecontent(opts.jsonsamp))
	samples = samplesfull['files']
	dsamples = []
	# all samples from file if nothing is specified in options
	if not opts.sample: opts.sample = ','.join([y['tag'] for (x,y) in samplesfull['files'].iteritems()])
	for sample in samples.itervalues():
		if not any([x in sample['tag'] for x in opts.sample]): dsamples += [sample['fname']]
	# remove some
	for dsample in dsamples:
		del samples[dsample]

	# load variable info
	variablesfull = json.loads(filecontent(opts.jsonvars))
	variables = variablesfull['variables']

	# get variables in ROOT
	inroot("vector<TString> variables; variables.clear();")
	for v in [x['bare'] for x in variables.itervalues()]: 
		for vsplit in v.strip().split(','): inroot('variables.push_back("%s");'%vsplit)
	# also add trigger results
	inroot('variables.push_back("%s");'%"triggerResult")

	# if opts.tree or charred trees inexistant: convert trees
	l1("Converting samples:")
	if opts.reformat:
		for sample in samples.itervalues():
			sname = sample['fname'][:-5]+'_reformatted.root'
			if os.path.exists(sname): os.remove(sname)
		sys.exit(red+"Reformat function was called. All reformatted trees were removed. Rerun for more converting, but REMOVE the reformat flag."+plain)
	for sample in samples.itervalues():
		sname = sample['fname'][:-5]+'_reformatted.root'
		if (not os.path.exists(sname)): 
			inroot('reformat("%s",variables)'%sample['fname'])
			sys.exit(red+"Sample reformat function was needed first. Rerun for actual plotting (or more converting)."+plain)

	# get samples in ROOT
	l1("Loading samples:")
	samplesroot = loadSamples(opts,samples) 
	
	# read/create output file
	if not os.path.exists(os.path.split(opts.fout)[0]): os.makedirs(os.path.split(opts.fout)[0])
	fout = TFile(opts.fout,'recreate' if not os.path.exists(opts.fout) else 'update')
	fout.cd()
	
	# fill histograms and save
	l1('Filling and drawing histograms:')
	for trg in opts.trigger:
		for sel in opts.selection:
			for v in variables.itervalues():
				if not v['var'] in opts.variable: continue
				for s in sorted(samplesroot):
					if opts.fill: do_fill(opts,fout,s,v,sel,trg)
					if opts.draw or opts.redraw: do_draw(opts,fout,s,v,sel,trg)
				if opts.drawstack or opts.redrawstack: do_drawstack(opts,fout,samplesroot,v,sel,trg)
				### END LOOP over samples
			### END LOOP over variables
		### END LOOP over selections
	### END LOOP over triggers

	# try to clean up 
	dumpSamples(samplesroot)
	fout.Close()





####################################################################################################
if __name__=='__main__':
	main()
