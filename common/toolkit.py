#!/usr/bin/env python

import sys,os,json
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath)

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv


# PRINTING #########################################################################################
def l1(text):
	print blue+'\n+ %s'%(text)+plain
def l2(text):
	print purple+'  ++ %s'%(text)+plain
def l3(text):
	print plain+'  ++++ %s'%(text)+plain

# COLORS ########################################################################################## 
red 	= "\033[0;31m"
green	= "\033[0;32m"
yellow	= "\033[0;33m"
blue	= "\033[0;34m"
purple	= "\033[0;35m"
cyan	= "\033[0;36m"
Red		= "\033[1;31m"
Green	= "\033[1;32m"
Yellow	= "\033[1;33m"
Blue	= "\033[1;34m"
Purple	= "\033[1;35m"
Cyan	= "\033[1;36m"
plain	= "\033[m"


# ACCESS FILE CONTENT ##############################################################################
def filecontent(fname):
	f = file(fname,'r')
	content = f.read()
	f.close()
	return content


# RUN inside ROOT ##################################################################################
def inroot(cmd):
	gROOT.ProcessLineSync(cmd)


# SPLIT COMMA SEPARATED OPTION LIST ################################################################
def optsplitlist(option,opt,value,parser):
#	if ';' in value: setattr(parser.values, option.dest, [x.split(';') for x in value.split(',')])
#	else: setattr(parser.values, option.dest, [value.split(',')])
	setattr(parser.values, option.dest, [x.split(';') for x in value.split(',')])

def optsplit(option,opt,value,parser):
	setattr(parser.values, option.dest, value.split(','))

def setdefaults(option,opt,value,parser):
	jsondefaults = json.loads(filecontent(value))
	for ok,oval in jsondefaults.iteritems():
		if '.json' in oval: oval = os.path.join(basepath,oval)
		setattr(parser.values, ok, oval)
		l2("Set from opts file: %s --> %s"%(ok,oval))

# SAVING HELPER FUNCTIONS ##########################################################################
def makeDirsRoot(fout,ndir):
	gDirectory.cd('%s:/'%fout.GetName())
	for i in range(len(ndir.split('/'))+1):
		ipath = '/'.join(ndir.split('/')[0:i])
		if not gDirectory.GetDirectory('/%s'%ipath): gDirectory.mkdir('%s'%ipath)

def makeDirs(ndir):
	if not os.path.exists(ndir): os.makedirs(ndir)


# PLOTTING/LAYOUT HELPER FUNCTIONS #################################################################
def getTLegend(left,bottom,right,top,columns=None,header=None,fillStyle=0,textColor=1,textSize=0.025):
	legend = TLegend(left,bottom,right,top)
	if not header==None: legend.SetHeader(header)
	if not columns==None: legend.SetNColumns(int(columns))
	legend.SetFillStyle(fillStyle)
	legend.SetTextColor(textColor)
	legend.SetTextSize(textSize)
	return legend

def getTPave(left,bottom,right,top,rows=None,fillColor=0,fillStyle=0,textColor=1,textSize=0.025):
	text = TPaveText(left,bottom,right,top,"NDC")
	text.SetFillColor(fillColor)
	text.SetFillStyle(fillStyle)
	text.SetTextColor(textColor)
	text.SetTextSize(textSize)
	text.SetTextAlign(13)
	text.SetBorderSize(0)
	return text

def setStyleTH1F(h,lineColor=1,lineStyle=1,fillColor=0,fillStyle=0,markerColor=1,markerStyle=0,lineWidth=3,markerSize=3):
	h.SetLineColor(lineColor)
	h.SetLineStyle(lineStyle)
	h.SetLineWidth(lineWidth)
	h.SetFillColor(fillColor)
	h.SetFillStyle(fillStyle)
	h.SetMarkerColor(markerColor)
	h.SetMarkerStyle(markerStyle)
	h.SetMarkerSize(markerSize)

def getRangeTH1F(h,ymin,ymax):
	if h.GetMaximum() > ymax: ymax = h.GetMaximum()
	if h.GetMinimum() < ymin: ymin = h.GetMinimum()
	return ymin,ymax

def setRangeTH1F(h,ymin,ymax,log=True):
	if log:
		h.SetMinimum(float("1e%i"%log10(ymin+0.1)))
		h.SetMaximum(float("1e%i"%(log10(ymax)+3)))
	else:
		h.SetMinimum(0)
		h.SetMaximum(round(ymax*1.3,2))

def getRatioPlotCanvas(canvas):
	c1 = TPad('c1','c1',0,0.2,1,1)
	c2 = TPad('c2','c2',0,0,1,0.2)
	c1.SetBottomMargin(0.0)
	c2.SetTopMargin(0.0)
	c2.SetBottomMargin(c2.GetBottomMargin()+0.1)
	c1.Draw()
	c2.Draw()
	canvas.Update()
	return c1,c2

def setStyleTH1Fratio(h):
	# main
	h.SetTitle("")
	h.GetYaxis().SetTitle('Data / MC')
	#h.GetYaxis().SetRangeUser(0.5,1.5)
	h.GetYaxis().SetRangeUser(0.0,2.0)
	h.GetYaxis().SetNdivisions(505)
	# fonts & offsets
	h.SetTitleOffset(3.25,'X')
	# filling
#	h.SetFillColor(kGray)
#	h.SetFillStyle(1)
	h.SetMarkerStyle(20)
	h.SetMarkerColor(kBlack)
	h.SetMarkerSize(2)

# PRINTOUT FUNCTIONS ###############################################################################
def write_bMapWght(bMapWghtFile='%s/bMapWght.root'%basepath):
	fmap = TFile.Open(bMapWghtFile)
	bmap = fmap.Get("bMap;1")
	bmaparray = []
	bmaplabels = []
	for iy in range(1,bmap.GetYaxis().GetNbins()+1):
		bmaparray += [[]]
		bmaplabels += [round(bmap.GetYaxis().GetBinLowEdge(iy),3)]
		for ix in range(1,bmap.GetXaxis().GetNbins()+1):
			bmaparray[iy-1] += [round(bmap.GetBinContent(ix,iy),4)]
	bmaplabels += [round(bmap.GetYaxis().GetBinLowEdge(iy)+bmap.GetYaxis().GetBinWidth(iy),3)]

	print "double csvBins[5] = {%s};"%(','.join([str(x) for x in bmaplabels]))
	print "double trig_eff[4][4] = %s;"%json.dumps(bmaparray).replace('[','{').replace(']','}')

