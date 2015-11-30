#!/usr/bin/env python

import ROOT
from ROOT import *
import sys,os,re

def putpave(x1,x2,y1,y2,text,size,color,align,orientation=0):
    p = TPaveText()
    p.SetX1(x1)
    p.SetX2(x2)
    p.SetY1NDC(y1)
    p.SetY2NDC(y2)
    p.SetFillStyle(0)
    p.SetBorderSize(0)
    p.SetTextFont(42)
    p.SetTextSize(size)
    p.SetTextColor(color)
    p.SetTextAlign(align)
    t = p.AddText(text)
    t.SetTextAngle(orientation)
    p.Draw()
    return p

gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
gROOT.SetBatch(1)
gStyle.SetPadLeftMargin(0.18)
gStyle.SetPadRightMargin(0.05)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetTitleSize(0.050,"XYZ")
gStyle.SetLabelSize(0.040,"XYZ")
gStyle.SetTitleOffset(1.5,"X")
gStyle.SetTitleOffset(1.00,"Y")
gStyle.SetStripDecimals(kFALSE)
gStyle.SetGridColor(17)

c = TCanvas("c","c",900,750)
c.SetLogy(1)
#c1 = TPad("c1","c1",0.0,0.0,1.0,1.0)
#c2 = TPad("c2","c2",0.0,0.0,1.0,1.0)
#c2.SetFillStyle(0)
#c1.Draw()
#c2.Draw()
#c1.SetLogy(1)
#c2.SetLogy(1)
#c.Update()

bins = ["None","p_{T} (x4)","#Delta #eta_{qq'} (#eta sorted)","m_{qq'} (#eta sorted)","b-tag (L2.5)","b-tag (L3)","#Delta #eta_{qq'} (b-tag sorted)","m_{qq'} (b-tag sorted)"]
bins = ["None","p_{T} (x4)","#Delta #eta_{qq'}","m_{qq'}","b-tag","b-tag","#Delta #eta_{qq'}","m_{qq'}"]
effi = [100,27.8,22.68,22.29,17.09,10.17,9.71,7.82]
effierr = [0.0,0.53,0.48,0.47,0.41,0.32,0.28,0.28]
rate = [2319.1,90.8,48.34,44.88,30.58,9.11,3.23,2.88]
rateerr = [0.0,3.17,2.34,2.25,1.87,1.02,0.61,0.57]

heffi = TH1F("heffi",";cut type;Efficiency (%)",8,0,8)
hrate = TH1F("hrate",";cut type;Rate (Hz)",8,0,8)

for i in range(len(effi)):
    heffi.GetXaxis().SetBinLabel(i+1,bins[i])
    heffi.SetBinContent(i+1,effi[i])
    heffi.SetBinError(i+1,effierr[i])
    hrate.SetBinContent(i+1,rate[i])
    hrate.SetBinError(i+1,rateerr[i])

heffi.SetLineColor(kBlack)
heffi.SetMarkerStyle(25)
heffi.SetMarkerSize(0.8)
heffiband = heffi.Clone("heffiband")
heffiband.SetFillColor(kGray+2)
heffiband.SetFillStyle(3003)
heffiband.SetMarkerSize(0)
hrate.SetLineColor(kRed+1)
hrate.SetLineWidth(2)
hrate.SetLineStyle(kDashed)
hrate.SetMarkerColor(kRed+2)
hrate.SetMarkerSize(0.8)

heffi.SetMinimum(1.00) #0)
heffi.SetMaximum(5000) #40)
#ymaxleft = 150# heffi.GetMaximum()*1.1
##ymaxright = hrate.GetMaximum()*1.1
#ymaxright = 5000.
hrate.SetMinimum(0.11)

#c1.cd()
#c1.SetTicks(0,0)
heffi.Draw("")
heffiband.Draw("same,e2")
gPad.Update()
#print gPad.GetUymax(),ymaxleft,ymaxright
#hrate.Scale(ymaxleft/ymaxright)
#hrate.Scale(1./2500.)

#c2.cd()
#c2.SetTicky(2)
#c2.Update()
#hrate.GetXaxis().SetLabelSize(0)
#hrate.GetXaxis().SetTitleSize(0)
#hrate.GetYaxis().SetAxisColor(kRed+2)
#hrate.GetYaxis().SetLabelColor(kRed+2)
hrate.Draw("same")
#axisright = TGaxis(gPad.GetUxmax(),gPad.GetUymin(),gPad.GetUxmax(),gPad.GetUymax(),0.001,100000,510,"+LG")
#axisright.SetLineColor(kRed+2)
#axisright.SetLabelColor(kRed+2)
#axisright.Draw("update")

