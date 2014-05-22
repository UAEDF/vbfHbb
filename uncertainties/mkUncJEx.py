#!/usr/bin/env python

import os,sys,re,json
from optparse import OptionParser,OptionGroup
from array import array
from time import time
from copy import deepcopy as dc

sys.path.append("../common")
sys.path.append("../fitbias")

from toolkit import *
from write_cuts import *
import main

import ROOT
from ROOT import *

lines = []
legends = []
texts = []
colours = {'Hbb':kBlack,'HbbJESUp':kBlue+1,'HbbJESDn':kRed+1,'HbbJERUp':kViolet+1,'HbbJERCl':kSpring-1,'HbbJERDn':kMagenta+1}
offset = {'Hbb':0,'HbbJESUp':5,'HbbJESDn':-5,'HbbJERUp':-10,'HbbJERCl':-7.5,'HbbJERDn':-5}

SEL = {}
TRG = {}
DTG = {}
REF = {}
WGT = {}
CUT = {}
LAB = {}

##################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()
	mu1 = OptionGroup(mp,"Extra options:")
	mu1.add_option("--tag",help="Tags for selection/trigger set.",default=[],type="str",action="callback",callback=optsplit,dest="tag")
	#mu1.add_option('-c','--categories',help=blue+'Pick for categories.'+plain,dest='categories',type="str",default=[],action='callback',callback=optsplit)
	mu1.add_option('-B','--categoryboundaries',help=blue+'Boundaries for categories.'+plain,dest='categoryboundaries',type="str",default=[[-1.001,0.0,0.25,0.70,0.88,1.001],[-1.001,0.0,0.3,0.65,1.001]],action='callback',callback=optsplitlist)
	mp.add_option_group(mu1)
	return mp 

##################################################
def gethname(weight,var,group,sample,SEL,TRG,DTRG,REF):
	folder1 = '-'.join(sorted(weight))
	folder1 = folder1.replace('#','.')
	folder2 = '_'.join([group,sample])
	folder3 = 's%s_t%s'%('-'.join(sorted(SEL)),'-'.join(sorted(TRG)))
	hname = "hNum_%s-B%s-%s-%s_%s_%s_s%s_t%s_d%s_r%s"%(var['var'],var['nbins_x'],var['xmin'],var['xmax'],group,sample,'-'.join(sorted(SEL)),'-'.join(sorted(TRG)),'-'.join(sorted(DTRG)),'-'.join(sorted(REF)))
	return folder1,folder2,folder3,hname

##################################################
def catveto(cat,var):
	if cat=="NOM" and any(x in var for x in ["mvaVBF","mbbReg2","mqq2"]): return True
	elif cat=="VBF" and any(x in var for x in ["mvaNOM","mbbReg1","mqq1"]): return True
	else: return False

##################################################
def estimate(ientry,nentries,tstart,tnow):
	tdelta   = tnow - tstart
	taverage = tdelta / float(ientry)
	nleft    = float(nentries - ientry) * taverage
	percdone = 100 - float(nentries - ientry) / float(nentries) * 100
	return floor(nleft/60.), nleft%60, percdone

##################################################
def time01(tstart,tnow,previous=[]):
	tdelta    = tnow - tstart
	previous += [tdelta]
	taverage  = sum(previous)/float(len(previous)) 
	return taverage

##################################################
def style01(h,color=kBlack,fill=None,line=1):
	h.SetLineColor(color)
	h.SetLineStyle(line)
	if fill==None: h.SetLineWidth(2)
	if not fill==None: 
		h.SetFillColor(fill)
		h.SetFillStyle(4030)
	return h


