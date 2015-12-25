#!/usr/bin/env python

import sys,os,json,re
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

from optparse import OptionParser

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from toolkit import *
from write_cuts import *
from math import *
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
    gStyle.SetPadTopMargin(0.067)
    gStyle.SetPadBottomMargin(0.105)
    gStyle.SetTitleOffset(1.01,"X")
    gStyle.SetTitleOffset(1.20,"Y")
    gStyle.SetTitleSize(0.045,"XY")
    gStyle.SetLabelSize(0.038,"XY")
    gStyle.SetFillColor(0)
    gStyle.SetPadBorderSize(0)
    gStyle.SetCanvasColor(-1); 
    gStyle.SetPadColor(-1); 
    #gStyle.SetFrameFillColor(-1); 
    gStyle.SetFrameFillStyle(0); 
    ##gStyle.SetHistFillColor(-1); 
    gStyle.SetFillStyle(0); 
    #gStyle.SetFillColor(-1); 
    gStyle.SetLineScalePS(2.1)
    
####################################################################################################
def hTag(a,b,c):
    return "h_s%s_v%s_c%s"%(a,b,c)

####################################################################################################
def FormatRatio(rat):
    rat.GetYaxis().SetTitle("Data/MC - 1")
    rat.GetYaxis().SetTitleSize(0.038)
    rat.GetYaxis().SetLabelSize(0.034)
    rat.GetYaxis().SetTitleOffset(1.50)
    rat.GetXaxis().SetDecimals(kTRUE)
    rat.GetYaxis().SetDecimals(kTRUE)
    rat.GetYaxis().SetNdivisions(405)
    rat.GetYaxis().SetTickSize(0.03*0.7/0.3)
    rat.SetMarkerSize(1.1)

####################################################################################################
def FormatStack(S):
    Sall = S.GetStack().Last()
    S.SetMinimum(1.0)
    S.SetMaximum(Sall.GetBinContent(Sall.GetMaximumBin())*100.)
    S.GetXaxis().SetTitle(Sall.GetXaxis().GetTitle())
    S.GetXaxis().SetTitleSize(0)
    S.GetXaxis().SetLabelSize(0)
    S.GetYaxis().SetTitle(Sall.GetYaxis().GetTitle())
    S.GetXaxis().SetDecimals(kTRUE)
    S.GetYaxis().SetDecimals(kTRUE)
    return Sall

####################################################################################################
def FormatCMSPaves(opts,s):
    pcms1 = TPaveText(0.6,1.0-gStyle.GetPadTopMargin(),1.0-gStyle.GetPadRightMargin(),1.0,"NDC")
    FormatPave(pcms1)
    pcms1.AddText("%.1f fb^{-1} (8 TeV)"%(float(opts.weight[0][0])/1000.))
    pcms1.SetTextAlign(32)
    pcms1.SetTextSize(gStyle.GetPadTopMargin()*2.6/4.)
    pcms2 = TPaveText(gStyle.GetPadLeftMargin(),1.0-gStyle.GetPadTopMargin(),0.5,1.0,"NDC")
    FormatPave(pcms2)
    pcms2.AddText("%s selection"%s[0].replace('NOM','Set A').replace('VBF','Set B').replace('TPN','Top A').replace('TPV','Top B'))
    pcms2.SetTextAlign(12)
    pcms2.SetTextSize(gStyle.GetPadTopMargin()*2.6/4.)
    return pcms1,pcms2

####################################################################################################
def FormatPads(can):
    p1 = TPad("p1","p1",0.0,0.0,1.0,1.0)
    p2 = TPad("p2","p2",0.0,0.0,1.0,1.0)
    p1.SetBottomMargin(0.3)
    p2.SetTopMargin(1.-0.29)
    p2.SetFillStyle(-1)
    p1.Draw()
    p2.Draw()
    can.Update()
    can.Modified()
    return p1,p2

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
        Lsamples[n]['g'] = jsoninfo['groups'][samples[n]['tag'].replace('_sNOM','').replace('_sVBF','').replace('_sTPN','').replace('_sTPV','')]    # group
        Lsamples[n]['s'] = jsonsamp[n]['scale']                     # scale
        Lsamples[n]['i'] = samples[n]                               # info
    return jsoninfo, jsonvars, jsonsamp, Lsamples

####################################################################################################
def closeSamples(Lsamples):
    for s in Lsamples.itervalues():
        s['f'].Close()

