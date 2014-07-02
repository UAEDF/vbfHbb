
#include "UAPDFSystTH1F.h"

#include <TROOT.h>
#include <string>
#include <iostream>
#include <iomanip>
#include <TCanvas.h>
using namespace std;

template<typename T>
std::string to_string( const T & Value )
{
    // utiliser un flux de sortie pour créer la chaîne
    std::ostringstream oss;
    // écrire la valeur dans le flux
    oss << Value;
    // renvoyer une string
    return oss.str();
}

//------------------------------------------------------------------------------
// Pad2TAxis
//------------------------------------------------------------------------------
void Pad2TAxis(TH1* hist, TString xtitle, TString ytitle)
{
  TAxis* xaxis = (TAxis*)hist->GetXaxis();
  TAxis* yaxis = (TAxis*)hist->GetYaxis();

  xaxis->SetLabelFont  (    42);
  xaxis->SetLabelOffset( 0.025);
  xaxis->SetLabelSize  (   0.1);
  xaxis->SetNdivisions (   505);
  xaxis->SetTitle      (xtitle);
  xaxis->SetTitleFont  (    42);
  xaxis->SetTitleOffset(  1.35);
  xaxis->SetTitleSize  (  0.11);

  yaxis->CenterTitle   (      );
  yaxis->SetLabelFont  (    42);
  yaxis->SetLabelOffset(  0.02);
  yaxis->SetLabelSize  (   0.1);
  yaxis->SetNdivisions (   505);
  yaxis->SetTitle      (ytitle);
  yaxis->SetTitleFont  (    42);
  yaxis->SetTitleOffset(  .6);
  yaxis->SetTitleSize  (  0.11);
}

//------------------------------------------------------------------------------
// GetMaximumIncludingErrors
//------------------------------------------------------------------------------
Double_t GetMaximumIncludingErrors(TH1F* h)
{
  Float_t maxWithErrors = 0;

  for (Int_t i=1; i<=h->GetNbinsX(); i++) {

    Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

    if (binHeight > maxWithErrors) maxWithErrors = binHeight;
  }

  return maxWithErrors;
}


// ----------------------Book Histos --------------------------

void UAPDFSystTH1F::Book ( const unsigned int nPDFsetsIn , const vector<unsigned int> nweightsIn , const vector<string> PDFNameIn , TTree* Tree)
{

   // Safety Checks

   //if ( ! bInit ) { cout << "[ERROR] UAPDFSystAna::Connect not initialized !" << endl ; return ; }   
   if ( nPDFsetsIn == 0 )                 { cout << "[ERROR] UAPDFSystAna::Connect nPDFsets = 0 !" << endl ; return ; }   
   if ( nweightsIn.size() != nPDFsetsIn ) { cout << "[ERROR] UAPDFSystAna::Connect nweightsIn wrong size() !" << endl ; return ; }
   if ( PDFNameIn.size()  != nPDFsetsIn ) { cout << "[ERROR] UAPDFSystAna::Connect PDFNameIn  wrong size() !" << endl ; return ; }

   // Copy Info

   nPDFsets = nPDFsetsIn ;
   for ( unsigned int iPDF = 0 ; iPDF < nPDFsets ; ++iPDF ) {
     nweights.push_back( nweightsIn.at(iPDF) ) ;
     PDFName .push_back( PDFNameIn.at(iPDF)  ) ; 
   }

   // Book Histograms

   TH1::SetDefaultSumw2(1);
   gROOT->cd();

   PDFStart.push_back(0);
   for (  unsigned int iPDF=2 ; iPDF <= nPDFsets ; ++iPDF ) {
      PDFStart.push_back(PDFStart.at(iPDF-2)+nweights.at(iPDF-2));
   }
   string Name;
   for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {

     Name =  Formula.NickName+"_Yld_Cent_"+to_string(iPDF);
     hYldCent.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Yld_Up_"+to_string(iPDF);
     hYldUp  .push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Yld_Down_"+to_string(iPDF);
     hYldDown.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Yld_ErrUp_"+to_string(iPDF);
     hYldErrUp  .push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Yld_ErrDown_"+to_string(iPDF);
     hYldErrDown.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );

     Name =  Formula.NickName+"_Acc_Cent_"+to_string(iPDF);
     hAccCent.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Acc_Up_"+to_string(iPDF);
     hAccUp  .push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Acc_Down_"+to_string(iPDF);
     hAccDown.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Acc_ErrUp_"+to_string(iPDF);
     hAccErrUp  .push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     Name =  Formula.NickName+"_Acc_ErrDown_"+to_string(iPDF);
     hAccErrDown.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );

     for (unsigned int i=PDFStart.at(iPDF-1) ; i < PDFStart.at(iPDF-1)+ nweights.at(iPDF-1) ; ++i ) {
       Name = Formula.NickName+"_All_"+to_string(i);
       hSystAll.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
       Name = Formula.NickName+"_Sel_"+to_string(i);
       hSystSel.push_back( new TH1F(Name.c_str(),Name.c_str(),nBins,xMin,xMax) );
     }
   } 

   // Connect

   Formula.MakFormula(Tree);
   bConnect = true ;

   // Init Counters
   originalEvents = 0 ;
   selectedEvents = 0 ;

   // Set the bBook flag

   bBook = true ;

}


