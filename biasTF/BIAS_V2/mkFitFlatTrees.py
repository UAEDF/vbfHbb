#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from write_cuts import *
import main

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mgf = OptionGroup(mp,cyan+"mkFlatTree settings"+plain)
	mgf.add_option('--tag',help='Tag set with this.',default=[],type='str',action='callback',callback=optsplit)

	mp.add_option_group(mgf)
	return mp


# mkFitFlatTree ####################################################################################
def mkFitFlatTree(opts,s,sel,trg):
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	ismc = True if not 'Data' in s['tag'] else False

	# prepare
	tag = 'VBF' if 'VBF' in trg else 'NOM'
	nfin = s['fname']
	nfout = nfin.replace('flatTree','Fit').replace('.root','_sel%s.root'%tag) 
	if not os.path.exists(opts.destination): makeDirs(opts.destination)
	fin = TFile.Open(opts.globalpath+nfin,"read")
	fout = TFile.Open(opts.destination+nfout,"recreate")
	l2("Working for %s"%s['tag'])
	l3("File in : %s"%nfin)
	l3("File out: %s"%nfout)

	# process
	fin.cd()
	tin = fin.Get("Hbb/events")
	hpass = fin.Get("Hbb/TriggerPass")

	tin.SetBranchStatus("*",0)
	for b in ["mvaNOM","mvaVBF","selNOM","selVBF","dPhibb","mbbReg","mbb","nLeptons","triggerResult"]:
		tin.SetBranchStatus(b,1)
	if ismc:
		for b in ["puWt","trigWtNOM","trigWtVBF"]:
			tin.SetBranchStatus(b,1)
		 
	# cuts
	cut,cutlabel = write_cuts(sel,trg,reftrig=["None"],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
	if opts.debug: l3("Cut %s: \n\t\t\t%s%s%s: \n\t\t\t%s"%(s['tag'],blue,cutlabel,plain,cut))
#	cut = ""
#	if tag=="NOM":
#		cut ="selNOM && (triggerResult[5] || triggerResult[7]) && nLeptons==0"
#	elif tag=="VBF":
#		cut = "selVBF && triggerResult[9] && (!(selNOM && (triggerResult[0] || triggerResult[1]))) && nLeptons==0"
#	else: sys.exit(Red+"Tag type unclear: NOM/VBF. Exiting."+plain)
#	if opts.debug: l3("Cut %s: %s%s%s"%(s['tag'],blue,cut,plain))

	# process
	fout.cd()
	if hpass: hpass.Write("TriggerPass")
	makeDirsRoot(fout,"Hbb")
	gDirectory.cd("%s:/%s"%(fout.GetName(),"Hbb"))
	tout = tin.CopyTree(cut)
	l3("Events: %d"%tout.GetEntries())
	tout.Write()

	# cleaning
	fout.Close()
	fin.Close()

def mkFitFlatTrees():
	# init main (including option parsing)
	opts,fout = main.main(parser(),True)
	
	# info
	l1('Loading:')
	l2('Globalpath: %s'%opts.globalpath)
 	l1('Loading samples:')
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	allsamples = jsonsamp['files']
	selsamples = []
	for s in sorted(allsamples.itervalues(),key=lambda x: (x['tag'] if not 'QCD' in x['tag'] else x['tag'][0:3],float(x['tag'][3:]) if 'QCD' in x['tag'] else 1)):
		# require regex in opts.sample
		if not opts.sample==[] and not any([(x in s['tag']) for x in opts.sample]): continue
	   # veto regex in opts.nosample
		if not opts.nosample==[] and any([(x in s['tag']) for x in opts.nosample]): continue
		# extra vetoes
		if 'VBF1' in s['fname'] and (not any(['VBF' in trg for trg in opts.trigger])): continue
		if ('BJetPlus' in s['fname'] or 'MultiJet' in s['fname']) and any(['VBF' in trg for trg in opts.trigger]): continue
		selsamples += [s]
		l2('%s: %s'%(s['tag'],s['fname']))
 	l1('Creating FitFlatTrees:')
	
	# consistensy check
	if not len(opts.trigger)==len(opts.selection): sys.exit(Red+"\n!!! Sel and trg options need to have the same length. Exiting.\n"+plain)
	
	# process	
	for i in range(len(opts.selection)):
		sel = opts.selection[i]
		trg = opts.trigger[i]
		for s in selsamples: mkFitFlatTree(opts,s,sel,trg)
		### END LOOP over samples
	### END LOOP over tags

if __name__=='__main__':
	mkFitFlatTrees()
	
