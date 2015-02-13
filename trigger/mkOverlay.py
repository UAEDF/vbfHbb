#!/usr/bin/env python

import ROOT
from ROOT import *

from optparse import OptionParser,OptionGroup
import os,re,sys
basedir = os.getcwd()
sys.path.append('%s/../common'%basedir)

from toolkit import *

# OPTION PARSER ####################################################################################
def parser(mp=None):
    if mp==None: mp = OptionParser()

    mgm  = OptionGroup(mp,cyan+"Main options"+plain)
    mgm.add_option('-o','--outputfile',help=blue+"Name of output file."+plain,dest='outputfile',default="%s/../trigger/rootfiles/vbfHbb.root"%basepath)

    mgtc = OptionGroup(mp,cyan+"Trigger uncertainty settings"+plain)
    mgtc.add_option('--files',help=blue+'Filenames for scalefactor plots (comma separated).'+plain,dest='files',default=[],type="str",action="callback",callback=optsplit)
    mgtc.add_option('--tags',help=blue+'Tags for the different overlays (comma separated).'+plain,dest='tags',default=[],type="str",action="callback",callback=optsplit)
    mgtc.add_option('--notext',help=blue+'No legend block at the right.'+plain,dest='notext',default=False,action="store_true")

    mp.add_option_group(mgm)
    mp.add_option_group(mgtc)
    return mp

####################################################################################################

def getMaps(opts,fout):
	l1("Reading scalefactor data from files.")
	fin = []
	for fname in opts.files:
		fin += [TFile(fname,"read")]
	
	maps = {}
	paves = {}
	for f in fin:
		fname = f.GetName()
		gDirectory.cd("%s:%s"%(fname,"/ScaleFactors/"))
		for key in gDirectory.GetListOfKeys():
			keyname = key.GetName()
			if not "ScaleFactors1D" in keyname: continue
			tag = re.search("ScaleFactors1D_(.*)",keyname).group(1)
			if not tag in maps: 
				maps[tag] = {}
				paves[tag] = {}
			fout.cd()
			maps[tag][fname] = f.Get("ScaleFactors/"+keyname).Clone()
			ctmp = f.Get("Canvases/"+keyname).Clone()
			paves[tag][fname] = extractPaves(ctmp)
			l2("Read %s%-30s%s from %s%-70s%s (%s)."%(Blue,keyname,purple,plain,fname,purple,maps[tag][fname]))
		print
		f.Close()

	return maps,paves