// ---------------------- Disconnect --------------------------
void UAPDFSystTH1F::Disconnect ()
{
   if ( ! bConnect ) return;
   //cout << "UAPDFSystTH1F::Disconnect() " <<  Formula.NickName << " -------" << endl;
   Formula.DelFormula();   
   bConnect = false;
}

// ----------------------Fill Histos --------------------------

void UAPDFSystTH1F::Fill (int iPDF , int iMem , bool bFullSel , double pdfwght )
{
   if ( ! bBook ) return;
   Formula.EvaFormula();
   if (iPDF==1&&iMem==0) ++originalEvents;
   hSystAll.at(PDFStart.at(iPDF-1)+iMem)->Fill(Formula.Result(),pdfwght);
   if (bFullSel) {
     if (iPDF==1&&iMem==0) ++selectedEvents;
     hSystSel.at(PDFStart.at(iPDF-1)+iMem)->Fill(Formula.Result(),pdfwght);
   }
}

// ----------------------Reset Histos --------------------------
void UAPDFSystTH1F::Reset()
{
   if ( ! bBook ) return;

   //cout << "UAPDFSystTH1F::Reset() " <<  Formula.NickName << " -------" << endl;

   for ( unsigned int iH=0 ; iH < hSystAll.size() ; ++iH ) delete hSystAll.at(iH) ;
   for ( unsigned int iH=0 ; iH < hSystSel.size() ; ++iH ) delete hSystSel.at(iH) ;
   hSystAll.clear();
   hSystSel.clear();

   for ( unsigned int iH=0 ; iH < hYldCent.size()    ; ++iH ) delete hYldCent.at(iH) ;  
   for ( unsigned int iH=0 ; iH < hYldUp.size()      ; ++iH ) delete hYldUp.at(iH)   ;
   for ( unsigned int iH=0 ; iH < hYldDown.size()    ; ++iH ) delete hYldDown.at(iH) ;  
   for ( unsigned int iH=0 ; iH < hYldErrUp.size()   ; ++iH ) delete hYldErrUp.at(iH)   ;
   for ( unsigned int iH=0 ; iH < hYldErrDown.size() ; ++iH ) delete hYldErrDown.at(iH) ;  
   hYldCent.clear();
   hYldUp  .clear();
   hYldDown.clear();
   hYldErrUp.clear();
   hYldErrDown.clear();

   for ( unsigned int iH=0 ; iH < hAccCent.size()    ; ++iH ) delete hAccCent.at(iH) ;  
   for ( unsigned int iH=0 ; iH < hAccUp.size()      ; ++iH ) delete hAccUp.at(iH)   ;
   for ( unsigned int iH=0 ; iH < hAccDown.size()    ; ++iH ) delete hAccDown.at(iH) ;  
   for ( unsigned int iH=0 ; iH < hAccErrUp.size()   ; ++iH ) delete hAccErrUp.at(iH)   ;
   for ( unsigned int iH=0 ; iH < hAccErrDown.size() ; ++iH ) delete hAccErrDown.at(iH) ;  
   hAccCent.clear();
   hAccUp  .clear();
   hAccDown.clear();
   hAccErrUp.clear();
   hAccErrDown.clear();

   bBook = false;
}

