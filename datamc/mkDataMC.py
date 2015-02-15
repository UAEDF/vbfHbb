#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../common/')

from optparse import OptionParser

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from write_cuts import *
import main

# OPTION PARSER ####################################################################################
def parser(mp=None):
	if mp==None: mp = OptionParser()

	mg1 = OptionGroup(mp,cyan+"DataMc settings"+plain)

	mp.add_option_group(mg1)
	return mp

####################################################################################################
def ROOTsetup():
    gROOT.SetBatch(1)
    gROOT.ProcessLineSync(".x ../common/styleCMSTDR.C")
    gStyle.SetPadLeftMargin(0.13)
    gStyle.SetPadRightMargin(0.04)
    gStyle.SetPadTopMargin(0.06)
    gStyle.SetPadBottomMargin(0.105)
    gStyle.SetTitleOffset(1.01,"X")
    gStyle.SetTitleOffset(1.20,"Y")
    gStyle.SetTitleSize(0.045,"XY")
    gStyle.SetLabelSize(0.038,"XY")
    
####################################################################################################
def FormatPave(P):
    P.SetTextSize(0.030)
    P.SetTextFont(62)
    P.SetTextColor(kBlack)
    P.SetFillStyle(-1)
    P.SetBorderSize(0)

####################################################################################################
def FormatLegend(L):
    L.SetTextSize(0.030)
    L.SetTextFont(42)
    L.SetTextColor(kBlack)
    L.SetNColumns(3)
    L.SetFillStyle(-1)
    L.SetBorderSize(0)

####################################################################################################
def loadSamples(opts,samples):
    toLoad = []
    for s in samples.keys():
        if any(x in s for x in opts.sample) and not any(x in s for x in opts.nosample):
            toLoad += [s]
    Lsamples = {}
    jsoninfo = json.loads(filecontent(opts.jsoninfo))
    jsonvars = json.loads(filecontent(opts.jsonvars))['variables']
    jsonsamp = json.loads(filecontent(opts.jsonsamp))['files']
    for n in toLoad:
        Lsamples[n] = {}
        Lsamples[n]['f'] = TFile.Open(opts.globalpath+"/"+n,"read") # file
        Lsamples[n]['t'] = Lsamples[n]['f'].Get("Hbb/events")       # tree
        Lsamples[n]['g'] = jsoninfo['groups'][samples[n]['tag'].replace('_sNOM','').replace('_sVBF','')]    # group
        Lsamples[n]['s'] = jsonsamp[n]['scale']                     # scale
        Lsamples[n]['i'] = samples[n]                               # info
    return jsoninfo, jsonvars, jsonsamp, Lsamples

def closeSamples(Lsamples):
    for s in Lsamples.itervalues():
        s['f'].Close()

####################################################################################################
def hists(s,v,c):
    h = {}
    for sn,si in s.iteritems():
        for vn,vi in v.iteritems():
            for cn in [''.join(x) for x in c]:
                st = si['i']['tag']
                vt = vn
                ct = cn
                ht = "h_s%s_v%s_c%s"%(st,vt,ct)
                binsize = (float(vi['xmax'])-float(vi['xmin']))/float(vi['nbins_x'])
                h[ht] = TH1F(ht,ht+";%s;%s"%(vi['title_x'],"Events / (%.2g)"%binsize),int(vi['nbins_x']),float(vi['xmin']),float(vi['xmax']))
                h[ht].Sumw2()
    for gn in list(set([x['g'] for (k,x) in s.iteritems()])):
        for vn,vi in v.iteritems():
            for cn in [''.join(x) for x in c]:
                ht = "h_s%s_v%s_c%s"%(gn,vn,cn)
                binsize = (float(vi['xmax'])-float(vi['xmin']))/float(vi['nbins_x'])
                h[ht] = TH1F(ht,ht+";%s;%s"%(vi['title_x'],"Events / (%.2g)"%binsize),int(vi['nbins_x']),float(vi['xmin']),float(vi['xmax']))
                h[ht].Sumw2()
    return h
    