####################################################################################################
def plotMaps(opts,fout,maps,paves):
	l1("Plotting overlayed scalefactor data.")
	makeDirs("%s/plots/%s/TriggerUncertainty/"%(basedir,fout.GetName().split('/')[-1][:-5]))
	
	colors = [kBlue, kRed, kGreen, kOrange]
	styles = [3254, 3245, 3259, 3295]
	files = []
	for fs in [x.keys() for x in maps.itervalues()]: files += fs
	files = list(set(files))
	
	for tag,content in sorted(maps.iteritems()):
		l2("Plotting %s%-10s%s to %s%-70s%s"%(Blue,tag,purple,plain,"./plots/%s/TriggerUncertainty/ScaleFactors1D_%s.png"%(fout.GetName().split('/')[-1][:-5],tag),purple))
		if not all([f in content.keys() for f in files]): continue
		c = TCanvas("c","c",1800 if not opts.notext else 1600,1200)
		c.cd()
		gPad.SetRightMargin(0.2 if not opts.notext else 0.08)
		labels = []
		pave = None
		for fi,f in enumerate(files):
			h = content[f]
			c.SetName(h.GetName())
			h.SetTitle("")
			h.GetYaxis().SetTitle("Trigger Scale Factor")
			h.GetYaxis().SetTitleOffset(1.0)
			h.GetYaxis().SetRangeUser(0,1.2)
			h.GetXaxis().SetLabelSize(0.05)
			h.SetLineWidth(3)
			h.SetLineColor(colors[fi])

			h.DrawCopy("" if fi==0 else "same")
			h.SetFillColor(colors[fi])
			h.SetFillStyle(styles[fi])
			h.Draw("e2same") #text70
		
			gPad.Update()
			for i in range(1,h.GetNbinsX()+1):
				if not 'ALL' in h.GetXaxis().GetBinLabel(i) and float(re.search('([A-Z]*)([0-9+-]*)',h.GetXaxis().GetBinLabel(i)).group(2))<0:
					ctr = h.GetXaxis().GetBinCenter(i)
					wid = h.GetXaxis().GetBinWidth(i)
					pave = TPave(ctr-wid/2.,gPad.GetUymin(),ctr+wid/2.,gPad.GetUymax())
					pave.SetFillColor(kGray+1)
					pave.SetFillStyle(3003)
					pave.Draw("same")
				if h.GetBinContent(i)==0: continue
				for text in setLabel(i-h.GetBinWidth(i)/2.,h.GetBinContent(i),["%.3f"%h.GetBinContent(i),"#pm %.3f"%h.GetBinError(i)],fi):
					labels += [text]
					labels[-1].SetTextColor(TColor.GetColorDark(colors[fi]))
					labels[-1].Draw("same")

		sampleinfo = editPaves([paves[tag][x]["sampleinfo"] for x in paves[tag].keys()],colors,'#varepsilon')
		sampleinfo.SetTextFont(62)
		if not opts.notext: sampleinfo.Draw("same")
		else:
			updated = []
			for key in sampleinfo.GetListOfLines():
				if any([x in key.GetTitle() for x in ['selection','2D map:','sample:']]): updated += [key.GetTitle()]
			sampleinfo.Clear()
			sampleinfo.SetTextSize(sampleinfo.GetTextSize()*1.4)
			for u in updated: sampleinfo.AddText(u)
			sampleinfo.SetX1NDC(0.30)
			sampleinfo.SetX2NDC(0.60)
			sampleinfo.SetY1NDC(0.15)
			sampleinfo.SetY2NDC(0.30)
			sampleinfo.Draw("same")
		selinfo = editPaves([paves[tag][x]["selinfo"] for x in paves[tag].keys()],colors,'trg:')
		y1samp = sampleinfo.GetY1NDC()
		y1sel = selinfo.GetY1NDC()
		y2sel = selinfo.GetY2NDC()
		selinfo.SetY2NDC(y1samp-0.04)
		selinfo.SetY1NDC(y1samp-0.04-abs(y1sel-y2sel))
		if not opts.notext: selinfo.Draw("same")

		x1,x2,y1,y2 = selinfo.GetX1NDC(),selinfo.GetX2NDC(),selinfo.GetY1NDC(),selinfo.GetY2NDC()
		y2 = selinfo.GetY1NDC()-0.04
		y1 = y2 - 0.030*(len(opts.tags)+1)
		overlayinfo = TLegend(x1,y1,x2,y2)
		overlayinfo.SetTextSize(0.020 if not opts.notext else 0.026)
		overlayinfo.SetTextFont(62)
		overlayinfo.SetHeader("Scale Factors")
		overlayinfo.SetTextFont(42)
		overlayinfo.SetFillStyle(0)
		overlayinfo.SetBorderSize(0)

		for ih,h in enumerate(content.itervalues()): overlayinfo.AddEntry(h,opts.tags[ih],"L")
		if opts.notext: 
			overlayinfo.SetX1(0.50)
			overlayinfo.SetX2(0.75)
			overlayinfo.SetY1(0.20)
			overlayinfo.SetY2(0.30)
			gPad.Update()
		overlayinfo.Draw("same")

		line = TLine(h.GetNbinsX()-1,0.0,h.GetNbinsX()-1,gPad.GetUymax())
		line.SetLineWidth(4)
		line.Draw("same")
                
                pcms1 = TPaveText(gPad.GetLeftMargin(),1.-gPad.GetTopMargin(),0.3,1.,"NDC")
                pcms1.SetTextAlign(12)
                pcms1.SetTextFont(62)
                pcms1.SetTextSize(gPad.GetTopMargin()*2.5/4.0)
                pcms1.SetFillStyle(-1)
                pcms1.SetBorderSize(0)
                pcms1.AddText("CMS")
                pcms1.Draw()
                
                pcms2 = TPaveText(0.6,1.-gPad.GetTopMargin(),1.-gPad.GetRightMargin()-0.015,1.,"NDC")
                pcms2.SetTextAlign(32)
                pcms2.SetTextFont(62)
                pcms2.SetTextSize(gPad.GetTopMargin()*2.5/4.0)
                pcms2.SetFillStyle(-1)
                pcms2.SetBorderSize(0)
                pcms2.AddText("%.1f fb^{-1} (8 TeV)"%(19.8 if 'NOM' in fout.GetName() else 18.3))
                pcms2.Draw()
                pcms2.Print()

		c.Update()
		c.SaveAs("%s/plots/%s/TriggerUncertainty/%s%s.pdf"%(basedir,fout.GetName().split('/')[-1][:-5],c.GetName(),'' if not opts.notext else '_noleg'))	
		c.SaveAs("%s/plots/%s/TriggerUncertainty/%s%s.png"%(basedir,fout.GetName().split('/')[-1][:-5],c.GetName(),'' if not opts.notext else '_noleg'))	
		c.Close()

	return 0