p1 = putpave(2,4,0.07,0.09,"#eta sorted",0.030,kBlack,22)
p2 = putpave(4,5,0.07,0.09,"L2.5",0.030,kBlack,22)
p3 = putpave(5,6,0.07,0.09,"L3",0.030,kBlack,22)
p4 = putpave(6,8,0.07,0.09,"b-tag sorted",0.030,kBlack,22)
p5 = putpave(-1.4,-0.8,0.65,0.85,"Rate (Hz)",0.05,kRed+1,12,90)

l1 = TLegend(0.66,0.6,0.95,0.92)
l1.SetTextSize(0.035)
l1.SetTextFont(42)
l1.SetFillStyle(0)
l1.SetBorderSize(0)
l1.AddEntry(heffi,"Efficiency","lp")
l1.AddEntry(hrate,"Rate","lp")
l1.SetY1(l1.GetY2()-2*0.035*1.2)
l1.Draw()

c.SaveAs("TrigDev.pdf")

c.Clear()
c1 = TPad("c1","c1",0.0,0.0,1.0,1.0)
c2 = TPad("c2","c2",0.0,0.0,1.0,1.0)
c2.SetFillStyle(0)
c2.SetTopMargin(0.63)
c1.SetBottomMargin(0.38)
c1.Draw()
c2.Draw()
c1.SetLogy(0)
c2.SetLogy(0)
c.Update()

hdiff = TH1F("hdiff","",8,0,8)
deffi = TH1F("deffi",";cut type; #Delta Efficiency (%)",8,0,8)
drate = TH1F("drate","",8,0,8)

for i in range(len(bins)):
    hdiff.GetXaxis().SetBinLabel(i+1,bins[i])
    deffi.GetXaxis().SetBinLabel(i+1,bins[i])
    drate.GetXaxis().SetBinLabel(i+1,bins[i])

for i in range(2,9):
    effiref = heffi.GetBinContent(i-1)
    rateref = hrate.GetBinContent(i-1)
    deffi.SetBinContent(i,heffi.GetBinContent(i)/effiref)
    drate.SetBinContent(i,hrate.GetBinContent(i)/rateref)
    #hdiff.SetBinContent(i,1./((effiref - heffi.GetBinContent(i))/(rateref - hrate.GetBinContent(i))))
#hdiff.Draw("")
c1.cd()
deffi.SetMaximum(1.4)
drate.SetLineColor(kRed+1)
drate.SetLineStyle(kDashed)
drate.SetLineWidth(2)
deffi.Draw()
drate.Draw("same")
deffi.GetYaxis().SetTickLength(0.02)
deffi.GetXaxis().SetTickLength(0.02)
c2.cd()
hdiff = deffi.Clone("hdiff")
hdiff.Divide(drate)
hdiff.GetYaxis().SetRangeUser(0.50,7.50)
hdiff.GetYaxis().SetNdivisions(204)
hdiff.GetYaxis().SetTickLength(0.02/0.38)
hdiff.GetXaxis().SetTickLength(0.02)
gPad.SetGrid(0,1)
for i in range(2,9):
    hdiff.SetBinError(i,0.001)
hdiff.Draw("pe")
deffi.GetXaxis().SetTitleSize(0)
deffi.GetXaxis().SetLabelSize(0)
hdiff.GetYaxis().SetTitle("#Delta Rate / #Delta Effi")
hdiff.GetYaxis().SetTitleSize(0.035)
hdiff.GetYaxis().SetTitleOffset(1.5)
#hdiff.GetXaxis().SetLabelSize(0.040)
hdiff.GetXaxis().SetLabelOffset(hdiff.GetXaxis().GetLabelOffset()*2.5)
gPad.Update()
tl1 = TLine(gPad.GetUxmin(),1.0,gPad.GetUxmax(),1.0)
tl1.SetLineColor(kGreen+1)
tl1.SetLineStyle(9)
tl1.Draw()
c.cd()
p1 = putpave(2,4,0.07,0.09,"#eta sorted",0.030,kBlack,22)
p2 = putpave(4,5,0.07,0.09,"L2.5",0.030,kBlack,22)
p3 = putpave(5,6,0.07,0.09,"L3",0.030,kBlack,22)
p4 = putpave(6,8,0.07,0.09,"b-tag sorted",0.030,kBlack,22)
p5 = putpave(-1.4,-0.8,0.55,0.90,"#Delta Rate (%)",0.05,kRed+1,12,90)
l1 = TLegend(0.20,0.6,0.55,0.92)
l1.SetTextSize(0.035)
l1.SetTextFont(42)
l1.SetFillStyle(0)
l1.SetBorderSize(0)
l1.AddEntry(deffi,"#Delta Efficiency","l")
l1.AddEntry(drate,"#Delta Rate","l")
l1.SetY1(l1.GetY2()-2*0.035*1.2)
l1.Draw()
t2 = putpave(0.35,0.8,0.78,0.85,"(w.r.t. total of previous cuts)",0.028,kBlack,12)
c.SaveAs("TrigDev2.pdf")


c.Close()


