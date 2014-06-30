#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

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
	mgf.add_option('--wsig',help='Signal workspace.',default="",type='str',dest='wsig')
	mgf.add_option('--xmin',help='Lower boundary',default=0.0,type='float',dest='xmin')
	mgf.add_option('--xmax',help='Upper boundary',default=0.0,type='float',dest='xmax')
	mgf.add_option('--xcen',help='Central value',default=0.0,type='float',dest='xcen')
	
	mp.add_option_group(mgf)
	return mp


# mkSigOverBkg #####################################################################################
def mkSigOverBkg(opts,samples,sel,trg):
	# cut 
	cut,cutlabel = write_cuts(sel,trg,reftrig=["None"],sample="DataA",jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
	if opts.debug: l3("Cut %s: \n\t\t\t%s%s%s: \n\t\t\t%s"%("DataA",blue,cutlabel,plain,cut))
	
	# category
	cat=''
	mbb=''
	print '-'.join(sel)
	if 'VBF' in '-'.join(sel): 
		cat=str(int(re.search('(mvaVBFC)([0-9]*)','-'.join(sel)).group(2))+3) if int(re.search('(mvaVBFC)([0-9]*)','-'.join(sel)).group(2))>0 else "-2"
		mbb='mbbReg[2]'
	elif 'NOM' in '-'.join(sel): 
		cat=str(int(re.search('(mvaNOMC)([0-9]*)','-'.join(sel)).group(2))-1)
		mbb='mbbReg[1]'
	elif 'None' == '-'.join(sel): 
		cat="ALL"
		mbb=''
	else: sys.exit(Red+"Don't know how to handle this selection: %s. Exiting"%('-'.join(sel))+plain)
	# limited categories
	if cat=='ALL' or not (int(cat)>=0 and int(cat)<7): return -99, None

	# container
	numbers = {}

	# input
	if not opts.wsig=='': 
		fin = TFile.Open(opts.wsig,"read")
		workspace = fin.Get("w")
		mean = workspace.var("mean_m125_CAT%s"%cat).getVal()
		fwhm = workspace.var("fwhm_m125_CAT%s"%cat).getVal()
		lower = mean - fwhm/2.
		upper = mean + fwhm/2.
	elif not (opts.xmin=='' or opts.xmax=='' or opts.xcen==''):
		mean = opts.xcen
		fwhm = 0
		lower = opts.xmin
		upper = opts.xmax
	else: sys.exit(Red+'Can\'t continue without boundaries. Exiting.'+plain)
	l2("Looking in [%.4f,%.4f] around %.4f"%(lower,upper,mean))
	numbers['nlower'] = lower
	numbers['nupper'] = upper
	numbers['nmean'] = mean

	# extra cut
	extracut = ["%s>=%.6f"%(mbb,lower),"%s<=%.6f"%(mbb,upper)]

	countSig = 0.0
	countBkg = 0.0

	for s in samples:
		cut,cutlabel = write_cuts(sel,trg,reftrig=["None"],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool),extra=extracut)
		if opts.debug: l3("Cut %s: \n\t\t\t%s%s%s: \n\t\t\t%s"%(s['tag'],blue,cutlabel,plain,cut))
		fsIn = TFile.Open(opts.globalpath+'/'+s['fname'].replace('flatTree','%sFlatTree'%opts.flatprefix).replace('.root','%s.root'%opts.flatsuffix) if not (opts.flatprefix=="" or opts.flatsuffix=="") else opts.globalpath+s['fname'])
		tsIn = fsIn.Get("Hbb/events")
		h = TH1F("hcount","hcount",1,0,1)
		tsIn.Draw("0.5>>hcount",cut)
		count = h.Integral()
		numbers[s['tag']] = count
		if any([x in s['tag'] for x in ['VBF','GluGlu']]): 
			countSig += count
		elif any([x in s['tag'] for x in ['Data']]): 
			countBkg += count
		else: 
			continue
		fsIn.Close()

	numbers['bkg'] = countBkg
	numbers['sig'] = countSig
	numbers['SoB'] = countSig / countBkg

	return cat,numbers

####################################################################################################
if __name__=='__main__':
	# init main (including option parsing)
	opts,fout = main.main(parser(),True)
	gROOT.SetBatch(opts.batch if opts.batch else 1)
	
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
		if not opts.sample=='' and not any([(x in s['tag']) for x in opts.sample]): continue
	   # veto regex in opts.nosample
		if not opts.nosample=='' and any([(x in s['tag']) for x in opts.nosample]): continue
		selsamples += [s]
		l2('%s: %s'%(s['tag'],s['fname']))
 	l1('Creating SigOverBkg:')

	# process	
	cat,numbers,allnumbers = -99, {}, {}
	for i in range(len(opts.selection)):
		sel = opts.selection[i]
		trg = opts.trigger[0]
		cat,numbers = mkSigOverBkg(opts,selsamples,sel,trg) 
		if not numbers==None: allnumbers[cat] = numbers
		### END LOOP over samples
	### END LOOP over tags

	print "%20s |"%"sample",
	for c in sorted(allnumbers.keys()): print "%15s |"%c,
	print
	print "%s"%("-"*(22+(18*len(allnumbers.keys()))))

	for s in sorted(allnumbers[allnumbers.keys()[0]].keys(),key=lambda x:('SoB' in x, 'bkg' in x,'sig' in x,any([y in x for y in ['nlower','nupper','nmean']]),x)):
		if s=='sig' or s=='SoB' or s=='nlower': print "%s"%("-"*(22+(18*len(allnumbers.keys()))))
		print "%20s |"%s,
		for c in sorted(allnumbers.keys()): 
			if not s=='SoB': print "%15.3f |"%allnumbers[c][s],
			else: print "%15.7f |"%allnumbers[c][s],
		print

