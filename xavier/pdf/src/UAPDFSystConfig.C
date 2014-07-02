#include "UAPDFSystConfig.h"

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
using namespace std;

// ---------------------- TOOLS ------------------------------------

vector<string> UATokenize(string input , char token){
  stringstream ssinput(input);
  string Element;
  vector<string> Elements;
  while (getline(ssinput, Element , token )) {
   Elements.push_back(Element);
  }
  return Elements;
}

// ---------------------- ReadCfg() --------------------------------

void UAPDFSystConfig::ReadCfg(string& ConFile){

  //InDir  = "/Users/xjanssen/cms/HWW2012/LatinoTrees2012/R53X_S1_V08_S2_V09_S3_V13/ReducedTrees_4L_WW_MoriondeffWPuWtriggW/";
  //InDir = "/Users/xjanssen/cms/HWW2012/LatinoTrees2012/R53X_S1_V08_S2_V09_S3_V13/MC_TightTight/4L_MoriondeffWPuWtriggW/";
  InDir  = "WWXsection/";
  OutDir = "testDir/";

  InputData_t Data;
  Data.NickName = "ggH125";
  Data.TreeName = "latino";
  Data.bFixScale         = true;
  Data.QScale.NickName   = "q-scale" ; 
  //Data.QScale.Expression = "MHiggs" ; 
  //Data.QScale.Expression = "sqrt(MHiggs*MHiggs+pdfscalePDF*pdfscalePDF)" ; 
  Data.QScale.Expression = "pdfscalePDF" ; 
  
  Data.bFixPDF  = true ;
//  Data.RefPDF   = "cteq66.LHgrid";
  Data.RefPDF   = "CT10nlo.LHgrid";

//  Data.FileName = "R53X_S1_V08_S2_V09_S3_v13_Pub2012_ggH125_WWsel.root";
//  InputData.push_back(Data);

//  Data.NickName = "ggH160";
//  Data.FileName = "R53X_S1_V08_S2_V09_S3_v13_Pub2012_ggH160_WWsel.root";

/*
  Data.NickName = "ggH125";  
  Data.FileName = "latino_1125_ggToH125toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "ggH160";  
  Data.FileName = "latino_1160_ggToH160toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "ggH350";  
  Data.FileName = "latino_1350_ggToH350toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "ggH500";  
  Data.FileName = "latino_1500_ggToH500toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "vbfH125";  
  Data.FileName = "latino_2125_vbfToH125toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "vbfH160";  
  Data.FileName = "latino_2160_vbfToH160toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "vbfH350";  
  Data.FileName = "latino_2350_vbfToH350toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);

  Data.NickName = "vbfH500";  
  Data.FileName = "latino_2500_vbfToH500toWWTo2LAndTau2Nu.root";
  InputData.push_back(Data);
*/

  
  Data.NickName = "WWJets2LPowheg";  
  Data.FileName = "latino_006_WWJets2LPowheg.root" ;
  InputData.push_back(Data);


  PreSel.Expression = "ch1*ch2==-1&&trigger==1&&pt1>20&&pt2>10";

  BaseSel.NickName   = "BaseSel" ;
  BaseSel.Expression = "ch1*ch2==-1&&trigger==1&&pt1>20&&pt2>10&&nextra==0&&pfmet>20.&&mll>12&&(zveto==1||!sameflav)&&mpmet>20.&&(!sameflav||((njet!=0||dymva1>0.88)&&(njet!=1||dymva1>0.84)&&(njet==0||njet==1||(pfmet>45.0))))&&(njet==0||njet==1||(dphilljetjet<pi/180.*165.||!sameflav))&&bveto_mu==1&&(bveto_ip==1&&nbjettche==0)&&ptll>30."; 

  BaseSel.Expression = "ch1*ch2==-1&&trigger==1&&pt1>20&&pt2>20&&nextra==0&&pfmet>20.&&mll>12&&(zveto==1||!sameflav)&&mpmet>20.&&(!sameflav||((njet!=0||dymva1>0.88)&&(njet!=1||dymva1>0.84)&&(njet==0||njet==1||(pfmet>45.0))))&&(njet==0||njet==1||(dphilljetjet<pi/180.*165.||!sameflav))&&bveto_mu==1&&(bveto_ip==1&&nbjettche==0)&&ptll>30.&&(!sameflav||ptll>45)";


  BaseWght.NickName   = "BaseWght" ;
  BaseWght.Expression   = "puW*baseW*effW*triggW";
  //BaseWght.Expression = "puW*baseW*effW*triggW"; 

  BaseLumi       =  1000. ;
  TargetLumi     = 19468. ;

  id1.NickName   = "id1" ;
  id1.Expression = "pdfid1" ;
  
  id2.NickName   = "id2" ;
  id2.Expression = "pdfid2" ;

  x1.NickName    = "x1" ;
  x1.Expression  = "pdfx1" ;

  x2.NickName    = "x2" ;
  x2.Expression  = "pdfx2" ;

  Q.NickName     = "Q" ;
  Q.Expression   = "pdfscalePDF" ;

  pdf1.NickName  = "pdf1" ;
  pdf1.Expression= "pdfx1PDF" ;

  pdf2.NickName  = "pdf2" ;
  pdf2.Expression= "pdfx2PDF" ;

//  PDFsets.push_back("cteq66.LHgrid");
  PDFsets.push_back("CT10nlo.LHgrid");
  PDFsets.push_back("MSTW2008nlo68cl.LHgrid");
  PDFsets.push_back("NNPDF23_nlo_as_0118.LHgrid");

  SystAna.push_back(UAPDFSystAna("WWsel","1."));
  SystAna.push_back(UAPDFSystAna("all_0jet","njet==0"));
  SystAna.push_back(UAPDFSystAna("all_1jet","njet==1"));
  SystAna.push_back(UAPDFSystAna("sf_0jet","njet==0&&sameflav"));
  SystAna.push_back(UAPDFSystAna("sf_1jet","njet==1&&sameflav"));
  SystAna.push_back(UAPDFSystAna("df_0jet","njet==0&&!sameflav"));
  SystAna.push_back(UAPDFSystAna("df_1jet","njet==1&&!sameflav"));



//  SystAna.push_back(UAPDFSystAna("all_2jet","njet==2"));


/*
  InDir  = "/Users/xjanssen/cms/HWW2012/UAPDFSyst/vbfHHbb/";
  OutDir = "testDir/";

  InputData_t Data;
  Data.NickName = "vbfHbb125";
  Data.TreeName = "Hbb/events";
  Data.bFixScale         = true;
  Data.QScale.NickName   = "q-scale" ; 
  //Data.QScale.Expression = "MHiggs" ; 
  Data.QScale.Expression = "Qscale" ; 
  //Data.QScale.Expression = "sqrt(125*125+Qscale*Qscale)" ; 
  Data.bFixPDF  = true ;
  Data.RefPDF   = "cteq66.LHgrid";
  Data.RefPDF   = "MSTW2008nlo90cl.LHgrid";

  Data.FileName = "flatTree_vbfPowheg_M125_CTEQ66_tmva.root";
  Data.FileName = "flatTree_vbfPowheg_M125_MSTW2008_tmva.root";
  InputData.push_back(Data);

  BaseSel.Expression = "(triggerResult[5]||triggerResult[7])&&(jetPt[0]>85&&jetPt[1]>70&&jetPt[2]>60&&jetPt[3]>40&&mqq>300&&abs(dEtaqq)>2.5 && puId[0]==1)&&(abs(dPhibb)<2.0)";
//  BaseSel.Expression = "(jetPt[0]>85&&jetPt[1]>70&&jetPt[2]>60&&jetPt[3]>40&&mqq>300&&abs(dEtaqq)>2.5 && puId[0]==1)&&(abs(dPhibb)<2.0)";

  BaseWght.NickName   = "BaseWght" ;
  BaseWght.Expression = "1."; 

  BaseLumi       = 1. ;
  TargetLumi     = 1. ;

  id1.NickName   = "id1" ;
  id1.Expression = "id1" ;
  
  id2.NickName   = "id2" ;
  id2.Expression = "id2" ;

  x1.NickName    = "x1" ;
  x1.Expression  = "x1" ;

  x2.NickName    = "x2" ;
  x2.Expression  = "x2" ;

  Q.NickName     = "Q" ;
  Q.Expression   = "Qscale" ;

  pdf1.NickName  = "pdf1" ;
  pdf1.Expression= "xpdf1" ;

  pdf2.NickName  = "pdf2" ;
  pdf2.Expression= "xpdf2" ;

  PDFsets.push_back("cteq66.LHgrid");
//  PDFsets.push_back("CT10nlo.LHgrid");
  PDFsets.push_back("MSTW2008nlo68cl.LHgrid");
  PDFsets.push_back("MSTW2008nlo90cl.LHgrid");
//  PDFsets.push_back("NNPDF23_nlo_as_0118.LHgrid");

  SystAna.push_back(UAPDFSystAna("Presel","1."));
  SystAna.push_back(UAPDFSystAna("CAT0","MLP < 0.54"));
  SystAna.push_back(UAPDFSystAna("CAT1","MLP >= 0.54 && MLP < 0.78"));
  SystAna.push_back(UAPDFSystAna("CAT2","MLP >= 0.78 && MLP < 0.90"));
  SystAna.push_back(UAPDFSystAna("CAT3","MLP >= 0.90 && MLP < 0.94"));
  SystAna.push_back(UAPDFSystAna("CAT4","MLP >= 0.94"));
*/

}


