#!/usr/bin/env python
import ROOT
from ROOT import *
from array import array

gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("6.2f")
gStyle.SetTitleOffset(1.5,"XY")

c = TCanvas("c1","c1")
c.Divide(2,2)

c.cd(1)
h = TH2F("h1","h1",10,0,10,10,0,20)
h.Sumw2()
h.Fill(2,4,2)
h.Fill(1,6,3)
h.SetMarkerSize(1.6)
h.Draw("TEXT,COLZ,ERROR")

c.cd(2)
x = array('f',[0,1,3,5,7])
y = array('f',[0,1,2,3,4])
h2 = TH2F("h2","h2",len(x)-1,x,len(y)-1,y)
h2.Sumw2()
h2.Fill(2,1,2)
h2.SetName("h2")
h2.SetTitle("h2")
h2.SetMarkerSize(1.6)
h2.GetZaxis().SetRangeUser(0,1.4)
gPad.SetLogx(1)
h2.Draw("TEXT45,COLZ,ERROR")

c.cd(4)
h3 = h2.Clone("h3")
h3.SetTitle("h3")
h3.Divide(h2,h2,1.0,1.0,'B')
h3.SetMarkerSize(1.6)
h3.Draw("TEXT,COLZ,ERROR")

c.SaveAs("test.pdf")
c.Close()
