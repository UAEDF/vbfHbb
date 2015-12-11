#!/usr/bin/env python
import ROOT
from ROOT import *

import os,sys,re
from toolkit import *

fin = TFile.Open("flatTree_VBFPowheg125_EvIntStep03%s_%s.root"%("Alt" if opts.alt else "",opts.sel),"read")
tin = fin.Get("jets")

fout = TFile.Open("bjetId_%s_MVA%s.root"%(opts.sel,"Alt" if opts.alt else ""),"recreate")

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

factory.PrepareTrainingAndTestTree(presel,"nTrainSignal=%d:nTrainBackground=%d:nTest_Signal=%d:nTest_Background=%d"%(N,N,N,N))

#factory.BookMethod(TMVA.Types.kLikelihood,"Likelihood");
factory.BookMethod(TMVA.Types.kBDT,"BDT_GRAD2","NTrees=600:nCuts=25:BoostType=Grad:Shrinkage=0.2");
factory.TrainAllMethods();
factory.TestAllMethods();
factory.EvaluateAllMethods(); 
