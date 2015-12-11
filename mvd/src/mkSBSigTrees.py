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
import main
from numpy import zeros
from copy import deepcopy
global paves
paves = []

# OPTION PARSER ####################################################################################
def parser(mp=None):
        if mp==None: mp = OptionParser()

        mg1 = OptionGroup(mp,cyan+"Tree making settings"+plain)
        mg1.add_option("--step",type='int',default=0)
        mg1.add_option("--sel",type='str',default='NOM')
        mg1.add_option("--alttag",type='str',default="")
        mg1.add_option("--alt",action='store_true',default=False)
        mg1.add_option("--replot",action='store_true',default=False)
        mg1.add_option("--tmva",type='str',default='BDT')
        mg1.add_option("-N","--nentries",type='int',default=-1)

        mp.add_option_group(mg1)
        return mp

####################################################################################################
def match(matchIdx,matchDR,Id):
    subvec = []
    for ii,idx in enumerate(matchIdx):
        if matchDR[ii]<0.25:
            subvec += [[idx,matchDR[ii],Id[ii]]]
    idxvec = [x for x,y,z in subvec]
    if sorted(idxvec) == range(4):
        return subvec
    else:
        remove = []
        for vi in subvec:
            if sum([vi[0]==x for x in idxvec])==1 and vi[0]<4: 
                continue 
            else: 
                remove += [vi]
        for vi in remove: subvec.remove(vi)
        return subvec 

####################################################################################################
def tlpave(text,scale=0.9,hl=0):
    global paves
    p = TText(gStyle.GetPadLeftMargin(),1.0-0.01,text)
    p.SetNDC()
    p.SetTextSize(gStyle.GetPadTopMargin()*scale)
    p.SetTextFont(42 if hl==0 else 62)
    p.SetTextAlign(13)
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def trpave(text,scale=0.9,hl=0):
    global paves
    p = TText(1.-gStyle.GetPadRightMargin(),1.0-0.01,text)
    p.SetNDC()
    p.SetTextSize(gStyle.GetPadTopMargin()*scale)
    p.SetTextFont(42 if hl==0 else 62)
    p.SetTextAlign(33)
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def epave(text,x,y,size=0.04):
    global paves
    p = TText(x,y,text)
    #p.SetNDC()
    p.SetTextSize(size)
    p.SetTextFont(42)
    p.SetTextAlign(21)
    p.SetTextColor(kBlack)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def epavetext(text,x,y,x2,y2,size=0.04,hl=1):
    global paves
    p = TPaveText(x,y,x2,y2,"NDC")
    p.SetTextSize(size)
    p.SetTextFont(42)
    p.SetTextAlign(11)
    p.SetTextColor(kBlack)
    p.SetFillStyle(0)
    p.SetBorderSize(0)
    for i,t in enumerate(text): 
        ti = p.AddText(t)
        if i==0: ti.SetTextFont(62)
    p.Draw("same")
    paves += [p]
    return p

####################################################################################################
def btagTrafo(hin,typ,fc,fs,lc):
    hout = TH1F("h%s_btagnew"%typ,"h%s_btagnew;CSV b-tag;N / (0.05)"%typ,23,-0.15,1.0)
    for i in range(4,hin.GetNbinsX()+1): hout.SetBinContent(i,hin.GetBinContent(i))
    hout.SetBinContent(1,hin.GetBinContent(1))
    hout.SetBinContent(2,hin.GetBinContent(3))
    hout.SetFillColor(fc)
    hout.SetFillStyle(fs)
    hout.SetLineColor(lc)
    hout.Scale(1./hout.Integral())
    hout.GetYaxis().SetRangeUser(0.0005,hout.GetBinContent(hout.GetMaximumBin())*75)
    hout.GetYaxis().SetNdivisions(4)
    return hout

####################################################################################################
def makeGraph(hsig,hbkg,direction="right"):
    n = hsig.GetName()
    xtrue = [0.]*1000
    yfake = [0.]*1000
    for i in range(hsig.GetNbinsX()):
        xtrue[i] = hsig.Integral(i,hsig.GetNbinsX())
        if not direction=="right": xtrue[i] = 1. - xtrue[i]
    for i in range(hbkg.GetNbinsX()):
        yfake[i] = 1. - hbkg.Integral(i,hbkg.GetNbinsX())
        if not direction=="right": yfake[i] = -yfake[i] + 1.
    g = TGraph(hsig.GetNbinsX(),array('f',xtrue[0:hsig.GetNbinsX()]),array('f',yfake[0:hsig.GetNbinsX()]))
    g.SetLineColor(kRed if "btag" in n else (kGreen+2 if "eta" in n else kBlue))
    g.GetXaxis().SetLimits(0.7,1.05)
    g.GetYaxis().SetRangeUser(0.0,1.1)
    g.GetXaxis().SetTitle("Efficiency of matched b-jets")
    g.GetYaxis().SetTitle("Rejection of matched non b-jets")
    g.GetXaxis().SetNdivisions(504)
    g.GetXaxis().SetTitleSize(0.045)
    g.GetYaxis().SetTitleSize(0.045)
    g.GetXaxis().SetLabelSize(0.038)
    g.GetYaxis().SetLabelSize(0.038)
    g.SetLineWidth(2)
    return g

####################################################################################################
def mkSBSigTrees(): 
# initialise
    global paves
    mp = parser()
    opts,fout = main.main(mp,True)
    fname = fout.GetName()
    fout.Close()
    os.remove(fname)
    prefix = basepath+'/../mvd'
    basetree = "flatTree_VBFPowheg125.root"

    makeDirs('/'.join([prefix,"rootfiles"]))
    makeDirs('/'.join([prefix,"plots"]))
        
