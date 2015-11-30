#!/usr/bin/env python
import ROOT
from ROOT import *
import sys,os,re

######################################################################################################################################################
def topright(text):                                                                                                          
    t = TPaveText(0.6,1.-gPad.GetTopMargin(),1.-gPad.GetRightMargin()+0.01,1.-0.005,"NDC")                                         
    t.SetTextFont(42)                                                                                                        
    t.SetTextSize(gPad.GetTopMargin()*0.6)                                                                                  
    t.SetTextColor(kBlack)                                                                                                   
    t.SetBorderSize(0)                                                                                                       
    t.SetFillStyle(0)                                                                                                       
    t.SetTextAlign(32)                                                                                                       
    t.AddText("%s"%text)                                                                                                     
    t.Draw()                                                                                                                 
    return t                                                                                                                 
                                                                                                                             
######################################################################################################################################################
def topleft(text):                                                                                                           
    t = TPaveText(gPad.GetLeftMargin()+0.07,1.-gPad.GetTopMargin(),0.5,1.-0.005,"NDC")                                             
    t.SetTextFont(42)                                                                                                        
    t.SetTextSize(gPad.GetTopMargin()*0.6)                                                                                  
    t.SetTextColor(kBlack)                                                                                                   
    t.SetBorderSize(0)                                                                                                       
    t.SetFillStyle(0)                                                                                                       
    t.SetTextAlign(12)                                                                                                       
    t.AddText("%s"%text)                                                                                                     
    t.Draw()                                                                                                                 
    return t                                                                                                                 

######################################################################################################################################################

xT = {"rho":"#rho (GeV)", "npu":"N_{PU}", "nvtx":"N_{PV}"}
yT = {"rho":"1 GeV", "npu":"1", "nvtx":"1"}
sel = {"":" (MC)","2":""}

