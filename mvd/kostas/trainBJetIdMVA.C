#include "TMVA/Factory.h"
#include "TFile.h"
#include "TTree.h"
#include "TCut.h" 
#include "TMath.h"
using namespace TMVA;
using namespace TMath;
void trainBJetIdMVA(TString SELECTION)
{
  // the training is done using a dedicated tree format
  TFile *src = TFile::Open("bjetId_"+SELECTION+".root");
  TTree *tr  = (TTree*)src->Get("jets"); 
  
  TFile *outf    = new TFile("bjetId_"+SELECTION+"_MVA.root","RECREATE");

  TCut signalCut       = "abs(partonId) == 5";
  TCut bkgCut          = "abs(partonId) != 5";
  TCut preselectionCut = "btagIdx<4 && etaIdx<4 && etaIdx>-1 && ptIdx<4";
  
  int N = 100000;
  cout<<"NUMBER OF TRAINING EVENTS = "<<N<<endl;
  
  TMVA::Factory* factory = new TMVA::Factory("factory_"+SELECTION+"_",outf,"!V:!Silent:Color:DrawProgressBar:Transformations=I;G:AnalysisType=Classification" );
  
  factory->SetInputTrees(tr,signalCut,bkgCut);
  
  factory->AddVariable("btagIdx",'I');
  factory->AddVariable("etaIdx" ,'I');
  factory->AddVariable("btag"   ,'F');
  factory->AddVariable("eta"    ,'F');

  char name[1000];
  sprintf(name,"nTrain_Signal=%d:nTrain_Background=%d:nTest_Signal=%d:nTest_Background=%d",N,N,N,N);
  factory->PrepareTrainingAndTestTree(preselectionCut,name);

  // specify the training methods
  factory->BookMethod(TMVA::Types::kLikelihood,"Likelihood");
  //factory->BookMethod(TMVA::Types::kBDT,"BDT_DEF");
  //factory->BookMethod(TMVA::Types::kBDT,"BDT_ADA","NTrees=600:AdaBoostBeta=0.1:nCuts=35"); 
  //factory->BookMethod(TMVA::Types::kBDT,"BDT_GRAD1","NTrees=600:nCuts=40:BoostType=Grad:Shrinkage=0.5");  
  factory->BookMethod(TMVA::Types::kBDT,"BDT_GRAD2","NTrees=600:nCuts=25:BoostType=Grad:Shrinkage=0.2");
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods(); 
}