// ----------------------Compute Syst --------------------------
void UAPDFSystTH1F::Compute()
{
  if ( ! bBook ) return;
 
  //cout << "------- " << Formula.NickName << " -------" << endl;
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
    unsigned int npairs = (nweights.at(iPDF-1)-1)/2;
    bool nnpdfFlag  = (PDFName.at(iPDF-1).substr(0,5)=="NNPDF");
    bool cteqFlag = (PDFName.at(iPDF-1).substr(0,4)=="cteq") || (PDFName.at(iPDF-1).substr(0,2)=="CT") ;

    //cout << "------- " << PDFName.at(iPDF-1) << " -------" << endl;

    for ( unsigned int iBin = 1 ; iBin <= nBins ; ++iBin ) {

      // ------ Systematic on YIELD ------

      double wplus_yield = 0.;
      double wminus_yield = 0.; 
      unsigned int nplus_yield = 0;
      unsigned int nminus_yield = 0;

      double CentVal = (hSystSel.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) ;

      if ( CentVal > 0. ) {
        for (unsigned int j=0; j<npairs; ++j) {
          double wa = (hSystSel.at(PDFStart.at(iPDF-1)+2*j+1))->GetBinContent(iBin) / CentVal -1. ;  
          double wb = (hSystSel.at(PDFStart.at(iPDF-1)+2*j+2))->GetBinContent(iBin) / CentVal -1. ;  
          if (nnpdfFlag) {
            if (wa>0.) {
              wplus_yield += wa*wa; 
              nplus_yield++;
            } else {
              wminus_yield += wa*wa;
              nminus_yield++;
            }
            if (wb>0.) {
              wplus_yield += wb*wb; 
              nplus_yield++;
            } else {
              wminus_yield += wb*wb;
              nminus_yield++;
            }
          } else { 
            if (wa>wb) {
              if (wa<0.) wa = 0.;
              if (wb>0.) wb = 0.;
              wplus_yield += wa*wa;
              wminus_yield += wb*wb;
            } else {
              if (wb<0.) wb = 0.;
              if (wa>0.) wa = 0.;
              wplus_yield += wb*wb;
              wminus_yield += wa*wa;
            }
          }
        }
      }
      if (wplus_yield>0)  wplus_yield  = sqrt(wplus_yield);
      if (wminus_yield>0) wminus_yield = sqrt(wminus_yield);
      if (nnpdfFlag) {
        if (nplus_yield>0) wplus_yield /= sqrt(nplus_yield);
        if (nminus_yield>0) wminus_yield /= sqrt(nminus_yield);
      } 
      if (cteqFlag) {
        //cout << "[INFO] CTEQ 90%->68% CL PDF rescaling done" << endl; 
        if (wplus_yield>0)  wplus_yield  /= 1.64485;
        if (wminus_yield>0) wminus_yield /= 1.64485;
      }

      (hYldCent.at(iPDF-1))->SetBinContent(iBin,CentVal);
      (hYldCent.at(iPDF-1))->SetBinError(iBin,(hSystSel.at(PDFStart.at(iPDF-1)))->GetBinError(iBin));
      (hYldUp.at(iPDF-1)  )->SetBinContent(iBin,CentVal*(1.+wplus_yield));
      (hYldUp.at(iPDF-1)  )->SetBinError(iBin,0);
      (hYldDown.at(iPDF-1))->SetBinContent(iBin,CentVal*(1.-wminus_yield));
      (hYldDown.at(iPDF-1))->SetBinError(iBin,0);
      (hYldErrUp.at(iPDF-1)  )->SetBinContent(iBin,(1.+wplus_yield));
      (hYldErrUp.at(iPDF-1)  )->SetBinError(iBin,0);
      (hYldErrDown.at(iPDF-1))->SetBinContent(iBin,(1.-wminus_yield));
      (hYldErrDown.at(iPDF-1))->SetBinError(iBin,0);


      // ------ Systematic on ACCEPTANCE ------

      double wplus_acc = 0.;
      double wminus_acc = 0.; 
      unsigned int nplus_acc = 0;
      unsigned int nminus_acc = 0;

      double acc_central     = 0.;
      double acc2_central    = 0.;
      if ( (hSystAll.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) > 0. ) {
        acc_central  = (hSystSel.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) / (hSystAll.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) ;
        acc2_central = pow((hSystSel.at(PDFStart.at(iPDF-1)))->GetBinError(iBin),2) / (hSystAll.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) ;
      }
      double waverage = (hSystAll.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin)/originalEvents;
      double acc_central_err = sqrt((acc2_central/waverage-acc_central*acc_central)/originalEvents); ;
       acc_central_err = 0;

      if ( acc_central > 0. ) {
        for (unsigned int j=0; j<npairs; ++j) {
          double wa = 0.;
          if ( (hSystAll.at(PDFStart.at(iPDF-1)+2*j+1))->GetBinContent(iBin) > 0. )
            wa = ( (hSystSel.at(PDFStart.at(iPDF-1)+2*j+1))->GetBinContent(iBin)/(hSystAll.at(PDFStart.at(iPDF-1)+2*j+1))->GetBinContent(iBin) )/acc_central-1.;
          double wb = 0.;
          if ( (hSystAll.at(PDFStart.at(iPDF-1)+2*j+2))->GetBinContent(iBin) > 0. )
            wb = ( (hSystSel.at(PDFStart.at(iPDF-1)+2*j+2))->GetBinContent(iBin)/(hSystAll.at(PDFStart.at(iPDF-1)+2*j+2))->GetBinContent(iBin) )/acc_central-1.;
          if (nnpdfFlag) {
            if (wa>0.) {
              wplus_acc += wa*wa; 
              nplus_acc++;
            } else {
              wminus_acc += wa*wa;
              nminus_acc++;
            }
            if (wb>0.) {
              wplus_acc += wb*wb; 
              nplus_acc++;
            } else {
              wminus_acc += wb*wb;
              nminus_acc++;
            }
          } else { 
            if (wa>wb) {
              if (wa<0.) wa = 0.;
              if (wb>0.) wb = 0.;
              wplus_acc += wa*wa;
              wminus_acc += wb*wb;
            } else {
              if (wb<0.) wb = 0.;
              if (wa>0.) wa = 0.;
              wplus_acc += wb*wb;
              wminus_acc += wa*wa;
            }
          }
        }
      }
      if (wplus_acc>0)  wplus_acc  = sqrt(wplus_acc);
      if (wminus_acc>0) wminus_acc = sqrt(wminus_acc);
      if (nnpdfFlag) {
        if (nplus_acc>0) wplus_acc /= sqrt(nplus_acc);
        if (nminus_acc>0) wminus_acc /= sqrt(nminus_acc);
      } 
      if (cteqFlag) {
        //cout << "[INFO] CTEQ 90%->68% CL PDF rescaling done" << endl; 
        if (wplus_acc>0)  wplus_acc  /= 1.64485;
        if (wminus_acc>0) wminus_acc /= 1.64485;
      }

      (hAccCent.at(iPDF-1))->SetBinContent(iBin,acc_central);
      (hAccCent.at(iPDF-1))->SetBinError(iBin,acc_central_err);
      (hAccUp.at(iPDF-1)  )->SetBinContent(iBin,acc_central*(1.+wplus_acc));
      (hAccUp.at(iPDF-1)  )->SetBinError(iBin,0);
      (hAccDown.at(iPDF-1))->SetBinContent(iBin,acc_central*(1.-wminus_acc));
      (hAccDown.at(iPDF-1))->SetBinError(iBin,0);
      (hAccErrUp.at(iPDF-1)  )->SetBinContent(iBin,(1.+wplus_acc));
      (hAccErrUp.at(iPDF-1)  )->SetBinError(iBin,0);
      (hAccErrDown.at(iPDF-1))->SetBinContent(iBin,(1.-wminus_acc));
      (hAccErrDown.at(iPDF-1))->SetBinError(iBin,0);

      // ------ Print ------
      //cout << acc_central << " " << (hSystSel.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) << " " << (hSystAll.at(PDFStart.at(iPDF-1)))->GetBinContent(iBin) << endl;
      //cout << "iBin= " << iBin << "\t ->YIELD: +" << 100.*wplus_yield << " / -" << 100.*wminus_yield << " [%]" 
      //                         << "\t ->ACC  : +" << 100.*wplus_acc   << " / -" << 100.*wminus_acc   << " [%]" << endl;

    } // END: for ( unsigned int iBin ...
  } // END: for (  unsigned int iPDF=1



}



