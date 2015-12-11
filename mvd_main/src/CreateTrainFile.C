#include <TFile.h>
#include <TTree.h>
#include <TString.h>
#include <TBranch.h>
//#include <stdio>
void CreateTrainFile(TString FILENAME, TString SELECTION)
{
  //TFile *inf = TFile::Open("../datamc/flatslim/DataSeparate/flatTree_"+FILENAME+"_s"+SELECTION+".root");
  TFile *inf = TFile::Open("../datamc/flatslim/flatTree_"+FILENAME+"_s"+SELECTION+".root");
  TTree *trIN = (TTree*)inf->Get("Hbb/events");

  TFile *outf = TFile::Open("flattrain/flatTree_"+FILENAME+"_sel"+SELECTION+"_train.root","RECREATE");
  TTree *trOUT = new TTree("events","events");

  int b1[4],b2[4],q1[4],q2[4];
  vector<float> *btag(0),*blik(0),*qgl(0),*eta(0),*pt(0);
  float cosTheta[4],mqq[4],dEtaqq[4],dPhiqq[4],mbbReg[4],softHt,ht,x1,x2,mjjTrig,dEtaTrig,sphericity;
  int nSoftJets,nSoftJets2,nSoftJets5,nJets;
  float btag_[4],blik_[4],qgl_[4],eta_[4],pt_[4];
  float cosTheta_,mqq_,dEtaqq_,dPhiqq_,softHt_,ht_,x1_,x2_,mbbReg_,mjjTrig_,dEtaTrig_,sphericity_;
  int nSoftJets_,nSoftJets2_,nSoftJets5_,nJets_;

  trOUT->Branch("btag"      ,&btag_      ,"btag_[4]/F");
  trOUT->Branch("blik"      ,&blik_      ,"blik_[4]/F");
  trOUT->Branch("qgl"       ,&qgl_       ,"qgl_[4]/F");
  trOUT->Branch("eta"       ,&eta_       ,"eta_[4]/F");
  trOUT->Branch("pt"        ,&pt_        ,"pt_[4]/F");
  trOUT->Branch("cosTheta"  ,&cosTheta_  ,"cosTheta_/F");
  trOUT->Branch("mqq"       ,&mqq_       ,"mqq_/F");
  trOUT->Branch("dEtaqq"    ,&dEtaqq_    ,"dEtaqq_/F");
  trOUT->Branch("dPhiqq"    ,&dPhiqq_    ,"dPhiqq_/F");
  trOUT->Branch("mbbReg"    ,&mbbReg_    ,"mbbReg_/F");
  trOUT->Branch("softHt"    ,&softHt_    ,"softHt_/F");
  trOUT->Branch("nSoftJets2",&nSoftJets2_,"nSoftJets2_/I");

  trIN->SetBranchAddress("jetBtag"   ,&btag);
  trIN->SetBranchAddress("jetQGL"    ,&qgl);
  trIN->SetBranchAddress("jetEta"    ,&eta);
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
  
  int iSEL(0);
  if (SELECTION == "NOM") {
    iSEL = 1;
    trIN->SetBranchAddress("jetBlikNOM",&blik);
  }  
  if (SELECTION == "VBF") {
    trIN->SetBranchAddress("jetBlikVBF",&blik);
    iSEL = 2;
  }
  
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
    y1 = b1[iSEL];
    y2 = b2[iSEL];
    y3 = q1[iSEL];
    y4 = q2[iSEL];
    blik_[0]    = (*blik)[y1];
    blik_[1]    = (*blik)[y2];
    blik_[2]    = (*blik)[y3];
    blik_[3]    = (*blik)[y4];
    qgl_[0]     = (*qgl)[y1];
    qgl_[1]     = (*qgl)[y2];
    qgl_[2]     = (*qgl)[y3];
    qgl_[3]     = (*qgl)[y4];
    eta_[0]     = (*eta)[y1];
    eta_[1]     = (*eta)[y2];
    eta_[2]     = (*eta)[y3];
    eta_[3]     = (*eta)[y4];
    pt_[0]      = (*pt)[y1];
    pt_[1]      = (*pt)[y2];
    pt_[2]      = (*pt)[y3];
    pt_[3]      = (*pt)[y4];
    dEtaqq_     = dEtaqq[iSEL];
    mqq_        = mqq[iSEL];
    mbbReg_     = mbbReg[iSEL];
    dPhiqq_     = dPhiqq[iSEL];
    cosTheta_   = cosTheta[iSEL];
    nSoftJets2_ = nSoftJets2;
    softHt_     = softHt;
    
    trOUT->Fill();
  }
  
  outf->cd();
  trOUT->Write("events");
  outf->Close();
  inf->Close();
}