####################################################################################################
def hists(s,v,c):
    h = {}
    for sn,si in s.iteritems():
        for vn,vi in v.iteritems():
            #for cn in [''.join(x) for x in c]:
            for cn in [x[0] for x in c]:
                st = si['i']['tag']
                vt = vn
                ct = cn
                ht = hTag(st,vt,ct)
                binsize = (float(vi['xmax'])-float(vi['xmin']))/float(vi['nbins_x'])
                h[ht] = TH1F(ht,ht+";%s;%s"%(vi['title_x'],"Events / (%.2g%s)"%(binsize," GeV" if "GeV" in vi['title_x'] else "")),int(vi['nbins_x']),float(vi['xmin']),float(vi['xmax']))
                h[ht].Sumw2()
    for gn in list(set([x['g'] for (k,x) in s.iteritems()])):
        for vn,vi in v.iteritems():
            #for cn in [''.join(x) for x in c]:
            for cn in [x[0] for x in c]:
                ht = hTag(gn,vn,cn)
                binsize = (float(vi['xmax'])-float(vi['xmin']))/float(vi['nbins_x'])
                h[ht] = TH1F(ht,ht+";%s;%s"%(vi['title_x'],"Events / (%.2g%s)"%(binsize," GeV" if "GeV" in vi['title_x'] else "")),int(vi['nbins_x']),float(vi['xmin']),float(vi['xmax']))
                h[ht].Sumw2()
    return h
    
####################################################################################################
def datamc():
    # options
    mp = parser()
    opts,fout,samples,variables = main.main(mp,False,True,True)

    # root setup
    ROOTsetup()
    eps = 0.0001

    # samples / variables
    ji, jv, js, Lsamples = loadSamples(opts,samples)
    Lvariables = {k:v for (k,v) in variables.iteritems() if k in opts.variable}

    # canvas
    can = TCanvas("c","c",900,750)
    can.cd()
    
    # histos
    histos = hists(Lsamples,Lvariables,opts.selection)
    stacks = {}

##################################################
    l1("Filling histograms")
    for s in opts.selection:
        for t in opts.trigger:
            # cms paves
            pcms1,pcms2 = FormatCMSPaves(opts,s)
####        # cuts
####        cut,cutlabel = write_cuts(s,t,reftrig=["None"],sample=Lsamples[Lsamples.keys()[0]]['i']['tag'],jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
####        cut1,cut2 = cut.split(' * ')[0][1:],cut.split(' * ')[1][:-1]
##################################################
            # sample loop
            for sn,si in sorted(Lsamples.iteritems()):
                l2("Sample: %s"%sn)
                st = si['i']['tag']
                sg = si['g']
                ca,calabel = write_cuts(s,t,reftrig=["None"],sample=st,jsonsamp=opts.jsonsamp,jsoncuts=opts.jsoncuts,weight=opts.weight,trigequal=trigTruth(opts.usebool))
                ca1,ca2 = ca.split(' * ')[0][1:],ca.split(' * ')[1][:-1]
                n = si['t'].GetEntries()
                print ca2
                # variable loop
                for vn,vi in sorted(Lvariables.iteritems()): 
                    l3(vn)
                    ht = hTag(st,vn,s[0])
                    si['t'].Draw("%s>>%s"%(vi['root'],ht),"%s"%ca2)
##################################################
            # stacking
            for sn,si in sorted(Lsamples.iteritems()):
                sg = si['g']
                st = si['i']['tag']
                for vn,vi in sorted(Lvariables.iteritems()):
                    hg = hTag(sg,vn,s[0])
                    ht = hTag(st,vn,s[0])
                    Hg = histos[hg]
                    Ht = histos[ht]
                    Hg.Add(Ht)
