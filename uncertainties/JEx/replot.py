#!/usr/bin/env python
import ROOT
from ROOT import *

import os,sys,re
global paves
paves = []

####################################################################################################
def putLine(x1,y1,x2,y2,style=kDashed,color=kGray+2,width=1):
    global paves
    l = TLine(x1,y1,x2,y2)
    l.SetLineStyle(style)
    l.SetLineColor(color)
    l.SetLineWidth(width)
    l.Draw()
    paves += [l]

####################################################################################################
def putPave(text,x1,y1,align=12,font=42,size=0.045,color=kBlack,ndc=1):
    global paves
    l = TLatex(x1,y1,text)
    l.SetNDC(1)
    l.SetTextFont(font)
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.SetTextAlign(align)
    l.Draw()
    paves += [l]

####################################################################################################
def styleLeg(leg):
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    return leg

####################################################################################################
f = TFile.Open("rootfiles/vbfHbb_uncertainties_JEx_CERN.root","read")

for sample in ["VBF125","GF125"]:
    if sample == "VBF125": continue
    samplebis = sample if "VBF" in sample else "GluGlu-Powheg125"
    f.cd("canvas/%s"%samplebis)
    #f.ls()
    
    cJES1 = f.Get("canvas/%s/cJES_mvaNOM-B20-0-1_%s_%s_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-nLeptons_tNOMMC_dNOMMC_rNone"%(samplebis,sample,samplebis))
    cJER1 = f.Get("canvas/%s/cJER_mvaNOM-B20-0-1_%s_%s_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-nLeptons_tNOMMC_dNOMMC_rNone"%(samplebis,sample,samplebis))
    cMBB1 = f.Get("canvas/%s/cJES_mbb1-B75-50-200_%s_%s_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetPt0_gt80-jetPt1_gt70-jetPt2_gt50-jetPt3_gt40-mqq1_gt250-nLeptons_tNOMMC_dNOMMC_rNone"%(samplebis,sample,samplebis))
    cJES2 = f.Get("canvas/%s/cJES_mvaVBF-B20-0-1_%s_%s_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-dPhibb2_lt2-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-nLeptons_tVBF_dVBF_rNone"%(samplebis,sample,samplebis))
    cJER2 = f.Get("canvas/%s/cJER_mvaVBF-B20-0-1_%s_%s_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-dPhibb2_lt2-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-nLeptons_tVBF_dVBF_rNone"%(samplebis,sample,samplebis))
    cMBB2 = f.Get("canvas/%s/cJES_mbb2-B75-50-200_%s_%s_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-dPhibb2_lt2-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-nLeptons_tVBF_dVBF_rNone"%(samplebis,sample,samplebis))
    
    #cJES1 = f.Get("canvas/VBF125/cJES_mvaNOM-B20-0-1_VBF_VBF125_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetUnsPt0_gt80-jetUnsPt1_gt70-jetUnsPt2_gt50-jetUnsPt3_gt40-mqq1_gt250-nLeptons_tNOMMC_dNOMMC_rNone")
    #cJER1 = f.Get("canvas/VBF125/cJER_mvaNOM-B20-0-1_VBF_VBF125_sBtag0_LL-dEtaqq1_gt2p5-dPhibb1_lt2-jetUnsPt0_gt80-jetUnsPt1_gt70-jetUnsPt2_gt50-jetUnsPt3_gt40-mqq1_gt250-nLeptons_tNOMMC_dNOMMC_rNone")
    #
    #cJES2 = f.Get("canvas/VBF125/cJES_mvaVBF-B20-0-1_VBF_VBF125_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-dPhibb2_lt2-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-nLeptons_tVBF_dVBF_rNone")
    #cJER2 = f.Get("canvas/VBF125/cJER_mvaVBF-B20-0-1_VBF_VBF125_sdEtaTrig_gt3p5-dEtaqq2_gt3p5-dPhibb2_lt2-jetPt3_gt30-jetPtAve_gt80-mjjTrig_gt700-mqq2_gt700-nLeptons_tVBF_dVBF_rNone")
    
    c = [cJES1,cJES2]
    ctop = [None]*4
    cbot = [None]*4
    h    = [None]*4
    
    for i,ci in enumerate(c):
        ctop[i] = ci.GetListOfPrimitives().FindObject("ptop")
        cbot[i] = ci.GetListOfPrimitives().FindObject("pbot")
        suffix = '_'.join(ci.GetName().split('_')[1:])
        typ = "JES" if "JES" in ci.GetName() else "JER"
        h[i] = [None]*5
        h[i][0] = ctop[i].GetListOfPrimitives().FindObject("hHbb_"+suffix)
        h[i][1] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sUp_"%(typ)+suffix)
        h[i][2] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sDn_"%(typ)+suffix)
        h[i][3] = cbot[i].GetListOfPrimitives().FindObject("rHbbJESUp")
        h[i][4] = cbot[i].GetListOfPrimitives().FindObject("rHbbJESDn")
    
    gROOT.SetBatch(1)
    gROOT.ProcessLineSync(".x ../../common/styleCMSTDR.C")
    gStyle.SetPadLeftMargin(0.14)
    gStyle.SetPadRightMargin(0.04)
    gStyle.SetPadBottomMargin(0.10)
    gStyle.SetPadTopMargin(0.07)
    gStyle.SetLineScalePS(1.8)
    gStyle.SetStripDecimals(0)
    
    ####################################################################################################
    cNew = TCanvas("c","c",1800,750)
    cNew.Divide(2,1)
    for selection in [0,1]:
        cNew.cd(selection+1)
        p1 = TPad("p1","p1",0,0,1,1)
        p2 = TPad("p2","p2",0,0,1,1)
        p1.SetBottomMargin(0.3)
        p2.SetTopMargin(0.7)
        p2.SetFillStyle(0)
        p1.Draw()
        p2.Draw("same")
        cNew.Update()
        cNew.Modified()
        p1.cd()
        #
        h[selection][1].GetYaxis().SetRangeUser(0,h[selection][1].GetBinContent(h[selection][1].GetMaximumBin())*1.2*(1 if "VBF" in sample else 1.75))
        h[selection][1].GetXaxis().SetTitleFont(42)
        h[selection][1].GetYaxis().SetTitleFont(42)
        h[selection][1].GetXaxis().SetTitleSize(0.0)
        h[selection][1].GetYaxis().SetTitleSize(0.05)
        h[selection][1].GetYaxis().SetTitleOffset(1.3)
        h[selection][1].GetYaxis().SetNdivisions(508)
        h[selection][1].GetXaxis().SetTickSize(0.02)
        h[selection][1].GetYaxis().SetTickSize(0.02)
        h[selection][3].GetXaxis().SetTitleFont(42)
        h[selection][3].GetYaxis().SetTitleFont(42)
        h[selection][3].GetXaxis().SetTitleSize(0.05)
        h[selection][3].GetYaxis().SetTitleSize(0.025)
        h[selection][3].GetXaxis().SetTitleOffset(1.0)
        h[selection][3].GetYaxis().SetTitleOffset(2.5)
        h[selection][1].GetXaxis().SetLabelFont(42)
        h[selection][1].GetYaxis().SetLabelFont(42)
        h[selection][1].GetXaxis().SetLabelSize(0.0)
        h[selection][1].GetYaxis().SetLabelSize(0.04)
        h[selection][3].GetXaxis().SetLabelFont(42)
        h[selection][3].GetYaxis().SetLabelFont(42)
        h[selection][3].GetXaxis().SetLabelSize(0.04)
        h[selection][3].GetYaxis().SetLabelSize(0.04)
        h[selection][1].GetYaxis().SetTitle("Events / Category")
        h[selection][3].GetXaxis().SetTitle("BDT output")
        h[selection][3].GetYaxis().SetNdivisions(404)
        h[selection][3].GetXaxis().SetTickSize(0.02)
        h[selection][3].GetYaxis().SetTickSize(0.02/0.3*0.7)
        #
        #
        for hi in h[selection]: hi.SetLineWidth(1)
        h[selection][1].Draw("hist")
        h[selection][0].Draw("hist,same")
        h[selection][2].Draw("hist,same")
        putPave("%.1f fb^{-1} (8 TeV)"%(19.8 if selection==0 else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),align=32)
        putPave("Set %s selection"%("A" if selection==0 else "B"),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),align=12,font=62)
        putPave("%s signal (m_{H} = 125 GeV)"%("VBF" if "VBF" in sample else "GF"),gStyle.GetPadLeftMargin()+0.03,1.-gStyle.GetPadTopMargin()-0.05,align=12,size=0.038,font=62)
        leg = TLegend(gStyle.GetPadLeftMargin()+0.02,0.5,0.5,1.-gStyle.GetPadTopMargin()-0.08)
        leg = styleLeg(leg)
        leg.SetTextSize(0.037)
        leg.SetTextFont(62)
        leg.SetHeader("JES variation")
        leg.SetTextFont(42)
        leg.AddEntry(h[selection][0],"Central","FL")
        leg.AddEntry(h[selection][1],"JES up","FL")
        leg.AddEntry(h[selection][2],"JES down","FL")
        leg.SetY1(leg.GetY2()-leg.GetNRows()*leg.GetTextSize()*1.25)
        leg.Draw()
        paves += [leg]
        gPad.RedrawAxis()
        p2.cd()
        h[selection][3].Draw("hist")
        h[selection][4].Draw("hist,same")
        putLine(-1,0,1,0)
        gPad.RedrawAxis()
    
    cNew.SaveAs("%s_JES.pdf"%sample)
    
    ####################################################################################################
    c = [cJER1,cJER2]
    ctop = [None]*4
    cbot1 = [None]*4
    cbot2 = [None]*4
    cbot3 = [None]*4
    h    = [None]*4
    
    ####################################################################################################
    for i,ci in enumerate(c):
        ctop[i] = ci.GetListOfPrimitives().FindObject("ptop")
        cbot1[i] = ci.GetListOfPrimitives().FindObject("pmod1")
        cbot2[i] = ci.GetListOfPrimitives().FindObject("pmod2")
        suffix = '_'.join(ci.GetName().split('_')[1:])
        typ = "JES" if "JES" in ci.GetName() else "JER"
        h[i] = [None]*6
        h[i][1] = ctop[i].GetListOfPrimitives().FindObject("hHbb_"+suffix)
        h[i][0] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sCl_"%(typ)+suffix)
        h[i][2] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sUp_"%(typ)+suffix)
        h[i][3] = cbot1[i].GetListOfPrimitives().FindObject("rHbbJERUp")
        h[i][4] = cbot1[i].GetListOfPrimitives().FindObject("rHbbJERUp")
        h[i][5] = cbot2[i].GetListOfPrimitives().FindObject("rHbbJERCl")
    
    ####################################################################################################
    cNew = TCanvas("c","c",1800,750)
    cNew.Divide(2,1)
    for selection in [0,1]:
        cNew.cd(selection+1)
        p1 = TPad("p1","p1",0,0,1,1)
        p2 = TPad("p2","p2",0,0,1,1)
        p3 = TPad("p3","p3",0,0,1,1)
        p1.SetBottomMargin(0.40)
        p2.SetTopMargin(0.60)
        p2.SetBottomMargin(0.25)
        p3.SetTopMargin(0.75)
        p2.SetFillStyle(0)
        p3.SetFillStyle(0)
        p1.Draw()
        p2.Draw("same")
        p3.Draw("same")
        cNew.Update()
        cNew.Modified()
        p1.cd()
        #
        h[selection][1].GetYaxis().SetRangeUser(0,h[selection][1].GetBinContent(h[selection][1].GetMaximumBin())*1.2*(1 if "VBF" in sample else 1.75))
        h[selection][1].GetXaxis().SetTitleFont(42)
        h[selection][1].GetYaxis().SetTitleFont(42)
        h[selection][1].GetXaxis().SetTitleSize(0.0)
        h[selection][1].GetYaxis().SetTitleSize(0.05)
        h[selection][1].GetYaxis().SetTitleOffset(1.3)
        h[selection][1].GetYaxis().SetNdivisions(508)
        h[selection][1].GetXaxis().SetTickSize(0.02)
        h[selection][1].GetYaxis().SetTickSize(0.02)
        h[selection][3].GetXaxis().SetTitleFont(42)
        h[selection][3].GetYaxis().SetTitleFont(42)
        h[selection][3].GetXaxis().SetTitleSize(0.05)
        h[selection][3].GetYaxis().SetTitleSize(0.025)
        h[selection][3].GetXaxis().SetTitleOffset(1.0)
        h[selection][3].GetYaxis().SetTitleOffset(2.5)
        h[selection][1].GetXaxis().SetLabelFont(42)
        h[selection][1].GetYaxis().SetLabelFont(42)
        h[selection][1].GetXaxis().SetLabelSize(0.0)
        h[selection][1].GetYaxis().SetLabelSize(0.04)
        h[selection][3].GetXaxis().SetLabelFont(42)
        h[selection][3].GetYaxis().SetLabelFont(42)
        h[selection][3].GetXaxis().SetLabelSize(0.04)
        h[selection][3].GetYaxis().SetLabelSize(0.04)
        h[selection][5].GetXaxis().SetLabelFont(42)
        h[selection][5].GetYaxis().SetLabelFont(42)
        h[selection][5].GetXaxis().SetLabelSize(0.00)
        h[selection][5].GetYaxis().SetLabelSize(0.04)
        h[selection][1].GetYaxis().SetTitle("Events / Category")
        h[selection][3].GetXaxis().SetTitle("BDT output")
        h[selection][3].GetYaxis().SetNdivisions(404)
        h[selection][5].GetYaxis().SetNdivisions(404)
        h[selection][3].GetXaxis().SetTickSize(0.02)
        h[selection][3].GetYaxis().SetTickSize(0.02/0.3*0.7)
        h[selection][5].GetXaxis().SetTitleFont(42)
        h[selection][5].GetYaxis().SetTitleFont(42)
        h[selection][5].GetXaxis().SetTitleSize(0.00)
        h[selection][5].GetYaxis().SetTitleSize(0.025)
        h[selection][5].GetYaxis().SetTitleOffset(2.5)
        h[selection][5].GetXaxis().SetTickSize(0.02)
        h[selection][5].GetYaxis().SetTickSize(0.02/0.3*0.7)
        #
        #
        for hi in h[selection]: hi.SetLineWidth(1)
        h[selection][1].Draw("hist")
        h[selection][0].Draw("hist,same")
        h[selection][2].Draw("hist,same")
        putPave("%.1f fb^{-1} (8 TeV)"%(19.8 if selection==0 else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),align=32)
        putPave("Set %s selection"%("A" if selection==0 else "B"),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),align=12,font=62)
        putPave("%s signal (m_{H} = 125 GeV)"%("VBF" if "VBF" in sample else "GF"),gStyle.GetPadLeftMargin()+0.03,1.-gStyle.GetPadTopMargin()-0.05,align=12,size=0.038,font=62)
        leg = TLegend(gStyle.GetPadLeftMargin()+0.02,0.5,0.5,1.-gStyle.GetPadTopMargin()-0.08)
        leg = styleLeg(leg)
        leg.SetTextSize(0.037)
        leg.SetTextFont(62)
        leg.SetHeader("JER variation")
        leg.SetTextFont(42)
        leg.AddEntry(h[selection][1],"Central","FL")
        leg.AddEntry(h[selection][0],"JER up","FL")
        leg.AddEntry(h[selection][2],"JER up max","FL")
        leg.SetY1(leg.GetY2()-leg.GetNRows()*leg.GetTextSize()*1.25)
        leg.Draw()
        paves += [leg]
        gPad.RedrawAxis()
        p2.cd()
        h[selection][5].Draw("hist")
        gPad.Update()
        putLine(-1,1,1,1)
        p3.cd()
        h[selection][3].SetMarkerSize(0)
        h[selection][3].Draw("hist")
        h[selection][3].SetFillStyle(1001)
        h[selection][3].SetFillColor(h[selection][2].GetLineColor()-9)
        h[selection][3].Draw("e2")
        putLine(-1,1,1,1)
        gPad.RedrawAxis()
    
    cNew.SaveAs("%s_JER.pdf"%sample)
    
