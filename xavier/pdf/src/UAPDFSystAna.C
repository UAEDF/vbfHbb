
#include "UAPDFSystAna.h"

#include <iostream>
#include <iomanip>
using namespace std;


// ---------------------- Connect -----------------------------

void UAPDFSystAna::Connect( const string DataSetIn , const unsigned int nPDFsetsIn , const vector<unsigned int> nweightsIn , const vector<string> PDFNameIn , TTree* Tree )
{

   // Safety Checks

   if ( ! bInit ) { cout << "[ERROR] UAPDFSystAna::Connect not initialized !" << endl ; return ; }   
   if ( nPDFsetsIn == 0 )                 { cout << "[ERROR] UAPDFSystAna::Connect nPDFsets = 0 !" << endl ; return ; }   
   if ( nweightsIn.size() != nPDFsetsIn ) { cout << "[ERROR] UAPDFSystAna::Connect nweightsIn wrong size() !" << endl ; return ; }
   if ( PDFNameIn.size()  != nPDFsetsIn ) { cout << "[ERROR] UAPDFSystAna::Connect PDFNameIn  wrong size() !" << endl ; return ; }
   if ( Tree == NULL )                    { cout << "[ERROR] UAPDFSystAna::Connect Tree is NULL ! " << endl ; return ; }   

   // Copy Info

   DataSet  = DataSetIn ;
   nPDFsets = nPDFsetsIn ;
   for ( unsigned int iPDF = 0 ; iPDF < nPDFsets ; ++iPDF ) {
     nweights.push_back( nweightsIn.at(iPDF) ) ;
     PDFName .push_back( PDFNameIn.at(iPDF)  ) ; 
   }

   // Connect Tree to Formula
    
   Selection.MakFormula(Tree);   

   // Histograms

   SystTH1F.push_back(new UAPDFSystTH1F(DataSet+"_"+NickName,"0.5",1,0.,1.));
//   SystTH1F.push_back(new UAPDFSystTH1F("MLP_"+DataSet+"_"+NickName,"MLP",20,0.,1.));
//   SystTH1F.push_back(new UAPDFSystTH1F("mbb_"+DataSet+"_"+NickName,"mbb",20,60.,200.));

   SystTH1F.push_back(new UAPDFSystTH1F("mll_"+DataSet+"_"+NickName,"mll",30,0.,300.));
   SystTH1F.push_back(new UAPDFSystTH1F("mth_"+DataSet+"_"+NickName,"mth",30,0.,300.));
   
   for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Book(nPDFsetsIn,nweightsIn,PDFNameIn,Tree); 
 
   // Set the bConnect flag

   bConnect = true ;
 
}

// ---------------------- Disconnect -----------------------------
void UAPDFSystAna::Disconnect( ) 
{
  if (! bConnect) return; 
  Selection.DelFormula();
  for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Disconnect();
  bConnect =false;
}

// ---------------------- Fill -----------------------------------
void UAPDFSystAna::Fill (int iPDF , int iMem , bool bBaseSel , double pdfwght )
{
   if ( ! bConnect ) return ;
   Selection.EvaFormula();
   bool bFullSel = ( bBaseSel && Selection.Result()>0 ); 
   for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Fill(iPDF,iMem,bFullSel,pdfwght);
}

// ---------------------- Print -----------------------------------
void  UAPDFSystAna::Print()
{
   cout << "############ " << NickName << " ############" << endl;
   (SystTH1F.at(0))->Print(); 
   //for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Print(); 
}

// ---------------------- Plot -----------------------------------
void  UAPDFSystAna::Plot()
{
   for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Plot(); 
}

// ---------------------- Save -----------------------------------
void  UAPDFSystAna::Save()
{
   for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) (SystTH1F.at(iH))->Save(); 
}



// ---------------------- Reset -----------------------------------
void  UAPDFSystAna::Reset()
{
   //cout << "UAPDFSystAna::Reset() " <<  NickName << "-------" << endl; 
   // Disconnect
   Disconnect();

   // Clear all vectors
   DataSet ="";
   nPDFsets=0;
   nweights.clear();
   PDFName.clear();
   PDFStart.clear();
   for ( unsigned int iH = 0 ; iH < SystTH1F.size() ; ++iH ) delete (SystTH1F.at(iH));
   SystTH1F.clear();
}