##################################################
            # k-factor
            INTEGRALS = {"Data":0.0,"QCD":0.0,"Other":0.0,"TTJets":0.0}
            if "KF" in opts.weight[1] and not ('TP' in t[0]):
                #print "if"
                for ig,g in enumerate(list(set([x['g'] for (k,x) in Lsamples.iteritems()]))):
                    var = Lvariables.keys()[0]
                    hg = hTag(g,var,s[0]) 
                    if g=="VBF125": continue
                    elif g=="Data": INTEGRALS["Data"] += float(histos[hg].Integral())
                    elif g=="QCD": INTEGRALS["QCD"] += float(histos[hg].Integral())
                    else: INTEGRALS["Other"] += float(histos[hg].Integral())
                kfactor = (INTEGRALS["Data"]-INTEGRALS["Other"])/INTEGRALS["QCD"]
                l1("K-factor: %.2f"%kfactor)
            elif "KF" in opts.weight[1]:
                #print "elif"
                for ig,g in enumerate(list(set([x['g'] for (k,x) in Lsamples.iteritems()]))):
                    var = Lvariables.keys()[0]
                    hg = hTag(g,var,s[0]) 
                    if g=="VBF125": continue
                    elif g=="Data": INTEGRALS["Data"] += float(histos[hg].Integral())
                    elif g=="TTJets": INTEGRALS["TTJets"] += float(histos[hg].Integral())
                    else: INTEGRALS["Other"] += float(histos[hg].Integral())
                kfactor = (INTEGRALS["Data"]-INTEGRALS["Other"])/INTEGRALS["TTJets"]
                l1("K-factor: %.2f"%kfactor)
##################################################
            # groups
            l1("Group iteration")
            can.Clear()
            for vn,vi in sorted(Lvariables.iteritems()):
                fout.cd()
                # set pads
                p1,p2 = FormatPads(can)
##################################################
                # top pad
                p1.cd()
                # containers 
                l2("Variable: %s"%(vn))
                DRAW = {}
                hs = "s_v%s_c%s"%(vn,s[0])
                S  = THStack(hs,hs)
                L = TLegend(gStyle.GetPadLeftMargin()+0.03,0.5,gStyle.GetPadLeftMargin()+0.03+0.23*3,1.-gStyle.GetPadTopMargin()-0.025)
                FormatLegend(L)
                # group loop
                for ig,g in enumerate(sorted(list(set([x['g'] for (k,x) in Lsamples.iteritems()])),key=lambda y:(not '125' in y,not 'WJets' in y,histos[hTag(y,vn,s[0])].Integral()))):
                    l3("%s"%(g))
                    hg = hTag(g,vn,s[0])
                    Hg = histos[hg]
                    print Hg.Integral()
                    # underflow
                    Hg.SetBinContent(1,0.5*(Hg.GetBinContent(0)+Hg.GetBinContent(1)))
                    Hg.SetBinError(1,sqrt(pow(Hg.GetBinError(0),2.)+pow(Hg.GetBinError(1),2.)))
                    # overflow
                    Hg.SetBinContent(Hg.GetNbinsX(),0.5*(Hg.GetBinContent(Hg.GetNbinsX())+Hg.GetBinContent(Hg.GetNbinsX()+1)))
                    Hg.SetBinError(Hg.GetNbinsX(),sqrt(pow(Hg.GetBinError(Hg.GetNbinsX()),2.)+pow(Hg.GetBinError(Hg.GetNbinsX()+1),2.)))
                    # type handling
                    if g=="Data":
                        Hg.SetMarkerStyle(20)
                        Hg.SetMarkerColor(kBlack)
                        Hg.SetMarkerSize(1.2)
                        DRAW["Data"] = Hg
                    elif g=="VBF125":
                        Hg.SetLineStyle(1)
                        Hg.SetLineColor(ji['colours'][g])
                        Hg.SetLineWidth(3)
                        Hg.Scale(10.)
                        DRAW["SIG"] = Hg
                    elif g=="GF125":
                        Hg.SetLineStyle(7)
                        Hg.SetLineColor(ji['colours'][g])
                        Hg.SetLineWidth(3)
                        Hg.Scale(10.)
                        DRAW["SIGGF"] = Hg
                    else:
                        Hg.SetLineStyle(1)
                        Hg.SetLineColor(kBlack)
                        Hg.SetFillStyle(1001)
                        Hg.SetFillColor(ji['colours'][g])
                        if g=="QCD" and (not "TP" in t[0]) and "KF" in opts.weight[1]: Hg.Scale(kfactor)
                        if g=="TTJets" and ("TP" in t[0]) and "KF" in opts.weight[1]: Hg.Scale(kfactor)
                        if not Hg.GetEntries()==0: S.Add(Hg)
                # Full stack (bkg)
                DRAW["BKG"] = S
                S.Draw()
                Sall = FormatStack(S)
                # MC err 
                histos[hTag("MCerr",vn,s[0])] = Sall.Clone(hTag("MCerr",vn,s[0])) 
                Hg = histos[hTag("MCerr",vn,s[0])]
                Hg.SetFillStyle(3004)
                Hg.SetFillColor(kGray+2)#kBlack)
                Hg.SetMarkerSize(0)
                DRAW["MCerr"] = Hg
                # Fill legend
                L.AddEntry(histos[hTag("Data",vn,s[0])],"Data","P")
                L.AddEntry(histos[hTag("QCD",vn,s[0])],"%s%s"%("QCD"," (x%.2f)"%kfactor if ("KF" in opts.weight[1] and not "TP" in t[0]) else ""),"F")
                L.AddEntry(histos[hTag("ZJets",vn,s[0])],"%s"%("ZJets"),"F")
                L.AddEntry(histos[hTag("VBF125",vn,s[0])],"10x VBF H(125)","L")
                if hTag("Tall",vn,s[0]) in histos:
                    L.AddEntry(histos[hTag("Tall",vn,s[0])],"%s%s"%("T"," (x%.2f)"%kfactor if ("KF" in opts.weight[1] and "TP" in t[0]) else ""),"F")
                else: 
                    L.AddEntry(histos[hTag("TTJets",vn,s[0])],"%s%s"%("TTJets"," (x%.2f)"%kfactor if ("KF" in opts.weight[1] and "TP" in t[0]) else ""),"F")
                L.AddEntry(histos[hTag("WJets",vn,s[0])],"%s"%("WJets"),"F")
                L.AddEntry(histos[hTag("GF125",vn,s[0])],"10x GF H(125)","L")
                if not hTag("Tall",vn,s[0]) in histos:
                    L.AddEntry(histos[hTag("singleT",vn,s[0])],"%s"%("singleT"),"F")
                L.AddEntry(histos[hTag("MCerr",vn,s[0])],"MC stat. unc.","F")
                # Draw
                DRAW["BKG"].Draw("hist")
                DRAW["Data"].Draw("PE,same")
                DRAW["SIG"].Draw("hist,same")
                DRAW["SIGGF"].Draw("hist,same")
                DRAW["MCerr"].Draw("E2,same")
                # Edit legend
                L.SetY1(L.GetY2()-L.GetNRows()*0.04)
                L.Draw()
                # Draw paves
                pcms1.Draw()
                pcms2.Draw()
                # Edit canvas
                gPad.SetLogy(1)
                gPad.RedrawAxis()
                p1.Write(p1.GetName()+("NOM" if "NOM" in opts.selection[0] else "VBF")+vn)
