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
		if opts.debug: l3("%sSample: %s%s"%(purple,s['tag'],plain))
		### Clean some
		if opts.debug and 'KFAC' in opts.weight[1]: l3("Option specified k-factor ignored in k-factor calculation.")
		opts.weightlocal = dc(opts.weight)
		opts.weightlocal[1] = list(set(opts.weight[1])-set(['KFAC']))
		### Get cut and weight
		trg,trg_orig = trigData(opts,s,trg)
		cut = write_cuts(sel,trg,sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weightlocal,trigequal=trigTruth(opts.usebool))[0]
		trg = dc(trg_orig)
		if opts.debug: l3("Cut: %s"%cut)
		### Data
		if 'Data' in s['tag'] or 'DataV' in s['tag']:
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hDat.GetName(),"0.5",cut))
		### QCD 
		elif 'QCD' in s['tag']:
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hQCD.GetName(),"0.5",cut))
		### Bkg
		else:
			inroot('%s.draw("%s","%s","%s")'%(s['pointer'],ROOT.hBkg.GetName(),"0.5",cut))
	#	print "Data: %8.2f  | Bkg: %8.2f  | QCD: %8.2f"%(ROOT.hDat.Integral(),ROOT.hBkg.Integral(),ROOT.hQCD.Integral())
	### finish
	KFWght = (ROOT.hDat.Integral()-ROOT.hBkg.Integral())/ROOT.hQCD.Integral()
	inroot('delete hDat; delete hQCD; delete hBkg;')
	if opts.debug: l2("KFWght calculated at: %f"%KFWght)
	return KFWght

def get2DMap(opts,fout,samples,variables,sel,trg,ref,vx,vy):
	# info 
	l1("Creating 2D maps for (%s,%s):"%(vx[0],vy[0]))
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	groups = list(set([jsoninfo['groups'][x['tag']] for x in samples]))
	samplesbygroup = {}
	for group in groups:
		samplesbygroup[group] = [sample for sample in samples if jsoninfo['groups'][sample['tag']]==group]
	ratios = []
	if 'JetMon' in groups and 'QCD' in groups:
		ratios += ['JetMon-QCD']
# storage
	gDirectory.cd("%s:/"%fout.GetName())
	for group in groups:
		makeDirsRoot(fout,'2DMaps/%s'%group)
# calculate
	xvals = array.array('f',[float(x) for x in vx[1].split("#")])
	yvals = array.array('f',[float(x) for x in vy[1].split("#")])
	maps = {}
	cuts = {}
	inroot('TTree *t = 0;')
# LOOP over ALL GROUPS
	for group in groups:
		l2("Filling for group: %s%s%s"%(purple,group,plain))
		maps[group] = {}
		cuts[group] = {}
		for tag in ['Num','Den','Rat']:
			trg,trg_orig = trigData(opts,'',trg)
			mapname = "2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s"%(group,tag,'-'.join(sel),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0],vy[0])
			maptitle = "%s;%s;%s"%(mapname,variables[vx[0]]['title_x'],variables[vy[0]]['title_x'])
			trg = dc(trg_orig)
			maps[group][tag] = fout.FindObjectAny(mapname)
			if not maps[group][tag]:
				maps[group][tag] = TH2F(mapname,maptitle,len(xvals)-1,xvals,len(yvals)-1,yvals)
				maps[group][tag].Sumw2()
## LOOP over ALL SAMPLES
				for s in samplesbygroup[group]:
					if tag=='Rat': continue
					l3("Filling for sample: %s%s (%s)%s"%(cyan,s['tag'],tag,plain))
					trg,trg_orig = trigData(opts,s,trg)
					inroot('t = (TTree*)%s.gett();'%s['pointer'])	
					cuts[group][tag] = write_cuts(sel,trg if tag=='Num' else [],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=ref,varskip=[variables[vx[0]]['root'],variables[vy[0]]['root']],trigequal=trigTruth(opts.usebool),weight=opts.weight)[0]
					inroot('t->Draw("%s:%s>>+%s",TCut("%s"));'%(variables[vy[0]]['root'],variables[vx[0]]['root'],maps[group][tag].GetName(),cuts[group][tag]))
					trg = dc(trg_orig)
			else:
				l3("Loaded from file for group: %s%s%s"%(cyan,group,plain))
