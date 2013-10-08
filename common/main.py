#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from dependencyFactory import *
from optparse import OptionParser,OptionGroup
import datetime
today=datetime.date.today().strftime('%Y%m%d')

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mgj = OptionGroup(mp,cyan+"json settings"+plain)
	mgj.add_option('-D','--jsondefaults',help="Set jsons accoring to default file.",dest='jsondefaults',default="%s/vbfHbb_defaults.json"%(basepath),type='str',action='callback',callback=setdefaults)
	mgj.add_option('-S','--jsonsamp',help="File name for json with sample info.",dest='jsonsamp',default="%s/vbfHbb_samples.json"%(basepath),type='str')
	mgj.add_option('-V','--jsonvars',help="File name for json with variable info.",dest='jsonvars',default="%s/vbfHbb_variables.json"%(basepath),type='str')
	mgj.add_option('-C','--jsoncuts',help="File name for json with cut info.",dest='jsoncuts',default="%s/vbfHbb_cuts.json"%(basepath),type='str')
	mgj.add_option('-I','--jsoninfo',help="File name for json with general info.",dest='jsoninfo',default="%s/vbfHbb_info.json"%(basepath),type='str')
	mgj.add_option('-G','--globalpath',help="Global prefix for samples.",dest='globalpath',default="",type='str')
	mgj.add_option('-F','--fileformat',help="File format for samples (1: 2012, 2: 2013).",dest='fileformat',default=1,type='int')

	mgr = OptionGroup(mp,cyan+"root settings"+plain)
	mgr.add_option('-o','--fout',help="File name for output file.",dest='fout',default='rootfiles/vbfHbb.root',type='str')

	mgd = OptionGroup(mp,cyan+"detail settings"+plain)
	mgd.add_option('-n','--new',help="Overwrite ROOT file (fout) if it already exists.",action='store_true',default=False)
	mgd.add_option('-b','--batch',help="Set batch mode for ROOT = FALSE.",action='store_false',default=True)
	mgd.add_option('-d','--debug',help="Write extra printout statements.",action='store_true',default=False)
	mgd.add_option('-R','--reformat',help="Reformat all trees, even when present allready.",action='store_true',default=False)
	mgd.add_option('-K','--KFWght',help="Recalculate KFWght from current list of samples.",action='store_true',default=False)
	mgd.add_option('-B','--BMapWght',help="Recalculate BMapWght from current list of samples. Provide sel, trg and reftrig. Format: (sample) for standard map or (sample,sample) for ratiomap.",action='callback',callback=optsplit,default=[],type='str')
	mgd.add_option('--usebool',help="Use original trees, not the char ones.",action='store_true',default=False)

	mgst = OptionGroup(mp,cyan+"Run for subselection determined by variable, sample and/or selection/trigger"+plain)
	mgst.add_option('-v','--variable',help=purple+"Run only for these variables (comma separated)."+plain,dest='variable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--novariable',help=purple+"Don't run for these variables (comma separated)."+plain,dest='novariable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-s','--sample',help=purple+"Run only for these samples (comma separated)."+plain,dest='sample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--nosample',help=purple+"Don't run for these samples (comma separated)."+plain,dest='nosample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-t','--trigger',help=purple+"Run only for these triggers (comma and colon separated)."+plain,dest='trigger',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-p','--selection',help=purple+"Run only for these selections (comma and colon separated)."+plain,dest='selection',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-r','--reftrig',help=purple+"Add reference trigger to selection."+plain,dest='reftrig',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-w','--weight',help=purple+"Put this weight (\"lumi,weight1;weight2;...,bmapfilename,manualKFWght\")"+plain,dest='weight',default=[[''],['']],type='str',action='callback',callback=optsplitlist)
	
	mp.add_option_group(mgj)
	mp.add_option_group(mgr)
	mp.add_option_group(mgd)
	mp.add_option_group(mgst)
	return mp





# LOADING SAMPLES ##################################################################################
def loadSamples(opts,samples):
	l1("Loading samples:")
	samplesroot = [] 
	for isample,sample in enumerate(sorted(samples.itervalues())): 
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in sample['tag']) for x in opts.sample]): continue
		# veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in sample['tag']) for x in opts.nosample]): continue
		# configure
		if not opts.usebool: inroot('sample mysample%i = sample("%s/%s_reformatted.root","Hbb/events",variables);'%(isample,opts.globalpath,sample['fname'][:-5]))
		else: inroot('sample mysample%i = sample("%s/%s.root","Hbb/events",variables);'%(isample,opts.globalpath,sample['fname'][:-5]))
		samplesroot.append({'pointer':'mysample%i'%isample, 'fname':sample['fname'], 'tag':sample['tag'], 'colour':sample['colour']})
		l2(samplesroot[-1])
	return samplesroot

# CLEANING SAMPLES #################################################################################
def dumpSamples(samples):
	l1("Cleaning memory.")
	for sample in samples:
		inroot("%s.getf()->cd();"%sample['pointer'])
		inroot("%s.delt();"%sample['pointer'])
		inroot("%s.delf();"%sample['pointer'])