##################################################
                # bottom pad
                p2.cd()
                # histo = 1
                one = DRAW["Data"].Clone("one")
                for ibin in range(0,one.GetNbinsX()+2): 
                    one.SetBinContent(ibin,1.)
                    one.SetBinError(ibin,0.)
                # ratio Data/MC - 1
                rat = DRAW["Data"].Clone(DRAW["Data"].GetName().replace('h','hRat'))
                FormatRatio(rat)
                rat.Divide(DRAW["BKG"].GetStack().Last())
                rat.Add(one,-1.)
                histos[hTag("Data/MC",vn,s[0])] = rat
                # ratio MCerr/MC - 1
                ratMCerr = histos[hTag("MCerr",vn,s[0])].Clone("ratMCerr")
                ratMCerr.Divide(DRAW["BKG"].GetStack().Last())
                ratMCerr.Add(one,-1.)
                histos[hTag("MCerrDataMC",vn,s[0])] = ratMCerr
                # Draw
                rat.Draw()
                ratMCerr.Draw("E2,same")
                # Edit pad
                rat.GetYaxis().SetRangeUser(-1.0+eps,1.0-eps)
                gPad.SetGridy(1)
                gPad.Update()
                line = TF1("l1","0.",gPad.GetUxmin(),gPad.GetUxmax())
                line.SetLineColor(kBlack)
                line.Draw("same")
                gPad.RedrawAxis()
##################################################
                # save
                plotdir = "./plots/%s"%s[0]
                if not os.path.exists(plotdir): makeDirs(plotdir)
                can.SaveAs("%s/%s_s%s.pdf"%(plotdir,vn,s[0]))
                can.SaveAs("%s/%s_s%s.png"%(plotdir,vn,s[0]))
                fout.cd()
                can.Clear()
    
##################################################
    # clean   
    can.Close()
    closeSamples(Lsamples)

           
####################################################################################################
if __name__=='__main__':
    datamc()