// ----------------------Print Syst --------------------------
void UAPDFSystTH1F::Print()
{
  if ( ! bBook ) return;
  if ( ! bComputed) Compute();

  cout << "------- " << Formula.NickName << " -------" << endl;
  cout << "Total number of analyzed data: " << originalEvents << " [events]" << endl;
  double originalAcceptance = double(selectedEvents)/double(originalEvents);
  cout << "Total number of selected data: " << selectedEvents << " [events], corresponding to acceptance: [" 
       << originalAcceptance*100 << " +- " << 100*sqrt( originalAcceptance*(1.-originalAcceptance)/originalEvents) << "] %" << endl;

  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
    cout << "------- " << PDFName.at(iPDF-1) << " -------" << endl;
    for ( unsigned int iBin = 1 ; iBin <= nBins ; ++iBin ) {
      float cent_yield   = (hYldCent.at(iPDF-1))->GetBinContent(iBin);
      float stat_yield   = (hYldCent.at(iPDF-1))->GetBinError(iBin);
      float wplus_yield  = (hYldErrUp.at(iPDF-1)  )->GetBinContent(iBin) - 1.;
      float wminus_yield = (hYldErrDown.at(iPDF-1)  )->GetBinContent(iBin) - 1.;
      float cent_acc     = (hAccCent.at(iPDF-1))->GetBinContent(iBin);
      float stat_acc     = (hAccCent.at(iPDF-1))->GetBinError(iBin);
      float wplus_acc    = (hAccErrUp.at(iPDF-1)  )->GetBinContent(iBin) - 1.;
      float wminus_acc   = (hAccErrDown.at(iPDF-1)  )->GetBinContent(iBin) - 1.;

      cout << "iBin= " << iBin << "\t ->YIELD: " << cent_yield 
                               << "\t STAT: +- " << 100.*(stat_yield/cent_yield) << " [%]"
                               << "\t SYST: +" << 100.*wplus_yield << " / " << 100.*wminus_yield << " [%]" << endl;

      cout                     << "\t ->ACC  : " << 100.*cent_acc  
                               << "\t STAT: +- " << 100.*(stat_acc/cent_acc)    << " [%]"
                               << "\t SYST: +" << 100.*wplus_acc   << " / " << 100.*wminus_acc   << " [%]" << endl;

    }
  }
  cout << endl;

}