####################################################################################################
def setLabel(xcenter,ycenter,lines,position=0): # nw ne se sw
	text = []
	if position>3: position = position%4
	for iline,line in enumerate(lines):
		lineskip = 0.12*iline
		if position in [0,1]: 
			y    = ycenter - 0.1
			yend = ycenter + 0.2
		elif position in [2,3]:
			y    = ycenter + 0.1
			yend = ycenter - 0.2
		if position in [0,3]:
			x    = xcenter - 0.30 + lineskip 
			xend = xcenter - 0.20 + lineskip
		elif position in [1,2]:
			x    = xcenter + 0.20 + lineskip 
			xend = xcenter + 0.30 + lineskip
		text += [TPaveText(x,y,xend,yend)]
		text[-1].SetFillStyle(0)
		text[-1].SetBorderSize(0)
		text[-1].SetTextSize(0.028)
		text[-1].SetTextAlign(12)
		theline = text[-1].AddText(line)
		theline.SetTextAngle(90)
	return text

####################################################################################################
def extractPaves(canvas):
	tag = False
	paves = {}
	labels = ["sampleinfo","selinfo"]
	index = 0
	if len(canvas.GetListOfPrimitives())<10: sys.exit("mkTriggerUncertainty canvases have to be created WITHOUT option noleg for this!")
	for ikey,key in enumerate(canvas.GetListOfPrimitives()):
		keyname = key.GetName()
		if "TLine" in keyname: tag=True
		if tag==False: continue
		elif "TPave" in keyname: 
			paves[labels[index]] = key.Clone()
			index += 1
	return paves

####################################################################################################
def editPaves(paves,colors,passkey):
	mainpave = paves[0].Clone()
	y1 = mainpave.GetY1NDC()
	y2 = mainpave.GetY2NDC()
	nl = len(mainpave.GetListOfLines())
	mainpave.Clear()
	# first run
	passline = False
	for iline,line in enumerate(paves[0].GetListOfLines()):
		if passkey in line.GetTitle(): passline=True
		if passline==True: break
		thisline = mainpave.AddText(line.GetTitle())
		if not any([line.GetTitle()==x.GetTitle() for x in paves[1].GetListOfLines()]):	thisline.SetTextColor(colors[0])
	passline = False
	for iline,line in enumerate(paves[1].GetListOfLines()):
		if passkey in line.GetTitle(): passline=True
		if passline==True: break
		if not any([line.GetTitle()==x.GetTitle() for x in mainpave.GetListOfLines()]): 
			thisline = mainpave.AddText(line.GetTitle())
			thisline.SetTextColor(colors[1])
	# second  run (seltrg split)
	passline = False
	for iline,line in enumerate(paves[0].GetListOfLines()):
		if passkey in line.GetTitle(): passline=True
		if passline==False: continue
		thisline = mainpave.AddText(line.GetTitle())
		if not any([line.GetTitle()==x.GetTitle() for x in paves[1].GetListOfLines()]):	thisline.SetTextColor(colors[0])
	passline = False
	for iline,line in enumerate(paves[1].GetListOfLines()):
		if passkey in line.GetTitle(): passline=True
		if passline==False: continue
		if not any([line.GetTitle()==x.GetTitle() for x in mainpave.GetListOfLines()]): 
			thisline = mainpave.AddText(line.GetTitle())
			thisline.SetTextColor(colors[1])
	nlprime = len(mainpave.GetListOfLines())
	dline = abs(y2 - y1)/float(nl)
	y1prime = y2 - dline*nlprime
	mainpave.SetY1NDC(y1prime)
	return mainpave

####################################################################################################
def mkOverlay():
	## init main (including option parsing)
	#opts,samples,variables,loadedSamples,fout,KFWghts = main.main(parser())
	mp = parser()
	opts,args = mp.parse_args()
	
	fout = TFile(opts.outputfile,"recreate")
	gROOT.ProcessLine("gErrorIgnoreLevel = kWarning;")
	gROOT.SetBatch(1)
	gStyle.SetOptStat(0)
	
	maps,paves = getMaps(opts,fout)
	plotMaps(opts,fout,maps,paves)
	
	fout.Close()

if __name__=='__main__':
    mkOverlay()

