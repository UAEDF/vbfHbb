#!/usr/bin/env python

import sys,os,json,re
sys.path.append('../common/')

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

	mgj = OptionGroup(mp,cyan+"json settings"+plain)
	mgj.add_option('-S','--jsonsamp',help="File name for json with sample info.",dest='jsonsamp',default="vbfHbb_samples_%s.json"%today,type='str')
	mgj.add_option('-V','--jsonvars',help="File name for json with variable info.",dest='jsonvars',default="vbfHbb_variables_%s.json"%today,type='str')
	mgj.add_option('-C','--jsoncuts',help="File name for json with cut info.",dest='jsoncuts',default="vbfHbb_cuts_%s.json"%today,type='str')
	mgj.add_option('-I','--jsoninfo',help="File name for json with general info.",dest='jsoninfo',default="vbfHbb_info.json",type='str')

	mgr = OptionGroup(mp,cyan+"root settings"+plain)
	mgr.add_option('-o','--fout',help="File name for output file.",dest='fout',default='rootfiles/vbfHbb_turnonCurves_%s.root'%today,type='str')
	mgr.add_option('-b','--batch',help="Set batch mode for ROOT.",action='store_true',default=False)

	mgd = OptionGroup(mp,cyan+"detail settings"+plain)
	mgd.add_option('-d','--debug',help="Write extra printout statements.",action='store_true',default=False)

	mgst = OptionGroup(mp,cyan+"Run for subselection determined by variable, sample and/or selection/trigger"+plain)
	mgst.add_option('-v','--variable',help=purple+"Run only for these variables (comma separated)."+plain,dest='variable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-s','--sample',help=purple+"Run only for these samples (comma separated)."+plain,dest='sample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-t','--trigger',help=purple+"Run only for these triggers (comma and colon separated)."+plain,dest='trigger',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-p','--selection',help=purple+"Run only for these selections (comma and colon separated)."+plain,dest='selection',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-r','--reftrig',help=purple+"Add reference trigger to selection."+plain,action='store_true',default=False)
	
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
		inroot('sample mysample%i = sample("%s_reformatted.root","Hbb/events",%.16f,variables);'%(isample,sample['fname'][:-5],1.0/float(sample['scale'])))
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
	cut,cutlabel = write_cuts(sel,trg,sample=s['fname'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts)
	if opts.debug: l3("Cut: %s: %s"%(cutlabel,cut))

	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])

	# containers
	canvas = TCanvas("c","c",2400,1800)
	h      = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
	h.Sumw2()

	# do actual filling
	inroot('%s.draw("%s","%s","%s")'%(sample,h.GetName(),v['root'],cut))
	if opts.debug: l3("%sFilled: %30s(%9d)%s"%(yellow,h.GetName(),h.GetEntries(),plain))
	
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
	c.Close()