## END LOOP over ALL SAMPLES
		# ratio
		maps[group]['Rat'].Divide(maps[group]['Num'],maps[group]['Den'],1.0,1.0,'B')
		# save		
		gDirectory.cd('%s:/2DMaps/%s'%(fout.GetName(),group))
		for tag in ['Num','Den','Rat']:
			maps[group][tag].Write(maps[group][tag].GetName(),TH1.kOverwrite)
# END LOOP over ALL GROUPS

# FOCUS ON RATIO MAPS JetMon / QCD
	gDirectory.cd("%s:/"%fout.GetName())
	for ratio in ratios:
		# store
		makeDirsRoot(fout,'2DMaps/%s'%ratio)
		maps[ratio] = {}
		l2("Getting ratio for: %s%s%s"%(purple,ratio,plain))
		# create
		trg,trg_orig = trigData(opts,'',trg)
		mapname = "2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s"%(ratio,'Rat','-'.join(sel),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0],vy[0])
		maptitle = "%s;%s;%s"%(mapname,variables[vx[0]]['title_x'],variables[vy[0]]['title_x'])
		trg = dc(trg_orig)
		maps[ratio]['Rat'] = TH2F(mapname,maptitle,len(xvals)-1,xvals,len(yvals)-1,yvals)
		maps[ratio]['Rat'].Sumw2()
		maps[ratio]['Rat'].Divide(maps[ratio.split('-')[0]]['Rat'],maps[ratio.split('-')[1]]['Rat'],1.0,1.0,'B')
		# save		
		gDirectory.cd('%s:/2DMaps/%s'%(fout.GetName(),ratio))
		maps[ratio]['Rat'].Write(maps[ratio]['Rat'].GetName(),TH1.kOverwrite)
		# plot
		canvas = TCanvas("cmap","cmap",1800,1200)
		canvas.cd()
		gPad.SetGrid(0,0)
		gPad.SetRightMargin(0.12)
		maps[ratio]['Rat'].SetTitleOffset(1.0,"Y")
		gStyle.SetPaintTextFormat("6.3f")
		maps[ratio]['Rat'].Draw('colz,error,text90')
		path = "plots/2DMaps/%s"%ratio
		makeDirs(path)
		canvas.SaveAs("%s/%s.png"%(path,maps[ratio]['Rat'].GetName()))
		canvas.Close()




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
		for s in sorted(samples,key=lambda x:(x['tag'],jsoninfo['crosssections'][x['tag']])):
			if not tag=='Rat': 
				inroot('t = (TTree*)%s.gett();'%s['pointer'])
				cuts['Num'] = write_cuts(sel,trg if (opts.datatrigger==[] or not ('Data' in s['tag'] or 'JetMon' in s['tag'])) else opts.datatrigger[opts.trigger.index(trg)],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=reftrig,trigequal=('49' if not opts.usebool else '1'))[0]
				cuts['Den'] = write_cuts(sel,['None'],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=reftrig,trigequal=('49' if not opts.usebool else '1'))[0]
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
	print samplesnum
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

def loadTwoDWght(fout,mapfile,mapname):
	# clean
	try: ROOT.wghtHist.Delete()
	except: pass
	# correct file
	if not fout.GetName()==mapfile: inroot('TFile *fmap = TFile::Open("%s");'%mapfile)
	inroot('gDirectory->cd("%s:/");'%fout.GetName())
	# load & clone
	if not fout.GetName()==mapfile: inroot('TH2F *wghtHist = (TH2F*)fmap->Get("%s;1").Clone();'%mapname)
	else: inroot('TH2F *wghtHist = (TH2F*)gDirectory->Get("%s;1").Clone();'%mapname)
	# close if unneeded
	if not fout.GetName()==mapfile: inroot('fmap->Close();')

def loadBMapWght(fout,mapfile,mapname):
	# clean
	try: ROOT.bmap.Delete()
	except: pass
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
	opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())

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