######################################################################################################################################################
######################################################################################################################################################
# step 01: NOM/PRK selection
    if opts.step==1:
        fin = TFile.Open('/'.join([opts.globalpath,basetree]),"read")
        tin = fin.Get("Hbb/events")

        l1("Step 01: %s selection"%opts.sel)

        fout = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep01_%s.root"%opts.sel)]),"recreate")
        makeDirsRoot(fout,"Hbb")
        gDirectory.cd("Hbb")

        #cut,label = write_cuts(opts.selection[0],opts.trigger[0],reftrig=[],jsoncuts=opts.jsoncuts,jsonsamp=opts.jsonsamp,sample="VBF125",weight=opts.weight,trigequal=trigTruth(True))
        cut,label = write_cuts([],opts.trigger[0],reftrig=[],jsoncuts=opts.jsoncuts,jsonsamp=opts.jsonsamp,sample="VBF125",weight=opts.weight,trigequal=trigTruth(True))
        l2("Cut %s: %s"%(opts.sel,cut))

        tout = tin.CopyTree(cut)
        fout.Write()

        fin.Close()
        fout.Close()
        
######################################################################################################################################################
######################################################################################################################################################
    if opts.step==2:
        fin = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep01_%s.root"%opts.sel)]),"read")
        tin = fin.Get("Hbb/events")

        l1("Step 02: %s: eta/btag variable only slimming"%(opts.sel))

        tin.SetBranchStatus('*',0)
        for b in ['jetBtag','btagIdx','jetEta','etaIdx','partonId','partonMatchIdx','partonMatchDR','jetPt','jetPhi','jetMass','blikNOMIdx','blikVBFIdx','mqq','mbb','dEtaqq']:
            tin.SetBranchStatus(b,1)

        fout = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep02_%s.root"%(opts.sel))]),"recreate")
        makeDirsRoot(fout,"Hbb")
        gDirectory.cd("Hbb")

        tout = tin.CloneTree()
        fout.Write(fout.GetName(),TH1.kOverwrite)

        fin.Close()
        fout.Close()

######################################################################################################################################################
######################################################################################################################################################
    if opts.step==3:
        fin = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep02_%s.root"%(opts.sel))]),"read")
        tin = fin.Get("Hbb/events")
        nin = tin.GetEntriesFast()

        l1("Step 03%s: %s: jets tree transformation"%(" (Alt)" if opts.alt else "",opts.sel))

        fout = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep03%s_%s.root"%("Alt" if opts.alt else "",opts.sel))]),"recreate")
        makeDirsRoot(fout,"Hbb")
        gDirectory.cd("Hbb")

        v_eta,v_btag,v_pt,v_phi,v_mass = zeros(1,dtype='float32'),zeros(1,dtype='float32'),zeros(1,dtype='float32'),zeros(1,dtype='float32'),zeros(1,dtype='float32')
        v_etaIdx,v_btagIdx,v_pid,v_ptIdx = zeros(1,dtype='int32'),zeros(1,dtype='int32'),zeros(1,dtype='int32'),zeros(1,dtype='int32')
# new branches
        tout = TTree("jets","jets")
        tout.Branch("eta",v_eta,"eta/F")
        tout.Branch("etaIdx",v_etaIdx,"etaIdx/I")
        tout.Branch("btag",v_btag,"btag/F")
        tout.Branch("btagIdx",v_btagIdx,"btagIdx/I")
        tout.Branch("pid",v_pid,"pid/I")
        tout.Branch("ptIdx",v_ptIdx,"ptIdx/I")
        tout.Branch("pt",v_pt,"pt/F")
        tout.Branch("phi",v_phi,"phi/F")
        tout.Branch("mass",v_mass,"mass/F")
# loop over tree
        tref = now()
        for iEv,Ev in enumerate(tin):
            if iEv%20000==0: 
                [m,s],p = testimate(tref,iEv,nin)
                print "%6d/%-10d (est. %dm %ds, %.1f%%)"%(iEv,nin,m,s,p)
            if opts.nentries>0 and iEv>opts.nentries: break
# loop over partons  
            for pj in range(len(Ev.partonMatchDR)):
                if Ev.partonMatchDR[pj] > 0.25: continue
#                if Ev.partonMatchIdx[pj] > len(Ev.jetPt): continue
                ptIdx = Ev.partonMatchIdx[pj]
                v_ptIdx[0] = Ev.partonMatchIdx[pj]
                v_pid[0]   = Ev.partonId[pj]
                v_btag[0]  = Ev.jetBtag[ptIdx]
                v_pt[0]    = Ev.jetPt[ptIdx]
                v_eta[0]   = Ev.jetEta[ptIdx]
                v_phi[0]   = Ev.jetPhi[ptIdx]
                v_mass[0]  = Ev.jetMass[ptIdx]
                if opts.alt:
                    if (ptIdx in list(Ev.btagIdx)) and (ptIdx in list(Ev.etaIdx)):
                        v_btagIdx[0] = list(Ev.btagIdx).index(ptIdx)
                        v_etaIdx[0]  = list(Ev.etaIdx).index(ptIdx) 
                    else: continue
                else:
                    if ptIdx < len(list(Ev.btagIdx)):
                        v_btagIdx[0] = Ev.btagIdx[ptIdx]
                        v_etaIdx[0]  = Ev.etaIdx[ptIdx]
                tout.Fill()
# save
        fout.Write(fout.GetName(),TH1.kOverwrite)

######################################################################################################################################################
######################################################################################################################################################
    if opts.step==4:
        l1("Step 04%s: %s: blik training"%(" (Alt)" if opts.alt else "",opts.sel))

        fin = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep03%s_%s.root"%("Alt" if opts.alt else "",opts.sel))]),"read")
        tin = fin.Get("Hbb/jets")
        
        fout = TFile.Open("rootfiles/bjetId_%s_MVA%s.root"%(opts.sel,"Alt" if opts.alt else ""),"recreate")
        
        sigCut = TCut("abs(pid) == 5")
        bkgCut = TCut("abs(pid) != 5")
        presel = TCut("btagIdx<4 && etaIdx<4 && etaIdx>-1 && ptIdx<4 && btagIdx>-1 && ptIdx>-1")
        
        Nin = tin.GetEntries()
        N = 100000
        l1("Input tree: %d events"%Nin)
        l1("Using %d events"%N)
          
        factory = TMVA.Factory("factory_%s%s_"%(opts.sel,"_Alt" if opts.alt else ""),fout,"!V:!Silent:Color:DrawProgressBar:Transformations=I;G:AnalysisType=Classification")
        factory.SetInputTrees(tin,sigCut,bkgCut)
        
        factory.AddVariable("btag"   ,'F');
        factory.AddVariable("eta"    ,'F');
        factory.AddVariable("btagIdx",'I');
        factory.AddVariable("etaIdx" ,'I');
        
        factory.PrepareTrainingAndTestTree(presel,"nTrain_Signal=%d:nTrain_Background=%d:nTest_Signal=%d:nTest_Background=%d"%(N,N,N,N))
        
        factory.BookMethod(TMVA.Types.kLikelihood,"Likelihood");
        factory.BookMethod(TMVA.Types.kBDT,"BDT_GRAD2","NTrees=600:nCuts=25:BoostType=Grad:Shrinkage=0.2");
        factory.TrainAllMethods();
        factory.TestAllMethods();
        factory.EvaluateAllMethods(); 

        fin.Close()
        fout.Close()

