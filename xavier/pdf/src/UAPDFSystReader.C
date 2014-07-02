

#include <iostream>
#include <iomanip>
#include <iterator>
#include <math.h>
using namespace std;

#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

#include "UAPDFSystConfig.h"
#include "UAPDFSystAna.h"
#include "Progressbar.h"

void UAPDFSystReader(UAPDFSystConfig& Cfg){

  bool bTree = Cfg.GetbTree();

  TFile* File ;
  TTree* Tree ;
  TTree* Tout ;
  TFile* FTout ; 
  TFile* FHout ; 

  gROOT->ProcessLine("#include <vector>"); 
  vector<Float_t>* weight_pdf1 = new vector<Float_t>;
  vector<Float_t>* weight_pdf2 = new vector<Float_t>;
  vector<Float_t>* weight_pdf3 = new vector<Float_t>;

  for ( vector<InputData_t>::iterator itD = (Cfg.GetInputData())->begin() ; itD != (Cfg.GetInputData())->end() ; ++itD ) {
    
    // ------------ Output Histograms ----------------

    TH1F* hQ   = new TH1F("hQ"  ,"hQ"  ,600, 0.,600.); 
    TH1F* hx1  = new TH1F("hx1" ,"hx1" , 40, 0.,0.8 ); 
    TH1F* hx2  = new TH1F("hx2" ,"hx2" , 40, 0.,0.8 ); 
    TH2F* hx12 = new TH2F("hx12","hx12", 40, 0.,0.8 , 40, 0.,0.8 );
    TH2F* hid  = new TH2F("hid" ,"hid" ,13 ,-7,7,13,-7,7);

    // ------------ Init PDF Sets --------------------

    unsigned int nPDFsets = 0;
    vector<unsigned int> nweights;
    vector<string> PDFName;

    if (itD->bFixPDF) {
       ++nPDFsets;
       PDFName.push_back(itD->RefPDF);
       LHAPDF::initPDFSet(nPDFsets,itD->RefPDF);  
       nweights.push_back(1);  
       nweights.at(nPDFsets-1) += LHAPDF::numberPDF(nPDFsets);
    }
    
    for ( vector<string>::iterator itPS = (Cfg.GetPDFsets())->begin() ; itPS != (Cfg.GetPDFsets())->end() ; ++itPS) {
      if (itD->bFixPDF) {
        if ( itD->RefPDF == *itPS ) continue;
      }
      if ( nPDFsets >= 3 ) { cout << "[WARNING] More then 3 PDF Sets: " << *itPS << " will be skiped !" << endl ; continue ; } 
      ++nPDFsets;
      PDFName.push_back(*itPS);
      LHAPDF::initPDFSet(nPDFsets,*itPS);
      nweights.push_back(1);   
      nweights.at(nPDFsets-1) += LHAPDF::numberPDF(nPDFsets);
    }

    weight_pdf1->clear();
    weight_pdf2->clear();
    weight_pdf3->clear();
    if ( nweights.size() >= 1 ) weight_pdf1->resize(nweights.at(0),0.);
    if ( nweights.size() >= 2 ) weight_pdf2->resize(nweights.at(1),0.);
    if ( nweights.size() >= 3 ) weight_pdf3->resize(nweights.at(2),0.);

    // ------------ Open Tree ------------------------

    cout << "Opening TTree: " << itD->NickName << " " << itD->FileName << " " << itD->TreeName << endl;
    File = new TFile((Cfg.GetInDir()+"/"+itD->FileName).c_str(),"READ");
    Tree = (TTree*) File->Get((itD->TreeName).c_str());
    Tree->SetBranchStatus("*",1);

    // ------------- Create New Tree -----------------

    if (bTree) {
      // Make file and Tree
      string TOFileName = Cfg.GetOutDir() + "/PDFSyst_Tree_" + itD->FileName ;
      FTout = new TFile( TOFileName.c_str(),"RECREATE" );      
      Tout  = Tree->CloneTree(0);
      Tout->SetName("UAPDFSyst");
      // Add New Branches
      if ( nweights.size() >= 1 ) Tout->Branch("UAPDFSyst_weight_pdf1", &weight_pdf1);   
      if ( nweights.size() >= 2 ) Tout->Branch("UAPDFSyst_weight_pdf2", &weight_pdf2);   
      if ( nweights.size() >= 3 ) Tout->Branch("UAPDFSyst_weight_pdf3", &weight_pdf3);   
    }

    // ------------- Connect Analysis ----------------

    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Connect(itD->NickName,nPDFsets,nweights,PDFName,Tree);

    // ------------ Init Formulas  -------------------

    (Cfg.GetPreSel())->MakFormula(Tree);
    (Cfg.GetBaseSel())->MakFormula(Tree);
    (Cfg.GetBaseWght())->MakFormula(Tree);
    (Cfg.Getid1())->MakFormula(Tree);
    (Cfg.Getid2())->MakFormula(Tree);
    (Cfg.Getx1())->MakFormula(Tree);
    (Cfg.Getx2())->MakFormula(Tree);
    (Cfg.GetQ())->MakFormula(Tree);
    (Cfg.Getpdf1())->MakFormula(Tree);
    (Cfg.Getpdf2())->MakFormula(Tree);
    if ( itD->bFixScale ) (itD->QScale).MakFormula(Tree);

    // ------------ Event Loop -----------------------     

    Int_t nEntriesAll = Tree->GetEntries();   
    Int_t nEntries    = nEntriesAll;
    if (Cfg.GetNMax() > 0 ) nEntries = min(Cfg.GetNMax(),nEntries) ;
    double WghtNMax = double(nEntriesAll)/double(nEntries);
    cout << "[INFO] nEntriesAll= " << nEntriesAll << " nEntriesMax= " << nEntries << " --> WghtNMax= " << WghtNMax << endl;

    ProgressBar Bar1(cout,nEntries);
    Bar1.SetStyle(2);

    for (Int_t jEntry = 0 ;  jEntry < nEntries ; ++jEntry) {

      Tree->GetEntry(jEntry);
      if( jEntry% 1000 == 0)
      {
         Bar1.Update(jEntry + 1);
         Bar1.Print();
      }

      double Wght = WghtNMax;

      // ------------ Eval Formulas (Sel&Wght)  --------
      (Cfg.GetPreSel())->EvaFormula();
      bool bPreSel = ( (Cfg.GetPreSel())->Result() > 0 );
      if (!bPreSel) continue;
      (Cfg.GetBaseSel())->EvaFormula();
      bool bBaseSel = ( (Cfg.GetBaseSel())->Result() > 0 );
      (Cfg.GetBaseWght())->EvaFormula();
      Wght *= (Cfg.GetBaseWght())->Result();
      Wght *= (Cfg.GetTargetLumi())/(Cfg.GetBaseLumi()); 
      if ( Wght <= 0 ) continue ;

      // ------------ Eval Formulas  -------------------
      (Cfg.Getid1())->EvaFormula();
      (Cfg.Getid2())->EvaFormula();
      (Cfg.Getx1())->EvaFormula();
      (Cfg.Getx2())->EvaFormula();
      (Cfg.GetQ())->EvaFormula();
      (Cfg.Getpdf1())->EvaFormula();
      (Cfg.Getpdf2())->EvaFormula();
      if ( itD->bFixScale ) (itD->QScale).EvaFormula();

      int    id1  = (Cfg.Getid1())->Result() ; 
      int    id2  = (Cfg.Getid2())->Result() ; 
      double x1   = (Cfg.Getx1())->Result()  ; 
      double x2   = (Cfg.Getx2())->Result()  ; 
      double Q    = (Cfg.GetQ())->Result()   ; 
      double pdf1 = (Cfg.Getpdf1())->Result();
      double pdf2 = (Cfg.Getpdf2())->Result();

      // ----------- Correct Q ------------------------

      if ( itD->bFixScale ) Q = (itD->QScale).Result();

      // ----------- Fill Some Histos -----------------

      hQ->Fill(Q); 
      hid->Fill(id1,id2);
      hx1->Fill(x1);   
      hx2->Fill(x2);   
      hx12->Fill(x1,x2);   
 
      // ----------- Fix PDF --------------------------

      if ( itD->bFixPDF ) {
        LHAPDF::usePDFMember(1,0);
        pdf1 = LHAPDF::xfx(1, x1, Q, id1)/x1;
        pdf2 = LHAPDF::xfx(1, x2, Q, id2)/x2;
      }      

      // ----------- PDF Weights ----------------------

      for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
        for (unsigned int i=0; i<nweights.at(iPDF-1); ++i) {
          LHAPDF::usePDFMember(iPDF,i);
          double newpdf1 = LHAPDF::xfx(iPDF, x1, Q, id1)/x1;
          double newpdf2 = LHAPDF::xfx(iPDF, x2, Q, id2)/x2;
          double pdfwght = newpdf1/pdf1*newpdf2/pdf2 ;
          for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Fill(iPDF,i,bBaseSel,Wght*pdfwght);
          if ( iPDF == 1 ) weight_pdf1->at(i) = pdfwght ;
          if ( iPDF == 2 ) weight_pdf2->at(i) = pdfwght ;
          if ( iPDF == 3 ) weight_pdf3->at(i) = pdfwght ;

        }
      }

      if (bTree) {
        Tout->Fill();
      }
    
    // ------------ Event Loop (END) -----------------     

    }

    Bar1.Update(nEntries);
    Bar1.Print();
    Bar1.PrintLine();
    cout << endl;


    // ------------ Disconnect Analysis --------------

    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Disconnect();

    // ------------ Delete Formulas  -----------------

    (Cfg.GetPreSel())->DelFormula();
    (Cfg.GetBaseSel())->DelFormula();
    (Cfg.GetBaseWght())->DelFormula();
    (Cfg.Getid1())->DelFormula();
    (Cfg.Getid2())->DelFormula();
    (Cfg.Getx1())->DelFormula();
    (Cfg.Getx2())->DelFormula();
    (Cfg.GetQ())->DelFormula();
    (Cfg.Getpdf1())->DelFormula();
    (Cfg.Getpdf2())->DelFormula();
    if ( itD->bFixScale ) (itD->QScale).DelFormula();   
 
    // ------------ Close Tree ------------------------

    delete Tree ;
    File->Close();
    delete File;

    if (bTree) {
      Tout->AutoSave();
      delete Tout;
      FTout->Close();
      delete FTout;
    }

    // ------------ Summary & Plot --------------------
 
    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Print();
    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Plot();

    // ------------ Save Histograms -------------------

    string FOFileName = Cfg.GetOutDir() + "/PDFSyst_Hist_" + itD->FileName ;
    FHout = new TFile( FOFileName.c_str(),"RECREATE" );  
    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Save();
    hQ->Write();
    hid->Write();
    hx1->Write();
    hx2->Write();
    hx12->Write();    
    FHout->Close(); 
    delete FHout;

    delete hQ;
    delete hid;
    delete hx1;
    delete hx2;
    delete hx12;

    // ------------ Reset Analysis --------------------

    for ( vector<UAPDFSystAna>::iterator itSA = (Cfg.GetSystAna())->begin() ; itSA != (Cfg.GetSystAna())->end() ; ++itSA) itSA->Reset();

  }
}