####################################################################################################
    c = [cMBB1,cMBB2]
    ctop = [None]*4
    cbot = [None]*4
    h    = [None]*4
    frame,ftmp,x,h1,m,s,a,n,fwhm,b,bkg,fsig,sig,model = [None]*2,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6,[None]*6

    for i,ci in enumerate(c):
        ctop[i] = ci.GetListOfPrimitives().FindObject("ptop")
        cbot[i] = ci.GetListOfPrimitives().FindObject("pbot")
        suffix = '_'.join(ci.GetName().split('_')[1:])
        typ = "JES" if "JES" in ci.GetName() else "JER"
        h[i] = [None]*5
        #for key in ctop[i].GetListOfPrimitives():
        #    print key.GetName()
        h[i][0] = ctop[i].GetListOfPrimitives().FindObject("hHbb_"+suffix)
        h[i][1] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sUp_"%(typ)+suffix)
        h[i][2] = ctop[i].GetListOfPrimitives().FindObject("hHbb%sDn_"%(typ)+suffix)
        h[i][3] = cbot[i].GetListOfPrimitives().FindObject("rHbbJESUp")
        h[i][4] = cbot[i].GetListOfPrimitives().FindObject("rHbbJESDn")
        #extra = "_Comp[signal_bkg_hHbb_%s]"%suffix[:95]
        #print "\033[1;31msignal_model_hHbb_%s_Norm[mbb]%s\033[m"%(suffix[:95],extra)
        #h[i][5] = ctop[i].GetListOfPrimitives().FindObject("signal_model_hHbb_%s_Norm[mbb]"%(suffix[:95]))#,extra))
        #extra = "_Comp[signal_bkg_hHbbJESUp_%s]"%suffix[:90]
        #h[i][6] = ctop[i].GetListOfPrimitives().FindObject("signal_model_hHbbJESUp_%s_Norm[mbb]%s"%(suffix[:90],extra))
        #extra = "_Comp[signal_bkg_hHbbJESDn_%s]"%suffix[:90]
        #h[i][7] = ctop[i].GetListOfPrimitives().FindObject("signal_model_hHbbJESDn_%s_Norm[mbb]%s"%(suffix[:90],extra))
        #h[i][5].Print()
        h[i][0].Rebin(3)
        h[i][1].Rebin(3)
        h[i][2].Rebin(3)
        tmp = h[i][0].Clone()
        tmp.Scale(-1)
        h[i][3] = h[i][1].Clone()
        h[i][3].Add(tmp)
        h[i][3].Divide(h[i][0])
        h[i][4] = h[i][2].Clone()
        h[i][4].Add(tmp)
        h[i][4].Divide(h[i][0])
        h[i][3].GetYaxis().SetTitle("(shifted - central) / central")

    ####################################################################################################
        x[i]  = RooRealVar("mbb%d"%i,"mbb",50,200)
        for loop in range(3):
            I = loop*2+i
            h1[I] = RooDataHist("roombb%d"%I,"roombb",RooArgList(x[i]),h[i][loop])
            m[I]  = RooRealVar("mean%d"%I,"mean",120,110,130)
            s[I]  = RooRealVar("sigma%d"%I,"sigma",12,3,30)
            a[I]  = RooRealVar("a%d"%I,"a",1,-10,10)
            n[I]  = RooRealVar("n%d"%I,"n",1,0,100)
            fwhm[I] = RooRealVar("fwhm%d"%I,"fwhm",25,0,100)
            b[I] = [None]*4
            for j in range(4):
                b[I][j] = RooRealVar("b%d%d"%(j,I),"b%d"%j,0.5,0,1.)
            bkg[I] = RooBernstein("bkg%d"%I,"bkg",x[i],RooArgList(b[I][0],b[I][1],b[I][2]))
            fsig[I] = RooRealVar("fsig%d"%I,"fsig",0.7,0,1)
            sig[I] = RooCBShape("sig%d"%I,"sig",x[i],m[I],s[I],a[I],n[I])
            model[I] = RooAddPdf("model%d"%I,"model",RooArgList(sig[I],bkg[I]),RooArgList(fsig[I]))
            model[I].fitTo(h1[I],RooFit.SumW2Error(kFALSE))

    ####################################################################################################
    cNew = TCanvas("c","c",1800,750)
    cNew.Divide(2,1)
    for selection in [0,1]:
        cNew.cd(selection+1)
        p1 = TPad("p1","p1",0,0,1,1)
        p2 = TPad("p2","p2",0,0,1,1)
        p1.SetBottomMargin(0.3)
        p2.SetTopMargin(0.7)
        p2.SetFillStyle(0)
        p1.Draw()
        p2.Draw("same")
        cNew.Update()
        cNew.Modified()
        p1.cd()
        #
        #h[selection][1].GetYaxis().SetRangeUser(0.01,h[selection][1].GetBinContent(h[selection][1].GetMaximumBin())*1.2)
        #h[selection][1].GetXaxis().SetTitleFont(42)
        #h[selection][1].GetYaxis().SetTitleFont(42)
        #h[selection][1].GetXaxis().SetTitleSize(0.0)
        #h[selection][1].GetYaxis().SetTitleSize(0.05)
        #h[selection][1].GetYaxis().SetTitleOffset(1.2)
        #h[selection][1].GetYaxis().SetNdivisions(508)
        #h[selection][1].GetXaxis().SetTickSize(0.02)
        #h[selection][1].GetYaxis().SetTickSize(0.02)
        #h[selection][1].GetXaxis().SetLabelFont(42)
        #h[selection][1].GetYaxis().SetLabelFont(42)
        #h[selection][1].GetXaxis().SetLabelSize(0.0)
        #h[selection][1].GetYaxis().SetLabelSize(0.04)
        h[selection][3].GetYaxis().SetRangeUser(-0.7,0.7)
        h[selection][3].GetXaxis().SetTitleFont(42)
        h[selection][3].GetYaxis().SetTitleFont(42)
        h[selection][3].GetXaxis().SetTitleSize(0.045)
        h[selection][3].GetYaxis().SetTitleSize(0.025)
        h[selection][3].GetXaxis().SetTitleOffset(1.08)
        h[selection][3].GetYaxis().SetTitleOffset(2.5)
        h[selection][3].GetXaxis().SetLabelFont(42)
        h[selection][3].GetYaxis().SetLabelFont(42)
        h[selection][3].GetXaxis().SetLabelSize(0.04)
        h[selection][3].GetYaxis().SetLabelSize(0.04)
        h[selection][3].GetXaxis().SetTitle("m_{b#bar{b}} GeV")
        h[selection][3].GetYaxis().SetNdivisions(404)
        h[selection][3].GetXaxis().SetTickSize(0.02)
        h[selection][3].GetYaxis().SetTickSize(0.02/0.3*0.7)
        #
        h[selection][3].SetFillStyle(3003)
        h[selection][4].SetFillStyle(3003)
        h[selection][3].SetFillColor(h[selection][1].GetLineColor())
        h[selection][4].SetFillColor(h[selection][2].GetLineColor())
        #
        for hi in h[selection]: hi.SetLineWidth(1)
        #
        frame[selection] = x[selection].frame()
        #frame[selection].GetYaxis().SetRangeUser(0.01,h[selection][1].GetBinContent(h[selection][1].GetMaximumBin())*1.2)
        frame[selection].GetYaxis().SetTitle("Events / (6 GeV)")
        frame[selection].GetXaxis().SetTitleFont(42)
        frame[selection].GetYaxis().SetTitleFont(42)
        frame[selection].GetXaxis().SetTitleSize(0.0)
        frame[selection].GetYaxis().SetTitleSize(0.046)
        frame[selection].GetYaxis().SetTitleOffset(1.4)
        frame[selection].GetYaxis().SetNdivisions(508)
        frame[selection].GetXaxis().SetTickSize(0.02)
        frame[selection].GetYaxis().SetTickSize(0.02)
        frame[selection].GetXaxis().SetLabelFont(42)
        frame[selection].GetYaxis().SetLabelFont(42)
        frame[selection].GetXaxis().SetLabelSize(0.0)
        frame[selection].GetYaxis().SetLabelSize(0.04)
        #
        frame[selection].GetYaxis().SetRangeUser(0.0,h[selection][1].GetBinContent(h[selection][1].GetMaximumBin())*1.25)
        frame[selection].GetXaxis().SetLimits(50,200)
        h1[selection].plotOn(frame[selection],RooFit.MarkerSize(0),RooFit.LineWidth(0))
        for loop in range(3):
