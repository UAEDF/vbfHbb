#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TCut.h"
#include <iostream>
void PrepareDataForFit(TString SAMPLE,TString SELECTION,bool isMC)
{
  cout<<"Preparing sample: "<<SAMPLE<<endl;
  TString PATH("/afs/cern.ch/user/s/salderwe/eosaccess/cms/store/cmst3/group/vbfhbb/flat/flatTree_");
  //TString PATH("root://eoscms//eos/cms/store/cmst3/group/vbfhbb/flat/flatTree_");
  TFile *inf  = TFile::Open(PATH+SAMPLE+".root");
  TTree *tIN  = (TTree*)inf->Get("Hbb/events");
  TH1F *hPass = (TH1F*)inf->Get("Hbb/TriggerPass"); 
  
  tIN->SetBranchStatus("*",0);
  tIN->SetBranchStatus("mvaNOM",1);
  tIN->SetBranchStatus("mvaVBF",1);
  tIN->SetBranchStatus("selNOM",1);
  tIN->SetBranchStatus("selVBF",1);
  tIN->SetBranchStatus("dPhibb",1);
  tIN->SetBranchStatus("mbbReg",1);
  tIN->SetBranchStatus("mbb",1);
  tIN->SetBranchStatus("nLeptons",1);
  if (isMC) {
    tIN->SetBranchStatus("puWt",1);
    tIN->SetBranchStatus("trigWtNOM",1);
    tIN->SetBranchStatus("trigWtVBF",1);
  } 
  tIN->SetBranchStatus("triggerResult",1);
  
  TCut CUT_TRIGGER("");
  TCut CUT_SELECTION("");
  TCut CUT_LEPTONS("nLeptons==0"); 

  if (SELECTION == "NOM") {
    CUT_TRIGGER = "triggerResult[0] || triggerResult[1]";
    CUT_SELECTION = "selNOM";
  }
  if (SELECTION == "VBF") {
    CUT_TRIGGER = "triggerResult[9] && !((triggerResult[0] || triggerResult[1]) && selNOM)";
    CUT_SELECTION = "selVBF";
  }
   
  TFile *outf = TFile::Open("Fit_"+SAMPLE+"_sel"+SELECTION+".root","RECREATE");
  outf->cd();
  hPass->Write("TriggerPass");
  
  TDirectoryFile *dir = (TDirectoryFile*)outf->mkdir("Hbb");
  dir->cd();
  TCut CUT_TOTAL(CUT_TRIGGER+CUT_SELECTION+CUT_LEPTONS);
  cout << CUT_TOTAL.GetTitle() << endl;
  TTree *tOUT = (TTree*)tIN->CopyTree(CUT_TOTAL);
  cout<<"Events: "<<tOUT->GetEntries()<<endl;
  tOUT->Write("events");
  dir->Close();  
    
  outf->Close();
  inf->Close();
}
