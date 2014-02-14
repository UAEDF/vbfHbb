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
from array import array


####################################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mg1 = OptionGroup(mp,cyan+"dependencyFactory settings"+plain)
	mg1.add_option('--bmap',help='Calculate btagmap JetMon/QCD.',default=False,action='store_true')
	mg1.add_option('--kfac',help='Calculate k-factor.',default=False,action='store_true')
	mp.add_option_group(mg1)
	return mp

####################################################################################################
def drawNsave(fout,h,hpath,htitle,hopts,printout):
	canvas = TCanvas('ctmp','ctmp',1800,1200)
	canvas.cd()
	gPad.SetRightMargin(0.14)
	gPad.SetTopMargin(0.07)
	#if set(hopts.split(','))==set('text,colz,error'.split(',')): h.SetMarkerSize(h.GetMarkerSize()*0.75)
	if set(hopts.split(','))==set('text,colz,error'.split(',')): h.SetMarkerSize(0.75)
	h.SetTitleOffset(1.0,'Y')
	h.Draw(hopts)
	makeDirs('plots/%s/%s'%(fout.GetName().split('/')[-1].strip(".root"),hpath))
	canvas.SaveAs('plots/%s/%s/%s.png'%(fout.GetName().split('/')[-1].strip(".root"),hpath,htitle))
	canvas.SaveAs('plots/%s/%s/%s.pdf'%(fout.GetName().split('/')[-1].strip(".root"),hpath,htitle))
	l3("%-45s (eog%-s"%(printout.split('(eog')[0],printout.split('(eog')[1]))
	canvas.Close()

####################################################################################################
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
		if opts.debug and 'KFAC' in opts.weight[1]: l3("Option specified k-factor and puWt ignored in k-factor calculation.")
		opts.weightlocal = dc(opts.weight)
		opts.weightlocal[1] = list(set(opts.weight[1])-set(['KFAC','PU']))
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
		print "Data: %8.2f  | Bkg: %8.2f  | QCD: %8.2f"%(ROOT.hDat.Integral(),ROOT.hBkg.Integral(),ROOT.hQCD.Integral())
	### finish
	KFWght = (ROOT.hDat.Integral()-ROOT.hBkg.Integral())/ROOT.hQCD.Integral()
	inroot('delete hDat; delete hQCD; delete hBkg;')
	if opts.debug: l2("KFWght calculated at: %f"%KFWght)
	return KFWght

####################################################################################################
def get2DMapCombo(opts,fout,inputs):
	# info
	map1 = inputs[0]
	map2 = inputs[1]
	cutx = float(inputs[2]) if not inputs[2]=="" else None
	cuty = float(inputs[3]) if not inputs[3]=="" else None
	extra = inputs[4]
	l1("Combining 2D maps:")
	l2("Using map1: %s"%map1)
	l2("Using map2: %s"%map2)
	# check
	if not (cutx==None or cuty==None):
		sys.exit("%sSpecify either x or y cut, not both. Exiting.%s"%(red,plain))
	l2("Cut at x=%.3f"%cutx if cutx else "Cut at y=%.3f"%cuty)  
	l2("Extra tag: %s"%extra)
	path,name = os.path.split(map1)
	name = name.strip(';1')
	name += "_%s"%extra
	# get
	m1 = fout.Get(map1)
	m2 = fout.Get(map2)
	# combine
	canvas = TCanvas("cmap","cmap",1800,1200)
	gPad.SetGrid(0,0)
	gPad.SetRightMargin(0.14)
	gStyle.SetPaintTextFormat("6.2f")
	# limits
	binsx1 = []
	binsy1 = []
	binsx2 = []
	binsy2 = []
	for xi in range(m1.GetXaxis().GetNbins()+1): binsx1 += [m1.GetXaxis().GetBinUpEdge(xi)]
	for yi in range(m1.GetYaxis().GetNbins()+1): binsy1 += [m1.GetYaxis().GetBinUpEdge(yi)]
	for xi in range(m2.GetXaxis().GetNbins()+1): binsx2 += [m2.GetXaxis().GetBinUpEdge(xi)]
	for yi in range(m2.GetYaxis().GetNbins()+1): binsy2 += [m2.GetYaxis().GetBinUpEdge(yi)]
	if cutx and not binsy1==binsy2: sys.exit(red+"Maps should match in non-cut dimension (y). Exiting."+plain)
	elif cuty and not binsx1==binsx2: sys.exit(red+"Maps should match in non-cut dimension (x). Exiting."+plain)
	if cutx: 
		binsx3 = dc([x for x in binsx1 if x<=cutx] + [x for x in binsx2 if x>cutx])
		binsy3 = dc(binsy1)
	if cuty: 
		binsx3 = dc(binsx1)
		binsy3 = dc([x for x in binsy1 if x<=cuty] + [x for x in binsy2 if x>cuty])
	# new map
	mc = TH2F(name,"%s;%s;%s"%(name,m1.GetXaxis().GetTitle(),m1.GetYaxis().GetTitle()),len(binsx3)-1,array('f',binsx3),len(binsy3)-1,array('f',binsy3))
	mc.Sumw2()
	# names
	mc.SetName(name)
	mc.SetTitle("%s;%s;%s"%(name,m1.GetXaxis().GetTitle(),m1.GetYaxis().GetTitle()))
	gStyle.SetPaintTextFormat("6.2f")

	# fill
	for xi in range(mc.GetXaxis().GetNbins()+1):
		for yi in range(mc.GetYaxis().GetNbins()+1):
			#print xi,yi,m1.GetBinContent(xi,yi),m2.GetBinContent(xi,yi)
			xi1 = m1.GetXaxis().FindBin(mc.GetXaxis().GetBinUpEdge(xi)-0.001)
			yi1 = m1.GetYaxis().FindBin(mc.GetYaxis().GetBinUpEdge(yi)-0.001)
			xi2 = m2.GetXaxis().FindBin(mc.GetXaxis().GetBinUpEdge(xi)-0.001)
			yi2 = m2.GetYaxis().FindBin(mc.GetYaxis().GetBinUpEdge(yi)-0.001)
			if cutx: 
				binUpLim = mc.GetXaxis().GetBinUpEdge(xi)
				if binUpLim <= cutx: 
					mc.SetBinContent(xi,yi,m1.GetBinContent(xi1,yi1))
					mc.SetBinError(xi,yi,m1.GetBinError(xi1,yi1))
				if binUpLim > cutx:  
					mc.SetBinContent(xi,yi,m2.GetBinContent(xi2,yi2))
					mc.SetBinError(xi,yi,m2.GetBinError(xi2,yi2))
			elif cuty:
				binUpLim = mc.GetYaxis().GetBinUpEdge(yi)
				if binUpLim <= cuty: 
					mc.SetBinContent(xi,yi,m1.GetBinContent(xi1,yi1))
					mc.SetBinError(xi,yi,m1.GetBinError(xi1,yi1))
				if binUpLim > cuty:  
					mc.SetBinContent(xi,yi,m2.GetBinContent(xi2,yi2))
					mc.SetBinError(xi,yi,m2.GetBinError(xi2,yi2))

	# save		
	makeDirsRoot(fout,path)
	gDirectory.cd('%s:/%s'%(fout.GetName(),path))
	mc.Write(mc.GetName(),TH1.kOverwrite)
	mc.GetYaxis().SetTitleOffset(1)
	mc.Draw("colz,error,text90")
	makeDirs('plots/%s'%path)
	canvas.SaveAs('plots/%s/%s/%s.png'%(fout.GetName().split('/')[-1][:-5],path,name))
	canvas.SaveAs('plots/%s/%s/%s.pdf'%(fout.GetName().split('/')[-1][:-5],path,name))
	l2("Written map to plots/%s/%s/%s.png"%(fout.GetName().split('/')[-1][:-5],path,name))
	# clean
	canvas.Close()

