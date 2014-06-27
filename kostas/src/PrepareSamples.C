#include "PrepareDataForFit.C"

void PrepareSamples()
{
  const int N(23);
  TString SAMPLE[N] = {"GFPowheg115","GFPowheg120","GFPowheg125","GFPowheg130","GFPowheg135","VBFPowheg115","VBFPowheg120","VBFPowheg125","VBFPowheg130","VBFPowheg135","QCD100","QCD250","QCD500","QCD1000","ZJets","WJets","TTJets","T_s-channel","T_t-channel","T_tW-channel","Tbar_s-channel","Tbar_t-channel","Tbar_tW-channel"};
  TString SEL[2] = {"NOM","VBF"};
  
  PrepareDataForFit("MultiJetA", "NOM",false);
  PrepareDataForFit("BJetPlusXB","NOM",false);
  PrepareDataForFit("BJetPlusXC","NOM",false);
  PrepareDataForFit("BJetPlusXD","NOM",false);
  PrepareDataForFit("VBF1ParkedB","VBF",false);
  PrepareDataForFit("VBF1ParkedC","VBF",false);
  PrepareDataForFit("VBF1ParkedD","VBF",false);
  
  for(int isample=0;isample<N;isample++) {
    for(int isel=0;isel<2;isel++) {
      PrepareDataForFit(SAMPLE[isample],SEL[isel],true);
    }
  } 
   
}