// ----------------------Plot  Syst --------------------------
void UAPDFSystTH1F::Plot()
{
  if ( ! bBook ) return;
  if ( ! bComputed) Compute();

  // Yield

  TCanvas* Canvas ;
  TPad* pad1;
  TPad* pad2;
    
  string CanName= Formula.NickName+"_Yield_";
  Canvas = new TCanvas( CanName.c_str() , CanName.c_str() , 600 , 1.2*600 );
   
  pad1 = new TPad("pad1", "pad1", 0, 0.25, 1, 1);
  pad1->SetTopMargin   (0.05);
  pad1->SetBottomMargin(0.08);
  pad1->SetRightMargin(0.05);
  pad1->SetLeftMargin(0.15);
  pad1->Draw();
  
  pad2 = new TPad("pad2", "pad2", 0, 0, 1, 0.3);
  pad2->SetTopMargin   (-0.08);
  pad2->SetBottomMargin(0.35);
  pad2->SetRightMargin(0.05);
  pad2->SetLeftMargin(0.15);
  pad2->Draw(); 
  
  Double_t hMax = 0;
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) hMax = max(hMax,GetMaximumIncludingErrors(hYldUp.at(iPDF-1)));
  hYldCent.at(0)->GetYaxis()->SetRangeUser( 0.   , 1.55*hMax);  
    
   
  pad1->cd();
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
    hYldCent.at(iPDF-1)->SetLineWidth(2);
    hYldUp.at(iPDF-1)->SetLineWidth(2);
    hYldDown.at(iPDF-1)->SetLineWidth(2);
    if   (iPDF == 2 ) {
      hYldCent.at(iPDF-1)->SetLineColor(kBlue);
      hYldUp.at(iPDF-1)->SetLineColor(kBlue);
      hYldDown.at(iPDF-1)->SetLineColor(kBlue);
    } 
    if   (iPDF == 3 ) {
      hYldCent.at(iPDF-1)->SetLineColor(kRed);
      hYldUp.at(iPDF-1)->SetLineColor(kRed);
      hYldDown.at(iPDF-1)->SetLineColor(kRed);
    } 
    if   (iPDF == 1 ) hYldCent.at(iPDF-1)->Draw("e"); 
    else              hYldCent.at(iPDF-1)->Draw("esame"); 
    hYldUp.at(iPDF-1)->Draw("histsame");
    hYldDown.at(iPDF-1)->Draw("histsame");
  }

  TLegend* Legend = new TLegend (.18,.90-nPDFsets*.045,.58,.90);
  Legend->SetHeader(Formula.NickName.c_str());
  Legend->SetBorderSize(0);
  Legend->SetFillColor(0);
  Legend->SetFillStyle(0);
  Legend->SetTextFont(42); 
  Legend->SetTextAlign(12);
  Legend->SetTextSize(0.035);
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
    Legend->AddEntry( hYldCent.at(iPDF-1) , TString(" ")+(PDFName.at(iPDF-1)).c_str() , "lp" ); 
  } 
  Legend->Draw("same");


  pad2->cd();
  Pad2TAxis(hYldErrUp.at(0),(Formula.Expression).c_str(),"PDFSyst [%]");
  hYldErrUp.at(0)->GetYaxis()->SetRangeUser(0.95,1.05);
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {
    hYldErrUp.at(iPDF-1)->SetLineWidth(2);
    hYldErrDown.at(iPDF-1)->SetLineWidth(2);
    if   (iPDF == 2 ) {
      hYldErrUp.at(iPDF-1)->SetLineColor(kBlue);
      hYldErrDown.at(iPDF-1)->SetLineColor(kBlue);
    }
    if   (iPDF == 3 ) {
      hYldErrUp.at(iPDF-1)->SetLineColor(kRed);
      hYldErrDown.at(iPDF-1)->SetLineColor(kRed);
    }
    if   (iPDF == 1 ) hYldErrUp.at(iPDF-1)->Draw("hist");
    else              hYldErrUp.at(iPDF-1)->Draw("histsame");
    hYldErrDown.at(iPDF-1)->Draw("histsame");
  }
 

 
  string FigName ;
  FigName = "plots/"+Formula.NickName+"_Yield"+".png";
  Canvas->SaveAs(FigName.c_str());
  FigName = "plots/"+Formula.NickName+"_Yield"+".pdf";
  Canvas->SaveAs(FigName.c_str());  

  delete pad1;
  delete pad2;
  delete Canvas;

