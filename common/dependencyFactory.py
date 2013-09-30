#!/usr/bin/env python

import sys,os,json,array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

from toolkit import *
from write_cuts import *
from weightFactory import *

import main
from optparse import OptionParser,OptionGroup

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from copy import deepcopy as dc



def parser(mp=None):
	if mp==None: mp = OptionParser()
	mg1 = OptionGroup(mp,cyan+"dependencyFactory settings"+plain)
	mg1.add_option('--bmap',help='Calculate btagmap JetMon/QCD.',default=False,action='store_true')
	mg1.add_option('--kfac',help='Calculate k-factor.',default=False,action='store_true')
	mp.add_option_group(mg1)
	return mp


def getKFWght(opts,loadedSamples,sel,trg):	
	inroot('float nDat=0.0, nQCD=0.0, nBkg=0.0;')
	inroot('TH1F *hDat = new TH1F("hDat","hDat",1,0,1);')
	inroot('TH1F *hQCD = new TH1F("hQCD","hQCD",1,0,1);')
	inroot('TH1F *hBkg = new TH1F("hBkg","hBkg",1,0,1);')
	### LOOP over samples
	for s in loadedSamples:
		### Skip some
		if any([x in s['tag'] for x in ['JetMon','VBF','GluGlu']]): continue
		### Clean some
		if opts.debug and 'KFAC' in opts.weight[1]: l3("Option specified k-factor ignored in k-factor calculation.")
		opts.weightlocal = dc(opts.weight)
		opts.weightlocal[1] = list(set(opts.weight[1])-set(['KFAC']))
		### Get cut and weight
		cut = write_cuts(sel,trg,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weightlocal,trigequal=('49' if not opts.usebool else '1'))[0]
#		wf = weightFactory(opts.jsonsamp,opts.weight[0][0] if not opts.weight[0][0]=='' else '19000')
#		weight = wf.getFormula(','.join(['XSEC','LUMI']),s['tag']) 
	#	print cut
	#	print cyan, s['tag'], 'added to:',
		### Data
		if 'Data' in s['tag']:
#			inroot('nDat += (%s.count("%s"))*(%s);'%(s['pointer'],cut,weight))
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hDat.GetName(),"0.5",cut))
	#		print 'Data'
		### QCD 
		elif 'QCD' in s['tag']:
#			inroot('nQCD += (%s.count("%s"))*(%s);'%(s['pointer'],cut,weight))
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hQCD.GetName(),"0.5",cut))
	#		print 'QCD'
		### Bkg
		else:
#			inroot('nBkg += (%s.count("%s"))*(%s);'%(s['pointer'],cut,weight))
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hBkg.GetName(),"0.5",cut))
	#		print 'Bkg'
	#	print plain
	#	print "Data: %8.2f  | Bkg: %8.2f  | QCD: %8.2f"%(ROOT.hDat.Integral(),ROOT.hBkg.Integral(),ROOT.hQCD.Integral())
	### finish
	#KFWght = (ROOT.nDat-ROOT.nBkg)/ROOT.nQCD
	KFWght = (ROOT.hDat.Integral()-ROOT.hBkg.Integral())/ROOT.hQCD.Integral()
	l2("KFWght calculated at: %f"%KFWght)
	return KFWght

def getBMapWght(opts,fout,samples,sel,trg,reftrig):
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	group = jsoninfo['groups'][samples[0]['tag']]
	l3("Map for %s"%group)
	# store
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,'bMapWghts/%s/'%group)
	# calculate
	xvals = array.array('f',[0.0,0.244,0.679,0.898,1.001])
	maps = {}
	cuts = {}
	inroot('TTree *t = 0;')
	for itag,tag in enumerate(['Num','Den','Rat']):
		maps[tag] = TH2F("bMapWght%s%s"%(group,tag),"bMapWght%s%s;CSV_{0};CSV_{1}"%(group,tag),4,xvals,4,xvals)
		maps[tag].Sumw2()
		for s in samples:
			if not tag=='Rat': 
				inroot('t = (TTree*)%s.gett();'%s['pointer'])
				cuts['Num'] = write_cuts(sel,trg,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=reftrig,trigequal=('49' if not opts.usebool else '1'))[0]
				cuts['Den'] = write_cuts(sel,['NONE'],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=reftrig,trigequal=('49' if not opts.usebool else '1'))[0]
				wf = weightFactory(opts.jsonsamp,opts.weight[0][0] if not opts.weight[0][0]=='' else '19000')
				weight = wf.getFormula(','.join(opts.weight[1] if not opts.weight[1]==[''] else ['XSEC','LUMI']),s['tag']) 
				inroot('t->Draw("jetBtag[btagIdx[1]]:jetBtag[btagIdx[0]]>>+%s",TCut("%s*%s"));'%(maps[tag].GetName(),cuts[tag],weight))
		if tag=='Rat': maps['Rat'].Divide(maps['Num'],maps['Den'],1.0,1.0,"B")
	# save
	gDirectory.cd('%s:/bMapWghts/%s/'%(fout.GetName(),group))
	maps['Rat'].SetName("bMapWght_%s_s%s_t%s_r%s"%(group,sel[0],trg[0],reftrig[0]))
	maps['Rat'].SetTitle("bMapWght_%s_s%s_t%s_r%s;CSV_{0};CSV_{1}"%(group,sel[0],trg[0],reftrig[0]))
	maps['Rat'].Write(maps['Rat'].GetName(),TH1.kOverwrite)
	# return
	return maps['Rat']

