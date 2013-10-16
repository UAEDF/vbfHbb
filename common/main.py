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
	mp.usage += green+'''
	\nExtracting k-factor and yields table:
	\n./main.py -D vbfHbb_defaultOpts_2012.json --nosample 'JetMon' -t NOM -p 'ElfMuf;CAT0;MBBPart;puId,ElfMuf;CAT1;MBBPart;puId,ElfMuf;CAT2;MBBPart;puId,ElfMuf;CAT3;MBBPart;puId,ElfMuf;CAT4;MBBPart;puId' -w '19012.,XSEC;LUMI;KFAC;TRSF' -K -y -d
	\n
	\nTesting the plotter:
	\n./mkHist.py -D ../common/vbfHbb_defaultOpts_2012.json -v 'jetPt0,jetPt1,dEtaqq' --drawstack -w '19012.,XSEC;LUMI;PU;KFAC,,1.31' -d -t 'NOMMC' --datatrigger 'NOM' -p 'ElfMuf;puId;Btag0;softHt;NOMoldPlusPhi' -o rootfiles/testPlotter.root -y -K --binning 'jetPt0;46;80;1000,jetPt1;46;80;1000'
	'''+plain

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
	mgd.add_option('-y','--yields',help='Print yields for each sample for specified sel+trg+cuts',action='store_true',default=False)
	mgd.add_option('-l','--latex',help='Print latex output.',action='store_true',default=False)

	mgst = OptionGroup(mp,cyan+"Run for subselection determined by variable, sample and/or selection/trigger"+plain)
	mgst.add_option('-v','--variable',help=purple+"Run only for these variables (comma separated)."+plain,dest='variable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--novariable',help=purple+"Don't run for these variables (comma separated)."+plain,dest='novariable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-s','--sample',help=purple+"Run only for these samples (comma separated)."+plain,dest='sample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--nosample',help=purple+"Don't run for these samples (comma separated)."+plain,dest='nosample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-t','--trigger',help=purple+"Run only for these triggers (comma and colon separated)."+plain,dest='trigger',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('--datatrigger',help=purple+"Run only for these triggers (comma and colon separated) (override for data sample(s))."+plain,dest='datatrigger',default=[],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-p','--selection',help=purple+"Run only for these selections (comma and colon separated)."+plain,dest='selection',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-r','--reftrig',help=purple+"Add reference trigger to selection."+plain,dest='reftrig',default=[['NONE']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-w','--weight',help=purple+"Put this weight (\"lumi,weight1;weight2;...,bmapfilename,manualKFWght\")"+plain,dest='weight',default=[[''],['']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('--skip',help=purple+"Skip certain variable for selection."+plain,dest='skip',default=[],type='str',action='callback',callback=optsplit)
	mgst.add_option('--binning',help=purple+"Override default binning for certain variables",dest='binning',default=[[]],type='str',action='callback',callback=optsplitlist)
	
	mp.add_option_group(mgj)
	mp.add_option_group(mgr)
	mp.add_option_group(mgd)
	mp.add_option_group(mgst)
	return mp





# LOADING SAMPLES ##################################################################################
def loadSamples(opts,samples):
	l1("Loading samples:")
	samplesroot = [] 
	l2("Global path: "+opts.globalpath)
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

# GET YIELDS #######################################################################################
def getYields(opts,loadedSamples,KFWghts):
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	l1("Extracting yields:")
	yieldarchive = {}
# selection
	for sel in opts.selection:
		l1("Running for sel: %s"%('-'.join(sel)))
# trigger
		for itrg,trg in enumerate(opts.trigger):
			l1("Running for trg: %s"%('-'.join(trg))+("" if opts.datatrigger==[] else " (data: %s)"%('-'.join(opts.datatrigger[opts.trigger.index(trg)]))))
			# KFWght
			KFWght = KFWghts[('-'.join(sel),'-'.join(trg))]	
			# samples
			groupcounts = {}
			# category
			if 'CAT' in '-'.join(sel): cat = re.search('(CAT[0-9]{1})','-'.join(sel)).group(1)
			else: cat='ALL'
			selmincat = ('-'.join(sel)).replace('-'+cat,'')
			if not (selmincat,'-'.join(trg)) in yieldarchive: yieldarchive[(selmincat,'-'.join(trg))] = {}
			for k,v in {'ALL':{},'CAT0':{},'CAT1':{},'CAT2':{},'CAT3':{},'CAT4':{}}.iteritems():
				if not k in yieldarchive[(selmincat,'-'.join(trg))]: yieldarchive[(selmincat,'-'.join(trg))][k] = v		
			for sample in loadedSamples: 
				if opts.debug: l3("%sSample: %s%s"%(purple,sample['tag'],plain))
				trg,trg_orig = trigData(opts,sample,trg)
				cut,cutlabel = write_cuts(sel,trg,sample=sample['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool),varskip=opts.skip)
				if opts.debug: l3("Cut: %s%s%s: %s"%(blue,cutlabel,plain,cut))
				inroot('float nCount = %s.count("%s");'%(sample['pointer'],cut))  
				l3("Entries %s%-40s: N=%10.f %s"%(cyan,"(%s)"%sample['tag'],ROOT.nCount,plain))
				yieldarchive[(selmincat,'-'.join(trg_orig))][cat][sample['tag']] = ROOT.nCount
				if jsoninfo['groups'][sample['tag']] in groupcounts: groupcounts[jsoninfo['groups'][sample['tag']]] += ROOT.nCount
				else: groupcounts[jsoninfo['groups'][sample['tag']]] = ROOT.nCount
				trg = dc(trg_orig)
			yieldarchive[(selmincat,'-'.join(trg))][cat].update(groupcounts)

			for group,groupval in groupcounts.iteritems():
				l3("Entries %s%-40s: N=%10.f %s"%(purple,"(%s)"%group,groupval,plain))
			print

	allkeys = []
	for y in yieldarchive.itervalues():
		for tag in y:
			allkeys += [str(x) for x in y[tag].keys()]
	allkeys = list(set(allkeys))

	printYieldTable(opts,yieldarchive,['Data','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])
	printYieldTable(opts,yieldarchive,sorted(list(set(allkeys)-set(['Data','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])),key=lambda x:(x[0:3],len(x),x)))
	
	if opts.latex: printYieldTableLatex(opts,yieldarchive,['Data','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])
	if opts.latex: printYieldTableLatex(opts,yieldarchive,sorted(list(set(allkeys)-set(['Data','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])),key=lambda x:(x[0:3],len(x),x)))

# HELPER FUNCTIONS #################################################################################
def printKFWghtsTable(KFWghts):
	print "%45s | %30s | %10s |"%('sel','trg','K-factor')
	tprev=""
	for s,t in sorted(KFWghts.iterkeys(),key=lambda (x,y):(y,x)):
		if not tprev==t: 
			print '-'*(3*3 + 10 + 60 + 15)
		print "%45s | %30s |"%(s,t),
		print "%10s |"%("%.4f"%KFWghts[(s,t)] if KFWghts[(s,t)] else "-")
		tprev=t
	print

def printYieldTable(opts,yieldarchive,keys):
	print "%30s | %45s | %30s | %10s | %10s | %10s | %10s | %10s | %10s |"%('sample','sel','trg','ALL','CAT0','CAT1','CAT2','CAT3','CAT4')
	tprev=""
	sprev=""
	for s,t in sorted(yieldarchive.iterkeys(),key=lambda (x,y):(y,x)):
		for sample in keys:
			if (not tprev==t) or (not sprev==s): 
				print '-'*(3*9 + 90 + 60 + 15)
			if not any(sample in x for x in yieldarchive[(s,t)].itervalues()): break
			tcorr = '-'.join(opts.datatrigger[opts.trigger.index(t.split('-'))]) if any([x in sample for x in ['Data','DataV','JetMon']]) and not opts.datatrigger==[] else t
			print "%30s | %45s | %30s |"%(sample,s,tcorr),
			for cat in sorted(yieldarchive[(s,t)].iterkeys()):
				if yieldarchive[(s,t)][cat]=={}: print "%10s |"%("-"),
				else: print "%10s |"%("%.f"%(yieldarchive[(s,t)][cat][sample])),
			print
			tprev=t
			sprev=s
	print

def printYieldTableLatex(opts,yieldarchive,keys):
	print "\\begin{tabular}{*{9}{|c}|}\\hline"
	print "%30s & %45s & %30s & %10s & %10s & %10s & %10s & %10s & %10s \\\\"%('sample','sel','trg','ALL','CAT0','CAT1','CAT2','CAT3','CAT4'),
	tprev=""
	sprev=""
	for s,t in sorted(yieldarchive.iterkeys(),key=lambda (x,y):(y,x)):
		for sample in keys:
			if (not tprev==t) or (not sprev==s): 
				#print '-'*(4*9 + 90 + 60 + 15)
				print "\\hline"
			if not any(sample in x for x in yieldarchive[(s,t)].itervalues()): break
			tcorr = '-'.join(opts.datatrigger[opts.trigger.index(t.split('-'))]) if any([x in sample for x in ['Data','DataV','JetMon']]) and not opts.datatrigger==[] else t
			print '%30s & %45s & %30s &'%(sample,s,tcorr),
			for cat in sorted(yieldarchive[(s,t)].iterkeys()):
				if yieldarchive[(s,t)][cat]=={}: print ('%10s &'%("-") if not cat=='CAT4' else '%10s '%("-")),
				elif cat=="CAT4": print '%10s'%("%.f"%(yieldarchive[(s,t)][cat][sample])),
				else: print '%10s &'%("%.f"%(yieldarchive[(s,t)][cat][sample])),
			print "\\\\"
			tprev=t
			sprev=s
	print "\\hline\\end{tabular}"





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
	# override binning if requested
	if opts.binning: 
		for v,b,x1,x2 in opts.binning:
			if v in variables: 
				variables[v]['nbins_x'] = b
				variables[v]['xmin'] = x1
				variables[v]['xmax'] = x2


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
			for itrg,trg in enumerate(opts.trigger):
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

# print kfwght
	KFWghts = {}
	for sel in opts.selection:
		if opts.debug: l1("Running for sel: %s"%('-'.join(sel)))
		for trg in opts.trigger:
			if opts.debug: l1("Running for trg: %s"%('-'.join(trg))+("" if opts.datatrigger==[] else " (data: %s)"%('-'.join(opts.datatrigger[opts.trigger.index(trg)]))))
			# two cases
			if opts.KFWght: KFWghts[('-'.join(sel),'-'.join(trg))] = getKFWght(opts,loadedSamples,sel,trg) if (not len(opts.weight)>3) else float(opts.weight[3][0])
			else: KFWghts[('-'.join(sel),'-'.join(trg))] = None 
	print
	print KFWghts
	printKFWghtsTable(KFWghts)
	
# print yields
	if opts.yields:
		getYields(opts,loadedSamples,KFWghts)

	
# continue to subprograms
	return opts, samples, variables, loadedSamples, fout, KFWghts


####################################################################################################
if __name__=='__main__':
	main()