/*  
  // Acceptance
  for (  unsigned int iPDF=1 ; iPDF <= nPDFsets ; ++iPDF ) {  

    TCanvas* Canvas ;
    TPad* pad1;
    TPad* pad2;
    
    string CanName= Formula.NickName+"_Acc_"+PDFName.at(iPDF-1);
    Canvas = new TCanvas( CanName.c_str() , CanName.c_str() , 600 , 1.2*600 );
   
    pad1 = new TPad("pad1", "pad1", 0, 0.25, 1, 1);
    pad1->SetTopMargin   (0.05);
    pad1->SetBottomMargin(0.08);
    pad1->SetRightMargin(0.05);
    pad1->SetLeftMargin(0.15);
    pad1->Draw();
  
    pad2 = new TPad("pad2", "pad2", 0, 0, 1, 0.3);
    pad2->SetTopMargin   (-0.08);
    pad2->SetBottomMargin(0.35);
    pad2->SetRightMargin(0.05);
    pad2->SetLeftMargin(0.15);
    pad2->Draw(); 
  
    Double_t hMax = GetMaximumIncludingErrors(hAccUp.at(iPDF-1));
    hAccCent.at(iPDF-1)->GetYaxis()->SetRangeUser( 0.   , 1.55*hMax);  
   
    pad1->cd();
    hAccCent.at(iPDF-1)->Draw("e"); 
    hAccUp.at(iPDF-1)->Draw("histsame");
    hAccDown.at(iPDF-1)->Draw("histsame");
  
    pad2->cd();
    Pad2TAxis(hAccErrUp.at(iPDF-1),(Formula.Expression).c_str(),"PDFSyst [%]");
    hAccErrUp.at(iPDF-1)->GetYaxis()->SetRangeUser(0.95,1.05);
    hAccErrUp.at(iPDF-1)->Draw("hist");
    hAccErrDown.at(iPDF-1)->Draw("histsame");
  
  
    string FigName ;
    FigName = "plots/"+Formula.NickName+"_Acc_"+PDFName.at(iPDF-1)+".png";
    Canvas->SaveAs(FigName.c_str());
    FigName = "plots/"+Formula.NickName+"_Acc_"+PDFName.at(iPDF-1)+".pdf";
    Canvas->SaveAs(FigName.c_str());  

    delete pad1;
    delete pad2;
    delete Canvas;

  }
*/

}