def getBMapWghtRatio(opts,fout,samplesnum,samplesden,sel,trg,reftrig):
	# info
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	gnum = jsoninfo['groups'][samplesnum[0]['tag']]
	gden = jsoninfo['groups'][samplesden[0]['tag']]
	l2("Ratio map for %s / %s"%(gnum,gden))
	# store
	gDirectory.cd("%s:/"%fout.GetName())
	makeDirsRoot(fout,'bMapWghtRatios/%s_%s/'%(gnum,gden))	
	# calculate
	maps = {}
	maps['Num'] = getBMapWght(opts,fout,samplesnum,sel,trg,reftrig)
	maps['Den'] = getBMapWght(opts,fout,samplesden,sel,trg,reftrig)
	maps['Rat'] = maps['Num'].Clone("bMapWghtRatio_%s_%s_s%s_t%s_r%s"%(gnum,gden,sel[0],trg[0],reftrig[0]))
	maps['Rat'].Divide(maps['Num'],maps['Den'],1.0,1.0,"B")
	maps['Rat'].SetTitle("bMapWghtRatio_%s_%s;CSV_{0};CSV_{1}"%(gnum,gden))
	# save
	gDirectory.cd('%s:/bMapWghtRatios/%s_%s/'%(fout.GetName(),gnum,gden))
	maps['Rat'].Write(maps['Rat'].GetName(),TH1.kOverwrite)

def loadBMapWght(fout,mapfile,mapname):
	# clean
	try:
		ROOT.bmap.Delete()
	except:
		pass
	# correct file
	if not fout.GetName()==mapfile: inroot('TFile *fmap = TFile::Open("%s");'%mapfile)
	inroot('gDirectory->cd("%s:/");'%fout.GetName())
	# load & clone
	if not fout.GetName()==mapfile: inroot('TH2F *bMap = (TH2F*)fmap->Get("%s;1").Clone();'%mapname)
	else: inroot('TH2F *bMap = (TH2F*)gDirectory->Get("%s;1").Clone();'%mapname)
	# close if unneeded
	if not fout.GetName()==mapfile: inroot('fmap->Close();')
	# check
	if not ROOT.bMap: sys.exit('bMap histogram not loaded correctly. Check: %s. Exiting.'%ROOT.bMap)



########################################
def examples():
	# init main
	opts,samples,variables,loadedSamples,fout = main.main(parser())

	if opts.kfac:
		# KFWght	
		l1("Calculating KFWght:")
		KFWght = getKFWght(opts,loadedSamples,opts.selection[0],opts.trigger[0])

	if opts.bmap:
		# BMapWght
		l1("Calculating BMapWght:")
		getBMapWghtRatio(opts,fout,[s for s in loadedSamples if 'JetMon' in s['tag']],[s for s in loadedSamples if 'QCD' in s['tag']],opts.selection[0],opts.trigger[0],opts.reftrig[0])

	main.dumpSamples(loadedSamples)

########################################
if __name__=='__main__':
	examples()



# RUN EXAMPLE:
# ./../common/dependencyFactory.py -I ../common/vbfHbb_info.json -S ../common/vbfHbb_samples_SA_2012Paper.json -V ../common/vbfHbb_variables_2012Paper.json -C ../common/vbfHbb_cuts.json --nosample JetMon -t 'NOMMC' -p 'NOMold'
# ./../common/dependencyFactory.py -D ../common/vbfHbb_KK_defaultOpts.json --nosample JetMon -t 'NOMMC' -p 'NOMold' --weight "19000.,XSEC;LUMI;PU"