for setname in ["SetA","SetB"]:
    f = TFile.Open("puReweight_%s.root"%setname,"read")
    for suffix in ["","2"]:
        for var in ["rho","npu","nvtx"]:
            gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
            gStyle.SetLineScalePS(2.2)
            gStyle.SetPadLeftMargin(0.13)
            gStyle.SetPadBottomMargin(0.10)
            
            c = TCanvas("c","c",900,900)
            c1 = TPad("c1","c1",0.0,0.0,1.0,1.0)
            c2 = TPad("c2","c2",0.0,0.0,1.0,1.0)
            c1.SetTopMargin(0.055)
            c1.SetBottomMargin(0.3)
            c2.SetTopMargin(0.71)
            c2.SetFillStyle(0)
            c1.Draw()
            c2.Draw("same")
            c.Update()
            
            h1 = f.Get("%sd%s"%(var,suffix))
            h2 = f.Get("%sq%s"%(var,suffix))
            h3 = f.Get("%sqcorr%s"%(var,suffix))
            print h1
            print h2
            print h3
            
            scale = h1.Integral()/h2.Integral()
            h2.Scale(scale)
            h3.Scale(scale)
            
            h1.SetMarkerStyle(20)
            h1.SetMarkerSize(1.2)
            h1.SetMarkerColor(kBlack)
            
            h3.SetLineColor(kGreen+3)
            h3.SetLineStyle(kDashed)
            h3.SetLineWidth(2)
            h3.SetFillColor(kGray+1)
            h3.SetFillStyle(3003)
            #
            g3 = h3.Clone("g3")
            g3.SetMarkerStyle(0)
            g3.SetFillColor(kGray+1)
            g3.SetFillStyle(3004)
            for i in g3.GetListOfFunctions():
                if i.GetName()=="stats": i.Delete()
            
            h2.SetLineColor(kRed)
            h2.SetFillStyle(0)
            h2.SetLineWidth(2)
            
            # ratio
            a1 = h1.Clone("a1")
            for i in range(0,a1.GetNbinsX()+1): 
                a1.SetBinContent(i,1.0)
                a1.SetBinError(i,0.0)
            r2 = h1.Clone("r2")
            r3 = h1.Clone("r3")
            r2.Divide(h2)
            r2.Add(a1,-1)
            r2.GetYaxis().SetRangeUser(-0.99,0.99)
            r2.GetYaxis().SetNdivisions(504)
            r2.SetLineColor(kRed)
            r2.SetMarkerStyle(0)
            r3.Divide(h3)
            r3.Add(a1,-1)
            r3.SetLineColor(kGreen+3)
            r3.SetMarkerStyle(0)
            r4 = h3.Clone("r4")
            for i in r4.GetListOfFunctions():
                if i.GetName()=="stats": i.Delete()
            r4.Divide(h3)
            r4.Add(a1,-1)
            for i in range(0,r4.GetNbinsX()+1): r4.SetBinContent(i,0.0)
            r4.SetFillColor(kGray+1)
            r4.SetFillStyle(3004)
            r4.SetLineWidth(0)
            g3.SetLineWidth(0)
            
            c1.cd()
            gStyle.SetErrorX(0.5)
            ym = max([x.GetBinContent(x.GetMaximumBin()) for x in [h1,h2,h3]])
            h2.GetYaxis().SetRangeUser(0.0,ym*1.1)
            h2.GetXaxis().SetTitle()
            h2.GetYaxis().SetTitle("Events / (%s)"%(yT[var]))
            h2.GetXaxis().SetTitleSize(0)#0.040)
            h2.GetYaxis().SetTitleSize(0.040)
            h2.GetXaxis().SetTitleOffset(1.00)
            h2.GetYaxis().SetTitleOffset(1.34)
            h2.GetXaxis().SetLabelSize(0)#.033)
            h2.GetYaxis().SetLabelSize(0.033)
            h2.GetXaxis().SetTickLength(0.02)
            h2.GetYaxis().SetTickLength(0.02)
            h2.GetYaxis().SetNdivisions(505)
            TGaxis.SetMaxDigits(4)
            h2.Draw("hist")
            h3.Draw("hist,same")
            h1.Draw("pe,same")
            g3.Draw("e2,same")
            ##
            l1 = topleft("Set %s selection%s"%(setname[-1],sel[suffix]))
            l2 = topright("%.1f fb^{-1} (8 TeV)"%(19.8 if "A" in setname else 18.3))
            l1.Draw("same")
            l2.Draw("same")
            ##
            c2.cd()
            r2.GetXaxis().SetTitle(xT[var])
            r2.GetYaxis().SetTitle("Data/Sim - 1")
            r2.GetXaxis().SetTitleSize(0.040)
            r2.GetYaxis().SetTitleSize(0.037)
            r2.GetXaxis().SetTitleOffset(1.00)
            r2.GetYaxis().SetTitleOffset(1.45)
            r2.GetXaxis().SetLabelSize(0.033)
            r2.GetYaxis().SetLabelSize(0.033)
            r2.GetXaxis().SetTickLength(0.02)
            r2.GetYaxis().SetTickLength(0.02/0.31)
            r2.SetMarkerStyle(20)
            r3.SetMarkerStyle(20)
            r2.SetMarkerColor(kRed)
            r3.SetMarkerColor(kGreen+3)
            r2.SetMarkerSize(1.2)
            r3.SetMarkerSize(1.2)
            gStyle.SetGridColor(17)
            r2.Draw()
            gPad.RedrawAxis()
            gPad.SetTickx(1)
            gPad.Update()
            gPad.SetGrid(0,1)
            line = TLine(gPad.GetUxmin(),0.0,gPad.GetUxmax(),0.0)
            line.SetLineColor(1)
            line.SetLineWidth(1)
            line.Draw("same")
            r3.Draw("same")
            r4.Draw("e2,same")
            
            l = TLegend(0.64,0.7,0.9,0.92)
            l.SetFillStyle(0)
            l.SetBorderSize(0)
            l.SetTextFont(42)
            l.SetTextSize(0.028)
            l.AddEntry(h1,"Data","pl")
            l.AddEntry(h2,"QCD","l")
            l.AddEntry(h3,"QCD (PU reweighted)","lf")
            l.AddEntry(g3,"Sim. stat. unc.","f")
            l.SetY1(l.GetY2()-4*0.040)
            l.Draw()
            
            c.SaveAs("plots/%s/%s_overlay_%s%s.pdf"%(setname,var,setname,"-MC" if not suffix=="2" else ""))
            c.Close()

    f.Close()

                                                                                                                             