#            style = kSolid if loop == 0 else 9
            if loop == 0 : color = kBlack
            elif loop == 1 : color = kBlue
            else : color = kRed + 1
            model[selection+loop*2].plotOn(frame[selection],RooFit.LineWidth(1),RooFit.LineColor(color),RooFit.LineStyle(kSolid))
            model[selection+loop*2].plotOn(frame[selection],RooFit.Components("bkg%d"%(selection+loop*2)),RooFit.LineColor(color),RooFit.LineStyle(kDotted),RooFit.LineWidth(1))
        frame[selection].Draw()
        #
#        ftmp[selection] = model[selection].asTF(RooArgList(x[selection]),RooArgList(fsig[selection]),RooArgSet(x[selection]))
 #       print ftmp[selection].Integral(50,200)
#        h[selection][0].Scale(1./ftmp[selection].Integral(50,200))
        h[selection][0].Draw("hist,same")
        h[selection][1].Draw("hist,same")
        h[selection][2].Draw("hist,same")
        frame[selection].Draw("same")
        putPave("%.1f fb^{-1} (8 TeV)"%(19.8 if selection==0 else 18.3),1.-gStyle.GetPadRightMargin()-0.01,1.-0.5*gStyle.GetPadTopMargin(),align=32)
        putPave("Set %s selection"%("A" if selection==0 else "B"),gStyle.GetPadLeftMargin()+0.01,1.-0.5*gStyle.GetPadTopMargin(),align=12,font=62)
        putPave("%s signal (m_{H} = 125 GeV)"%("VBF" if "VBF" in sample else "GF"),gStyle.GetPadLeftMargin()+0.03,1.-gStyle.GetPadTopMargin()-0.05,align=12,size=0.038,font=62)
        leg = TLegend(gStyle.GetPadLeftMargin()+0.02,0.5,0.5,1.-gStyle.GetPadTopMargin()-0.08)
        leg = styleLeg(leg)
        leg.SetTextSize(0.037)
        leg.SetTextFont(62)
        leg.SetHeader("JES variation")
        leg.SetTextFont(42)
        leg.AddEntry(h[selection][0],"Central","FL")
        leg.AddEntry(h[selection][1],"JES up","FL")
        leg.AddEntry(h[selection][2],"JES down","FL")
        leg.SetY1(leg.GetY2()-leg.GetNRows()*leg.GetTextSize()*1.25)
        leg.Draw()
        paves += [leg]
        gPad.RedrawAxis()
        p2.cd()
        h[selection][3].Draw("hist")
        h[selection][4].Draw("hist,same")
        putLine(50,0,200,0)
        gPad.RedrawAxis()
    
    cNew.SaveAs("%s_MBB.pdf"%sample)
    
####################################################################################################

f.Close()
