#include "KKousour/CMGAnalysis/plugins/BJetLikelihood.h"

BJetLikelihood::BJetLikelihood(std::string weights)
{
  weights_ = weights;
  reader_ = new TMVA::Reader("!Color:!Silent");
  
  reader_->AddVariable("btagIdx",&var_[0]);
  reader_->AddVariable("etaIdx" ,&var_[1]);
  reader_->AddVariable("btag"   ,&var_[2]);
  reader_->AddVariable("eta"    ,&var_[3]);
  
  edm::FileInPath f1(weights_);
  reader_->BookMVA("BDT",f1.fullPath());  
  
}
//-------------------------------------------------------------
float BJetLikelihood::eval(int btagIdx,int etaIdx,float btag,float eta)
{
  var_[0]  = btagIdx;
  var_[1]  = etaIdx; 
  var_[2]  = btag;
  var_[3]  = eta;
  
  return reader_->EvaluateMVA("BDT");
}
//-------------------------------------------------------------
BJetLikelihood::~BJetLikelihood()
{
  delete reader_;
}