##################################################
def func01(tag,c,d,sel="",trg=""):
	sample = d['Hbb'][0].GetName().split('_')[3]
	nh     = d['Hbb'][0].GetName().split('_')[1].split('-')[0]
	ncat = "Hbb"	
	group = "JES" if any(["JES" in x[0].GetName() for x in d.itervalues()]) else "JER"
	c.SetTitle("")

	tit,xtit,ytit = "",d[ncat][0].GetXaxis().GetTitle(),d[ncat][0].GetYaxis().GetTitle()
	#for (incat,ncat) in [(ix,x.GetName().split('_')[3]) for x in enumerate(h)]:
	for hi,fi in d.itervalues(): 
		hi.SetTitle("%s;%s;%s"%(tit,xtit,ytit))
		hi.GetYaxis().SetTickLength(0.015)
		#hi.GetXaxis().SetLimits(50,200)
		#if fi['ful']: fi['ful'].GetXaxis().SetLimits(50,200)
	global lines
	global legends
	global texts
	c.cd()
	p1 = TPad("ptop","ptop",0.0,0.30,1.0,1.0)
	p2 = TPad("pbot","pbot",0.0,0.0,1.0,0.30)
	p1.SetRightMargin(0.22)
	p1.SetBottomMargin(0)
	p1.SetTicks(1,1)
	p2.SetRightMargin(0.22)
	p2.SetTopMargin(0)
	p2.SetTicks(1,1)
	p1.Draw()
	p2.Draw()
	
	c.Update()

	p2.cd()
	p2.SetGrid(1)
	r = {}
	for key in d.keys():
		if key=="Hbb": continue
		r[key] = d[key][0].Clone("r%s"%key)
		r[key].Add(d["Hbb"][0],-1.)
		r[key].Divide(d["Hbb"][0])
		r[key].GetYaxis().SetRangeUser(-0.15,0.15)
		if group == "JES": r[key].SetFillStyle(3003)
		if group == "JES": r[key].SetFillColor(r[key].GetLineColor())
		r[key].GetXaxis().SetTickLength(0.06)
		r[key].GetYaxis().SetTickLength(0.015)
		#r[key].GetYaxis().SetNdivisions(-506)
		r[key].GetYaxis().SetTitle("(shifted - central) / central")
		r[key].GetYaxis().SetTitleSize(30)
		r[key].GetYaxis().SetTitleOffset(r[key].GetYaxis().GetTitleOffset()*1.2)
		r[key].GetYaxis().SetRangeUser(-0.3,0.3)
		#r[key].GetXaxis().SetLimits(50,200)

	for i,ri in enumerate(sorted(r.itervalues(),key=lambda x:('Up' in x.GetName(),'Cl' in x.GetName(),'Dn' in x.GetName()))):
		if i==0: ri.DrawCopy('hist')
		else: ri.DrawCopy('hist,same')

	gPad.Update()
	left,right = 0.79,0.99
	nrows = sum([1 for x in sel])+1
	t2 = getSelLegend(left,0.96-nrows*(0.03/0.3*0.7),right,0.96,None,0,0,1,0.022/0.3*0.7)
	t2.SetTextFont(82)
	for iline,line in enumerate(sorted([x.strip() for x in sel])): t2.AddText('%s %s'%('sel:' if iline==0 else ' '*4, line))
	t2.AddText('trg: %s (MC)'%(','.join(trg)))
	t2.Draw()

	p2.Update()
	lines += [TLine(p2.GetUxmin(),0.,p2.GetUxmax(),0.)]
	lines[-1].SetLineWidth(2)
	lines[-1].SetLineColor(kBlack)
	lines[-1].Draw()
	gPad.Update()
	gPad.WaitPrimitive()

	p1.cd()

	x = sorted([(d[key][0],d[key][0].GetBinContent(d[key][0].GetMaximumBin())) for key in d.keys()],key=lambda (x,y):y)
	x[-1][0].Draw("hist")
	for (hi,fi) in sorted(d.itervalues(),key=lambda x:(not "Hbb_" in x[0].GetName())):
		hi.Draw('hist,same')
		if fi['ful']: 
			fi['ful'].Draw('same')
	
	left,bottom,right,top = 0.79,0.96-0.035*5,0.99,0.96
	t1 = TPaveText(left,bottom,right,top,"NDC")
	t1.SetFillColor(0)
	t1.SetFillStyle(0)
	t1.SetBorderSize(0)
	t1.SetTextSize(0.025)
	t1.SetTextColor(kBlack)
	t1.SetTextAlign(11)
	t1.AddText("CMS preliminary")
	t1.AddText("VBF H#rightarrow b#bar{b}")
	t1.AddText("L = %.1f fb^{-1}"%(19800./1000. if tag=="NOM" else 18300./1000. if tag=="VBF" else -1.))
	t1.AddText("%s selection"%tag)
	t1.AddText("sample: %s"%sample)
	t1.Draw()

	legends += [TLegend(0.79,0.76-(4 if group=="JES" else 5)*0.035,0.985,0.76,"%s variation"%(group))]
	leg = legends[-1]
	leg.SetTextSize(0.025)
	leg.SetFillColor(0)
	leg.SetBorderSize(1)
	leg.AddEntry(d['Hbb'][0],"central","LF")
	if group == "JER":
		for ri in r.itervalues(): leg.AddEntry(ri,"%s smear%s"%(group,'_max' if 'Up' in ri.GetName() else '_min' if 'Dn' in ri.GetName() else ''),"LF")
	else:
		for ri in r.itervalues(): leg.AddEntry(ri,"%s %s"%(group,'up' if 'Up' in ri.GetName() else 'down' if 'Dn' in ri.GetName() else '?'),"L")
	leg.Draw()
	
	nlines = 3 if group=='JES' else 4
	left,bottom,right,top = 0.79,0.5-0.025*(nlines*2+0.5 if 'mbbReg' in nh else nlines),0.99,0.5
	t3 = TPaveText(left,bottom,right,top,"NDC")
	t3.SetFillColor(0)
	t3.SetFillStyle(0)
	t3.SetBorderSize(0)
	t3.SetTextFont(82)
	t3.SetTextSize(0.018)
	t3.SetTextColor(kBlack)
	t3.SetTextAlign(13)
	if 'mbbReg' in nh:
	# Get centers
		t3.AddText("Hbb      x0: %.2f"%d['Hbb'][1]['params'][0])
		if group=='JER': 
			l = t3.AddText("Hbb%sCl x0: %.2f (%.1f%%)"%(group,d['Hbb%sCl'%group][1]['params'][0],abs(d['Hbb%sCl'%group][1]['params'][0]-d['Hbb'][1]['params'][0])*100/d['Hbb'][1]['params'][0]))
			l.SetTextColor(d['Hbb%sCl'%group][0].GetLineColor())
		l = t3.AddText("Hbb%sUp x0: %.2f (%.1f%%)"%(group,d['Hbb%sUp'%group][1]['params'][0],abs(d['Hbb%sUp'%group][1]['params'][0]-d['Hbb'][1]['params'][0])*100/d['Hbb'][1]['params'][0]))
		l.SetTextColor(d['Hbb%sUp'%group][0].GetLineColor())
		l = t3.AddText("Hbb%sDn x0: %.2f (%.1f%%)"%(group,d['Hbb%sDn'%group][1]['params'][0],abs(d['Hbb%sDn'%group][1]['params'][0]-d['Hbb'][1]['params'][0])*100/d['Hbb'][1]['params'][0]))
		l.SetTextColor(d['Hbb%sDn'%group][0].GetLineColor())
		l = t3.AddText("")
		l.SetTextSize(l.GetTextSize()*0.5)
	# Get Ns
	t3.AddText("Hbb      N: %d"%d['Hbb'][0].GetEntries())
	if group=='JER': 
		l = t3.AddText("Hbb%sCl N: %d (%.3f)"%(group,d['Hbb%sCl'%group][0].GetEntries(),d['Hbb%sCl'%group][0].GetEntries()/d['Hbb'][0].GetEntries()))
		l.SetTextColor(d['Hbb%sCl'%group][0].GetLineColor())
	l = t3.AddText("Hbb%sUp N: %d (%.3f)"%(group,d['Hbb%sUp'%group][0].GetEntries(),d['Hbb%sUp'%group][0].GetEntries()/d['Hbb'][0].GetEntries()))
	l.SetTextColor(d['Hbb%sUp'%group][0].GetLineColor())
	l = t3.AddText("Hbb%sDn N: %d (%.3f)"%(group,d['Hbb%sDn'%group][0].GetEntries(),d['Hbb%sDn'%group][0].GetEntries()/d['Hbb'][0].GetEntries()))
	l.SetTextColor(d['Hbb%sDn'%group][0].GetLineColor())
	t3.Draw()

	texts += [t1,t2,t3]
	c.Update()
	return c

