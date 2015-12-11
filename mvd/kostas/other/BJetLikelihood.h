#ifndef BJetLikelihood_h
#define BJetLikelihood_h

#include "TMVA/Reader.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"

class BJetLikelihood
{
  public:
    BJetLikelihood(std::string weights);
    ~BJetLikelihood();
    float eval(int btagIdx,int etaIdx,float btag,float eta);
    
  private:
    std::string weights_;
    TMVA::Reader *reader_;
    float var_[4];
};
#endif
