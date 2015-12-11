#!/usr/bin/env python

import ROOT
from ROOT import *
from math import *

global paves
paves = []

####################################################################################################
def epave(text,x,y,pos="left",hl=0,color=kBlack,size=0):
    global paves
    p = TLatex(x,y,text)
    p.SetNDC()
    p.SetTextSize(size if not size==0 else 0.037)
    p.SetTextFont(42 if not hl else 62)
    p.SetTextAlign(12 if pos=="left" else (32 if pos=="right" else 22))
    p.SetTextColor(color)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def tpave(text,pos="left",hl=0,color=kBlack,size=0):
    global paves
    if pos=="left": p = TLatex(gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),text)
    elif pos=="right": p = TLatex(1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),text)
    else: p = TLatex(0.5,1.-0.5*gStyle.GetPadTopMargin(),text)
    p.SetNDC()
    p.SetTextSize(0.75*gStyle.GetPadTopMargin() if size==0 else size)
    p.SetTextFont(42 if not hl else 62)
    p.SetTextAlign(12 if pos=="left" else (32 if pos=="right" else 22))
    p.SetTextColor(color)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################

gROOT.SetBatch(1)
gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gStyle.SetOptStat(0)
gStyle.SetOptFit(0)
gStyle.SetLineScalePS(2.0)
gStyle.SetTitleSize(0.05,"XYZT")
gStyle.SetLabelSize(0.04,"XYZT")
gStyle.SetTitleOffset(1.08,"X")
gStyle.SetTitleOffset(1.25,"Y")
gStyle.SetPadTopMargin(0.07)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetPadLeftMargin(0.14)
gStyle.SetPadRightMargin(0.04)
gStyle.SetErrorX(0)

tc1 = TChain("Hbb/events")
tc1.Add("/usb/data2/UAData/2015/flatTree_VBFPowheg125.root")

REDO = True
SEL = "VBF"

fout = TFile("regression.root","update")
fout.cd()

h1 = fout.Get("mbb_%s"%SEL)
h2 = fout.Get("mbbReg_%s"%SEL)

if REDO or not h1 or not h2:
    ct1,cs1,cp = TCut(),TCut(),TCut()
    if SEL=="NOM":
        ct1 = TCut("triggerResult[0]==1||triggerResult[1]==1")
        cs1 = TCut("jetBtag[b1[1]]>0.244 && jetBtag[b2[1]]>0.244 && jetPt[3]>40. && jetPt[2]>50. && jetPt[1]>70. && jetPt[0]>80. && dEtaqq[1]>2.5 && mqq[1]>250 && dPhibb[1]<2.0 && nLeptons==0")
        cp  = TCut("1.")#puWt[0]*trigWtNOM[1]")
    elif SEL=="VBF": 
        ct1 = TCut("triggerResult[9]==1")
        cs1 = TCut("jetBtag[b1[1]]>0.679 && jetBtag[b2[1]]>0.244 && jetPt[3]>30. && 0.5*(jetPt[0]+jetPt[1])>80. && mjjTrig>700. && mqq[2]>700. && dEtaqq[2]>3.5 && dEtaTrig>3.5 && dPhibb[2]<2.0 && nLeptons==0")
        cp  = TCut("1.")#puWt[0]*trigWtNOM[1]")

    fout.cd()
    h1 = TH1F("mbb_%s"%SEL,"mbb1;m_{b#bar{b}} (GeV);Prob. density / (2 GeV)",55,60,170)
    h1.Sumw2()
    h2 = TH1F("mbbReg_%s"%SEL,"mbbReg1;m_{b#bar{b}} (GeV);Prob. density / (2 GeV)",55,60,170)
    h2.Sumw2()
    h1.SetMarkerColor(kBlack)
    h1.SetMarkerStyle(20)
    h2.SetMarkerColor(kRed+1)
    h1.SetMarkerStyle(21)
    h1.SetLineColor(kBlack)
    h2.SetLineColor(kRed+1)
    h1.SetLineWidth(2)
    h2.SetLineWidth(2)
    h2.SetFillColor(kRed-10)
    h2.SetFillStyle(1001)
    
    tc1.Draw("mbb[%d]>>%s"%(1 if SEL=="NOM" else 2,h1.GetName()),ct1*cs1*cp)
    tc1.Draw("mbbReg[%d]>>%s"%(1 if SEL=="NOM" else 2,h2.GetName()),ct1*cs1*cp)
    h1.Scale(1./h1.Integral())
    h2.Scale(1./h2.Integral())

c = TCanvas("c","c",900,750)
c.cd(1)
#h2.GetYaxis().SetRangeUser(0.0,0.075)
#h2.Draw("hist")
#h2.Draw("pe1,same")
#h1.Draw("hist,same")
#h1.Draw("pe1,same")
#tpave("Set A selection","left",1,kBlack,0.045)
#tpave("19.8 fb^{-1} (8 TeV)","right",0,kBlack,0.045)
#c.SaveAs("mbbRegression.pdf")

l = TLegend(gPad.GetLeftMargin()+0.03,0.5,gPad.GetLeftMargin()+0.03+0.25,1.-gPad.GetTopMargin()-0.03,"VBF H #rightarrow b#bar{b} (m_{H} = 125 GeV)")
l.SetBorderSize(0)
l.SetFillStyle(0)
l.SetTextSize(0.04)
l.SetTextFont(42)
a1 = l.AddEntry(h1,"Raw","PL")
a2 = l.AddEntry(h2,"Regressed","FPL")
a1.SetTextColor(kBlack)
a2.SetTextColor(kRed+1)
l.SetY1(l.GetY2()-l.GetNRows()*l.GetTextSize()*1.25)

