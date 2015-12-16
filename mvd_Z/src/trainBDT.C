#include "TMVA/Factory.h"
#include "TFile.h"
#include "TTree.h"
#include "TCut.h" 
#include "TMath.h"
#include "TString.h"
using namespace TMVA;
using namespace TMath;
void trainBDT(TString SELECTION)
{
  // the training is done using a dedicated tree format
  TFile *srcbkg = 0;
  if (SELECTION=="Z") { srcbkg = TFile::Open("inputs/flatTree_BJetPlusXB_selZ_train.root"); } 
  TFile *srcsig = TFile::Open("inputs/flatTree_ZJets_selZ_train.root");
  TTree *trbkg  = (TTree*)srcbkg->Get("events"); 
  TTree *trsig  = (TTree*)srcsig->Get("events"); 
  
  TFile *outf    = new TFile(TString::Format("BDT_").Data()+SELECTION+".root","RECREATE");

  int N = trsig->GetEntries();
  cout<<"NUMBER OF TRAINING EVENTS = "<<N<<endl;
  int Nover2 = (int)((float)N/2.);
	  
  TMVA::Factory* factory = new TMVA::Factory(TString::Format("factory_").Data()+SELECTION+"_",outf,"!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Classification" );
  
  factory->SetSignalTree(trsig,1.0);
  factory->SetBackgroundTree(trbkg,1.0);
  
  factory->AddVariable("dEtaqq",'F');
  factory->AddVariable("etabb",'F');
  factory->AddVariable("btag[0]",'F');
  factory->AddVariable("qgl[0]",'F');
  factory->AddVariable("qgl[1]",'F');
  factory->AddVariable("qgl[2]",'F');
  factory->AddVariable("qgl[3]",'F');

  char name[1000];
  sprintf(name,"nTrain_Signal=%d:nTrain_Background=%d:nTest_Signal=%d:nTest_Background=%d",Nover2,450000,Nover2,450000);
  TCut preselectionCut = TCut("1.");
  factory->PrepareTrainingAndTestTree(preselectionCut,name);

  // specify the training methods
//  factory->BookMethod( TMVA::Types::kFisher, "Fisher", "H:!V:Fisher:VarTransform=None");
  factory->BookMethod( TMVA::Types::kFisher, "Fisher", "H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" );
//  factory->BookMethod( TMVA::Types::kFisher, "Fisher", "H:!V:Fisher:VarTransform=Gauss");
//  factory->BookMethod( TMVA::Types::kLD, "LD", "H:!V:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" );
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods(); 
}
