#ifndef __TreeFormula_t_H__
#define __TreeFormula_t_H__

#include <string>
using namespace std;

#include <TTree.h>
#include <TTreeFormula.h>

class TreeFormula_t {
  public:
  TreeFormula_t(){ Expression = "1" ; bEvaluated = false ;}
  virtual ~TreeFormula_t(){;}
  string        NickName   ;
  string        Expression ;
  private:
  TTreeFormula* Formula    ;
  bool          bEvaluated ;
  float         Result_    ;
  public:
  void MakFormula (TTree *);
  void EvaFormula ()       ;
  void DelFormula ()       ;
  float   Result()         ;
};

void TreeFormula_t::MakFormula (TTree* Tree){
  Formula = new TTreeFormula(NickName.c_str(),Expression.c_str(),Tree);
}
void TreeFormula_t::EvaFormula (){
  if ( Formula ) {
    Formula->GetNdata();
    Result_    = Formula->EvalInstance() ;
    bEvaluated = true ;
  } else {
    cout << "[TreeFormula_t::EvaFormula] Formula not associated to a Tree: " << NickName << endl ;
    Result_ = 0. ;
  }
}
void TreeFormula_t::DelFormula (){
  bEvaluated = false ;
  delete Formula;
}
Float_t TreeFormula_t::Result(){
  if ( bEvaluated ) {
    return Result_ ;
  } else {
    cout << "[TreeFormula_t::EvaFormula] Formula not evaluated: " << NickName << endl ;
    return 0.;
  }
}

#endif