x = RooRealVar("mbb","mbb",60,170)

hs = [h1,h2]
i1 = [125,12,12,12,1,1,0.5,0.5,0.5,0.5,0.7]
i2 = [110,3,3,3,-10,0,0,0,0,0,0]
i3 = [140,30,30,30,10,100,1,1,1,1,1]
vs = [None]*22
bkg = [None,None] #roobernstein
sig = [None,None] #roobifurgauss
model = [None,None]
for i in range(2):
    for vi,v in enumerate(["m","s","sL","sR","a","n","b0","b1","b2","b3","fsig"]):
        vs[2*vi+i] = RooRealVar("%s%d"%(v,i),"%s%d"%(v,i),i1[vi],i2[vi],i3[vi])

H = [None,None]  #roodatahist
H[0] = RooDataHist("hm0","hm0",RooArgList(x),hs[0])
H[1] = RooDataHist("hm1","hm1",RooArgList(x),hs[1])

for i in range(2):
    bkg[i] = RooBernstein("bkg%d"%i,"bkg%d"%i,x,RooArgList(vs[12+i],vs[14+i],vs[16+i],vs[18+i]))
    sig[i] = RooBifurGauss("sig%d"%i,"sig%d"%i,x,vs[i],vs[4+i],vs[6+i])
#    sig[i] = RooCBShape("sig%d"%i,"sig%d"%i,x,vs[i],vs[2+i],vs[8+i],vs[10+i])
    model[i] = RooAddPdf("model%d"%i,"model%d"%i,RooArgList(sig[i],bkg[i]),RooArgList(vs[20+i]))
#    model[i] = RooAddPdf("model%d"%i,"model%d"%i,RooArgList(sig[i]),RooArgList(vs[20+i]))
    model[i].fitTo(H[i],RooFit.SumW2Error(kFALSE))#,"q")
#    model[i].Print()

frame = x.frame()
H[0].plotOn(frame,RooFit.LineColor(kBlack),RooFit.LineWidth(1),RooFit.MarkerColor(kBlack),RooFit.MarkerStyle(21),RooFit.MarkerSize(1),RooFit.XErrorSize(0))
model[0].plotOn(frame,RooFit.LineColor(kBlack),RooFit.LineWidth(2))
H[1].plotOn(frame,RooFit.LineColor(kRed+1),RooFit.LineWidth(1),RooFit.MarkerColor(kRed+1),RooFit.MarkerStyle(20),RooFit.MarkerSize(1),RooFit.XErrorSize(0))
model[1].plotOn(frame,RooFit.LineColor(kRed+1),RooFit.LineWidth(2))
h2.SetMaximum(0.075)
h2.Draw("hist")
h1.Draw("hist,same")
frame.GetYaxis().SetRangeUser(0.,0.075)
frame.Draw("hist,same")
l.Draw("same")
gPad.RedrawAxis()

tmp_func1 = model[0].asTF(RooArgList(x),RooArgList(vs[20]),RooArgSet(x))
tmp_func2 = model[1].asTF(RooArgList(x),RooArgList(vs[21]),RooArgSet(x))
y01 = tmp_func1.GetMaximum()
x01 = tmp_func1.GetMaximumX()
x11 = tmp_func1.GetX(y01/2.,60,x01)
x21 = tmp_func1.GetX(y01/2.,x01,200)
FWHM1 = x21-x11

y02 = tmp_func2.GetMaximum()
x02 = tmp_func2.GetMaximumX()
x12 = tmp_func2.GetX(y02/2.,60,x02)
x22 = tmp_func2.GetX(y02/2.,x02,200)
FWHM2 = x22-x12

tpave("Set A selection" if SEL=="NOM" else "Set B selection","left",1,kBlack,0.045)
tpave("%.1f fb^{-1} (8 TeV)"%(19.8 if SEL=="NOM" else 18.3),"right",0,kBlack,0.045)

epave("PEAK: %.1f"%x01,0.175,0.65,"left",0,kBlack)
epave("FWHM: %.1f"%FWHM1,0.175,0.605,"left",0,kBlack)
epave("PEAK: %.1f"%x02,0.175,0.52,"left",0,kRed+1)
epave("FWHM: %.1f"%FWHM2,0.175,0.475,"left",0,kRed+1)

tl1 = TLine(x11,y01,x21,y01)
tl1.SetNDC(0)
tl1.SetLineColor(kGray+2)
tl1.SetLineStyle(kDotted)
tl1.Draw("same")
tl2 = TLine(x12,y02,x22,y02)
tl2.SetNDC(0)
tl2.SetLineColor(kGray+2)
tl2.SetLineStyle(kDotted)
tl2.Draw("same")
tl3 = TLine(x01,0,x01,2*y01)
tl3.SetNDC(0)
tl3.SetLineColor(kGray+2)
tl3.SetLineStyle(kDotted)
tl3.Draw("same")
tl4 = TLine(x02,0,x02,2*y02)
tl4.SetNDC(0)
tl4.SetLineColor(kGray+2)
tl4.SetLineStyle(kDotted)
tl4.Draw("same")

c.SaveAs("mbbRegression_%s_fit.pdf"%SEL)
c.Close()

h1.Write(h1.GetName(),TH1.kOverwrite)
h2.Write(h2.GetName(),TH1.kOverwrite)
fout.Close()