##################################################
def mkUncJEx():
	##################################################	
	# initialising
	#print gSystem.Load("../fitbias/fitTF1")
	gSystem.AddIncludePath("-I/opt/Software/include")
	gROOT.ProcessLine(".L ../fitbias/fitTF1.C++")
	opts,fout,variables = main.main(parser(),False,True,False)
	gDirectory.cd("%s:/"%fout.GetName())

	jsoninfo = json.loads(filecontent(opts.jsoninfo))
	jsonsamp = json.loads(filecontent(opts.jsonsamp))
	jsonvars = json.loads(filecontent(opts.jsonvars))
	jsoncuts = json.loads(filecontent(opts.jsoncuts))

	global SEL
	global TRG
	global DTG
	global REF
	global CUT
	global LAB
	global colours
	global offset
	catbounds = {}
	for tag in opts.tag: catbounds[tag] = array('f',opts.categoryboundaries[0]) if tag=="NOM" else array('f',opts.categoryboundaries[1])
	
	if (not len(opts.selection) == len(opts.trigger)) or (not len(opts.selection) == len(opts.tag)): sys.exit("Selection/trigger/tag options are broken. Exiting.")
	for i in range(len(opts.selection)):
		s = opts.selection[i]
		t = opts.trigger[i]
		d = opts.datatrigger[i] if opts.datatrigger and len(opts.datatrigger)>1 else opts.datatrigger[0] if opts.datatrigger else t 
		r = opts.reftrig[i] if opts.reftrig and len(opts.reftrig)>1 else opts.reftrig[0] if opts.reftrig else 'None'
		w = opts.weight[1] if opts.weight else "???"
		tag = opts.tag[i]
		SEL[tag] = s
		TRG[tag] = t
		DTG[tag] = d
		REF[tag] = r
		WGT[tag] = w
		CUT[tag],LAB[tag] = write_cuts(s,t,reftrig=["None"],sample="VBF125",jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal='1')

	##################################################	
	# some ROOT settings
	gStyle.SetOptStat(0)
	gROOT.SetBatch(1)
	TH1.SetDefaultSumw2(1)
	ROOT.gErrorIgnoreLevel = kWarning
	gROOT.ProcessLine("TH1::SetDefaultSumw2(1);")
	gStyle.SetPadTopMargin(0.02)
	gStyle.SetPadBottomMargin(0.18)
	gStyle.SetLabelFont(43,"XYZ")
	gStyle.SetLabelSize(35,"XYZ")
	gStyle.SetTitleFont(43,"XYZ")
	gStyle.SetTitleSize(40,"XYZ")
	gStyle.SetTitleOffset(3.2,"X")
	gStyle.SetTitleOffset(2.0,"Y")
	gStyle.SetLabelOffset(0.020,"X")
	gStyle.SetTitleColor(kBlue+2)
	gStyle.SetTickLength(0.02)
	
	##################################################	
	# reading sample properties
	friends = ["HbbJESUp","HbbJESDn","HbbJERUp","HbbJERDn","HbbJERCl"] 
	sampleproperties = {}
	for s in opts.sample:
		sampleproperties[s] = {}
		sprops = sampleproperties[s]
		# load sample properties
		sprops['tag']    = s
		sprops['group']  = jsoninfo['groups'][s]
		sprops['file']   = [k for (k,v) in jsonsamp['files'].iteritems() if v['tag']==s][0]
		sprops['scale']  = jsonsamp['files'][sprops['file']]['scale']
		sprops['colour'] = jsonsamp['files'][sprops['file']]['colour']
		sprops['tfile']  = TFile(opts.globalpath+'/'+sprops['file'],"read")
		sprops['ttree'] = {}
		for f in ["%s"%x for x in ['Hbb']+friends]: 
			if sprops['tfile'].Get("%s/events"%f): sprops['ttree'][f] = sprops['tfile'].Get("%s/events"%f)
			else: sprops['ttree'][f] = None

		sprops['th1'] = {}
		sprops['tf1'] = {}

		for tag in opts.tag:
			for incat,ncat in enumerate(["%s"%x for x in ['Hbb']+friends]):
				for inh,nh in enumerate(opts.variable):
					key = (tag,ncat,nh)
					sprops[key] = {'th1':None,'tf1':{'ful':None,'bkg':None,'params':None}}
					if incat==0: 
						sprops[(tag,'JES',nh)] = {'tca':None}
						sprops[(tag,'JER',nh)] = {'tca':None}
					
					if catveto(tag,nh): continue
					
					v = variables[nh]['root']
					n = variables[nh]['var']
					xmin = float(variables[nh]['xmin'])
					xmax = float(variables[nh]['xmax'])
					bins = int(variables[nh]['nbins_x'])
					tx = variables[nh]['title_x']
					ty = variables[nh]['title_y']
				
					f1,f2,f3,hname = gethname(WGT[tag],variables[nh],sprops['group'],sprops['tag'],SEL[tag],TRG[tag],DTG[tag],REF[tag])
					hname = hname.replace('hNum','h%s'%ncat)
					
					if "mva" in v: sprops[key]['th1'] = TH1F(hname,"%s;%s;%s"%(hname,tx,ty),len(catbounds[tag])-1,catbounds[tag])
					else: sprops[key]['th1'] = TH1F(hname,"%s;%s;%s"%(hname,tx,ty),bins,xmin,xmax)
					sprops[key]['th1'].Sumw2()
					if incat==0: 
						sprops[(tag,'JES',nh)]['tca'] = TCanvas(hname.replace('h%s'%ncat,'cJES'),hname.replace('h%s'%ncat,'cJES'),1800,1800)
						sprops[(tag,'JER',nh)]['tca'] = TCanvas(hname.replace('h%s'%ncat,'cJER'),hname.replace('h%s'%ncat,'cJER'),1800,1800)

	# summarize load block
	l1("Loaded properties for:")
	print "%s%12s | %12s | %8s | %15s | %40s | %15s | %15s | %55s |%s"%(blue,"tag","group","colour","scale","file","tree name","object type","alternatives",plain)
	print "-"*(15*2 + 11 + 18 + 43 + 36 + 58 - 1)
	for sp in sampleproperties.itervalues():
		print "%12s | %12s | %8s | %15s | %40s | %15s | %15s | %55s |"%( \
				sp["tag"],sp["group"],sp["colour"],sp["scale"],sp["file"], \
				sp["ttree"]["Hbb"].GetName() if not sp["ttree"]["Hbb"]==None else "%s%15s%s"%(Red,"None",plain), \
				sp["ttree"]["Hbb"].IsA().GetName() if not sp["ttree"]["Hbb"]==None else "%s%15s%s"%(Red,"None",plain), \
				", ".join([x for x in sprops["ttree"].keys()]) if len(sprops["ttree"].keys())>0 else "%s%30s%s"%(Red,"None",plain) \
				)
	
	# summarize selections & triggers:
	l1("Running these selections:")
	for tag in opts.tag:
		print "%s%s%s: %s\n\t%s%s%s"%(Black,tag,plain,LAB[tag],grey,CUT[tag],plain)
	
	##################################################	
	# loop
	makeDirs("plots/uncertainties")
	f0 = "histos"

	for isp,sp in enumerate(sampleproperties.itervalues()):
		# start
		stag = sp['tag']
		l1("Working with sample: %s"%stag)
		sp['tfile'].cd()
		tarray = []

		for tag in opts.tag:
			for incat,ncat in enumerate(["%s"%x for x in ["Hbb"]+friends]):
				l2("Category %s (%s)"%(ncat,tag))
				tree = sp['ttree'][ncat]
				treedraw = tree.Draw
				for inh,(nhf,nhr,nh) in enumerate([(variables[x],variables[x]['root'],variables[x]['var']) for x in opts.variable]):
					f1,f2,f3,hname = gethname(WGT[tag],nhf,sp['group'],sp['tag'],SEL[tag],TRG[tag],DTG[tag],REF[tag])
					hname = hname.replace('hNum','h%s'%ncat)
					makeDirsRoot(fout,'%s/%s/%s/%s'%(f0,f1,f2,f3))

					sp['tfile'].cd()
					if catveto(tag,nh): continue

