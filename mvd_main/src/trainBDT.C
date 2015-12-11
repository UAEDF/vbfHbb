#include "TMVA/Factory.h"
#include "TFile.h"
#include "TTree.h"
#include "TCut.h" 
#include "TMath.h"
#include "TString.h"
using namespace TMVA;
using namespace TMath;
//void trainBDT(TString SELECTION,float m115=0.1,float m125=0.8,float m135=0.1)
void trainBDT(TString SELECTION,int group=5)
{
  // the training is done using a dedicated tree format
  TFile *srcbkg = 0;
  if (SELECTION=="NOM") { srcbkg = TFile::Open("flattrain/flatTree_BJetPlusXB_sel"+SELECTION+"_train.root"); } 
  else if (SELECTION=="VBF") { srcbkg = TFile::Open("flattrain/flatTree_VBF1ParkedB_sel"+SELECTION+"_train.root"); }
  TFile *srcsig1 = TFile::Open("flattrain/flatTree_VBFPowheg115_sel"+SELECTION+"_train.root");
  TFile *srcsig2 = TFile::Open("flattrain/flatTree_VBFPowheg125_sel"+SELECTION+"_train.root");
  TFile *srcsig3 = TFile::Open("flattrain/flatTree_VBFPowheg135_sel"+SELECTION+"_train.root");
  TTree *trbkg  = (TTree*)srcbkg->Get("events"); 
  TTree *trsig1  = (TTree*)srcsig1->Get("events"); 
  TTree *trsig2  = (TTree*)srcsig2->Get("events"); 
  TTree *trsig3  = (TTree*)srcsig3->Get("events"); 
  
  TFile *outf    = new TFile(TString::Format("BDT-groups1-%d_",group).Data()+SELECTION+".root","RECREATE");

  int N = (SELECTION=="NOM") ? 110000 : 32000;
  cout<<"NUMBER OF TRAINING EVENTS = "<<N<<endl;
	  
  TMVA::Factory* factory = new TMVA::Factory(TString::Format("factory-group1-%d_",group).Data()+SELECTION+"_",outf,"!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Classification" );
  
  //factory->SetInputTrees(tr);
  factory->SetSignalTree(trsig1,0.25);
  factory->SetSignalTree(trsig2,0.5);
  factory->SetSignalTree(trsig3,0.25);
  factory->SetBackgroundTree(trbkg,1.0);
  
  if (group > 0) {
	  factory->AddVariable("mqq",'F');
	  factory->AddVariable("dEtaqq",'F');
	  factory->AddVariable("dPhiqq",'F');
  }
  if (group > 1) {
	  factory->AddVariable("btag_[0]",'F');
	  factory->AddVariable("btag_[1]",'F');
  }
  if (group > 2) {
	  factory->AddVariable("qgl_[0]",'F');
	  factory->AddVariable("qgl_[1]",'F');
	  factory->AddVariable("qgl_[2]",'F');
	  factory->AddVariable("qgl_[3]",'F');
  }
  if (group > 3) {
	  factory->AddVariable("softHt",'F');
	  factory->AddVariable("nSoftJets2",'F');
  }
  if (group > 4) {
	  factory->AddVariable("cosTheta",'F');
  }

  char name[1000];
  sprintf(name,"nTrain_Signal=%d:nTrain_Background=%d:nTest_Signal=%d:nTest_Background=%d",N,N,N,N);
  TCut preselectionCut = TCut("1.");
  factory->PrepareTrainingAndTestTree(preselectionCut,name);

  // specify the training methods
  factory->BookMethod(TMVA::Types::kBDT,"BDT_GRAD2","NTrees=600:BoostType=Grad:Shrinkage=0.2");
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods(); 
}