// ----------------------Reset Histos --------------------------
void UAPDFSystTH1F::Save()
{
   if ( ! bBook ) return;
   if ( ! bComputed) Compute();

   cout << "UAPDFSystTH1F::Save() " <<  Formula.NickName << " -------" << endl;

   for ( unsigned int iH=0 ; iH < hSystAll.size() ; ++iH ) (hSystAll.at(iH))->Write() ;
   for ( unsigned int iH=0 ; iH < hSystSel.size() ; ++iH ) (hSystSel.at(iH))->Write() ;

   for ( unsigned int iH=0 ; iH < hYldCent.size()    ; ++iH ) (hYldCent.at(iH))->Write() ;  
   for ( unsigned int iH=0 ; iH < hYldUp.size()      ; ++iH ) (hYldUp.at(iH))->Write()   ;
   for ( unsigned int iH=0 ; iH < hYldDown.size()    ; ++iH ) (hYldDown.at(iH))->Write() ;  
   for ( unsigned int iH=0 ; iH < hYldErrUp.size()   ; ++iH ) (hYldErrUp.at(iH))->Write()   ;
   for ( unsigned int iH=0 ; iH < hYldErrDown.size() ; ++iH ) (hYldErrDown.at(iH))->Write() ;  

   for ( unsigned int iH=0 ; iH < hAccCent.size()    ; ++iH ) (hAccCent.at(iH))->Write() ;  
   for ( unsigned int iH=0 ; iH < hAccUp.size()      ; ++iH ) (hAccUp.at(iH))->Write()   ;
   for ( unsigned int iH=0 ; iH < hAccDown.size()    ; ++iH ) (hAccDown.at(iH))->Write() ;  
   for ( unsigned int iH=0 ; iH < hAccErrUp.size()   ; ++iH ) (hAccErrUp.at(iH))->Write()   ;
   for ( unsigned int iH=0 ; iH < hAccErrDown.size() ; ++iH ) (hAccErrDown.at(iH))->Write() ;  
}

