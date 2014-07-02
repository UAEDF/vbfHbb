#ifndef __UAPDFSystTH1F_H__
#define __UAPDFSystTH1F_H__

#include <TH1F.h>
#include <string>
#include <vector>
using namespace std;

#include <TTree.h>
#include "TreeFormula_t.h"

class UAPDFSystTH1F {

  private:

    bool                  bBook     ;
    bool                  bConnect  ;
    bool                  bComputed ;

    // Histo Setup
    //string                NickName  ;
    //string                Expression; 
    TreeFormula_t         Formula   ;
    unsigned int          nBins     ;
    float                 xMin      ;
    float                 xMax      ;
    string                XaxisTitle;

    // PDF Setup
    unsigned int          nPDFsets  ;
    vector<unsigned int>  nweights  ;
    vector<string>        PDFName   ;
    vector <unsigned int> PDFStart  ;

    // TH1F
    vector<TH1F*>         hSystAll  ;
    vector<TH1F*>         hSystSel  ;

    vector<TH1F*>         hYldCent     ;
    vector<TH1F*>         hYldUp       ;
    vector<TH1F*>         hYldDown     ;
    vector<TH1F*>         hYldErrUp    ;
    vector<TH1F*>         hYldErrDown  ;

    vector<TH1F*>         hAccCent     ;
    vector<TH1F*>         hAccUp       ;
    vector<TH1F*>         hAccDown     ;
    vector<TH1F*>         hAccErrUp    ;
    vector<TH1F*>         hAccErrDown  ;

    // Counter
    
    unsigned int          originalEvents;
    unsigned int          selectedEvents;

  public:

    // Constructor
    UAPDFSystTH1F ()     { Formula.NickName = "NoVar" ; Formula.Expression = "0.5" ; nBins = 1 ; xMin = 0. ; xMax = 1. ; XaxisTitle = "NoVar" ; bBook = false ; bConnect = false ; bComputed = false ; }
    UAPDFSystTH1F ( string NickName , string Expression , int nBinsIn , double xMinIn, double xMaxIn ) { Formula.NickName = NickName ; Formula.Expression = Expression ; nBins = nBinsIn  ; xMin = xMinIn ; xMax = xMaxIn ; XaxisTitle = "NoVar" ; bBook = false ; bConnect = false ; bComputed = false ; }

    // Destructor
    virtual ~UAPDFSystTH1F () { Reset() ; }
    
    // Book & Fill & Reset Histos
    void Book ( const unsigned int , const vector<unsigned int> , const vector<string> , TTree* ) ;
    void Fill(int,int,bool,double);
    void Disconnect();
    void Reset();

    // Compute & Print & Plot & Save
    void Compute();
    void Print(); 
    void Plot();
    void Save(); 

};

#endif