def do_draw(opts,fout,s,v,sel,trg):
	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	hname = '_'.join(['h',v['var'],s['tag'],selname,trgname])
	gDirectory.cd('%s:/'%fout.GetName())
	path = '/plots/%s/%s_%s/%s;1'%(s['tag'], selname, trgname, hname)
	hload = gDirectory.Get(path)
	if not hload:
		hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
		hnew.SetTitle(hname)
		l3("%s doesn\'t exist. Filling first."%(path))
		do_fill(opts,fout,s,v,sel,trg)
		hload = gDirectory.Get(path)
	if opts.debug: l3("%sLoaded: %30s(%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),plain))
	canvas = TCanvas("c","c",2400,1800)
	hload.Draw()	
	legend = TLegend(gPad.GetLeftMargin()+0.02,1-gPad.GetTopMargin()-0.04-0.02,gPad.GetLeftMargin()+0.22,1-gPad.GetTopMargin()-0.02)
	legend.SetFillStyle(0)
  	legend.SetTextColor(kBlue-2)
	legend.SetTextSize(0.025)
	legend.AddEntry(hload,s['tag'],'LP')
	legend.Draw()
	ndir = '%s/plots'%(os.path.split(fout.GetName())[1][:-5]) # strip off the path and the suffix, keep the basename
	if not os.path.exists('plots/%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname)): os.makedirs('plots/%s/%s/%s_%s'%(ndir, s['tag'], selname, trgname))
	canvas.SetName("c%s"%hload.GetName()[1:])
	canvas.SetTitle(canvas.GetName())
	canvas.SaveAs('plots/%s/%s/%s_%s/%s.png'%(ndir, s['tag'], selname, trgname, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'plots/%s/%s/%s_%s/%s.png'%(ndir, s['tag'], selname, trgname, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())

def do_drawcomplex(opts,fout,s,v,sel,trg,samples):
	# names
	sample = s['pointer']
	selname = 's'+'-'.join(sel)
	trgname = 't'+'-'.join(trg)
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))
	group = jsoninfo['groups'][s['tag']]
	htags = [k for k,val in jsoninfo['groups'].iteritems() if val==group]
	htags = [x for x in htags if x in opts.sample]
	hnames = ['_'.join(['h',v['var'],x,selname,trgname]) for x in htags]
	stackname = '_'.join(['s',v['var'],group,selname,trgname])

	canvas = TCanvas("c","c",2400,1800)
	hs = []
	hstack = THStack(stackname, "%s;%s;%s"%(stackname,v['title_x'],v['title_y']))

	for hname in hnames:
		htag = hname.split('_')[2]
		hind = map(itemgetter('tag'), samples).index(htag) 
		gDirectory.cd('%s:/'%fout.GetName())
		path = '/plots/%s/%s_%s/%s;1'%(htag, selname, trgname, hname)
		hload = gDirectory.Get(path)
		if not hload:
			hnew = TH1F(hname,';'.join([hname,v['title_x'],v['title_y']]),int(v['nbins_x']),float(v['xmin']),float(v['xmax']))
			hnew.SetTitle(hname)
			l3("%s doesn\'t exist. Filling first."%(path))
			do_fill(opts,fout,samples[hind],v,sel,trg)
			hload = gDirectory.Get(path)
		if opts.debug: l3("%sLoaded: %30s(%9d)%s"%(yellow,hload.GetName(),hload.GetEntries(),plain))
		hs += [hload]
		hs[-1].SetLineColor(int(samples[hind]['colour']))
		print hs
		hstack.Add(hs[-1])
	hstack.Draw()

	legend = TLegend(gPad.GetLeftMargin()+0.02,1-gPad.GetTopMargin()-0.04*len(hs)-0.04-0.02,gPad.GetLeftMargin()+0.22,1-gPad.GetTopMargin()-0.02)
	legend.SetFillStyle(0)
  	legend.SetTextColor(kBlue-2)
	legend.SetTextSize(0.025)
	for ih,h in enumerate(hs): legend.AddEntry(h,htags[ih]+" #rightarrow %s"%group,'LP')
	legend.Draw()
	gPad.Update()
	# change the title background to nothing
	#titlebox = gPad.GetPrimitive("title")
	#titlebox.SetFillStyle(0)
	gPad.Update()
	ndir = 'draws'
	if not gDirectory.GetDirectory('/%s'%(ndir)): gDirectory.mkdir('%s'%(ndir))
	if not gDirectory.GetDirectory('/%s/%s'%(ndir, group)): gDirectory.mkdir('%s/%s'%(ndir, group))
	if not gDirectory.GetDirectory('/%s/%s/%s_%s'%(ndir, group, selname, trgname)): gDirectory.mkdir('%s/%s/%s_%s'%(ndir, group, selname, trgname))
	gDirectory.cd('%s:/%s/%s/%s_%s'%(fout.GetName(), ndir, group, selname, trgname))
	ndir = '%s/draws/'%(os.path.split(fout.GetName())[1][:-5]) # strip off the path and the suffix, keep the basename
	if not os.path.exists('plots/%s/%s/%s_%s'%(ndir, group, selname, trgname)): os.makedirs('plots/%s/%s/%s_%s'%(ndir, group, selname, trgname))
	#gPad.SetRightMargin(0.14)
	#gPad.Update()
	canvas.SetName("c%s"%hstack.GetName()[1:])
	canvas.SetTitle(canvas.GetName())
	#canvas.Write(canvas.GetName(),TH1.kOverwrite)
	canvas.SaveAs('plots/%s/%s/%s_%s/%s.png'%(ndir, group, selname, trgname, canvas.GetName()))
	if opts.debug: l3("%sWritten plots to: %s%s"%(yellow,'plots/%s/%s/%s_%s/%s.png'%(ndir, group, selname, trgname, canvas.GetName()),plain))
	gDirectory.cd('%s:/'%fout.GetName())





# MAIN FUNCTION ####################################################################################
def main():
	# parse options
	mp = parser()
	opts,args = mp.parse_args()

	# check actions
	if not (opts.fill or opts.draw): sys.exit(red+"Specify either fill or draw option to run. Exiting."+plain) 
	
	# decide batch mode
	if opts.batch: gROOT.SetBatch(1)
	# suppress blabla messages (... has been created)
	ROOT.gErrorIgnoreLevel = kWarning # or 1001 
	
	# load C++ modules
	inroot('.L ../common/sample.C+')
	inroot('.L ../common/reformat.C+')
	# load style
	inroot('.x ../common/styleCMS.C+')
	inroot('gROOT->ForceStyle();')

	# load sample info
	samplesfull = json.loads(filecontent(opts.jsonsamp))
	samples = samplesfull['files']
	dsamples = []
	for sample in samples:
		if not any([x in sample for x in opts.sample]): dsamples += [sample]
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
	for sample in samples.itervalues():
		if not os.path.exists(sample['fname'][:-5]+'_reformatted.root'): 
			inroot('reformat("%s",variables)'%sample['fname'])
			sys.exit("Sample reformat function was needed first. Rerun for actual plotting.")

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
					if opts.draw: do_draw(opts,fout,s,v,sel,trg)
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