####################################################################################################
def datamc():
    mp = parser()
    opts,fout,samples,variables = main.main(mp,False,True,True)

    ROOTsetup()
    eps = 0.0001

    ji, jv, js, Lsamples = loadSamples(opts,samples)
    Lvariables = {k:v for (k,v) in variables.iteritems() if k in opts.variable}

    can = TCanvas("c","c",900,900)
    can.cd()
    
    # histos
    histos = hists(Lsamples,Lvariables,opts.selection)
    stacks = {}

    l1("Filling histograms")
    for s in opts.selection:
        for t in opts.trigger:
            pcms1 = TPaveText(0.6,1.0-gStyle.GetPadTopMargin(),1.0-gStyle.GetPadRightMargin(),1.0,"NDC")
            FormatPave(pcms1)
            pcms1.AddText("%.1f fb^{-1} (8 TeV)"%(float(opts.weight[0][0])/1000.))
            pcms1.SetTextAlign(32)
            pcms1.SetTextSize(gStyle.GetPadTopMargin()*2.5/4.)
            pcms2 = TPaveText(gStyle.GetPadLeftMargin(),1.0-gStyle.GetPadTopMargin(),0.5,1.0,"NDC")
            FormatPave(pcms2)
            pcms2.AddText("%s selection"%s[0].replace('NOM','Set A').replace('VBF','Set B'))
            pcms2.SetTextAlign(12)
            pcms2.SetTextSize(gStyle.GetPadTopMargin()*2.5/4.)
            # cuts
            cut,cutlabel = write_cuts(s,t,reftrig=["None"],sample=Lsamples[Lsamples.keys()[0]]['i']['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
            cut1,cut2 = cut.split(' * ')[0][1:],cut.split(' * ')[1][:-1]
            # sample loop
            for sn,si in sorted(Lsamples.iteritems()):
                l2("Sample: %s"%sn)
                st = si['i']['tag']
                sg = si['g']
                ca,cal = write_cuts(s,t,reftrig=["None"],sample=st,jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
                ca1,ca2 = ca.split(' * ')[0][1:],ca.split(' * ')[1][:-1]
                n = si['t'].GetEntries()
                # variable loop
                for vn,vi in Lvariables.iteritems(): 
                    l3(vn)
                    ht = "h_s%s_v%s_c%s"%(st,vn,s[0])
                    si['t'].Draw("%s>>%s"%(vi['root'],ht),"%s"%ca2)
            # stacking
            for sn,si in sorted(Lsamples.iteritems()):
                sg = si['g']
                st = si['i']['tag']
                for vn,vi in Lvariables.iteritems():
                    hg = "h_s%s_v%s_c%s"%(sg,vn,s[0])
                    ht = "h_s%s_v%s_c%s"%(st,vn,s[0])
                    Hg = histos[hg]
                    Ht = histos[ht]
                    Hg.Add(Ht)
            # k-factor
            INTEGRALS = {"Data":0.0,"QCD":0.0,"Other":0.0}
            for ig,g in enumerate(list(set([x['g'] for (k,x) in Lsamples.iteritems()]))):
                var = Lvariables.keys()[0]
                hg = "h_s%s_v%s_c%s"%(g,var,s[0]) 
                if g=="VBF125": continue
                elif g=="Data": INTEGRALS["Data"] += float(histos[hg].Integral())
                elif g=="QCD": INTEGRALS["QCD"] += float(histos[hg].Integral())
                else: INTEGRALS["Other"] += float(histos[hg].Integral())
            kfactor = (INTEGRALS["Data"]-INTEGRALS["Other"])/INTEGRALS["QCD"]
            l1("K-factor: %.2f"%kfactor)
            # groups
            l1("Group iteration")
            for vn,vi in Lvariables.iteritems():
                p1 = TPad("p1","p1",0.0,0.0,1.0,1.0)
                p2 = TPad("p2","p2",0.0,0.0,1.0,1.0)
                p1.SetBottomMargin(0.3)
                p2.SetTopMargin(1.-0.29)
                p2.SetFillStyle(-1)
                p1.Draw()
                p2.Draw()
                can.Update()
                can.Modified()
                # top pad
                p1.cd()
                l2("Variable: %s"%(vn))
                DRAW = {}
                hs = "s_v%s_c%s"%(vn,s[0])
                S  = THStack(hs,hs)
                L = TLegend(gStyle.GetPadLeftMargin()+0.03,0.5,gStyle.GetPadLeftMargin()+0.03+0.22*3,1.-gStyle.GetPadTopMargin()-0.025)
                FormatLegend(L)
                for ig,g in enumerate(sorted(list(set([x['g'] for (k,x) in Lsamples.iteritems()])),key=lambda y:(histos["h_s%s_v%s_c%s"%(y,vn,s[0])].Integral()))):
                    l3("%s"%(g))
                    hg = "h_s%s_v%s_c%s"%(g,vn,s[0])
                    Hg = histos[hg]
                    #Hg.Fill(Hg.GetBinCenter(Hg.GetNbinsX()+0),Hg.GetBinContent(Hg.GetNbinsX()+1))
                    Hg.SetBinContent(Hg.GetNbinsX(),0.5*(Hg.GetBinContent(Hg.GetNbinsX())+Hg.GetBinContent(Hg.GetNbinsX()+1)))
                    Hg.SetBinError(Hg.GetNbinsX(),sqrt(pow(Hg.GetBinError(Hg.GetNbinsX()),2.)+pow(Hg.GetBinError(Hg.GetNbinsX()+1),2.)))
                    if g=="Data":
                        Hg.SetMarkerStyle(20)
                        Hg.SetMarkerColor(kBlack)
                        Hg.SetMarkerSize(1.2)
                        DRAW["Data"] = Hg
                    elif g=="VBF125":
                        Hg.SetLineStyle(1)
                        Hg.SetLineColor(ji['colours'][g])
                        Hg.SetLineWidth(2)
                        Hg.Scale(10.)
                        DRAW["SIG"] = Hg
                    else:
                        Hg.SetLineStyle(1)
                        Hg.SetLineColor(kBlack)
                        Hg.SetFillStyle(1001)
                        Hg.SetFillColor(ji['colours'][g])
                        if g=="QCD": Hg.Scale(kfactor)
                        S.Add(Hg)
                L.AddEntry(Hg,"Data","P")
                L.AddEntry(histos["h_s%s_v%s_c%s"%("QCD",vn,s[0])],"%s (x%.2f)"%("QCD",kfactor),"F")
                L.AddEntry(histos["h_s%s_v%s_c%s"%("ZJets",vn,s[0])],"%s"%("ZJets"),"F")
                L.AddEntry(histos["h_s%s_v%s_c%s"%("VBF125",vn,s[0])],"VBF (125) (x10)","L")
                L.AddEntry(histos["h_s%s_v%s_c%s"%("Tall",vn,s[0])],"%s"%("T"),"F")
                L.AddEntry(histos["h_s%s_v%s_c%s"%("WJets",vn,s[0])],"%s"%("WJets"),"F")
                DRAW["BKG"] = S

                DRAW["BKG"].Draw("hist")
                S.SetMinimum(1.0)
                S.SetMaximum(S.GetStack().Last().GetBinContent(S.GetStack().Last().GetMaximumBin())*100.)
#                S.GetStack().Last().GetYaxis().SetRangeUser(1.0,S.GetStack().Last().GetBinContent(S.GetStack().Last().GetMaximumBin())*100.)
                S.GetXaxis().SetTitle(S.GetStack().Last().GetXaxis().GetTitle())
                S.GetXaxis().SetTitleSize(0)
                S.GetXaxis().SetLabelSize(0)
                S.GetYaxis().SetTitle(S.GetStack().Last().GetYaxis().GetTitle())
                S.GetXaxis().SetDecimals(kTRUE)
                S.GetYaxis().SetDecimals(kTRUE)
                Sall = S.GetStack().Last()
                MCerr = Sall.Clone("MCerr") 
                MCerr.SetFillStyle(3004)
                MCerr.SetFillColor(kBlack)
                MCerr.SetMarkerSize(0)
                gPad.Update()
                DRAW["Data"].Draw("PE,same")
                DRAW["SIG"].Draw("hist,same")
                MCerr.Draw("E2,same")
                L.AddEntry(MCerr,"MC stat. unc.","F")
                L.SetY1(L.GetY2()-L.GetNRows()*0.04)
                L.Draw()
                pcms1.Draw()
                pcms2.Draw()
                gPad.SetLogy(1)
                gPad.RedrawAxis()
                # bottom pad
                p2.cd()
                one = DRAW["Data"].Clone("one")
                for ibin in range(0,one.GetNbinsX()+2): 
                    one.SetBinContent(ibin,1.)
                    one.SetBinError(ibin,0.)
                rat = DRAW["Data"].Clone(DRAW["Data"].GetName().replace('h','hRat'))
                rat.GetYaxis().SetTitle("Data/MC - 1")
                rat.GetYaxis().SetTitleSize(0.038)
                rat.GetYaxis().SetLabelSize(0.034)
                rat.GetYaxis().SetTitleOffset(1.50)
                rat.GetXaxis().SetDecimals(kTRUE)
                rat.GetYaxis().SetDecimals(kTRUE)
                rat.GetYaxis().SetNdivisions(405)
                rat.GetYaxis().SetTickSize(0.03*0.7/0.3)
                rat.SetMarkerSize(1.1)
                rat.Divide(DRAW["BKG"].GetStack().Last())
                rat.Add(one,-1.)
                rat.Draw()
                rat.GetYaxis().SetRangeUser(-1.0+eps,1.0-eps)
                ratMCerr = MCerr.Clone("ratMCerr")
                ratMCerr.Divide(DRAW["BKG"].GetStack().Last())
                ratMCerr.Add(one,-1.)
                ratMCerr.Draw("E2,same")
                gPad.SetGridy(1)
                gPad.Update()
                line = TF1("l1","0.",gPad.GetUxmin(),gPad.GetUxmax())
                line.SetLineColor(kBlack)
                line.Draw("same")
                gPad.RedrawAxis()
                # save
                can.SaveAs("%s_s%s.pdf"%(vn,s[0]))
                can.SaveAs("%s_s%s.png"%(vn,s[0]))
                can.Clear()

    
    # clean   
    can.Close()
    closeSamples(Lsamples)

           
####################################################################################################
if __name__=='__main__':
    datamc()

