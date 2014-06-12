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
from write_cuts import *
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
	\n./mkHist.py -D ../common/vbfHbb_defaultOpts_2012.json -v 'jetPt0,jetPt1,dEtaqq' --drawstack -w '19012.,XSEC;LUMI;PU;KFAC,1.31' -d -t 'NOMMC' --datatrigger 'NOM' -p 'ElfMuf;puId;Btag0;softHt;NOMoldPlusPhi' -o rootfiles/testPlotter.root -y -K --binning 'jetPt0;46;80;1000,jetPt1;46;80;1000'
	\n
	\nCreating a 2D map:
	\n./main.py -D vbfHbb_defaultOpts_2013.json -s 'JetMon,QCD' -t 'VBF' --datatrigger 'VBFOR' -p 'mjjMax850;HT300;dEta;jetPt1;ElfMuf' -r 'AV80' -o 'rootfiles/2DMaps_2013.root' -w '19012.,XSEC;LUMI;PU' -m 'ht;300#325#350#425#500#1000,dEtaqq3;3.5#4.25#5.4#6.0#8.0'
	\n
	\nJust print cutstrings:
	\n./main.py -D ../common/vbfHbb_defaultOpts_2013.json -w '19012.,XSEC;LUMI;PU;MAP#ht#dEtaqq[3],,../common/rootfiles/2DMaps_2013.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_smjjMax850-HT300-dEta-jetPt1-ElfMuf-tVBF-rAV80-dVBFOR_ht-dEtaqq3;1' -d -t 'VBF' --datatrigger 'VBFOR' -p 'ElfMuf;dEta;jetPt1;HT300;mjjMax850' -o rootfiles/vbfHbb_2013_2DMapCorrected_turnons.root --binning 'mjjMax;70;500;1200,mqq2;70;500;1200,mbb2;30;0;300,ht;50;0;1000,dEtaqq2;60;2;8,dEtaqq3;60;2;8,mbbReg2;30;0;300,jetPt0;40;0;400,jetPt1;30;0;300' -s 'JetMon,QCD' -r 'AV80'
	\n
	\nThe full thing: turnon curves
	\n./mkHist.py -D ../common/vbfHbb_defaultOpts_2013.json -w '14014,XSEC;LUMI;PU;KFAC;MAP#ht#dEtaqq[3],,../common/rootfiles/2DMaps_2013.root;2DMaps/JetMon-QCD/2DMap_JetMon-QCD-Rat_smjjMax850-HT300-dEta-jetPt1-ElfMuf-tVBF-rAV80-dVBFOR_ht-dEtaqq3;1' -d -t 'VBF' --datatrigger 'VBFOR' -p 'ElfMuf;dEta;jetPt1;HT300;mjjMax850;BtagLM' -o rootfiles/vbfHbb_2013_2DMapCorrected_controlplots.root --binning 'mjjMax;70;500;1200,mqq2;70;500;1200,mbb2;30;0;300,ht;50;0;1000,dEtaqq2;60;2;8,dEtaqq3;60;2;8,mbbReg2;30;0;300,jetPt0;40;0;400,jetPt1;30;0;300' --nosample 'JetMon,VBF115,VBF120,VBF130,VBF135,DataA,DataB,DataC,DataD' -v 'mqq2' --drawstack -K
	'''+plain

	mgj = OptionGroup(mp,cyan+"json settings"+plain)
	mgj.add_option('-D','--jsondefaults',help="Set jsons accoring to default file.",dest='jsondefaults',default="%s/vbfHbb_defaults.json"%(basepath),type='str',action='callback',callback=setdefaults)
	mgj.add_option('-S','--jsonsamp',help="File name for json with sample info.",dest='jsonsamp',default="%s/vbfHbb_samples.json"%(basepath),type='str')
	mgj.add_option('-V','--jsonvars',help="File name for json with variable info.",dest='jsonvars',default="%s/vbfHbb_variables.json"%(basepath),type='str')
	mgj.add_option('-C','--jsoncuts',help="File name for json with cut info.",dest='jsoncuts',default="%s/vbfHbb_cuts.json"%(basepath),type='str')
	mgj.add_option('-I','--jsoninfo',help="File name for json with general info.",dest='jsoninfo',default="%s/vbfHbb_info.json"%(basepath),type='str')
	mgj.add_option('-G','--globalpath',help="Global prefix for samples.",dest='globalpath',default="",type='str')
	mgj.add_option('-F','--fileformat',help="File format for samples (1: 2012, 2: 2013).",dest='fileformat',default=1,type='int')
	mgj.add_option('--source',help="Filepath for original flatTrees.",dest='source',default="",type='str')

	mgr = OptionGroup(mp,cyan+"root settings"+plain)
	mgr.add_option('-o','--fout',help="File name for output file.",dest='fout',default='rootfiles/vbfHbb.root',type='str')

	mgd = OptionGroup(mp,cyan+"detail settings"+plain)
	mgd.add_option('-n','--new',help="Overwrite ROOT file (fout) if it already exists.",action='store_true',default=False)
	mgd.add_option('-b','--batch',help="Set batch mode for ROOT = FALSE.",action='store_false',default=True)
	mgd.add_option('-d','--debug',help="Write extra printout statements.",action='store_true',default=False)
	mgd.add_option('-R','--reformat',help="Reformat all trees, even when present allready.",action='store_true',default=False)
	mgd.add_option('-K','--KFWght',help="Recalculate KFWght from current list of samples.",action='store_true',default=False)
	mgd.add_option('--usebool',help="Use original trees, not the char ones.",action='store_true',default=False)
	mgd.add_option('-y','--yields',help='Print yields for each sample for specified sel+trg+cuts',action='store_true',default=False)
	mgd.add_option('-l','--latex',help='Print latex output.',action='store_true',default=False)
	mgd.add_option('-m','--map',help='Create 2D map ("var1;binlim1#binlim2#...,var2;binlim1#binlim2#...").',type='str',action='callback',callback=optsplitlist)
	mgd.add_option('--numonly',help='Create 2D map numerator only.',action='store_true',default=False)
	mgd.add_option('-c','--cor',help='Create 1D map ("var1;binlim1#binlim2#...").',type='str',action='callback',callback=optsplitlist)
	mgd.add_option('--significance',help='Do significance map calculations; give: var1,var2.',type='str',action='callback',callback=optsplit)
	mgd.add_option('--redo',help='Refill if existing.',action='store_true',default=False)
	mgd.add_option('--notext',help='Don\'t draw legends.',action='store_true',default=False)

	mgst = OptionGroup(mp,cyan+"Run for subselection determined by variable, sample and/or selection/trigger"+plain)
	mgst.add_option('-v','--variable',help=purple+"Run only for these variables (comma separated)."+plain,dest='variable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--novariable',help=purple+"Don't run for these variables (comma separated)."+plain,dest='novariable',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-s','--sample',help=purple+"Run only for these samples (comma separated)."+plain,dest='sample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('--nosample',help=purple+"Don't run for these samples (comma separated)."+plain,dest='nosample',default='',type='str',action='callback',callback=optsplit)
	mgst.add_option('-t','--trigger',help=purple+"Run only for these triggers (comma and colon separated)."+plain,dest='trigger',default=[['None']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('--datatrigger',help=purple+"Run only for these triggers (comma and colon separated) (override for data sample(s))."+plain,dest='datatrigger',default=[],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-p','--selection',help=purple+"Run only for these selections (comma and colon separated)."+plain,dest='selection',default=[['None']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-r','--reftrig',help=purple+"Add reference trigger to selection."+plain,dest='reftrig',default=[['None']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('-w','--weight',help=purple+"Put this weight (\"lumi,weight1;weight2;...,manualKFWght,mapfile;mapname\")"+plain,dest='weight',default=[[''],['']],type='str',action='callback',callback=optsplitlist)
	mgst.add_option('--skip',help=purple+"Skip certain variable for selection."+plain,dest='skip',default=[],type='str',action='callback',callback=optsplit)
	mgst.add_option('--binning',help=purple+"Override default binning for certain variables",dest='binning',type='str',action='callback',callback=optsplitlist)
	mgst.add_option('--treepreselection',help=purple+"Put this selection on the trees before running (comma separated)."+plain,dest='treepreselection',default=[],type='str',action='callback',callback=optsplit)
	mgst.add_option('--preselect',help=purple+"Preselect all trees, even when present allready.",action='store_true',default=False)
	
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
		tag = 'reformatted' if opts.treepreselection == [] else 'preselected' 
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in sample['tag']) for x in opts.sample]): continue
		# veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in sample['tag']) for x in opts.nosample]): continue
		# configure
		if not opts.usebool: inroot('sample mysample%i = sample("%s/%s_%s.root","Hbb/events",variables);'%(isample,opts.globalpath,sample['fname'][:-5],tag))
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
	elif opts.preselect:
		for sample in samples.itervalues():
			sname = opts.globalpath+'/'+sample['fname'][:-5]+'_preselected.root'
			if os.path.exists(sname): os.remove(sname)
		sys.exit(red+"Preselect function was called. All preselected trees were removed. Rerun for more converting, but REMOVE the preselect flag (else you'll keep deleting the files)."+plain)

	# actually reformat/preselect trees (one at a time to avoid memory filling up) 
	for sample in samples.itervalues():
		if opts.treepreselection == []:
			sname = opts.globalpath+'/'+sample['fname'][:-5]+'_reformatted.root'
			if (not os.path.exists(sname)): 
				inroot('reformat("%s","%s",variables,%s,"%s")'%(opts.globalpath,sample['fname'],str(opts.fileformat),opts.source))
				sys.exit(red+"Sample reformat function was needed first. Rerun for actual plotting (or more converting)."+plain)
		else:
			sname = opts.globalpath+'/'+sample['fname'][:-5]+'_preselected.root'
			if (not os.path.exists(sname)): 
				cut,label = write_cuts(opts.treepreselection,[],[],[],sample=sample['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,trigequal=trigTruth(opts.usebool),varskip=opts.skip)
				inroot('preselect("%s","%s",variables,"%s","%s")'%(opts.globalpath,sample['fname'],cut,opts.source))
				sys.exit(red+"Sample preselect function was needed first. Rerun for actual plotting (or more converting)."+plain)


# PRINT SEL & TRG OPTIONS ##########################################################################
def printSelTrg(opts,KFWghts):
	from write_cuts import write_cuts
	l1("Listing cutstrings for control:")
	for s in opts.selection:
		for t in opts.trigger:
			KFWght = KFWghts[('-'.join(sorted(s)),'-'.join(t))]
			l2("Sel: %20s, Trg: %20s"%("(%s)"%s,"(%s)"%t))
			cutsel    = write_cuts(s,[],sample='Data' if opts.fileformat=='1' else 'DataA',jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool))[0]
			cutsel2   = write_cuts(s,[],sample='QCD250',jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool))[0]
			cuttrg    = write_cuts([],t,sample='QCD250',jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool))[0]
			cuttrgdat = write_cuts([],trigData(opts,"",t)[0],sample='Data' if opts.fileformat=='1' else 'DataA',jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,KFWght=KFWght,trigequal=trigTruth(opts.usebool))[0]
			l3("%s   Sel:   (e.g. Data) %s %s"%(Red,plain,cutsel))
			l3("%s   Sel: (e.g. QCD250) %s %s"%(Red,plain,cutsel2))
			l3("%s   Trg: (e.g. QCD250) %s %s"%(Purple,plain,cuttrg))
			l3("%sTrgDat:   (e.g. Data) %s %s"%(Purple,plain,cuttrgdat))
			print

# GET YIELDS #######################################################################################
def getYields(opts,loadedSamples,KFWghts):
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	l1("Extracting yields:")
	yieldarchive = {}
# selection
	for sel in opts.selection:
		l1("Running for sel: %s"%('-'.join(sorted(sel))))
# trigger
		for itrg,trg in enumerate(opts.trigger):
			l1("Running for trg: %s"%('-'.join(trg))+("" if opts.datatrigger==[] else " (data: %s)"%('-'.join(opts.datatrigger[opts.trigger.index(trg)]))))
			# KFWght
			KFWght = KFWghts[('-'.join(sorted(sel)),'-'.join(trg))]	
			# samples
			groupcounts = {}
			# category
			if 'CAT' in '-'.join(sorted(sel)): cat = re.search('(CAT[0-9]{1})','-'.join(sorted(sel))).group(1)
			else: cat='ALL'
			selmincat = ('-'.join(sorted(sel))).replace('-'+cat,'')
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

	#print allkeys

	printYieldTable(opts,yieldarchive,sorted(['Data','DataV','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'],key=lambda x:(x[0:3],len(x),x)))
	printYieldTable(opts,yieldarchive,sorted(list(set(allkeys)-set(['Data','DataV','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])),key=lambda x:(x[0:3],len(x),x)))
	
	if opts.latex: printYieldTableLatex(opts,yieldarchive,['Data','DataV','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])
	if opts.latex: printYieldTableLatex(opts,yieldarchive,sorted(list(set(allkeys)-set(['Data','DataV','QCD','ZJets','TTJets','singleT','WJets','VBF125','GluGlu-Powheg125'])),key=lambda x:(x[0:3],len(x),x)))

# HELPER FUNCTIONS #################################################################################
def printKFWghtsTable(KFWghts):
	print "%115s | %30s | %12s |"%('sel','trg','K-factor')
	tprev=""
	for s,t in sorted(KFWghts.iterkeys(),key=lambda (x,y):(y,x)):
		if not tprev==t: 
			print '-'*(3*3 + 157)
		print "%115s | %30s |"%(s,t),
		print "%12s |"%("%.6f"%KFWghts[(s,t)] if KFWghts[(s,t)] else "-")
		tprev=t
	print

def printYieldTable(opts,yieldarchive,keys):
	print "%30s | %65s | %30s | %10s | %10s | %10s | %10s | %10s | %10s |"%('sample','sel','trg','ALL','CAT0','CAT1','CAT2','CAT3','CAT4')
	tprev=""
	sprev=""
	for s,t in sorted(yieldarchive.iterkeys(),key=lambda (x,y):(y,x)):
		for sample in keys:
			#print s,t
			#print [x for x in yieldarchive[(s,t)].itervalues()]
			if not any(sample in x for x in yieldarchive[(s,t)].itervalues()): 
				#print "\033[1;31m%s not in archive.\033[m"%sample
				continue	
			if (not tprev==t) or (not sprev==s): 
				print '-'*(3*9 + 90 + 60 + 15 + 10 + 10)
			tcorr = '-'.join(opts.datatrigger[opts.trigger.index(t.split('-'))]) if any([x in sample for x in ['Data','DataV','JetMon']]) and not opts.datatrigger==[] else t
			print "%30s | %65s | %30s |"%(sample,s,tcorr),
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
def main(mp=None,parseronly=False,variables=None,samples=None):
	l1("Parsing options:")
	mp = parser(mp)
	opts,args = mp.parse_args() 


# open/create output file
	if not os.path.exists(os.path.split(opts.fout)[0]) and not os.path.split(opts.fout)[0]=='': os.makedirs(os.path.split(opts.fout)[0])
	fout = TFile(opts.fout,'recreate' if (not os.path.exists(opts.fout) or opts.new) else 'update')
	fout.cd()

	if parseronly: return opts,fout

# initialize
	# decide batch mode
	if opts.batch: gROOT.SetBatch(1)
	# suppress blabla messages (... has been created)
	ROOT.gErrorIgnoreLevel = kWarning # or 1001 
	# load C++ modules
	inroot('.L %s'%(os.path.join(basepath,'../common/sample.C+')))
	if not opts.usebool: inroot('.L %s'%(os.path.join(basepath,'../common/reformat.C+')))
	if not opts.treepreselection == []: inroot('.L %s'%(os.path.join(basepath,'../common/preselect.C+')))
	inroot('.L %s'%(os.path.join(basepath,'../common/oneDWght.C+')))
	inroot('.L %s'%(os.path.join(basepath,'../common/twoDWght.C+')))
	# load style
	inroot('.x %s'%(os.path.join(basepath,'../common/styleCMS.C+')))
	inroot('gROOT->ForceStyle();')

	
# load sample info
	if not samples==False:
		samplesfull = json.loads(filecontent(opts.jsonsamp))
		samples = samplesfull['files'] # dictionary
		# all samples from file if nothing is specified in options
		if not opts.sample: opts.sample = ','.join([y['tag'] for (x,y) in samplesfull['files'].iteritems()])
		# veto/accept according to opts.nosample and opts.sample
		for key in samples.keys():
			if any([x in samples[key]['tag'] for x in opts.nosample]): del samples[key] 
			elif not any([x in samples[key]['tag'] for x in opts.sample]): del samples[key]

# load variable info
	if not variables==False:
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
					#print x1,x2,b,v
					variables[v]['title_y'] = 'Events / %.2f'%((float(x2)-float(x1))/float(b))

	if (not samples==False and not variables==False): return opts,fout,samples,variables
	elif not samples==False: return opts,fout,samples
	elif not variables==False: return opts,fout,variables

# convert samples
	if not (opts.usebool and not opts.preselect): convertSamples(opts,samples)

# load samples
	loadedSamples = loadSamples(opts,samples)

# load oneDWght (if needed)
	if len(opts.weight)>1:
		if not opts.weight == [[''],['']] and 'COR' in [x[0:3] for x in opts.weight[1]]: 
			l1("Loaded oneDWght() and map.")
			# checks
			if not len(opts.weight)>3: sys.exit(red+"Check oneDWght weight settings. Exiting."+plain)
			if not len(opts.weight[3])>1: sys.exit(red+"Please provide filename;keyname for the oneDMap. Exiting."+plain)
			if not os.path.exists(opts.weight[3][0]): sys.exit(red+"Check oneDWght file path. Exiting."+plain)
			loadOneDWght(fout,opts.weight[3][0],opts.weight[3][1])

# load twoDWght (if needed)
	if len(opts.weight)>1:
		if not opts.weight == [[''],['']] and 'MAP' in [x[0:3] for x in opts.weight[1]]: 
			l1("Loaded twoDWght() and map.")
			# checks
			if not len(opts.weight)>3: sys.exit(red+"Check twoDWght weight settings. Exiting."+plain)
			if not len(opts.weight[3])>1: sys.exit(red+"Please provide filename;keyname for the twoDMap. Exiting."+plain)
			if not os.path.exists(opts.weight[3][0]): sys.exit(red+"Check twoDWght file path. Exiting."+plain)
			loadTwoDWght(fout,opts.weight[3][0],opts.weight[3][1])
		
# print kfwght
	KFWghts = {}
	for sel in opts.selection:
		if opts.debug: l1("Running for sel: %s"%('-'.join(sorted(sel))))
		for trg in opts.trigger:
			if opts.debug: l1("Running for trg: %s"%('-'.join(trg))+("" if opts.datatrigger==[] else " (data: %s)"%('-'.join(opts.datatrigger[opts.trigger.index(trg)]))))
			# two cases
			if opts.KFWght: KFWghts[('-'.join(sorted(sel)),'-'.join(trg))] = getKFWght(opts,loadedSamples,sel,trg) if ((not len(opts.weight)>2) or opts.weight[2][0] == '') else float(opts.weight[2][0])
			else: KFWghts[('-'.join(sorted(sel)),'-'.join(trg))] = None 
	print
	print KFWghts
	printKFWghtsTable(KFWghts)
	
# print sel & trg info
	printSelTrg(opts,KFWghts)

# print yields
	if opts.yields:
		getYields(opts,loadedSamples,KFWghts)

# 1D map creation
	if opts.cor:
		for s in opts.selection:
			for t in opts.trigger:
				for r in opts.reftrig:
					get1DMap(opts,fout,loadedSamples,variables,s,t,r,opts.cor[0])

# 2D map creation
	if opts.map:
		for s in opts.selection:
			for t in opts.trigger:
				for r in opts.reftrig:
					get2DMap(opts,fout,loadedSamples,variables,s,t,r,opts.map[0],opts.map[1])
	
# significance maps
	if opts.significance:
		for s in opts.selection:
			for t in opts.trigger:
					getSignificance(opts,fout,opts.sample,variables,s,t,opts.reftrig,opts.significance[0],opts.significance[1])

# continue to subprograms
	return opts, samples, variables, loadedSamples, fout, KFWghts


####################################################################################################
if __name__=='__main__':
	main()
