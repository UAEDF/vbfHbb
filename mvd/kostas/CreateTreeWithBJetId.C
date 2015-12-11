#include <iostream>
#include "TTree.h"
#include "TFile.h"
#include "TMath.h"
using std::cin;
using std::cout;
using std::endl;

void order(vector<float> const& v, vector<int>* idx, int Nmax);

void CreateTreeWithBJetId(TString SELECTION)
{
  TFile *inf   = TFile::Open("/usb/data2/UAData/fromKostas/autumn2013/flatTree_VBFPowheg125.root");
//TFile *inf   = TFile::Open("root://eoscms//eos/cms/store/cmst3/group/vbfhbb/flat/flatTree_VBFPowheg125.root");
  TTree *trIN  = (TTree*)inf->Get("Hbb/events");
  TFile *outf  = TFile::Open("flatTree_Blik"+SELECTION+".root","RECREATE");
  TTree *trOUT = 0;
    if (SELECTION == "NOM") {
  		trOUT = (TTree*)trIN->CopyTree("triggerResult[0]==1 || triggerResult[1]==1","");
    }
    if (SELECTION == "VBF") {
  	    trOUT = (TTree*)trIN->CopyTree("triggerResult[9]==1");
    }

  vector<int> *partonId(0),*btagIdx(0),*etaIdx(0),*partonMatchIdx(0),*blikIdx(0),*blikIdxOld(0);
  vector<float> *btag(0),*eta(0),*partonMatchDR(0),*blik(0),*pt_(0),*phi_(0),*mass_(0);
  vector<bool>  *triggerResult(0);
  blik = new vector<float>();
  blikIdx = new vector<int>();
  blik->clear();
  blikIdx->clear();

  float blikmbb,blikmqq,blikdetaqq;
  float btag_,eta_;
  int btagIdx_,etaIdx_;
  int ptIdx_,partonId_;
  float var_[4],blik_[4];
  
  //------- output tree --------------
  trOUT->SetBranchAddress("partonId"         ,&partonId);
  trOUT->SetBranchAddress("partonMatchDR"    ,&partonMatchDR);
  trOUT->SetBranchAddress("partonMatchIdx"   ,&partonMatchIdx);
  trOUT->SetBranchAddress("btagIdx"          ,&btagIdx);
  trOUT->SetBranchAddress("etaIdx"           ,&etaIdx);
  trOUT->SetBranchAddress("jetBtag"          ,&btag);
  trOUT->SetBranchAddress("jetEta"           ,&eta);
  trOUT->SetBranchAddress("jetPt"            ,&pt_);
  trOUT->SetBranchAddress("jetPhi"           ,&phi_);
  trOUT->SetBranchAddress("jetMass"          ,&mass_);
  trOUT->SetBranchAddress("blikNOMIdx"       ,&blikIdxOld);
 
  TBranch *bblik = trOUT->Branch("blik",&blik);
  TBranch *bblikIdx = trOUT->Branch("blikIdx",&blikIdx);
  TBranch *bmbb = trOUT->Branch("blikmbb",&blikmbb,"blikmbb/F");
  TBranch *bmqq = trOUT->Branch("blikmqq",&blikmqq,"blikmqq/F");
  TBranch *bdetaqq = trOUT->Branch("blikdetaqq",&blikdetaqq,"blikdetaqq/F");

  reader_ = new TMVA::Reader("!Color:!Silent");
  reader_->AddVariable("btagIdx",&var_[0]);
  reader_->AddVariable("etaIdx" ,&var_[1]);
  reader_->AddVariable("btag"   ,&var_[2]);
  reader_->AddVariable("eta"    ,&var_[3]);
  reader_->BookMVA("BDT","/data/AA_UA/Workdir/git/vbfHbb/mvd/kostas/weights/factory_NOM__BDT_GRAD2.weights.xml");

  int decade(0);
  int NN = trOUT->GetEntries();
  cout<<"Reading "<<NN<<" entries"<<endl;
  for(int iev=0;iev<NN;iev++) {
	blik->clear();
	blikIdx->clear();
    double progress = 10.0*iev/(1.0*NN);
    int k = TMath::FloorNint(progress); 
    if (k > decade) 
      cout<<10*k<<" %"<<endl;
    decade = k; 
    trOUT->GetEntry(iev);
    for(unsigned j=0;j<partonId->size();j++) {
      if ((*partonMatchDR)[j] > 0.25) continue;
      int i = (*partonMatchIdx)[j]; 
      partonId_ = (*partonId)[j]; 
      ptIdx_    = i;
	  if (i>3) continue;
	  for (unsigned k=0;k<4;k++) {
		  if ((*btagIdx)[k] == i) btagIdx_ = k; 
		  if ((*etaIdx)[k] == i) etaIdx_ = k; 
	  }
      //btagIdx_  = (*btagIdx)[i]; 
      //etaIdx_   = (*etaIdx)[i];
      btag_     = (*btag)[i]; 
      eta_      = (*eta)[i];
	  var_[0] = btagIdx_;
	  var_[1] = etaIdx_;
	  var_[2] = btag_;
	  var_[3] = eta_;
      blik_[ptIdx_] = reader_->EvaluateMVA("BDT");
//	  if (blik_[ptIdx_]>-0.10 && blik_[ptIdx_]<-0.07) {
//		  cout << blik_[ptIdx_] << " ";
//		  for (int ijet=0; ijet<4; ijet++) cout << var_[ijet] << " ";
//		  cout << endl << endl;
//	  }
    }
	for (int ijet=0; ijet<4; ijet++) {
		blik->push_back(float(blik_[ijet]));
		blikIdx->push_back(int(ijet));
	}
	order(*blik,blikIdx,4);
//	for (int ijet=0; ijet<4; ijet++) {
//		cout << (*blikIdx)[ijet] << " " << (*blikIdxOld)[ijet] << endl;
//	}
	//cout << endl;
	vector<TLorentzVector> *v = 0;
	v = new vector<TLorentzVector>;
	v->resize(4);
	for (int ijet=0; ijet<4; ijet++) {
		(*v)[ijet].SetPtEtaPhiM((*pt_)[(*blikIdx)[ijet]],(*eta)[(*blikIdx)[ijet]],(*phi_)[(*blikIdx)[ijet]],(*mass_)[(*blikIdx)[ijet]]);
	}
	blikmbb = ((*v)[0]+(*v)[1]).M();
	blikmqq = ((*v)[2]+(*v)[3]).M();
	blikdetaqq = fabs((*v)[2].Eta() - (*v)[3].Eta());
	bblik->Fill();
	bblikIdx->Fill();
	bmqq->Fill();
	bmbb->Fill();
	bdetaqq->Fill();
  } 
  outf->cd();
  trOUT->Write();
  outf->Close();
  inf->Close();
}

//====================================================================================================
//====================================================================================================
//====================================================================================================
void order(vector<float> const& v, vector<int>* idx, int Nmax)
{
  vector<float> tmp;
  int N = min(int(v.size()),Nmax);
  for(int i=0;i<N;i++) {
    idx->push_back(i);
    tmp.push_back(v[i]); 
  }
  for(int i=0;i<N;i++) {
    for(int j=i+1;j<N;j++) {
      if (tmp[j] > tmp[i]) {
        int k = (*idx)[i];
        (*idx)[i] = (*idx)[j];
        (*idx)[j] = k;
        float x = tmp[i]; 
        tmp[i] = tmp[j];
        tmp[j] = x;
      }
    } 
  }
}






