######################################################################################################################################################
######################################################################################################################################################
    if opts.step==5:
        l1("Step 05%s: %s: Sig/Bkg plots"%(" (Alt)" if opts.alt else "",opts.sel))

        fin = TFile.Open(prefix+"/rootfiles/flatTree_VBFPowheg125_EvIntStep03%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"read")
        tin = fin.Get("Hbb/jets")
        fout = TFile.Open(prefix+"/rootfiles/flatTree_VBFPowheg125_EvIntStep05%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"recreate")

        gStyle.SetOptStat(0)
        gStyle.SetOptTitle(0)
        gStyle.SetLineScalePS(2)
        gROOT.ProcessLineSync(".x %s/styleCMSTDR.C"%basepath)
        gStyle.SetPadRightMargin(0.02)
        gStyle.SetPadLeftMargin(0.16)
        gStyle.SetPadTopMargin(0.02)
        gStyle.SetPadBottomMargin(0.12)
        gROOT.SetBatch(1)
        gStyle.SetTitleSize(0.05,"XY")
        gStyle.SetLabelSize(0.04,"XY")
        gStyle.SetTitleOffset(1.35,"Y")
        gStyle.SetGridColor(17) 

        #
        fc = {"sig":kBlue-9,"bkg":kRed}
        fs = {"sig":1001,"bkg":3004}
        lc = {"sig":kBlue-7,"bkg":kRed}
        Ax  = ["#eta","#eta rank","CSV b-tag","CSV b-tag rank","(old) b-likelihood","(old) b-likelihood rank","b-likelihood","b-likelihood rank"]
        Ay  = ["N / (0.2)","N / (1)","N / (0.1)","N / (1)","N / (0.04)","N / (1)","N / (0.04)","N / (1)"]
        AN  = [50,4,110,4,50,4,50,4]
        Ami = [-5,-0.5,-10,-0.5,-1,-0.5,-1,-0.5]
        Ama = [5,3.5,1,3.5,1,3.5,1,3.5]
        Av  = ["jetEta","etaIdx","jetBtag","btagIdx","blikNOM","blikNOMIdx","myblikNOM","myblikNOMIdx"]
        hs = {}
        btagbinsinput = [-10,-9,-1,0]
        for i in range(1,int(1./0.05)+1): btagbinsinput += [round(float(i)*0.05,2)]
        btagbins = array('f',btagbinsinput)
        for a1 in ["sig","bkg"]:
            for i2,a2 in enumerate(["eta","etaIdx","btag","btagIdx"]):
                x,y,N,mi,ma = Ax[i2],Ay[i2],AN[i2],Ami[i2],Ama[i2]
                if not a2=="btag": hs["%s_%s"%(a1,a2)] = eval('TH1F("h%s_%s","h%s_%s;%s;%s",%d,%f,%f)'%(a1,a2,a1,a2,x,y,N,mi,ma))
                else: hs["%s_%s"%(a1,a2)] = TH1F("h%s_%s"%(a1,a2),"h%s_%s;%s;%s"%(a1,a2,x,y),len(btagbins)-1,btagbins)
                hs["%s_%s"%(a1,a2)].SetFillColor(fc[a1])
                hs["%s_%s"%(a1,a2)].SetFillStyle(fs[a1])
                hs["%s_%s"%(a1,a2)].SetLineColor(lc[a1])
        #
        hs["sig_etaIdx"].GetXaxis().SetNdivisions(4)
        hs["sig_btagIdx"].GetXaxis().SetNdivisions(4)
        TGaxis.SetMaxDigits(4)

        legs = [TLegend(1.-gStyle.GetPadRightMargin()-0.03-0.30,1.-gStyle.GetPadTopMargin()-0.03,1.-gStyle.GetPadRightMargin()-0.03,1.-gStyle.GetPadTopMargin()-0.03-0.055*3,"%s selection"%("Set A" if opts.sel=="NOM" else "Set B"))]
        legs[0].SetTextFont(42)
        legs[0].SetTextSize(0.05)
        legs[0].SetFillStyle(-1)
        legs[0].SetBorderSize(0)
        for i in range(4): legs += [deepcopy(legs[0])]
        #
        for var in ["eta","etaIdx","btag","btagIdx"]:
            for typ in ["sig","bkg"]:
                tin.Draw("%s>>h%s_%s"%(var,typ,var),"abs(pid)==5" if typ=="sig" else "abs(pid)!=5")
        #
        for h in hs.itervalues():
            h.Scale(1./h.Integral())
            h.GetYaxis().SetRangeUser(0.0 if not "Idx" in h.GetName() else 0.1,h.GetBinContent(h.GetMaximumBin())*1.40)

        hs["sig_btag"] = btagTrafo(hs["sig_btag"],"sig",fc["sig"],fs["sig"],lc["sig"])
        hs["bkg_btag"] = btagTrafo(hs["bkg_btag"],"bkg",fc["bkg"],fs["bkg"],lc["bkg"])

        c = TCanvas("c","c",1800,1300)
        c.Divide(2,2)
        for a1 in ["sig","bkg"]:
            for i2,a2 in enumerate(["btag","btagIdx","eta","etaIdx"]):
                c.cd(i2+1)
                h = hs["%s_%s"%(a1,a2)]
                h.Draw("" if a1=="sig" else "same")
                gPad.SetGrid(1,1)
                legs[i2].AddEntry(h,"signal" if a1=="sig" else "background","F")
                if a1=="bkg": legs[i2].Draw()
                if a2=="btag":
                    gPad.SetLogy(1)
                    epave("-1",-0.08,0.000306)
                    epave("-10",-0.135,0.000306)
        #
        makeDirs(prefix+"/plots")
        c.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesIn%s_%s.pdf"%("Alt" if opts.alt else "",opts.sel))

        fout.Write(fout.GetName(),TH1.kOverwrite)
        fin.Close()
        fout.Close()

######################################################################################################################################################
######################################################################################################################################################
    if opts.step==6:
        l1("Step 06%s: %s: weights filling & output plots."%(" (Alt)" if opts.alt else "",opts.sel))
        gROOT.SetBatch(1)
        gStyle.SetOptStat(0)
        gStyle.SetOptTitle(0)
        gStyle.SetLineScalePS(2)
        gROOT.ProcessLineSync(".x %s/styleCMSTDR.C"%basepath)
        gStyle.SetPadRightMargin(0.02)
        gStyle.SetPadLeftMargin(0.16)
        gStyle.SetPadTopMargin(0.05)
        gStyle.SetPadBottomMargin(0.12)
        gROOT.SetBatch(1)
        gStyle.SetTitleOffset(1.35,"Y")
        gStyle.SetPalette(1)
        gStyle.SetGridColor(17)
        TGaxis.SetMaxDigits(4)
        gStyle.SetTitleSize(0.05,"XYZ")
        gStyle.SetLabelSize(0.04,"XYZ")
        gStyle.SetTitleOffset(1.35,"Y")
        gStyle.SetGridColor(17) 
            
        #
        fc = {"sig":kBlue-9,"bkg":kRed}
        fs = {"sig":1001,"bkg":3004}
        lc = {"sig":kBlue-7,"bkg":kRed}
        Ax  = ["#eta","#eta rank","CSV b-tag","CSV b-tag rank","(old) b-likelihood","(old) b-likelihood rank","b-likelihood","b-likelihood rank","|#eta|","bbtag","bblik"]
        Ay  = ["N / (0.2)","N / (1)","N / (0.1)","N / (1)","N / (0.08)","N / (1)","N / (0.08)","N / (1)","N / (0.1)","N / (0.02)","N / (0.01)"]
        AN  = [50,4,110,4,25,4,25,4,100,550,200]
        Ami = [-5,-0.5,-10,-0.5,-1,-0.5,-1,-0.5,0,-10,-1]
        Ama = [5,3.5,1,3.5,1,3.5,1,3.5,5,1,1,1]
        Av  = ["jetEta","etaIdx","jetBtag","btagIdx","blik%s"%("NOM" if opts.sel=="NOM" else "VBF"),"blik%sIdx"%("NOM" if opts.sel=="NOM" else "VBF"),"blik","blikIdx","abseta","jetBtag","blik"]
        hs = {}
        btagbinsinput = [-10,-9,-1,0]
        for i in range(1,int(1./0.05)+1): btagbinsinput += [round(float(i)*0.05,2)]
        btagbins = array('f',btagbinsinput)
        for a1 in ["sig","bkg"]:
            for i2,a2 in enumerate(["eta","etaIdx","btag","btagIdx","blik","blikIdx","blik2","blik2Idx","abseta","bbtag","bblik"]):
                x,y,N,mi,ma = Ax[i2],Ay[i2],AN[i2],Ami[i2],Ama[i2]
                if not a2=="btag": hs["%s_%s"%(a1,a2)] = eval('TH1F("h%s_%s","h%s_%s;%s;%s",%d,%f,%f)'%(a1,a2,a1,a2,x,y,N,mi,ma))
                else: hs["%s_%s"%(a1,a2)] = TH1F("h%s_%s"%(a1,a2),"h%s_%s;%s;%s"%(a1,a2,x,y),len(btagbins)-1,btagbins)
                hs["%s_%s"%(a1,a2)].SetFillColor(fc[a1])
                hs["%s_%s"%(a1,a2)].SetFillStyle(fs[a1])
                hs["%s_%s"%(a1,a2)].SetLineColor(lc[a1])
        #
        if not opts.replot:
            fglobal = TFile.Open('/'.join([prefix,"rootfiles",basetree.replace(".root","_EvIntStep02_%s.root"%opts.sel)]),"read")
            tglobal = fglobal.Get("Hbb/events")
            eta,etaIdx,btag,btagIdx = zeros(1,'float32'),zeros(1,'float32'),zeros(1,'float32'),zeros(1,'float32')
            pid = ROOT.vector('int')()
            reader  = TMVA.Reader()
            if opts.alttag=="" or not ("Kostas" in opts.alttag or "CERN" in opts.alttag):
                reader.AddVariable("btag",btag)
                reader.AddVariable("eta",eta)
                reader.AddVariable("btagIdx",btagIdx)
                reader.AddVariable("etaIdx",etaIdx)
                reader.BookMVA(opts.tmva,"weights/factory_%s%s__BDT_GRAD2.weights.xml"%(opts.sel,"_Alt" if opts.alt else ""))
            elif "Kostas" in opts.alttag:
                reader.AddVariable("btagIdx",btagIdx)
                reader.AddVariable("etaIdx",etaIdx)
                reader.AddVariable("btag",btag)
                reader.AddVariable("eta",eta)
                reader.BookMVA(opts.tmva,"kostas/weights/factory_%s__BDT_GRAD2.weights.xml"%opts.sel)
            elif "CERN" in opts.alttag:
                reader.AddVariable("btagIdx",btagIdx)
                reader.AddVariable("etaIdx",etaIdx)
                reader.AddVariable("btag",btag)
                reader.AddVariable("eta",eta)
                reader.BookMVA(opts.tmva,"tmpcern/factory_BCanditate_%s_BDT_GRAD.weights.xml"%opts.sel)
#                reader.BookMVA(opts.tmva,"weights/kostas.NOM.xml")
            #
            blik       = ROOT.vector('float')()
            blikIdx    = ROOT.vector('int')()
            blikmqq    = zeros(1,'float32')
            blikmbb    = zeros(1,'float32')
            blikdetaqq = zeros(1,'float32')
            #
            fmvd = TFile.Open(prefix+"/rootfiles/flatTree_VBFPowheg125_EvIntStep04%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"recreate")
            makeDirsRoot(fmvd,"Hbb")
            gDirectory.cd("Hbb") 
            tmvd = tglobal.CloneTree(0)
            #
            tmvd.Branch("blik",blik)
            tmvd.Branch("blikIdx",blikIdx)
            tmvd.Branch("blikmqq",blikmqq,"blikmqq/F")
            tmvd.Branch("blikmbb",blikmbb,"blikmbb/F")
            tmvd.Branch("blikdetaqq",blikdetaqq,"blikdetaqq/F")
            tmvd.Branch("pid",pid)
            #
            nentries = tglobal.GetEntriesFast()
            tref = now()
            for iEv,Ev in enumerate(tglobal):
                blik.resize(4,0)
                blikIdx.resize(4,0)
                pid.resize(4,0)
                #
                if opts.nentries>0: 
                    if iEv>opts.nentries: break
                if iEv%5000==0: 
                    [m,s],p = testimate(tref,iEv,nentries)
                    print "%8d/%-10d (est. %dm %ds, %.1f%%)"%(iEv,nentries,m,s,p)
                #
                for ijet in range(4):
                    eta[0] = Ev.jetEta[ijet]
                    btag[0] = Ev.jetBtag[ijet]
                    if opts.alt:
                        etaIdx[0] = list(Ev.etaIdx).index(ijet)
                        btagIdx[0] = list(Ev.btagIdx).index(ijet)
                    else:
                        etaIdx[0] = Ev.etaIdx[ijet] 
                        btagIdx[0] = Ev.btagIdx[ijet] 
                    blik[ijet] = float(reader.EvaluateMVA(opts.tmva))
                #
                blikIdxPair = sorted([[ijet,blik[ijet]] for ijet in range(4)],key=lambda (x,y):y,reverse=True)
                #
                for ijet in range(4): blikIdx[ijet] = blikIdxPair[ijet][0]
                #
                for pj in range(len(Ev.partonMatchDR)):
                    if Ev.partonMatchDR[pj] > 0.25: continue
                    ptIdx = Ev.partonMatchIdx[pj]
                    if ptIdx >= len(Ev.btagIdx): continue
                    pid[ptIdx] = Ev.partonId[pj]
#                for ijet in range(4): 
#                    pidVals = sorted([(x,Ev.partonMatchDR[x]) for x in range(len(Ev.partonMatchIdx)) if (Ev.partonMatchIdx[x]==ijet and Ev.partonMatchDR[x]<0.25)],key=lambda (x,y):(y))
#                    if len(pidVals)<1: pid[ijet] =-999 
#                    else: pid[ijet] = Ev.partonId[pidVals[0][0]]
#                    if pid[ijet]!=-999: 
                    for i2,a2 in enumerate(["eta","etaIdx","btag","btagIdx","blik","blikIdx","blik2","blik2Idx","abseta","bbtag","bblik"]):
                        if a2=="blik": continue
                        h = hs["%s_%s"%("sig" if abs(pid[ptIdx])==5 else "bkg",a2)]
                        if not Av[i2] in ["blik","blikIdx","abseta"]:
                            v = eval("Ev.%s[%d]"%(Av[i2],ptIdx)) if not "Idx" in a2 else eval("list(Ev.%s).index(%d)"%(Av[i2],ptIdx))
                        elif Av[i2] == "blik": v = blik[ptIdx]
                        elif Av[i2] == "blikIdx": v = list(blikIdx).index(ptIdx)
                        elif Av[i2] == "abseta": v = abs(Ev.jetEta[ptIdx])
                        elif Av[i2] == "bbtag": v = Ev.jetBtag[ptIdx]
                        elif Av[i2] == "bblik": v = blik[ptIdx]
                        h.Fill(v)
                #
#                v = [TLorentzVector(),TLorentzVector(),TLorentzVector(),TLorentzVector()]
#                for j in range(4): 
#                    k = blikIdx[j]
#                    v[j].SetPtEtaPhiM(Ev.jetPt[k],Ev.jetEta[k],Ev.jetPhi[k],Ev.jetMass[k])
                v = []
                for jid in range(4):
                    v += [TLorentzVector()]
                    v[-1].SetPtEtaPhiM(Ev.jetPt[jid],Ev.jetEta[jid],Ev.jetPhi[jid],Ev.jetMass[jid])
                blikmqq[0] = (v[blikIdx[2]]+v[blikIdx[3]]).M()
                blikmbb[0] = (v[blikIdx[0]]+v[blikIdx[1]]).M()
                blikdetaqq[0] = abs(Ev.jetEta[int(blikIdx[2])]-Ev.jetEta[int(blikIdx[3])])
                tmvd.Fill()
        else:
            fmvd = TFile.Open(prefix+"/rootfiles/flatTree_VBFPowheg125_EvIntStep04%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"update")
            gDirectory.cd("Hbb")
            tmvd = fmvd.Get("Hbb/events")
            for a1 in ["sig","bkg"]:
                for i2,a2 in enumerate(["eta","etaIdx","btag","btagIdx","blik","blikIdx","blik2","blik2Idx"]):
                    eval('h%s_%s = fmvd.Get("Hbb/h%s_%s")'%(a1,a2,a1,a2))
        #
        c = TCanvas("c","c",1800,1500)
        c.Divide(4,4)
        Bv  = ["blikNOM" if opts.sel=="NOM" else "blikVBF","blikNOMIdx" if opts.sel=="NOM" else "blikVBFIdx","blik","blikIdx","mqq[0]","mqq[%d]"%(1 if opts.sel=="NOM" else 2),"blikmqq","NONE","dEtaqq[0]","dEtaqq[%d]"%(1 if opts.sel=="NOM" else 2),"blikdetaqq","NONE","mbb[0]","mbb[%d]"%(1 if opts.sel=="NOM" else 2),"blikmbb","NONE"]
        Bx  = ["(old) b-likelihood","(old) b-likelihood rank","b-likelihood","b-likelihood rank","(CSV) m_{qq'} (GeV)","(old) m_{qq'} (GeV)","(new) m_{qq'} (GeV)","","(CSV) #Delta#eta_{qq'}","(old) #Delta#eta_{qq'}","(new) #Delta#eta_{qq'}","","(CSV) m_{b#bar{b}} (GeV)","(old) m_{b#bar{b}} (GeV)","(new) m_{b#bar{b}} (GeV)",""]
        By  = ["N / (0.08)","N / (1)","N / (0.08)","N / (1)","N / (20 GeV)","N / (20 GeV)","N / (20 GeV)","","N / (0.1)","N / (0.1)","N / (0.1)","","N / (10 GeV)","N / (10 GeV)","N / (10 GeV)",""]
        BN  = [25,4,25,4,100,100,100,0,50,50,50,0,30,30,30,0]
        Bmi = [-1,-0.5,-1,-0.5,0,0,0,0,0,0,0,0,0,0,0,0]
        Bma = [1,3.5,1,3.5,2000,2000,2000,0,5,5,5,0,300,300,300,0]
        Bt  = ["(existing)","(existing)","(new)","(new)","(existing)","(existing)","(new)","","(existing)","(existing)","(new)","","(existing)","(existing)","(new)",""]
        for iv,v in enumerate(Bv):
            if v == "blikNOM" or v == "blikVBF": continue
            if v == "NONE": continue
            c.cd(iv+1)
            gPad.SetGrid(1,1)
            tmvd.Draw("%s>>h%d(%d,%f,%f)"%(v,iv+1,BN[iv],Bmi[iv],Bma[iv]))
            eval('h%d.GetXaxis().SetTitle("%s")'%(iv+1,Bx[iv]))
            eval('h%d.GetYaxis().SetTitle("%s")'%(iv+1,By[iv]))
            trpave(Bt[iv])
        
        makeDirs(prefix+"/plots")
        c.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesOut%s%s-1_%s.pdf"%("Alt" if opts.alt else "",opts.alttag if not opts.alttag=="" else "",opts.sel))
        c.Close()
        
        ci = TCanvas("ci","ci",900,750)
#        c.Divide(2,1)
        Bv  = ["blikmbb:mbb[0]","mbb[%d]:mbb[0]"%(1 if opts.sel=="NOM" else 2)]
        Bx  = ["CSV b-tag m_{b#bar{b}} (GeV)","CSV b-tag m_{b#bar{b}} (GeV)"]
        By  = ["b-likelihood m_{b#bar{b}} (GeV)","b-likelihood m_{b#bar{b}} (GeV)"]
        BN  = [[140,140],[140,140]]
        Bmi = [[0,0],[0,0]]
        Bma = [[700,700],[700,700]]
        Bt  = ["(new)","(existing)"]
        for iv,v in enumerate(Bv):
            if v == "NONE": continue
#            c.cd(iv+1)
            ci.cd()
            tmvd.Draw("%s>>h%d(%d,%f,%f,%d,%f,%f)"%(v,iv+1+12,BN[iv][0],Bmi[iv][0],Bma[iv][0],BN[iv][1],Bmi[iv][1],Bma[iv][1]),"","colz")
            gPad.SetRightMargin(0.14)
            gPad.SetTopMargin(0.06)
            gPad.SetBottomMargin(0.14)
            eval('ROOT.h%d.GetXaxis().SetTitle("%s")'%(iv+1+12,Bx[iv]))
            eval('ROOT.h%d.GetYaxis().SetTitle("%s")'%(iv+1+12,By[iv]))
            eval('ROOT.h%d.GetXaxis().SetTitleOffset(%.2f)'%(iv+1+12,1.1))
            #trpave(Bt[iv])
            tlpave("Set %s selection"%("A" if opts.sel=="NOM" else "B"),0.85,1)
            eval('ROOT.h%d.GetZaxis().SetRangeUser(1,4000)'%(iv+1+12))
            gPad.SetLogz(1)

            ci.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesOut%s%s-2%s_%s.pdf"%("Alt" if opts.alt else "",opts.alttag if not opts.alttag=="" else "","-new" if iv==0 else "-existing",opts.sel))
        #ci.Close()

        cb = TCanvas("cb","cb",1800,750)
        cb.Divide(2,1)
        c = TCanvas("c","c",2700,1950)
        c.Divide(3,3)
        for a1 in ["sig","bkg"]:
            for i2,a2 in enumerate(["eta","etaIdx","btag","btagIdx","blik","blikIdx","blik2","blik2Idx","abseta","bbtag","bblik"]):
                h = hs["%s_%s"%(a1,a2)]
                if "Idx" in a2: h.GetXaxis().SetNdivisions(4)
                if not h.Integral()==0: h.Scale(1./h.Integral())
                h.GetYaxis().SetRangeUser(0.001 if a2 in ["btag","blik","blik2","bbtag","bblik"] else 0.0,h.GetBinContent(h.GetMaximumBin())*(75 if a2 in ["btag","blik","blik2","bbtag","bblik"] else 1.4))

        legs = [TLegend(1.-gStyle.GetPadRightMargin()-0.03-0.30,1.-gStyle.GetPadTopMargin()-0.03,1.-gStyle.GetPadRightMargin()-0.03,1.-gStyle.GetPadTopMargin()-0.03-0.055*3,"%s selection"%("Set A" if opts.sel=="NOM" else "Set B"))]
        legs[0].SetTextFont(42)
        legs[0].SetTextSize(0.05)
        legs[0].SetFillStyle(-1)
        legs[0].SetBorderSize(0)
        for i in range(8): legs += [deepcopy(legs[0])]

        hsigbtagnew = btagTrafo(hs["sig_btag"],"sig",fc["sig"],fs["sig"],lc["sig"])
        hbkgbtagnew = btagTrafo(hs["bkg_btag"],"bkg",fc["bkg"],fs["bkg"],lc["bkg"])

        for i2,a2 in enumerate(["blik2","blik2Idx","blikIdx","btag","btagIdx","NONE","eta","etaIdx","NONE"]):
            if a2=="blik2": cb.cd(1)
            elif a2=="blik2Idx": cb.cd(2)
            else: c.cd(i2+1)
            for a1 in ["sig","bkg"]:
                gPad.SetRightMargin(0.02)
                gPad.SetBottomMargin(0.12)
                if a2=="NONE": continue
                h = hs["%s_%s"%(a1,a2)]
                if a2=="btag" and a1=="sig": h = hsigbtagnew
                elif a2=="btag" and a1=="bkg": h = hbkgbtagnew
                gPad.SetGrid(1,1)
                if a2 in ["btag","blik","blik2"]: gPad.SetLogy(1) 
                else: gPad.SetLogy(0)
                h.Draw("" if a1=="sig" else "same")
                legs[i2].AddEntry(h,"signal" if a1=="sig" else "background","F")
                if a1=="bkg": legs[i2].Draw()
                h.GetXaxis().SetTitleSize(0.05)
                h.GetYaxis().SetTitleSize(0.05)
                h.GetXaxis().SetTitleOffset(1.1)
                h.GetYaxis().SetTitleOffset(1.35)
                h.GetXaxis().SetLabelSize(0.04)
                h.GetYaxis().SetLabelSize(0.04)
                if a2=="btag":
                    epave("-1",-0.08,0.000306)
                    epave("-10",-0.13,0.000306)
                gPad.Update()
                if "blik2" in a2 and a1=="bkg": cb.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesOut%s%s-3a_%s.pdf"%("Alt" if opts.alt else "",opts.alttag if not opts.alttag=="" else "",opts.sel))

        c.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesOut%s%s-3_%s.pdf"%("Alt" if opts.alt else "",opts.alttag if not opts.alttag=="" else "",opts.sel))
        
        c = TCanvas("c","c",900,750) 
        c.cd()
        legs = [TLegend(gStyle.GetPadLeftMargin()+0.05,gStyle.GetPadBottomMargin()+0.05,gStyle.GetPadLeftMargin()+0.3,gStyle.GetPadBottomMargin()+0.05+0.050*4,"%s selection"%("Set A" if opts.sel=="NOM" else "Set B"))]
        legs[0].SetTextFont(42)
        legs[0].SetTextSize(0.045)
        legs[0].SetFillStyle(0)
        legs[0].SetBorderSize(0)
        gs = {}
        for i2,a2 in enumerate(["bblik","bbtag","abseta"]):
            hsig = hs["sig_%s"%a2]
            hbkg = hs["bkg_%s"%a2]
            g = makeGraph(hsig,hbkg,"right" if not a2=="abseta" else "left")
            g.Write()
            gs[a2] = g
            legs[0].AddEntry(g,"b-likelihood" if "blik" in a2 else ("CSV b-tag" if a2=="bbtag" else "|#eta|"),"L")
            g.Draw("A,L" if i2==0 else "same,L")
        legs[0].Draw()
        legs[0].SetY2(legs[0].GetY1()+legs[0].GetNRows()*0.050+0.05)
        gPad.Update()
        c.SaveAs(prefix+"/plots/EvIntDiscriminant_variablesOut%s%s-4_%s.pdf"%("Alt" if opts.alt else "",opts.alttag if not opts.alttag=="" else "",opts.sel))

        if opts.replot:
            for i in range(20):
                h = eval("ROOT.h%d"%(i))
                if h: h.Write(h.GetName(),TH1.kOverwrite)
            for a1 in ["sig","bkg"]:
                for i2,a2 in enumerate(["blik2","blik2Idx","blikIdx","btag","btagIdx","NONE","eta","etaIdx","NONE"]):
                    if a2=="NONE": continue
                    h = hs["%s_%s"%(a1,a2)]
                    if h: h.Write(h.GetName(),TH1.kOverwrite)
            for g in gs.itervalues():
                if g: g.Write(g.GetName(),TH1.kOverwrite)
        else:
            fmvd.Write()
        #
        fmvd.Close()

######################################################################################################################################################
######################################################################################################################################################
    if opts.step==7:
        l1("Step 07%s: %s: more plots."%(" (Alt)" if opts.alt else "",opts.sel))
        gROOT.SetBatch(1)
        gStyle.SetOptStat(0)
        gStyle.SetLineScalePS(2)
        gROOT.ProcessLineSync(".x %s/styleCMSTDR.C"%basepath)
        gStyle.SetPadRightMargin(0.02)
        gStyle.SetPadLeftMargin(0.16)
        gStyle.SetPadTopMargin(0.05)
        gStyle.SetPadBottomMargin(0.12)
        gROOT.SetBatch(1)
        gStyle.SetTitleOffset(1.35,"Y")
        gStyle.SetTitleSize(0.05,"XYZ")
        gStyle.SetLabelSize(0.04,"XYZ")
        gStyle.SetPalette(1)
        gStyle.SetGridColor(17)
        TGaxis.SetMaxDigits(4)
        
        fin = TFile.Open("rootfiles/bjetId_%s_MVA%s.root"%(opts.sel,"Alt" if opts.alt else ""),"read")
        tin = fin.Get("TestTree")
        fout = TFile.Open(prefix+"/rootfiles/flatTree_VBFPowheg125_EvIntStep07%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"recreate")

        NTrue = float(tin.GetEntries("classID==0"))
        NFake = float(tin.GetEntries("classID==1"))

        V = ["btag","btag","abs(eta)","abs(eta)","BDT_GRAD2","BDT_GRAD2"]
        Av = ["btagTrue","btagFake","etaTrue","etaFake","blikTrue","blikFake"]
        Ax = ["CSV b-tag","CSV b-tag","|#eta|","|#eta|","b-likelihood","b-likelihood"]
        Ay = ["N / (0.05)","N / (0.05)","N / (0.2)","N / (0.2)","N / (0.08)","N / (0.08)"]
        Ami = [0,0,0,0,-1,-1]
        Ama = [1,1,5,5,1,1]
        AN = [20,20,25,25,25,25]
        hs = {}
        for a in range(len(Av)):
            hs["%s"%Av[a]] = TH1F("h%s"%Av[a],"h%s;%s;%s"%(Av[a],Ax[a],Ay[a]),AN[a],Ami[a],Ama[a])
            h = hs["%s"%Av[a]]
            if "True" in Av[a]:
                h.SetLineColor(kBlue)
                h.SetFillColor(kBlue-9)
                h.SetFillStyle(1001)
            elif "Fake" in Av[a]:
                h.SetLineColor(kRed)
                h.SetFillColor(kRed)
                h.SetFillStyle(3004)
        for v in range(len(V)):
            tin.Draw("%s>>h%s"%(V[v],Av[v]),"classID==0" if "True" in Av[v] else "classID==1")
            if "True" in Av[v]: hs[Av[v]].Scale(1./NTrue)
            elif "Fake" in Av[v]: hs[Av[v]].Scale(1./NFake)
        
        c = TCanvas("c","c",900,1950)
        c.Divide(1,3)
        legs = [TLegend(1.-gStyle.GetPadRightMargin()-0.03-0.30,1.-gStyle.GetPadTopMargin()-0.03,1.-gStyle.GetPadRightMargin()-0.03,1.-gStyle.GetPadTopMargin()-0.03-0.055*3,"%s selection"%("Set A" if opts.sel=="NOM" else "Set B"))]
        legs[0].SetTextFont(42)
        legs[0].SetTextSize(0.05)
        legs[0].SetFillStyle(-1)
        legs[0].SetBorderSize(0)
        for i in range(20): legs += [deepcopy(legs[0])]
        for a in range(len(Av)):
            c.cd(divmod(a+2,2)[0])
            h = hs["%s"%Av[a]]
            h.Draw("" if "True" in Av[a] else "same")
            legs[divmod(a+2,2)[0]].AddEntry(h,"signal" if "True" in Av[a] else "background","F")
            if "Fake" in Av[a]: legs[divmod(a+2,2)[0]].Draw()
            if "btag" in Av[a] or "blik" in Av[a]: 
                if "True" in Av[a]: h.GetYaxis().SetRangeUser(0.001,h.GetBinContent(h.GetMaximumBin())*75)
                gPad.SetLogy(1)
            else:
                if "True" in Av[a]: h.GetYaxis().SetRangeUser(0.0,h.GetBinContent(h.GetMaximumBin())*1.4)
                gPad.SetLogy(0)
        c.SaveAs("plots/performance%s-1_%s.pdf"%("Alt" if opts.alt else "",opts.sel))
        c.Close()

        xtrue = [0.]*1000
        yfake = [0.]*1000

        c = TCanvas("c","c",900,750) 
        c.cd()
        legs = [TLegend(gStyle.GetPadLeftMargin()+0.05,gStyle.GetPadBottomMargin()+0.05,gStyle.GetPadLeftMargin()+0.3,gStyle.GetPadBottomMargin()+0.05+0.050*4,"%s selection"%("Set A" if opts.sel=="NOM" else "Set B"))]
        legs[0].SetTextFont(42)
        legs[0].SetTextSize(0.045)
        legs[0].SetFillStyle(-1)
        legs[0].SetBorderSize(0)
        for i in range(20): legs += [deepcopy(legs[0])]
        gs = {}
        for a in range(len(Av)):
            if "True" in Av[a]:
                xtrue = [0.]*1000
                yfake = [0.]*1000
                for i in range(hs[Av[a]].GetNbinsX()):
                    xtrue[i] = hs[Av[a]].Integral(i,hs[Av[a]].GetNbinsX())
                    if "eta" in Av[a]: xtrue[i] = 1. - xtrue[i]
            elif "Fake" in Av[a]:
                for i in range(hs[Av[a]].GetNbinsX()):
                    yfake[i] = 1. - hs[Av[a]].Integral(i,hs[Av[a]].GetNbinsX())
                    if "eta" in Av[a]: yfake[i] = -yfake[i] + 1.
                gs[Av[a][0:-4]] = TGraph(hs[Av[a]].GetNbinsX(),array('f',xtrue[0:hs[Av[a]].GetNbinsX()]),array('f',yfake[0:hs[Av[a]].GetNbinsX()]))
                g = gs[Av[a][0:-4]]
                g.SetLineColor(kRed if "btag" in Av[a] else (kGreen+2 if "eta" in Av[a] else kBlue))
        gPad.SetGrid(1,1)
        gs["btag"].GetXaxis().SetLimits(0.7,1.05)
        gs["btag"].GetYaxis().SetRangeUser(0.0,1.1)
        gs["btag"].GetXaxis().SetTitle("Efficiency of matched b-jets")
        gs["btag"].GetYaxis().SetTitle("Rejection of matched non b-jets")
        gs["btag"].GetXaxis().SetNdivisions(504)
        gs["btag"].Draw("AL")
        gs["eta"].Draw("sameL")
        gs["blik"].Draw("sameL")
        legs[-1].AddEntry(gs["btag"],"CSV b-tag","L")
        legs[-1].AddEntry(gs["eta"],"|#eta|","L")
        legs[-1].AddEntry(gs["blik"],"b-likelihood","L")
        legs[-1].Draw()

        c.SaveAs("plots/performance%s-2_%s.pdf"%("Alt" if opts.alt else "",opts.sel))
        c.Close()

        c1s = fin.Get("CorrelationMatrixS")
        c1b = fin.Get("CorrelationMatrixB")

        gStyle.SetGridColor(kBlack)
        c = TCanvas("c","c",900*2,850*1)
        c.Divide(2,1)
        c.cd(1)
        gPad.SetGrid(1,1)
        gPad.SetTopMargin(0.14)
        gPad.SetRightMargin(0.13)
        c1s.SetMarkerColor(kBlack)
        c1s.Draw("colz,text")
        epavetext(["Correlation matrix (signal)","%s selection"%("Set A" if opts.sel=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
        epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
        gPad.Update()
        gPad.RedrawAxis()
        c.cd(2)
        gPad.SetGrid(1,1)
        gPad.SetTopMargin(0.14)
        gPad.SetRightMargin(0.13)
        c1b.SetMarkerColor(kBlack)
        c1b.Draw("colz,text")
        epavetext(["Correlation matrix (background)","%s selection"%("Set A" if opts.sel=="NOM" else "Set B")],0.03,0.88,0.5,0.97)
        epavetext(["Linear correlation coefficients in %"],0.52,0.85,0.99,0.89,0.025,0)
        gPad.Update()
        gPad.RedrawAxis()

        c.SaveAs("plots/performance%s-3_%s.pdf"%("Alt" if opts.alt else "",opts.sel))
        c.Close()
        gStyle.SetGridColor(17)

        fout.Write(fout.GetName(),TH1.kOverwrite)
        fin.Close()
        fout.Close()



####################################################################################################
####################################################################################################
if __name__=='__main__':
    mkSBSigTrees()
