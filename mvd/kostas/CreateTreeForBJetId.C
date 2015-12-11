#include <iostream>
#include "TTree.h"
#include "TFile.h"
#include "TMath.h"
using std::cin;
using std::cout;
using std::endl;

void CreateTreeForBJetId(TString SELECTION)
{
//  TFile *inf   = TFile::Open("/usb/data2/UAData/2015/flatTree_VBFPowheg125.root");
  TFile *inf   = TFile::Open("/usb/data2/UAData/fromKostas/autumn2013/flatTree_VBFPowheg125.root");
//TFile *inf   = TFile::Open("root://eoscms//eos/cms/store/cmst3/group/vbfhbb/flat/flatTree_VBFPowheg125.root");
  TTree *trIN  = (TTree*)inf->Get("Hbb/events");
  TFile *outf  = TFile::Open("bjetId_"+SELECTION+".root","RECREATE");
  TTree *trOUT = new TTree("jets","jets");

  vector<int>   *partonId(0),*partonMatchIdx(0),*btagIdx(0),*etaIdx(0);
  vector<float> *partonMatchDR(0),*btag(0),*eta(0);
  vector<bool>  *triggerResult(0);

  int partonId_,btagIdx_,etaIdx_,ptIdx_;
  float btag_,eta_;

  //------- input tree --------------
  trIN->SetBranchAddress("partonId"         ,&partonId);
  trIN->SetBranchAddress("partonMatchIdx"   ,&partonMatchIdx);
  trIN->SetBranchAddress("partonMatchDR"    ,&partonMatchDR);
  trIN->SetBranchAddress("btagIdx"          ,&btagIdx);
  trIN->SetBranchAddress("etaIdx"           ,&etaIdx);
  trIN->SetBranchAddress("jetBtag"          ,&btag);
  trIN->SetBranchAddress("jetEta"           ,&eta);
  trIN->SetBranchAddress("triggerResult"    ,&triggerResult);

  //------- output tree --------------
  trOUT->Branch("partonId",&partonId_,"partonId_/I");
  trOUT->Branch("btagIdx" ,&btagIdx_ ,"btagIdx_/I");
  trOUT->Branch("etaIdx"  ,&etaIdx_  ,"etaIdx_/I"); 
  trOUT->Branch("ptIdx"   ,&ptIdx_   ,"ptIdx_/I");
  trOUT->Branch("btag"    ,&btag_    ,"btag_/F");
  trOUT->Branch("eta"     ,&eta_     ,"eta_/F");

  int decade(0);
  int NN = trIN->GetEntries();
  cout<<"Reading "<<NN<<" entries"<<endl;
  for(int iev=0;iev<NN;iev++) {
    double progress = 10.0*iev/(1.0*NN);
    int k = TMath::FloorNint(progress); 
    if (k > decade) 
      cout<<10*k<<" %"<<endl;
    decade = k; 
    trIN->GetEntry(iev);
    bool PASS_TRIGGER(false);
    if (SELECTION == "NOM") {
      PASS_TRIGGER = ((*triggerResult)[0] || (*triggerResult)[1]);
    }
    if (SELECTION == "VBF") {
      PASS_TRIGGER = (*triggerResult)[9]; 
    }
    if (!PASS_TRIGGER) continue;
    for(unsigned j=0;j<partonId->size();j++) {
      if ((*partonMatchDR)[j] > 0.25) continue;
      int i = (*partonMatchIdx)[j]; 
      //cout<<i<<" "<<(*partonId)[j]<<" "<<(*btagIdx)[i]<<" "<<(*etaIdx)[i]<<" "<<(*btag)[i]<<" "<<(*eta)[i]<<endl;
      partonId_ = (*partonId)[j]; 
      ptIdx_    = i;
	 // btagIdx_ = -1;
	 // etaIdx_ = -1;
	 // for (unsigned l=0;l<btagIdx->size();l++) {
	 //     if ((*btagIdx)[l] == i) btagIdx_ = l; 
	 //     if ((*etaIdx)[l] == i) etaIdx_ = l; 
	 // }
	 // if (btagIdx_==-1 || etaIdx_==-1) continue;
      btagIdx_  = (*btagIdx)[i]; 
      etaIdx_   = (*etaIdx)[i];
      btag_     = (*btag)[i]; 
      eta_      = (*eta)[i];
      trOUT->Fill();
    }
  } 
  outf->cd();
  trOUT->Write();
  outf->Close();
  inf->Close();
}






