#					tstart = time()
#					if (isp==0 and incat==len(["%s"%x for x in ["Hbb"]+friends])-1 and inh==len(variables)-1): average = tarray[-1]
#					l3("%-40s %-40s"%("Variable %s"%nh,"(time expected %.fs + %d modules)"%(tarray[-1]*((5-inh)+(4-incat)*5) if len(tarray)>0 else -999,len(sampleproperties)-isp-1)))
					l3("%-40s"%("Variable %s"%nh))
					
					if "JER" in ncat: sp[(tag,'JER',nh)]['tca'].cd()
					else: sp[(tag,'JES',nh)]['tca'].cd()
		
					if fout.Get("%s/%s/%s/%s/%s;1"%(f0,f1,f2,f3,hname)):
						l4('%sLoading%s: %s \n%s%s(%s/%s/%s/%s)%s'%(red,plain,hname,grey,' '*9,f0,f1,f2,f3,plain))
						sp[(tag,ncat,nh)]['th1'] = fout.Get("%s/%s/%s/%s/%s;1"%(f0,f1,f2,f3,hname)).Clone()	
#						sp[(tag,ncat,nh)]['th1'].Sumw2()	
					else:
						l4('%sCreating%s: %s \n%s%s(%s/%s/%s/%s)%s'%(red,plain,hname,grey,' '*9,f0,f1,f2,f3,plain))
						treedraw("%s>>%s"%(nhr,sp[(tag,ncat,nh)]['th1'].GetName()),CUT[tag])
						oldwd = gDirectory.GetPath()
						gDirectory.cd("%s:/%s/%s/%s/%s/"%(fout.GetName(),f0,f1,f2,f3))
						sp[(tag,ncat,nh)]['th1'].Write(sp[(tag,ncat,nh)]['th1'].GetName(),TH1.kOverwrite)
						gDirectory.cd(oldwd)
					#tnow = time()
					#tarray += [time01(tstart,tnow,tarray)]

					if 'mbbReg' in nh:
						gROOT.ProcessLineSync('TCanvas *can = new TCanvas("%s","%s",1800,1800)'%(sp[(tag,ncat,nh)]['th1'].GetName()[:100],sp[(tag,ncat,nh)]['th1'].GetName()[:100]))
						gROOT.ProcessLineSync('TH1F hroot = (TH1F)gDirectory->FindObjectAny("%s").Clone("%s")'%(sp[(tag,ncat,nh)]['th1'].GetName(),sp[(tag,ncat,nh)]['th1'].GetName()[:100]))
						gROOT.ProcessLineSync('double params[8] = {0.,0.,0.,0.,0.,0.,0.,0.}')
						gROOT.ProcessLineSync('fitTF1(can,hroot,%.2f,%.2f,%.2f,params,%i)'%(110.+offset[ncat],140.+offset[ncat],(float(variables[nh]['xmax'])-float(variables[nh]['xmin']))/float(variables[nh]['nbins_x']),colours[ncat]))
						sp[(tag,ncat,nh)]['tf1']['params'] = dc(list(ROOT.params))
						count = 0
						for i in ROOT.can.GetListOfPrimitives():
							if i.IsA().GetName() == "RooCurve" and count==0:
								sp[(tag,ncat,nh)]['tf1']['ful'] = i.Clone()
								count += 1
							elif i.IsA().GetName() == "RooCurve" and count==1:
								sp[(tag,ncat,nh)]['tf1']['bkg'] = i.Clone()
								count += 1
								break
						gROOT.ProcessLineSync('can.Close()')

					
			for inh,nh in enumerate([variables[x]['var'] for x in opts.variable]):
				if catveto(tag,nh): continue
	
				# JES Up/Dn
				sp[(tag,'Hbb',nh)]['th1']      = style01(sp[(tag,'Hbb',nh)]['th1'],kBlack,kGray)
				sp[(tag,'HbbJESUp',nh)]['th1'] = style01(sp[(tag,'HbbJESUp',nh)]['th1'],kBlue+1,None,1)#7
				sp[(tag,'HbbJESDn',nh)]['th1'] = style01(sp[(tag,'HbbJESDn',nh)]['th1'],kRed+1,None,1)#10
				sp[(tag,'JES',nh)]['tca']      = func01(tag,sp[(tag,'JES',nh)]['tca'],dict((y,(sp[(tag,y,nh)]['th1'],sp[(tag,y,nh)]['tf1'])) for y in ['Hbb','HbbJESUp','HbbJESDn']),SEL[tag],TRG[tag]) 

				# JER Up/Dn
				sp[(tag,'HbbJERUp',nh)]['th1'] = style01(sp[(tag,'HbbJERUp',nh)]['th1'],kViolet+1,None,1)#7
				sp[(tag,'HbbJERCl',nh)]['th1'] = style01(sp[(tag,'HbbJERCl',nh)]['th1'],kSpring-1,None,1)#7
				sp[(tag,'HbbJERDn',nh)]['th1'] = style01(sp[(tag,'HbbJERDn',nh)]['th1'],kMagenta+1,None,9)#10
				sp[(tag,'JER',nh)]['tca']      = func01(tag,sp[(tag,'JER',nh)]['tca'],dict((y,(sp[(tag,y,nh)]['th1'],sp[(tag,y,nh)]['tf1'])) for y in ['Hbb','HbbJERUp','HbbJERCl','HbbJERDn']),SEL[tag],TRG[tag]) 

				#gDirectory.cd("%s:/"%fout.GetName())
				#makeDirsRoot(fout,"histos/%s"%stag)
				#gDirectory.cd("%s:/histos/%s"%(fout.GetName(),stag))
				#for ncat in ["%s"%x for x in ["Hbb"]+friends]: sp[(tag,ncat,nh)]['th1'].Write("%s"%(sp[(tag,ncat,nh)]['th1'].GetName()),TH1.kOverwrite)

				gDirectory.cd("%s:/"%fout.GetName())
				makeDirsRoot(fout,"canvas/%s"%stag)
				gDirectory.cd("%s:/canvas/%s"%(fout.GetName(),stag))
				sp[(tag,'JES',nh)]['tca'].Update()
				sp[(tag,'JES',nh)]['tca'].Write("%s"%(sp[(tag,'JES',nh)]['tca'].GetName()),TH1.kOverwrite)
				sp[(tag,'JER',nh)]['tca'].Update()
				sp[(tag,'JER',nh)]['tca'].Write("%s"%(sp[(tag,'JER',nh)]['tca'].GetName()),TH1.kOverwrite)

				sp[(tag,'JES',nh)]['tca'].Update()
				sp[(tag,'JES',nh)]['tca'].SaveAs("plots/uncertainties/%s.pdf"%sp[(tag,'JES',nh)]['tca'].GetName())
				sp[(tag,'JES',nh)]['tca'].Close()
				sp[(tag,'JER',nh)]['tca'].Update()
				sp[(tag,'JER',nh)]['tca'].SaveAs("plots/uncertainties/%s.pdf"%sp[(tag,'JER',nh)]['tca'].GetName())
				sp[(tag,'JER',nh)]['tca'].Close()
				
		sp['tfile'].Close()

	##################################################	
	fout.Close()
	##################################################	
	l1("Main Done.")

##################################################
if __name__=="__main__":
	mkUncJEx()
