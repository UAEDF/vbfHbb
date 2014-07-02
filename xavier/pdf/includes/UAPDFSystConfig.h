#ifndef __UAPDFSystConfig_H__
#define __UAPDFSystConfig_H__

#include <string>
#include <vector>
using namespace std;

// #include <TROOT.h>
#include <TFile.h>
#include <TTree.h>

#include "TreeFormula_t.h"
#include "UAPDFSystAna.h"

class InputData_t {
  public:
  InputData_t(){;}
  virtual ~InputData_t(){;}
  string          NickName  ;
  string          FileName  ;
  string          TreeName  ;
  bool            bFixScale ;
  TreeFormula_t   QScale    ;
  bool            bFixPDF   ;
  string          RefPDF    ;
};

class UAPDFSystConfig {

  private:

  bool                   bTree      ;
  int                    NMax       ;

  string                 InDir      ;
  string                 OutDir     ;
  vector<InputData_t>    InputData  ;
  TreeFormula_t          PreSel     ;
  TreeFormula_t          BaseSel    ;
  TreeFormula_t          BaseWght   ;
  float                  BaseLumi   ; 
  float                  TargetLumi ; 
  TreeFormula_t          id1        ;
  TreeFormula_t          id2        ; 
  TreeFormula_t          x1         ;
  TreeFormula_t          x2         ;
  TreeFormula_t          Q          ;
  TreeFormula_t          pdf1       ;
  TreeFormula_t          pdf2       ;
  vector<string>         PDFsets    ;
  vector<UAPDFSystAna>   SystAna    ;

  public:
  UAPDFSystConfig(){ bTree = false ;}
  virtual ~UAPDFSystConfig(){;}

  void ReadCfg(string&);

  void                    SetbTree( bool b)   { bTree = b            ; }
  bool                    GetbTree()          { return bTree         ; }
  void                    SetNMax(int N)      { NMax = N             ; }
  int                     GetNMax()           { return NMax          ; }   

  // Getters:
  string                  GetInDir()          { return InDir         ; }
  string                  GetOutDir()         { return OutDir        ; }
  vector<InputData_t>*    GetInputData()      { return &InputData    ; }
  TreeFormula_t*          GetPreSel()         { return &PreSel       ; }
  TreeFormula_t*          GetBaseSel()        { return &BaseSel      ; }
  TreeFormula_t*          GetBaseWght()       { return &BaseWght     ; }
  float                   GetBaseLumi()       { return BaseLumi      ; }
  float                   GetTargetLumi()     { return TargetLumi    ; }
  TreeFormula_t*          Getid1()            { return &id1          ; }
  TreeFormula_t*          Getid2()            { return &id2          ; }
  TreeFormula_t*          Getx1()             { return &x1           ; }
  TreeFormula_t*          Getx2()             { return &x2           ; }
  TreeFormula_t*          GetQ()              { return &Q            ; }
  TreeFormula_t*          Getpdf1()           { return &pdf1         ; }
  TreeFormula_t*          Getpdf2()           { return &pdf2         ; }
  vector<string>*         GetPDFsets()        { return &PDFsets      ; }
  vector<UAPDFSystAna>*   GetSystAna()        { return &SystAna      ; }

};


#endif
