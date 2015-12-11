#!/usr/bin/env python

import ROOT
from ROOT import *
from math import *

global paves
paves = []

####################################################################################################
def epave(text,x,y,size=0.028):
    global paves
    p = TText(x,y,text)
    #p.SetNDC()
    p.SetTextSize(size)
    p.SetTextFont(42)
    p.SetTextAlign(31)
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]
    return p
####################################################################################################

gROOT.SetBatch(0)
gStyle.SetLineScalePS(2.0)

C1 = 0.023
C2 = 0.017

scale = 16.0

R1 = sqrt(scale*C1 / pi) 
R2 = sqrt(scale*C2 / pi) 

O  = 0.009

a,t1,t2,r1,r2,A1,A2 = 0,0,0,0,0,0,0
for it2 in range(0,1000):
    t2 = float(it2)/1000. * pi
    a  = R2*sin(0.5*t2)
    r2 = R2*cos(0.5*t2)
    t1 = 2.*asin(a/R1)
    r1 = R1*cos(0.5*t1)
    A1 = 0.5*R1*R1*(t1 - sin(t1))
    A2 = 0.5*R2*R2*(t2 - sin(t2))
    if abs(A1+A2 - O*scale)/abs(O*scale) < 0.01: break

cdiff = r1+r2
x0,y0 = 0.4,0.38

#tl1 = TLine(x0-a,y0+r1,x0+a,y0+r1)
#tl1.SetLineColor(kRed)
#tl1.SetLineWidth(1)
#tl2 = TLine(x0,y0,x0,y0+r1)
#tl2.SetLineColor(kMagenta)
#tl2.SetLineWidth(1)
#tl3 = TLine(x0,y0+r1,x0,y0+r1+r2)
#tl3.SetLineColor(kBlack)
#tl3.SetLineWidth(1)
#tl4a = TLine(x0,y0,x0-a,y0+r1)
#tl4a.SetLineColor(kRed)
#tl4a.SetLineWidth(1)
#tl4b = TLine(x0,y0,x0+a,y0+r1)
#tl4b.SetLineColor(kRed)
#tl4b.SetLineWidth(1)
#tl4c = TLine(x0,y0+r1+r2,x0-a,y0+r1)
#tl4c.SetLineColor(kRed)
#tl4c.SetLineWidth(1)
#tl4d = TLine(x0,y0+r1+r2,x0+a,y0+r1)
#tl4d.SetLineColor(kRed)
#tl4d.SetLineWidth(1)

c = TCanvas("c","c",900,900)
circ1 = TEllipse(x0,y0,R1,R1)
circ2 = TEllipse(x0,y0+cdiff,R2,R2)

circ1.SetFillColor(kGreen+2)
circ2.SetFillColor(kBlue-4)
circ1.SetLineColor(kGreen+2)
circ2.SetLineColor(kBlue-4)
circ1.SetLineWidth(2)
circ2.SetLineWidth(2)
circ1.SetFillStyle(3003)
circ2.SetFillStyle(3005)

circ2.Draw()
circ1.Draw("same")

h1 = TH1F("h1","h1",10,0,1)
h2 = TH1F("h2","h2",10,0,1)
h1.SetFillColor(kGreen+2)
h2.SetFillColor(kBlue-4)
h1.SetLineColor(kGreen+2)
h2.SetLineColor(kBlue-4)
h1.SetLineWidth(2)
h2.SetLineWidth(2)
h1.SetFillStyle(3003)
h2.SetFillStyle(3005)

l = TLegend(0.78,0.7,1.02,0.92,"")
l.SetBorderSize(0)
l.SetFillStyle(0)
l.SetTextSize(0.038)
l.SetTextFont(42)
l.AddEntry(h1,"Set A","F")
l.AddEntry(h2,"Set B","F")
l.SetY1(l.GetY2()-0.045*l.GetNRows())
l.Draw()

epave("Inclusive Set A: 2.3%",0.97,0.77)
epave("Exclusive Set B: 0.8%",0.97,0.735)
epave("Overlap: 0.9%",0.97,0.70)



#tl1.Draw("same")
#tl2.Draw("same")
#tl3.Draw("same")
#tl4a.Draw("same")
#tl4b.Draw("same")
#tl4c.Draw("same")
#tl4d.Draw("same")
#
#epave("a = %.2f"%a,0.1,0.9)
#epave("r1 = %.2f"%r1,0.1,0.85)
#epave("r2 = %.2f"%r2,0.1,0.8)
#epave("R1 = %.2f"%R1,0.1,0.75)
#epave("R2 = %.2f"%R2,0.1,0.7)
#epave("t1 = %.2f"%t1,0.1,0.65)
#epave("t2 = %.2f"%t2,0.1,0.6)
c.SaveAs("SetABSelection.pdf")
c.Update()

c.Close()