####################################################################################################
def get1DMap(opts,fout,samples,variables,sel,trg,ref,vx):
	# info 
	l1("Creating 1D cors for (%s):"%(vx[0]))
	print "+ (sel,trg,ref): (%s,%s,%s)"%(sel,trg,ref)
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
		makeDirsRoot(fout,'1DMaps/%s'%group)
# calculate
	xvals = array('f',[float(x) for x in vx[1].split("#")])
	maps = {}
	cuts = {}
	inroot('TTree *t = 0;')
# To Save
	canvas = TCanvas("cmap","cmap",1800,1200)
	canvas.cd()
	gPad.SetGrid(0,0)
	gPad.SetRightMargin(0.14)
	gStyle.SetPaintTextFormat("6.2f")
# LOOP over ALL GROUPS
	for group in groups:
		l2("Filling for group: %s%s%s"%(purple,group,plain))
		maps[group] = {}
		cuts[group] = {}
		for tag in ['Num','Den','Rat']:
			trg,trg_orig = trigData(opts,'',trg)
			mapname = "1DMap_%s-%s_s%s-t%s-r%s-d%s_%s"%(group,tag,'-'.join(sorted(sel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0])
			maptitle = "%s;%s;Scale factor"%(mapname,variables[vx[0]]['title_x'])
			trg = dc(trg_orig)
			maps[group][tag] = fout.FindObjectAny(mapname)
			if (not maps[group][tag]) or (not len(xvals)-1==maps[group][tag].GetXaxis().GetNbins()):
				maps[group][tag] = TH1F(mapname,maptitle,len(xvals)-1,xvals)
				maps[group][tag].Sumw2()
## LOOP over ALL SAMPLES
				for s in sorted(samplesbygroup[group],key=lambda x:('QCD' in x['tag'],not 'WJets' in x['tag'],jsoninfo['crosssections'][x['tag']])):
					if tag=='Rat': continue
					l3("Filling for sample: %s%s (%s)%s"%(cyan,s['tag'],tag,plain))
					trg,trg_orig = trigData(opts,s,trg)
					inroot('t = (TTree*)%s.gett();'%s['pointer'])	
					cuts[group][tag] = write_cuts(sel,trg if tag=='Num' else [],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=ref,trigequal=trigTruth(opts.usebool),weight=opts.weight)[0] #,varskip=[variables[vx[0]]['root'],variables[vy[0]]['root']]
					if opts.debug: print yellow,cuts[group][tag],plain
					inroot('t->Draw("%s>>+%s",TCut("%s"));'%(variables[vx[0]]['root'],maps[group][tag].GetName(),cuts[group][tag]))
					trg = dc(trg_orig)
			else:
				l3("Loaded from file for group: %s%s%s"%(cyan,group,plain))
## END LOOP over ALL SAMPLES
		# to save
		path = 'plots/%s/1DMaps/%s'%(fout.GetName().split('/')[-1][:-5],group)
		makeDirs(path)
		# ratio
		maps[group]['Rat'].Divide(maps[group]['Num'],maps[group]['Den'],1.0,1.0,'B')
#$		maps[group]['Rat'] = TEfficiency(maps[group]['Num'],maps[group]['Den'])
		maps[group]['Rat'].SetName(mapname)
		maps[group]['Rat'].SetTitle(maptitle)
		# save		
		gDirectory.cd('%s:/1DMaps/%s'%(fout.GetName(),group))
##
		for tag in ['Num','Den','Rat']:
			if not tag in maps[group]: continue
			maps[group][tag].Write(maps[group][tag].GetName(),TH1.kOverwrite)
			gPad.SetRightMargin(0.14)
			maps[group][tag].SetTitleOffset(1.0,"Y")
			maps[group][tag].SetMarkerSize(maps[group][tag].GetMarkerSize()*0.75)
			maps[group][tag].Draw("text45,error")
			canvas.SaveAs('%s/%s.png'%(path,maps[group][tag].GetName()))
			canvas.SaveAs('%s/%s.pdf'%(path,maps[group][tag].GetName()))
			l3("Written %s map to (eog %s/%s.png)"%(tag,path,maps[group][tag].GetName()))
# END LOOP over ALL GROUPS

# FOCUS ON RATIO MAPS JetMon / QCD
	gDirectory.cd("%s:/"%fout.GetName())
	for ratio in ratios:
		# store
		makeDirsRoot(fout,'1DMaps/%s'%ratio)
		maps[ratio] = {}
		l2("Getting ratio for: %s%s%s"%(purple,ratio,plain))
		# create
		trg,trg_orig = trigData(opts,'',trg)
		mapname = "1DMap_%s-%s_s%s-t%s-r%s-d%s_%s"%(ratio,'Rat','-'.join(sorted(sel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0])
		maptitle = "%s;%s;Scale factor"%(mapname,variables[vx[0]]['title_x'])
		trg = dc(trg_orig)
		maps[ratio]['Rat'] = TH1F(mapname,maptitle,len(xvals)-1,xvals)
		maps[ratio]['Rat'].Sumw2()
#$		maps[ratio]['Rat'].Divide(maps[ratio.split('-')[0]]['Rat'].GetPaintedHistogram(),maps[ratio.split('-')[1]]['Rat'].GetPaintedHistogram())
		maps[ratio]['Rat'].Divide(maps[ratio.split('-')[0]]['Rat'],maps[ratio.split('-')[1]]['Rat'])

		# plot
		canvas.cd()
		maps[ratio]['Rat'].SetTitleOffset(1.0,"Y")
		maps[ratio]['Rat'].SetMarkerSize(maps[ratio]['Rat'].GetMarkerSize()*0.75)
		maps[ratio]['Rat'].Draw('text45,error')
		print '\033[1;31mRatio drawn\033[m'
		
		# save		
		gDirectory.cd('%s:/1DMaps/%s'%(fout.GetName(),ratio))
		maps[ratio]['Rat'].Write(maps[ratio]['Rat'].GetName(),TH1.kOverwrite)

		path = "plots/%s/1DMaps/%s"%(fout.GetName().split('/')[-1][:-5],ratio)
		makeDirs(path)
		for tag in ['Num','Den','Rat']:
			if not tag in maps[ratio]: continue
			canvas.SaveAs("%s/%s.png"%(path,maps[ratio][tag].GetName()))
			canvas.SaveAs("%s/%s.pdf"%(path,maps[ratio][tag].GetName()))
		l2("Written map to (eog %s/%s.png)"%(path,maps[ratio]['Rat'].GetName()))

		# 2d copy
		binsx = []
		for i in range(1,maps[ratio]['Rat'].GetNbinsX()+2): binsx += [maps[ratio]['Rat'].GetXaxis().GetBinLowEdge(i)]
		#print binsx
		binsx_array = array('f',binsx)
		binsy_array = array('f',[0.0,1.0])
		ratio2d = TH2F('ratio2D','ratio2D',len(binsx_array)-1,binsx_array,len(binsy_array)-1,binsy_array)
		for i in range(maps[ratio]['Rat'].GetNbinsX()+2):
			#print maps[ratio]['Rat'].GetXaxis().GetBinLowEdge(i)
			#print maps[ratio]['Rat'].GetBinContent(i)
			ratio2D.SetBinContent(i,1,maps[ratio]['Rat'].GetBinContent(i))
			ratio2D.SetBinError(i,1,maps[ratio]['Rat'].GetBinError(i))
		#plot 
		canvas.cd()
		ratio2D.SetTitle('%s;%s;%s'%('',maps[ratio]['Rat'].GetXaxis().GetTitle(),'Scale factor'))
		ratio2D.Draw('colz,error,text45')
		canvas.SaveAs("%s/2D%s.png"%(path,maps[ratio][tag].GetName()))
		canvas.SaveAs("%s/2D%s.pdf"%(path,maps[ratio][tag].GetName()))
		l2("Written map to (eog %s/2D%s.png)"%(path,maps[ratio]['Rat'].GetName()))

	# clean
	canvas.Close()

####################################################################################################
def get2DMap(opts,fout,samples,variables,sel,trg,ref,vx,vy):
	# info 
	l1("Creating 2D maps for (%s,%s):"%(vx[0],vy[0]))
	print "+ (sel,trg,ref): (%s,%s,%s)"%(sel,trg,ref)
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
	xvals = array('f',[float(x) for x in vx[1].split("#")])
	yvals = array('f',[float(x) for x in vy[1].split("#")])
	maps = {}
	cuts = {}
	inroot('TTree *t = 0;')
# To Save
	canvas = TCanvas("cmap","cmap",1800,1200)
	canvas.cd()
	gPad.SetGrid(0,0)
	gPad.SetRightMargin(0.14)
	gStyle.SetPaintTextFormat("6.2f")
# LOOP over ALL GROUPS
	for group in groups:
		l2("Filling for group: %s%s%s"%(purple,group,plain))
		maps[group] = {}
		cuts[group] = {}
		for tag in ['Num','Den','Rat']:
			trg,trg_orig = trigData(opts,'',trg)
			mapname = "2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s"%(group,tag,'-'.join(sorted(sel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0],vy[0])
			maptitle = "%s;%s;%s"%(mapname,variables[vx[0]]['title_x'],variables[vy[0]]['title_x'])
			trg = dc(trg_orig)
			maps[group][tag] = fout.FindObjectAny(mapname)
			if (not maps[group][tag]) or (not len(xvals)-1==maps[group][tag].GetXaxis().GetNbins()) or (not len(yvals)-1==maps[group][tag].GetYaxis().GetNbins()):
				maps[group][tag] = TH2F(mapname,maptitle,len(xvals)-1,xvals,len(yvals)-1,yvals)
				maps[group][tag].Sumw2()
## LOOP over ALL SAMPLES
				for s in sorted(samplesbygroup[group],key=lambda x:('QCD' in x['tag'],not 'WJets' in x['tag'],jsoninfo['crosssections'][x['tag']])):
					if tag=='Rat': continue
					l3("Filling for sample: %s%s (%s)%s"%(cyan,s['tag'],tag,plain))
					trg,trg_orig = trigData(opts,s,trg)
					inroot('t = (TTree*)%s.gett();'%s['pointer'])	
					cuts[group][tag] = write_cuts(sel,trg if tag=='Num' else [],sample=s['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,reftrig=ref,trigequal=trigTruth(opts.usebool),weight=opts.weight)[0] #,varskip=[variables[vx[0]]['root'],variables[vy[0]]['root']]
					if opts.debug: print yellow,cuts[group][tag],plain
					inroot('t->Draw("%s:%s>>+%s",TCut("%s"));'%(variables[vy[0]]['root'],variables[vx[0]]['root'],maps[group][tag].GetName(),cuts[group][tag]))
					trg = dc(trg_orig)
			else:
				l3("Loaded from file for group: %s%s%s"%(cyan,group,plain))
## END LOOP over ALL SAMPLES
		# to save
		path = 'plots/%s/2DMaps/%s'%(fout.GetName().split('/')[-1][:-5],group)
		makeDirs(path)
		# ratio
		maps[group]['Rat'].Divide(maps[group]['Num'],maps[group]['Den'],1.0,1.0,'B')
#$		maps[group]['Rat'] = TEfficiency(maps[group]['Num'],maps[group]['Den'])
		maps[group]['Rat'].SetName(mapname)
		maps[group]['Rat'].SetTitle(maptitle)
		# save		
		gDirectory.cd('%s:/2DMaps/%s'%(fout.GetName(),group))
		for tag in ['Num','Den','Rat']:
			if not tag in maps[group]: continue
			maps[group][tag].Write(maps[group][tag].GetName(),TH1.kOverwrite)
#$			if tag=='Rat': 
#$				maps[group][tag].Paint("colz,text90,error")
#$				maps[group][tag].GetPaintedHistogram().SetTitleOffset(1.0,"Y")
#$			else: maps[group][tag].SetTitleOffset(1.0,"Y")
			gPad.SetRightMargin(0.14)
			maps[group][tag].SetTitleOffset(1.0,"Y")
			maps[group][tag].SetMarkerSize(maps[group][tag].GetMarkerSize()*0.75)
			maps[group][tag].Draw("colz,text45,error")
			canvas.SaveAs('%s/%s.png'%(path,maps[group][tag].GetName()))
			canvas.SaveAs('%s/%s.pdf'%(path,maps[group][tag].GetName()))
			l3("Written %s map to (eog %s/%s.png)"%(tag,path,maps[group][tag].GetName()))
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
		mapname = "2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s"%(ratio,'Rat','-'.join(sorted(sel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx[0],vy[0])
		maptitle = "%s;%s;%s"%("",variables[vx[0]]['title_x'],variables[vy[0]]['title_x']) #mapname
		trg = dc(trg_orig)
		maps[ratio]['Rat'] = TH2F(mapname,maptitle,len(xvals)-1,xvals,len(yvals)-1,yvals)
		maps[ratio]['Rat'].Sumw2()
#$		maps[ratio]['Rat'].Divide(maps[ratio.split('-')[0]]['Rat'].GetPaintedHistogram(),maps[ratio.split('-')[1]]['Rat'].GetPaintedHistogram())
		maps[ratio]['Rat'].Divide(maps[ratio.split('-')[0]]['Rat'],maps[ratio.split('-')[1]]['Rat'])

		# plot
		canvas.cd()
		maps[ratio]['Rat'].SetTitleOffset(1.0,"Y")
		maps[ratio]['Rat'].SetTitleOffset(1.2,"X")
		if 'VBF' in trg:
			gPad.SetLogx(1)
			maps[ratio]['Rat'].GetXaxis().SetMoreLogLabels()
			maps[ratio]['Rat'].SetMarkerSize(maps[ratio]['Rat'].GetMarkerSize()*0.75)
		maps[ratio]['Rat'].Draw('colz,error,text')
		print '\033[1;31mRatio drawn\033[m'
		canvas.WaitPrimitive()
		
		# save		
		gDirectory.cd('%s:/2DMaps/%s'%(fout.GetName(),ratio))
		maps[ratio]['Rat'].Write(maps[ratio]['Rat'].GetName(),TH1.kOverwrite)

		path = "plots/%s/2DMaps/%s"%(fout.GetName().split('/')[-1][:-5],ratio)
		makeDirs(path)
		for tag in ['Num','Den','Rat']:
			if not tag in maps[ratio]: continue
			canvas.SaveAs("%s/%s.png"%(path,maps[ratio][tag].GetName()))
			canvas.SaveAs("%s/%s.pdf"%(path,maps[ratio][tag].GetName()))
		l2("Written map to (eog %s/%s.png)"%(path,maps[ratio]['Rat'].GetName()))
#		canvas.Close()

	# clean
	canvas.Close()

####################################################################################################
def loadOneDWght(fout,mapfile,mapname):
	# clean
	try: ROOT.wghtHist.Delete()
	except: pass
	# correct file
	if not fout.GetName()==mapfile: inroot('TFile *fmap = TFile::Open("%s");'%mapfile)
	inroot('gDirectory->cd("%s:/");'%fout.GetName())
	# load & clone
	if not fout.GetName()==mapfile: inroot('TH1F *wghtOneHist = (TH1F*)fmap->Get("%s;1").Clone();'%mapname)
	else: inroot('TH1F *wghtOneHist = (TH1F*)gDirectory->Get("%s;1").Clone();'%mapname)
	# close if unneeded
	if not fout.GetName()==mapfile: inroot('fmap->Close();')

####################################################################################################
def loadTwoDWght(fout,mapfile,mapname):
	# clean
	try: ROOT.wghtHist.Delete()
	except: pass
	# correct file
	if not fout.GetName()==mapfile: inroot('TFile *fmap = TFile::Open("%s");'%mapfile)
	inroot('gDirectory->cd("%s:/");'%fout.GetName())
	# load & clone
	if not fout.GetName()==mapfile: inroot('TH2F *wghtTwoHist = (TH2F*)fmap->Get("%s;1").Clone();'%mapname)
	else: inroot('TH2F *wghtTwoHist = (TH2F*)gDirectory->Get("%s;1").Clone();'%mapname)
	# close if unneeded
	if not fout.GetName()==mapfile: inroot('fmap->Close();')

####################################################################################################################################################################################
def getSignificance(opts,fout,samples,variables,sel,trg,references,vx,vy):
	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	groups = list(set(list(set([jsoninfo['groups'][x] for x in samples if x in jsoninfo['groups']])) + list(set([x for x in jsoninfo['groups'].itervalues() if x in samples]))))

# add combo ref
	comboref = any(['AV40' in x for x in references]) and any(['AV80' in x for x in references])
	if comboref: references += [['AV40AV80']]

# 0) get all maps
	mapnames = {} 
	maps = {}
	for group in groups: 
		mapnames[group] = {}
		maps[group] = {}
		for ref in sorted(references,key=lambda x:(len('-'.join(x)),not 'None' in '-'.join(x),('-'.join(x)))):
			reftag = '-'.join(ref)
			mapnames[group][reftag] = {}
			maps[group][reftag] = {}
			for tag in ['Num','Den','Rat']:
				trg,trg_orig = trigData(opts,'',trg)
				mapnames[group][reftag][tag] = "2DMaps/%s/2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s;1"%(group,group,tag,'-'.join(sorted(sel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx,vy)
				maps[group][reftag][tag] = fout.Get(mapnames[group][reftag][tag]) if not reftag == 'AV40AV80' else maps[group]['AV80'][tag].Clone(mapnames[group][reftag][tag].split('/')[-1])
				trg = trg_orig
	
# 1) get efficiencies
	gDirectory.cd('%s:/'%fout.GetName())
	makeDirsRoot(fout,'effMaps/')
	makeDirs('plots/%s/effMaps'%fout.GetName().split('/')[-1].strip(".root"))
	effnames = {}
	effs = {}
	effsInt = {}
	for group in mapnames.keys():
		l2('EffMaps for group %s'%group)
		gDirectory.cd('%s:/'%fout.GetName())
		makeDirsRoot(fout,'effMaps/%s'%group)
		makeDirs('plots/%s/effMaps/%s'%(fout.GetName().split('/')[-1].strip(".root"),group))
		makeDirsRoot(fout,'effIntMaps/%s'%group)
		makeDirs('plots/%s/effIntMaps/%s'%(fout.GetName().split('/')[-1].strip(".root"),group))
		effnames[group] = {}
		effs[group] = {}
		effsInt[group] = {}
		# canvas	
		gDirectory.cd("effMaps/%s"%(group))
		canvas = TCanvas('ceff','ceff',1800,1200)
		gDirectory.cd("/")
		for ref in sorted(mapnames[group].keys(),key=lambda x:(len(x),not 'None' in x,x)):
			effnames[group][ref] = {}
			effs[group][ref] = {}
			# LOOP over num,den only (skip rat)
			for tag in sorted(mapnames[group][ref].keys()):
				# new names
				effnames[group][ref][tag] = mapnames[group][ref][tag].replace('2DMap','effMap')
				# container
				effs[group][ref][tag] = maps[group][ref][tag].Clone(effnames[group][ref][tag]) ## THIS IS THE IMPORTANT CONTENT
				effs[group][ref][tag].SetTitle(effnames[group][ref][tag])
				effs[group][ref][tag].GetXaxis().SetTitle(maps[group][ref][tag].GetXaxis().GetTitle())
				effs[group][ref][tag].GetYaxis().SetTitle(maps[group][ref][tag].GetYaxis().GetTitle())
				effs[group][ref][tag].SetTitleOffset(1.0,'Y')
				effs[group][ref][tag].SetMarkerSize(effs[group][ref][tag].GetMarkerSize()*1.25)
				# canvas
				canvas.cd()
				gStyle.SetPaintTextFormat(".3f")
				gPad.SetRightMargin(0.14)
				gPad.Update()
				# scale in the AV40 case, to the AV80 lumi
				if ref=='AV40':
					lumisf = jsoninfo['luminosities']['HLT_PFJetAve80_v*'] / jsoninfo['luminosities']['HLT_PFJetAve40_v*']
					effs[group][ref][tag].Scale(lumisf)
				# combine in the AV40AV80 case
				if ref=='AV40AV80':
#					effsInt[group][tag] = effs[group][ref][tag].Clone(effs[group][ref][tag].GetName().replace('effMap','effIntMap'))
#					effsInt[group][tag].SetTitle('%s;%s;%s'%(effsInt[group][tag].GetName().split('/')[-1].strip(';1'),effs[group][ref][tag].GetXaxis().GetTitle(),effs[group][ref][tag].GetYaxis().GetTitle()))
#					effsInt[group][tag].SetTitleOffset(1.0,'Y')
#					effsInt[group][tag].SetMarkerSize(effsInt[group][tag].GetMarkerSize()*0.75)
					nbinsX = effs[group][ref][tag].GetNbinsX()
					nbinsY = effs[group][ref][tag].GetNbinsY()
					for ix in range(0,nbinsX+2):
						for iy in range(0,nbinsY+2):
							iysplit = effs[group][ref][tag].GetYaxis().FindBin(400)
							if iy < iysplit:
								val = effs[group]['AV40'][tag].GetBinContent(ix,iy)
								err = effs[group]['AV40'][tag].GetBinError(ix,iy)
							else:	
								val = effs[group]['AV80'][tag].GetBinContent(ix,iy)
								err = effs[group]['AV80'][tag].GetBinError(ix,iy)
							effs[group][ref][tag].SetBinContent(ix,iy,val)
							effs[group][ref][tag].SetBinError(ix,iy,err)
#							# integrate
#							err = ROOT.Double()
#							val = effs[group][ref][tag].IntegralAndError(ix,nbinsX+1,iy,nbinsY+1,err)
#							effsInt[group][tag].SetBinContent(ix,iy,val)
#							effsInt[group][tag].SetBinError(ix,iy,err)
			# get rat for AV40AV80 case (integrating)		
#			if ref=='AV40AV80':
#				tag = 'Rat'
#				effsInt[group][tag] = effsInt[group]['Num'].Clone(effsInt[group]['Num'].GetName().replace('Num',tag))
#				effsInt[group][tag].SetTitle('%s;%s;%s'%(effsInt[group][tag].GetName().split('/')[-1].strip(';1'),effs[group][ref]['Num'].GetXaxis().GetTitle(),effs[group][ref]['Num'].GetYaxis().GetTitle()))
#				effsInt[group][tag].SetTitleOffset(1.0,'Y')
#				#effsInt[group][tag].SetMarkerSize(effsInt[group][tag].GetMarkerSize()*0.75)
#				# divide
#				effsInt[group][tag].Divide(effsInt[group]['Num'],effsInt[group]['Den'],1.0,1.0,'B')	

			# global ratio (unintegrated)
			effs[group][ref]['Rat'].Divide(effs[group][ref]['Num'],effs[group][ref]['Den'],1.0,1.0,'B')	
			
		# save
		# (plain)
		gDirectory.cd("effMaps/%s"%(group))
		for ref in effs[group].keys():
			for tag in ['Num','Den','Rat']:
				setStyleTH2F(effs[group][ref][tag])
				effs[group][ref][tag].Write(effs[group][ref][tag].GetName(),TH1.kOverwrite)
				effs[group][ref][tag].Draw("text90,colz,error")
				canvas.SaveAs('plots/%s/effMaps/%s/%s.png'%(fout.GetName().split('/')[-1].strip(".root"),group,effs[group][ref][tag].GetName().split('/')[-1].strip(';1')))
				canvas.SaveAs('plots/%s/effMaps/%s/%s.pdf'%(fout.GetName().split('/')[-1].strip(".root"),group,effs[group][ref][tag].GetName().split('/')[-1].strip(';1')))
				l3("%-45s %s"%("Written effMap to:","(eog plots/%s/effMaps/%s/%s.png)"%(fout.GetName().split('/')[-1].strip(".root"),group,effs[group][ref][tag].GetName().split('/')[-1].strip(';1'))))
			print
		gDirectory.cd('/')
#		# (integrated)
#		gDirectory.cd("effIntMaps/%s"%(group))
#		for tag in ['Num','Den','Rat']:
#			effsInt[group][tag].Write(effsInt[group][tag].GetName(),TH1.kOverwrite)
#			effsInt[group][tag].Draw("text,colz,error")
#			canvas.SaveAs('plots/effIntMaps/%s/%s.png'%(group,effsInt[group][tag].GetName().split('/')[-1].strip(';1')))
#			l3("Written effIntMap to: (eog plots/effIntMaps/%s/%s.png)"%(group,effsInt[group][tag].GetName().split('/')[-1].strip(';1')))
#		gDirectory.cd('/')
		# clean
		canvas.Close()

#2) get efficiency ratio JetMon/QCD --> SF	
	for ref in (['AV40AV80'] if comboref else list(set(['-'.join(x) for x in references])-set(['-'.join(x) for x in [['None']]]))):
		l2('Ratio JetMon/QCD --> SF (%s)'%ref)
		ratio = {}
		if 'JetMon' in groups and 'QCD' in groups:
			# names
			ndat = 'JetMon'
			nqcd = 'QCD'
#			ref  = 'AV40AV80'
			# storage
			path = effs[ndat][ref]['Rat'].GetName().replace('JetMon','JetMon-QCD') 
			name = path.split('/')[-1]
			gDirectory.cd('%s:/'%fout.GetName())
			makeDirsRoot(fout,'/'.join(path.split('/')[:-1]))
			gDirectory.cd('/')
			makeDirs('/'.join(['plots',fout.GetName().split('/')[-1].strip(".root")]+path.split('/')[:-1]))
			# get
			if ndat in effs.keys() and nqcd in effs.keys() and ref in effs[ndat].keys() and ref in effs[nqcd].keys():
				# calculate
				ratio[ref] = effs[ndat][ref]['Rat'].Clone(name)
				ratio[ref].Divide(effs[ndat][ref]['Rat'],effs[nqcd][ref]['Rat'],1.0,1.0,'B')
				ratio[ref].SetTitle('%s;%s;%s'%(name.strip(';1'),effs[nqcd][ref]['Rat'].GetXaxis().GetTitle(),effs[nqcd][ref]['Rat'].GetYaxis().GetTitle()))
				# draw
				drawNsave(fout,ratio[ref],'/'.join(path.strip(';1').split('/')[:-1]),name.strip(';1'),'text90,colz,error','Written ratioMap (SF) to: (eog plots/%s/%s.png)'%(fout.GetName().split('/')[-1].strip(".root"),path.strip(';1')))
				ratio[ref].Write(ratio[ref].GetName(),TH1.kOverwrite)

#3a) reload N, with stricter cuts
	print
	extra = ['BtagML2','NOMveto']
	if extra:
		# canvas	
		gDirectory.cd("effMaps/%s"%(group))
		canvas = TCanvas('ceff','ceff',1800,1200)
		gDirectory.cd("/")
		# action
		newsel = dc(opts.selection[0])+extra
		newselStr = 's'+'-'.join(sorted(newsel))	
		emapnames = {} 
		emaps = {}
		for group in ['VBF','QCD']:
			if not group in groups: continue
			emapnames[group] = {}
			emaps[group] = {}
			for ref in [['None']]: 
				reftag = '-'.join(ref)
				emapnames[group][reftag] = {}
				emaps[group][reftag] = {}
				for tag in ['Num','Den']:
					trg,trg_orig = trigData(opts,'',trg)
					emapnames[group][reftag][tag] = "2DMaps/%s/2DMap_%s-%s_s%s-t%s-r%s-d%s_%s-%s;1"%(group,group,tag,'-'.join(sorted(newsel)),'-'.join(trg_orig),'-'.join(ref),'-'.join(trg),vx,vy)
					emaps[group][reftag][tag] = fout.Get(emapnames[group][reftag][tag]).Clone(emapnames[group][reftag][tag].replace('2DMap','effMap'))
					emaps[group][reftag][tag].SetTitle(emapnames[group][reftag][tag].replace('2DMap','effMap'))
					emaps[group][reftag][tag].GetXaxis().SetTitle(maps[group][maps[group].keys()[0]][tag].GetXaxis().GetTitle())
					emaps[group][reftag][tag].GetYaxis().SetTitle(maps[group][maps[group].keys()[0]][tag].GetYaxis().GetTitle())
					emaps[group][reftag][tag].SetTitleOffset(1.0,'Y')
					emaps[group][reftag][tag].SetMarkerSize(emaps[group][reftag][tag].GetMarkerSize()*1.25)
					trg = trg_orig
		# canvas
		canvas.cd()
		gStyle.SetPaintTextFormat(".3f")
		gPad.SetRightMargin(0.14)
		gPad.Update()
		# save
		# (plain)
		gDirectory.cd("effMaps/%s"%(group))
		ref = '-'.join(['None'])
		for group in ['VBF','QCD']:
			if not group in groups: continue
			l2('EffMaps for group %s (extracuts,noref)'%group)
			for tag in emaps[group][ref].keys():
				setStyleTH2F(emaps[group][ref][tag])
				emaps[group][ref][tag].Write(emaps[group][ref][tag].GetName(),TH1.kOverwrite)
				emaps[group][ref][tag].Draw("text90,colz,error")
				canvas.SaveAs('plots/%s/effMaps/%s/%s.png'%(fout.GetName().split('/')[-1].strip(".root"),group,emaps[group][ref][tag].GetName().split('/')[-1].strip(';1')))
				canvas.SaveAs('plots/%s/effMaps/%s/%s.pdf'%(fout.GetName().split('/')[-1].strip(".root"),group,emaps[group][ref][tag].GetName().split('/')[-1].strip(';1')))
				l3("%-45s %s"%("Written effMap to:","(eog plots/%s/effMaps/%s/%s.png)"%(fout.GetName().split('/')[-1].strip(".root"),group,emaps[group][ref][tag].GetName().split('/')[-1].strip(';1'))))
			print
		canvas.Close()

#3b) get product N x sf
	print
	folded = {}
	SoverSqSpB = {}
	SoverSqSpBScaled = {}
	for ratioref in ratio.keys():
		folded[ratioref] = {}
		for group in ['VBF','QCD']:
			if not group in groups: continue
			l2('N(%s) x SF (%s)'%(group,ratioref))
			folded[ratioref][group] = {}
			for tag in ['Num','Den']:
				folded[ratioref][group][tag] = {}
				for suffix in ['fold','foldNoSF','foldInt','foldIntNoSF','foldRebin','foldIntRebin']:
					# title and path
					base = emapnames[group]['None'][tag].replace('rNone','rNone-rSF%s'%ratioref).strip(';1').split('/')[-1]
					basepath = '/'.join(emapnames[group]['None'][tag].replace('rNone','rNone-rSF%s'%ratioref).strip(';1').split('/')[:-1])
					x    = emaps[group]['None'][tag].GetXaxis().GetTitle() 
					y    = emaps[group]['None'][tag].GetYaxis().GetTitle()
					title = base.replace('2DMap','%sMap'%suffix)
					path  = basepath.replace('2DMap','%sMap'%suffix)
					name  = '%s/%s'%(path,title)
					if not 'foldInt' in suffix:
						# folded
						folded[ratioref][group][tag][suffix] = emaps[group]['None'][tag].Clone(name)
						folded[ratioref][group][tag][suffix].SetTitle('%s;%s;%s'%(title,x,y))
						if tag=='Num': folded[ratioref][group][tag][suffix].Multiply(ratio[ratioref])
						if 'Rebin' in suffix: folded[ratioref][group][tag][suffix].Rebin2D(1,folded[ratioref][group][tag][suffix].GetNbinsY())
					else:
						# foldedInt
						folded[ratioref][group][tag][suffix] = folded[ratioref][group][tag][suffix.replace('Int','')].Clone(name)
						folded[ratioref][group][tag][suffix].SetTitle('%s;%s;%s'%(title,x,y))
						nbinsX = folded[ratioref][group][tag][suffix].GetNbinsX()
						nbinsY = folded[ratioref][group][tag][suffix].GetNbinsY()
						for ix in range(0,nbinsX+2):
							for iy in range(0,nbinsY+2):
								err = ROOT.Double(0.0)
								val = folded[ratioref][group][tag][suffix].IntegralAndError(ix,nbinsX+1,iy,nbinsY+1,err)
								folded[ratioref][group][tag][suffix].SetBinContent(ix,iy,val)
								folded[ratioref][group][tag][suffix].SetBinError(ix,iy,err)
					# drawing
					drawNsave(fout,folded[ratioref][group][tag][suffix],path,title,'text90,colz,error','Written %s %s (%s%s) to: (eog %s)'%(group,suffix,tag,'*sf' if tag=='Num' else '','plots/%s/%s.png'%(fout.GetName().split('/')[-1].strip(".root"),name)))
		
#4) S over sqrt(S+B)
		print
		l2('S over sqrt(S+B) (%s)'%ratioref)
		SoverSqSpB[ratioref] = {}
		SoverSqSpBScaled[ratioref] = {}
		if 'VBF' in groups and 'QCD' in groups:
			for tag in ['Num','Den']:
				SoverSqSpB[ratioref][tag] = {}
				SoverSqSpBScaled[ratioref][tag] = {}
				for suffix in ['foldInt','foldIntNoSF','foldIntRebin']:
					# path and title
					base = folded[ratioref]['VBF'][tag][suffix].GetName().replace('/VBF/','/').replace('_VBF','').strip(';1').split('/')[-1]
					basepath = '/'.join(folded[ratioref]['VBF'][tag][suffix].GetName().replace('/VBF/','/').replace('_VBF','').strip(';1').split('/')[:-1])
					x    = effs['VBF'][effs['VBF'].keys()[0]][tag].GetXaxis().GetTitle()
					y    = effs['VBF'][effs['VBF'].keys()[0]][tag].GetYaxis().GetTitle()
					title = base.replace('foldInt','SoverSqSpB')
					path  = basepath.replace('foldInt','SoverSqSpB')
					name  = '%s/%s'%(path,title)
					# do
					SoverSqSpB[ratioref][tag][suffix] = folded[ratioref]['VBF'][tag][suffix].Clone(name)
					SoverSqSpB[ratioref][tag][suffix].SetTitle('%s;%s;%s'%(title,x,y))
					nbinsX = folded[ratioref][group][tag][suffix].GetNbinsX()
					nbinsY = folded[ratioref][group][tag][suffix].GetNbinsY()
					for ix in range(0,nbinsX+2):
						for iy in range(0,nbinsY+2):
							s = folded[ratioref]['VBF'][tag][suffix].GetBinContent(ix,iy)
							b = folded[ratioref]['QCD'][tag][suffix].GetBinContent(ix,iy)
							es = folded[ratioref]['VBF'][tag][suffix].GetBinError(ix,iy)
							eb = folded[ratioref]['QCD'][tag][suffix].GetBinError(ix,iy)
							val = s / sqrt(s+b) 
							err = sqrt(((s*s/(4.*((s+b)*(s+b)*(s+b))))*eb*eb) + ((((2.*b+s)*(2.*b+s))/(4.*((s+b)*(s+b)*(s+b))))*es*es))
							SoverSqSpB[ratioref][tag][suffix].SetBinContent(ix,iy,val)
							SoverSqSpB[ratioref][tag][suffix].SetBinError(ix,iy,err)
					SoverSqSpBScaled[ratioref][tag][suffix] = SoverSqSpB[ratioref][tag][suffix].Clone(SoverSqSpB[ratioref][tag][suffix].GetName().replace('SoverSqSpB','SoverSqSpBScaled'))
					SoverSqSpBScaled[ratioref][tag][suffix].SetTitle(SoverSqSpB[ratioref][tag][suffix].GetTitle().replace('SoverSqSpB','SoverSqSpBScaled'))
					SoverSqSpBScaled[ratioref][tag][suffix].Scale(1./(SoverSqSpBScaled[ratioref][tag][suffix].GetBinContent(SoverSqSpBScaled[ratioref][tag][suffix].GetMaximumBin())))
					drawNsave(fout,SoverSqSpB[ratioref][tag][suffix],path,title,'text90,colz,error','Written SoverSqSpB %s (%s) to: (eog plots/%s/%s.png)'%(suffix,tag,fout.GetName().split('/')[-1][:-5],name))
					drawNsave(fout,SoverSqSpBScaled[ratioref][tag][suffix],path.replace('SoverSqSpB','SoverSqSpBScaled'),title.replace('SoverSqSpB','SoverSqSpBScaled'),'text90,colz,error','Written SoverSqSpBScaled %s (%s) to: (eog plots/%s/%s.png)'%(suffix,tag,fout.GetName().split('/')[-1][:-5],name.replace('SoverSqSpB','SoverSqSpBScaled')))
			

####################################################################################################################################################################################

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
