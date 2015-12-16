#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <TBranch.h>
//#include <stdio>
void CreateTrainFile(TString FILENAME, TString SELECTION)
{
  //TFile *inf = TFile::Open("inputs/flatTree_"+FILENAME+"_selNOM.root");
  TFile *inf = TFile::Open("/usb/data2/UAData/2015/flatTree_"+FILENAME+".root");
  TTree *trIN = (TTree*)inf->Get("Hbb/events");

  TFile *outf = TFile::Open("inputs/flatTree_"+FILENAME+"_sel"+SELECTION+"_train.root","RECREATE");
  TTree *trOUT = new TTree("events","events");

  bool selNOM;
  int b1[4],b2[4],q1[4],q2[4];
  vector<float> *btag(0),*blik(0),*qgl(0),*eta(0),*pt(0),*mass(0),*phi(0);
  float cosTheta[4],mqq[4],dEtaqq[4],dPhiqq[4],mbbReg[4],softHt,ht,x1,x2,mjjTrig,dEtaTrig,sphericity;
  int nSoftJets,nSoftJets2,nSoftJets5,nJets;
  float btag_[4],blik_[4],qgl_[4],eta_[4],pt_[4];
  float cosTheta_,mqq_,dEtaqq_,dPhiqq_,softHt_,ht_,x1_,x2_,mbbReg_,mjjTrig_,dEtaTrig_,sphericity_,etabb_;
  int nSoftJets_,nSoftJets2_,nSoftJets5_,nJets_;
  TLorentzVector j1,j2;

  trIN->SetBranchAddress("jetBtag"   ,&btag);
  trIN->SetBranchAddress("jetQGL"    ,&qgl);
  trIN->SetBranchAddress("jetEta"    ,&eta);
  trIN->SetBranchAddress("jetPhi"    ,&phi);
  trIN->SetBranchAddress("jetMass"   ,&mass);
  trIN->SetBranchAddress("jetPt"     ,&pt);
  trIN->SetBranchAddress("b1"        ,&b1);
  trIN->SetBranchAddress("b2"        ,&b2);
  trIN->SetBranchAddress("q1"        ,&q1);
  trIN->SetBranchAddress("q2"        ,&q2);
  trIN->SetBranchAddress("nSoftJets2",&nSoftJets2);
  trIN->SetBranchAddress("softHt"    ,&softHt);
  trIN->SetBranchAddress("mbbReg"    ,&mbbReg);
  trIN->SetBranchAddress("mqq"       ,&mqq);
  trIN->SetBranchAddress("dEtaqq"    ,&dEtaqq);
  trIN->SetBranchAddress("dPhiqq"    ,&dPhiqq);
  trIN->SetBranchAddress("cosTheta"  ,&cosTheta);
  trIN->SetBranchAddress("selNOM"    ,&selNOM);
  
  trOUT->Branch("qgl"       ,&qgl_       ,"qgl_[4]/F");
  trOUT->Branch("btag"      ,&btag_      ,"btag_[4]/F");
  trOUT->Branch("dEtaqq"    ,&dEtaqq_    ,"dEtaqq_/F");
  trOUT->Branch("mbbReg"    ,&mbbReg_    ,"mbbReg_/F");
  trOUT->Branch("etabb"     ,&etabb_     ,"etabb_/F");

  cout << trIN->GetEntries() << endl;
  for(int i=0;i<trIN->GetEntries();i++) {
    trIN->GetEvent(i);
    int y1 = b1[0];
    int y2 = b2[0];
    int y3 = q1[0];
    int y4 = q2[0];
    btag_[0]    = (*btag)[y1];
    btag_[1]    = (*btag)[y2];
    btag_[2]    = (*btag)[y3];
    btag_[3]    = (*btag)[y4];
	if (! selNOM) continue;
	if (! (btag_[0]>0.679)) continue;
    y1 = b1[1];
    y2 = b2[1];
    y3 = q1[1];
    y4 = q2[1];
    qgl_[0]     = (*qgl)[y1];
    qgl_[1]     = (*qgl)[y2];
    qgl_[2]     = (*qgl)[y3];
    qgl_[3]     = (*qgl)[y4];
    dEtaqq_     = dEtaqq[1];
    mbbReg_     = mbbReg[1];
    y1 = b1[1];
    y2 = b2[1];
	j1.SetPtEtaPhiM(pt->at(y1),eta->at(y1),phi->at(y1),mass->at(y1));
	j2.SetPtEtaPhiM(pt->at(y2),eta->at(y2),phi->at(y2),mass->at(y2));
	etabb_ = abs((j1+j2).Eta());
    
    trOUT->Fill();
  }
  
  outf->cd();
  trOUT->Write("events");
  outf->Close();
  inf->Close();
}
