#!/usr/bin/env python

import sys,re,os
from glob import glob
from optparse import OptionParser
tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

def mapdrawopts(h,parsedargs):
    h.GetXaxis().SetLabelFont(43)
    h.GetYaxis().SetLabelFont(43)
    h.GetZaxis().SetLabelFont(43)
    h.GetXaxis().SetTitleFont(43)
    h.GetYaxis().SetTitleFont(43)
    h.GetZaxis().SetTitleFont(43)
    h.GetXaxis().SetLabelColor(kBlack)
    h.GetYaxis().SetLabelColor(kBlack)
    h.GetZaxis().SetLabelColor(kBlack)
    h.GetXaxis().SetTitleColor(kBlack)
    h.GetYaxis().SetTitleColor(kBlack)
    h.GetZaxis().SetTitleColor(kBlack)
    h.GetXaxis().SetLabelSize(32)
    h.GetYaxis().SetLabelSize(32)
    h.GetZaxis().SetLabelSize(28)
    h.GetXaxis().SetTitleSize(38)
    h.GetYaxis().SetTitleSize(38)
    h.GetZaxis().SetTitleSize(32)
    val = min(floor(log10(h.GetMaximum())),2)
    if "val" in parsedargs: val=int(parsedargs["val"])
    h.GetXaxis().SetLabelOffset(0.0+(val-1)*0.007)
    h.GetXaxis().SetTitleOffset(1.05-(val-1)*0.05)
    h.GetYaxis().SetTitleOffset(0.4+0.45*val)
#    h.GetXaxis().SetNdivisions(210)
    h.GetYaxis().SetNdivisions(210)
    h.GetYaxis().SetTickSize(0.015)
    h.GetXaxis().SetTitle(str(input("title x? ")) if not 'title x' in parsedargs else parsedargs['title x'])
    h.GetYaxis().SetTitle(str(input("title y? ")) if not 'title y' in parsedargs else parsedargs['title y'])
    h.SetMarkerSize(h.GetMarkerSize()*1.2)
    if "norm" in parsedargs and int(parsedargs["norm"])==1: h.Scale(1./h.Integral())
    if 'm_{q#bar{q}}' in h.GetXaxis().GetTitle(): 
        gPad.SetLogx(1)
        h.GetXaxis().SetMoreLogLabels(1)
    gPad.SetLeftMargin(0.11+0.03*(val-1))    
    gPad.SetRightMargin(0.13)   
    gPad.SetTopMargin(0.06)
    gPad.SetBottomMargin(0.115)
    gPad.Modified()

def main(opts,args):
# ROOT settings
    gROOT.SetBatch(1)
    gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
    gStyle.SetPalette(20)
    gStyle.SetPaintTextFormat("7.2f")

# Arguments
    parsedargs = {}
    otherargs = []
    while(args):
        a = args.pop(0)
        if ':' in a: parsedargs[a.split(':')[0]] = a.split(':')[1]
        else: otherargs.append(a)
    print(otherargs)

# Get File
    flist = glob("rootfiles/*.root")
    for fi,f in enumerate(sorted(flist)):
        print("%3d) %-s"%(fi+1,f))
    if not len(otherargs)==2: fj = int(input("File choice? "))
    else: fj = int(otherargs[0])
    fn = sorted(flist)[fj-1]
    f  = TFile(fn,"read")
    print()
    print(fn)
    print()

# Get Entry
    elist2 = [x.GetName() for x in f.GetListOfKeys()]
    elist1 = []
    elist  = []
    while(elist2):
        e = elist2.pop()
        o = f.Get(e)
        if o.IsFolder(): elist1 += [e+"/"+x.GetName() for x in o.GetListOfKeys()]
        else: elist1 += [e]
    while(elist1):
        e = elist1.pop()
        o = f.Get(e)
        if o.IsFolder(): elist += [e+"/"+x.GetName() for x in o.GetListOfKeys()]
        else: elist += [e]
    for ei,e in enumerate(sorted(elist)):
        print("%3d) %-s"%(ei+1,e))
    if not len(otherargs)==2: ej = int(input("Entry choice? "))
    else: ej = int(otherargs[1])
    en = sorted(elist)[ej-1]
    e  = f.Get(en) 
    print()
    print(en)
    print()

# Draw plot
    c = TCanvas("c","c",900,750)
    drawopts = str(input("Draw options? ")) if not 'drawopts' in parsedargs else parsedargs['drawopts']
    e.Draw(drawopts)
    mapdrawopts(e,parsedargs)
    p = TPaveText(gPad.GetLeftMargin()+0.04,0.5,0.4,1.-gPad.GetTopMargin()-0.04,"NDC")
    for t in parsedargs['text'].split(','):
        p.AddText(t)
    p.SetTextSize(0.05)
    p.SetTextColor(int(parsedargs['colour']))
    p.SetTextAlign(12)
    p.SetBorderSize(0)
    p.SetFillStyle(-1)
    p.Draw()
    gPad.Update()
    p.SetY1NDC(p.GetY2NDC()-p.GetListOfLines().GetSize()*0.06)
    p.Draw()

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
    pcms2.AddText("%.1f fb^{-1} (8 TeV)"%(19.8 if 'Set A' in parsedargs['text'] else 18.3))
    pcms2.Draw()

    gPad.RedrawAxis()
    savename = str(input("Filename? ")) if not 'savename' in parsedargs else parsedargs['savename']
    if not os.path.exists("plots/printSingleChoice"): os.makedirs("plots/printSingleChoice")
    c.SaveAs("plots/printSingleChoice/"+savename)

# Clean    
    c.Close()
    f.Close()

if __name__=='__main__':
    mp = OptionParser()
    opts,args = mp.parse_args()
    main(opts,args)