# CONVERT SAMPLES ##################################################################################
def convertSamples(opts,samples):
	l1("Converting samples:")
	# remove files if reformat called
	if opts.reformat:
		for sample in samples.itervalues():
			sname = opts.globalpath+'/'+sample['fname'][:-5]+'_reformatted.root'
			if os.path.exists(sname): os.remove(sname)
		sys.exit(red+"Reformat function was called. All reformatted trees were removed. Rerun for more converting, but REMOVE the reformat flag (else you'll keep deleting the files)."+plain)
	# actually reformat trees (one at a time to avoid memory filling up) 
	for sample in samples.itervalues():
		sname = opts.globalpath+'/'+sample['fname'][:-5]+'_reformatted.root'
		if (not os.path.exists(sname)): 
			inroot('reformat("%s/%s",variables,%s)'%(opts.globalpath,sample['fname'],str(opts.fileformat)))
			sys.exit(red+"Sample reformat function was needed first. Rerun for actual plotting (or more converting)."+plain)






# MAIN #############################################################################################
def main(mp=None):
	l1("Parsing options:")
	mp = parser(mp)
	opts,args = mp.parse_args() 

# initialize
	# decide batch mode
	if opts.batch: gROOT.SetBatch(1)
	# suppress blabla messages (... has been created)
	ROOT.gErrorIgnoreLevel = kWarning # or 1001 
	# load C++ modules
	inroot('.L %s'%(os.path.join(basepath,'../common/sample.C+')))
	if not opts.usebool: inroot('.L %s'%(os.path.join(basepath,'../common/reformat.C+')))
	inroot('.L %s'%(os.path.join(basepath,'../common/bMapWght.C+')))
	# load style
	inroot('.x %s'%(os.path.join(basepath,'../common/styleCMS.C++')))
	inroot('gROOT->ForceStyle();')


# load sample info
	samplesfull = json.loads(filecontent(opts.jsonsamp))
	samples = samplesfull['files'] # dictionary
	# all samples from file if nothing is specified in options
	if not opts.sample: opts.sample = ','.join([y['tag'] for (x,y) in samplesfull['files'].iteritems()])
	# veto/accept according to opts.nosample and opts.sample
	for key in samples.keys():
		if any([x in samples[key]['tag'] for x in opts.nosample]): del samples[key] 
		elif not any([x in samples[key]['tag'] for x in opts.sample]): del samples[key]


# load variable info
	variablesfull = json.loads(filecontent(opts.jsonvars))
	variables = variablesfull['variables'] # dictionary
	# get variables in ROOT
	inroot("vector<TString> variables; variables.clear();")
	for v in [x['bare'] for x in variables.itervalues()]: 
		for vsplit in v.strip().split(','): inroot('variables.push_back("%s");'%vsplit)
	# also add trigger results
	inroot('variables.push_back("%s");'%"triggerResult")
	# veto/accept according top opts.novariable and opts.variable
	if not opts.variable: opts.variable = ','.join([y['var'] for (x,y) in variablesfull['variables'].iteritems() if not y['var'] in opts.novariable])


# convert samples
	if not opts.usebool: convertSamples(opts,samples)

# load samples
	loadedSamples = loadSamples(opts,samples)


# open/create output file
	if not os.path.exists(os.path.split(opts.fout)[0]) and not os.path.split(opts.fout)[0]=='': os.makedirs(os.path.split(opts.fout)[0])
	fout = TFile(opts.fout,'recreate' if (not os.path.exists(opts.fout) or opts.new) else 'update')
	fout.cd()
	

# get bMapWght (if asked)
	if not opts.BMapWght == []:
		l1("Calculating bMapWghts.")
		for sel in opts.selection:
			for trg in opts.trigger:
				for reftrig in opts.reftrig:
					if len(opts.BMapWght)==1: getBMapWght(opts,fout,[s for s in loadedSamples if opts.BMapWght[0] in s['tag']],sel,trg,reftrig)
					elif len(opts.BMapWght)==2: getBMapWghtRatio(opts,fout,[s for s in loadedSamples if opts.BMapWght[0] in s['tag']],[s for s in loadedSamples if opts.BMapWght[1] in s['tag']],sel,trg,reftrig)
		sys.exit(red+"BMapWghts were calculated and written. Rerun for further calculations."+plain)

# load bMapWght (if needed)
	if not opts.weight == [[''],['']] and 'BMAP' in opts.weight[1]: 
		l1("Loaded bMapWght() and map.")
		# checks
		if not len(opts.weight)>2: sys.exit(red+"Check bMapWght weight settings. Exiting."+plain)
		if not len(opts.weight[2])>1: sys.exit(red+"Please provide filename;keyname for the BMap. Exiting."+plain)
		if not os.path.exists(opts.weight[2][0]): sys.exit(red+"Check bMapWght file path. Exiting."+plain)
		
		loadBMapWght(fout,opts.weight[2][0],opts.weight[2][1])

	
# continue to subprograms
	return opts, samples, variables, loadedSamples, fout


####################################################################################################
if __name__=='__main__':
	main()
