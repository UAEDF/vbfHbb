#include "TMVA/Factory.h"
#include "TFile.h"
#include "TTree.h"
#include "TCut.h" 
#include "TMath.h"
#include "TString.h"
using namespace TMVA;
using namespace TMath;

void useBDT(TString SELECTION)
{
  // the training is done using a dedicated tree format
  TFile *srcbkg = 0;
  if (SELECTION=="NOM") { srcbkg = TFile::Open("flattrain/flatTree_BJetPlusXB_sel"+SELECTION+".root"); } 
  else if (SELECTION=="VBF") { srcbkg = TFile::Open("flattrain/flatTree_VBF1ParkedB_sel"+SELECTION+".root"); }
  TFile *srcsig = TFile::Open("flattrain/flatTree_VBFPowheg125_sel"+SELECTION+".root");
  TTree *trbkg  = (TTree*)srcbkg->Get("Hbb/events"); 
  TTree *trsig  = (TTree*)srcsig->Get("Hbb/events"); 

  TFile *outbkg = 0;
  if (SELECTION=="NOM") { outbkg = TFile::Open("flattrain/flatTree_BJetPlusXB_sel"+SELECTION+"_out.root","recreate"); } 
  else if (SELECTION=="VBF") { outbkg = TFile::Open("flattrain/flatTree_VBF1ParkedB_sel"+SELECTION+"_out.root","recreate"); }
  TFile *outsig = TFile::Open("flattrain/flatTree_VBFPowheg125_sel"+SELECTION+"_out.root","recreate");

  outbkg->cd();
  gDirectory->mkdir("Hbb");
  gDirectory->cd("Hbb");
  TTree *toutbkg = (TTree*)trbkg->CopyTree("1.");
  
  outsig->cd();
  gDirectory->mkdir("Hbb");
  gDirectory->cd("Hbb");
  TTree *tsigbkg = (TTree*)trsig->CopyTree("1.");
  
  int b1[4],b2[4],q1[4],q2[4];
  vector<float> *btag(0),*blik(0),*qgl(0),*eta(0),*pt(0);
  float cosTheta[4],mqq[4],dEtaqq[4],dPhiqq[4],mbbReg[4],softHt,ht,x1,x2,mjjTrig,dEtaTrig,sphericity,mvaNOM,mvaVBF;
  int nSoftJets,nSoftJets2,nSoftJets5,nJets;
  float btag_[4],blik_[4],qgl_[4],eta_[4],pt_[4];
  float cosTheta_,mqq_,dEtaqq_,dPhiqq_,softHt_,ht_,x1_,x2_,mbbReg_,mjjTrig_,dEtaTrig_,sphericity_;
  int nSoftJets_,nSoftJets2_,nSoftJets5_,nJets_;
  float vars[12];
  float BDToutput=0;
  int I=0;

  TMVA::Reader *reader = new TMVA::Reader();
  reader->AddVariable("mqq",&vars[0]);
  reader->AddVariable("dEtaqq",&vars[1]);
  reader->AddVariable("dPhiqq",&vars[2]);
  reader->AddVariable("btag_[0]",&vars[3]);
  reader->AddVariable("btag_[1]",&vars[4]);
  reader->AddVariable("qgl_[0]",&vars[5]);
  reader->AddVariable("qgl_[1]",&vars[6]);
  reader->AddVariable("qgl_[2]",&vars[7]);
  reader->AddVariable("qgl_[3]",&vars[8]);
  reader->AddVariable("softHt",&vars[9]);
  reader->AddVariable("nSoftJets2",&vars[10]);
  reader->AddVariable("cosTheta",&vars[11]);
//  reader->BookMVA("BDT","v2/weights/factory-group1-5_"+SELECTION+"__BDT_GRAD2.weights.xml");
//  reader->BookMVA("BDT","weights/factory-group1-5_"+SELECTION+"__BDT_GRAD2.weights.xml");
  reader->BookMVA("BDT","kostas/factory_mvaNOM_BDT_GRAD.weights.xml");

  TBranch *bbdt = (TBranch*)toutbkg->Branch("BDToutput",&BDToutput,"BDToutput/F");
  
  toutbkg->SetBranchAddress("jetBtag"   ,&btag);
  toutbkg->SetBranchAddress("jetQGL"    ,&qgl);
  toutbkg->SetBranchAddress("jetEta"    ,&eta);
  toutbkg->SetBranchAddress("jetPt"     ,&pt);
  toutbkg->SetBranchAddress("b1"        ,&b1);
  toutbkg->SetBranchAddress("b2"        ,&b2);
  toutbkg->SetBranchAddress("q1"        ,&q1);
  toutbkg->SetBranchAddress("q2"        ,&q2);
  toutbkg->SetBranchAddress("nSoftJets2",&nSoftJets2);
  toutbkg->SetBranchAddress("softHt"    ,&softHt);
  toutbkg->SetBranchAddress("mbbReg"    ,&mbbReg);
  toutbkg->SetBranchAddress("mqq"       ,&mqq);
  toutbkg->SetBranchAddress("dEtaqq"    ,&dEtaqq);
  toutbkg->SetBranchAddress("dPhiqq"    ,&dPhiqq);
  toutbkg->SetBranchAddress("cosTheta"  ,&cosTheta);
  toutbkg->SetBranchAddress("mvaNOM"  ,&mvaNOM);
  toutbkg->SetBranchAddress("mvaVBF"  ,&mvaVBF);
  
  N = toutbkg->GetEntriesFast();
  I = (SELECTION=="NOM") ? 1 : 2;

  for (int iev=0; iev<N; iev++) {
	  if (iev%5000==0) cout << iev << " / " << N << endl;
	  toutbkg->GetEntry(iev);
	  vars[0] = mqq[I];
	  vars[1] = dEtaqq[I];
	  vars[2] = dPhiqq[I];
	  vars[3] = btag->at(b1[0]);
	  vars[4] = btag->at(b2[0]);
	  vars[5] = qgl->at(0);
	  vars[6] = qgl->at(1);
	  vars[7] = qgl->at(2);
	  vars[8] = qgl->at(3);
	  vars[9] = softHt;
	  vars[10] = nSoftJets2;
	  vars[11] = cosTheta[I];
	  BDToutput = float(reader->EvaluateMVA("BDT"));
//	  cout << BDToutput << " " << mvaNOM << endl;
	  bbdt->Fill();
  }
	
  outbkg->Write();
	
  outbkg->Close();
  outsig->Close();
  srcsig->Close();
  srcbkg->Close();
}
