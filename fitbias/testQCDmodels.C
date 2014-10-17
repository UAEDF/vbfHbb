//STANDARD ROOT INCLUDES
#include <TROOT.h>
#include <TH1.h>
#include <TH2.h>
#include <TProfile.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TTree.h>
#include <TFile.h>
#include <TChain.h>
#include <TDirectory.h>
#include <THStack.h>
#include <TLegend.h>

//STANDARD C++ INCLUDES
#include <iostream>
#include <sstream>
#include <cstring>
#include <string>
#include <math.h> 
#include <fstream>
#include <TMath.h>

//ROOFIT INCLUDES
#include "RooRealVar.h"
#include "RooWorkspace.h"
#include "RooDataHist.h"
#include "RooGenericPdf.h"
#include "RooArgList.h"
#include "RooArgSet.h"
#include "RooBernstein.h"
#include "RooCBShape.h"
#include "RooProdPdf.h"
#include "RooAddPdf.h"
#include "RooGaussian.h"
#include "RooExponential.h"
#include "RooFitResult.h"
#include "RooPlot.h"
#include "RooHist.h"
#include "TPaveText.h"
#include "RooCustomizer.h"

using namespace std;
using namespace RooFit;

void testQCDmodels(double XMIN,double XMAX, int CAT, TString FNAME){
    RooMsgService::instance().setSilentMode(kTRUE);
    for(int i=0;i<2;i++) {
        RooMsgService::instance().setStreamStatus(i,kFALSE);
    }
    char name[1000];
    TFile *file;
    TString bestModels = "Optimal models: ";
    TString ext = "CAT";
    ext += CAT;
    
    // --------------------------
    // --  Variables to be set --
    // --------------------------
    
    bool isTransfer = false;    // Makes full model with transfer functions
    bool addHiggs = false;       // Adds Higgs contribution in fit model
    double DX=0.1;
    TString ZModelStr = "Z_model_"+ext; 
    TString TopModelStr = "Top_model_"+ext; 
    TString HModelStr = "H_model_"+ext; 
    TString ZYieldStr = "yield_ZJets_"+ext;
    TString TopYieldStr = "yield_Top_"+ext;
    TString HYieldStr = "yield_H_"+ext;
    TString fileName = FNAME; //"data_shapes_workspace_0.00_0.70_0.84_BRN5.root";
    TString workspaceName = "w";
    TString xName = "mbbReg_"+ext;
    TString outName = "altModels_" + ext + "_";
    outName += XMIN;    
    outName += "-";
    outName += XMAX;
    outName += ".root";
    
    // --------------------------

    file = TFile::Open(fileName);
    RooWorkspace *w = (RooWorkspace*)file->Get(workspaceName);
//     w->Print();
    RooRealVar *x = (RooRealVar*)w->var(xName);
    
    RooWorkspace *newWS = new RooWorkspace(workspaceName, workspaceName);
    
    vector<RooAbsPdf*> QCDmodels;
    map<TString,int> ndof;
    double NllNull=0, ndofNull=0;
    
    //------- Get data histogram --------------
    RooDataHist *dataHist = (RooDataHist*) w->obj("data_hist_"+ext);
    cout << "Retrieved RooDataHist "<< ext << endl;
//     w->Print();
    
    //----------- Make QCD models ----------------      
    sprintf(name,"QCD_Bernstein2_p0_%s", ext.Data());
    RooRealVar QCD_p0_Bernstein2(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein2_p1_%s", ext.Data());
    RooRealVar QCD_p1_Bernstein2(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein2_p2_%s", ext.Data());
    RooRealVar QCD_p2_Bernstein2(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein2_%s", ext.Data());
    RooBernstein model_bernstein2(name,name,*x,RooArgSet(QCD_p0_Bernstein2,QCD_p1_Bernstein2,QCD_p2_Bernstein2));
    QCDmodels.push_back(&model_bernstein2);
    ndof[model_bernstein2.GetName()] = 3;
    
    sprintf(name,"QCD_Bernstein3_p0_%s", ext.Data());
    RooRealVar QCD_p0_Bernstein3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein3_p1_%s", ext.Data());
    RooRealVar QCD_p1_Bernstein3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein3_p2_%s", ext.Data());
    RooRealVar QCD_p2_Bernstein3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein3_p3_%s", ext.Data());
    RooRealVar QCD_p3_Bernstein3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein3_%s", ext.Data());
    RooBernstein model_bernstein3(name,name,*x,RooArgSet(QCD_p0_Bernstein3,QCD_p1_Bernstein3,QCD_p2_Bernstein3,QCD_p3_Bernstein3));
    QCDmodels.push_back(&model_bernstein3);
    ndof[model_bernstein3.GetName()] = 4;
    
    sprintf(name,"QCD_Bernstein4_p0_%s", ext.Data());
    RooRealVar QCD_p0_Bernstein4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein4_p1_%s", ext.Data());
    RooRealVar QCD_p1_Bernstein4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein4_p2_%s", ext.Data());
    RooRealVar QCD_p2_Bernstein4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein4_p3_%s", ext.Data());
    RooRealVar QCD_p3_Bernstein4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein4_p4_%s", ext.Data());
    RooRealVar QCD_p4_Bernstein4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein4_%s", ext.Data());
    RooBernstein model_bernstein4(name,name,*x,RooArgSet(QCD_p0_Bernstein4,QCD_p1_Bernstein4,QCD_p2_Bernstein4,QCD_p3_Bernstein4,QCD_p4_Bernstein4));
    QCDmodels.push_back(&model_bernstein4);
    ndof[model_bernstein4.GetName()] = 5;
    
    sprintf(name,"QCD_Bernstein5_p0_%s", ext.Data());
    RooRealVar QCD_p0_Bernstein5(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein5_p1_%s", ext.Data());
    RooRealVar QCD_p1_Bernstein5(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein5_p2_%s", ext.Data());
    RooRealVar QCD_p2_Bernstein5(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein5_p3_%s", ext.Data());
    RooRealVar QCD_p3_Bernstein5(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein5_p4_%s", ext.Data());
    RooRealVar QCD_p4_Bernstein5(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein5_p5_%s", ext.Data());
    RooRealVar QCD_p5_Bernstein5(name,name,0.1,0,1);      
    sprintf(name,"QCD_Bernstein5_%s", ext.Data());
    RooBernstein model_bernstein5(name,name,*x,RooArgSet(QCD_p0_Bernstein5,QCD_p1_Bernstein5,QCD_p2_Bernstein5,QCD_p3_Bernstein5,QCD_p4_Bernstein5,QCD_p5_Bernstein5));
    QCDmodels.push_back(&model_bernstein5);
    ndof[model_bernstein5.GetName()] = 6;

    sprintf(name,"QCD_Bernstein6_p0_%s", ext.Data());
    RooRealVar pb0(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein6_p1_%s", ext.Data());
    RooRealVar pb1(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein6_p2_%s", ext.Data());
    RooRealVar pb2(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein6_p3_%s", ext.Data());
    RooRealVar pb3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein6_p4_%s", ext.Data());
    RooRealVar pb4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein6_p5_%s", ext.Data());
    RooRealVar pb5(name,name,0.1,0,1);      
    sprintf(name,"QCD_Bernstein6_p6_%s", ext.Data());
    RooRealVar pb6(name,name,0.1,0,1); 
    sprintf(name,"QCD_Bernstein6_%s", ext.Data());
    RooBernstein model_bernstein6(name,name,*x,RooArgSet(pb0,pb1,pb2,pb3,pb4,pb5,pb6));
    QCDmodels.push_back(&model_bernstein6);
    ndof[model_bernstein6.GetName()] = 7;
    
    sprintf(name,"QCD_Bernstein7_p0_%s", ext.Data());
    RooRealVar QCD_p0_Bernstein7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein7_p1_%s", ext.Data());
    RooRealVar QCD_p1_Bernstein7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein7_p2_%s", ext.Data());
    RooRealVar QCD_p2_Bernstein7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein7_p3_%s", ext.Data());
    RooRealVar QCD_p3_Bernstein7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein7_p4_%s", ext.Data());
    RooRealVar QCD_p4_Bernstein7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein7_p5_%s", ext.Data());
    RooRealVar QCD_p5_Bernstein7(name,name,0.1,0,1); 
    sprintf(name,"QCD_Bernstein7_p6_%s", ext.Data());
    RooRealVar QCD_p6_Bernstein7(name,name,0.1,0,1);     
    sprintf(name,"QCD_Bernstein7_p7_%s", ext.Data());
    RooRealVar QCD_p7_Bernstein7(name,name,0.1,0,1);     
    sprintf(name,"QCD_Bernstein7_%s", ext.Data());
    RooBernstein model_bernstein7(name,name,*x, RooArgSet(QCD_p0_Bernstein7,QCD_p1_Bernstein7,QCD_p2_Bernstein7,QCD_p3_Bernstein7,QCD_p4_Bernstein7,QCD_p5_Bernstein7,QCD_p6_Bernstein7,QCD_p7_Bernstein7));
    QCDmodels.push_back(&model_bernstein7);
    ndof[model_bernstein7.GetName()] = 8;	
	
    sprintf(name,"QCD_Bernstein8_p0_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p0(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p1_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p1(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p2_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p2(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p3_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p3(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p4_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p4(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p5_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p5(name,name,0.1,0,1);      
    sprintf(name,"QCD_Bernstein8_p6_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p6(name,name,0.1,0,1); 
    sprintf(name,"QCD_Bernstein8_p7_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p7(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_p8_%s", ext.Data());
    RooRealVar QCD_Bernstein8_p8(name,name,0.1,0,1);
    sprintf(name,"QCD_Bernstein8_%s", ext.Data());
    RooBernstein model_bernstein8(name,name,*x, RooArgSet(QCD_Bernstein8_p0,QCD_Bernstein8_p1,QCD_Bernstein8_p2,QCD_Bernstein8_p3,QCD_Bernstein8_p4,QCD_Bernstein8_p5, QCD_Bernstein8_p6,QCD_Bernstein8_p7,QCD_Bernstein8_p8));
    QCDmodels.push_back(&model_bernstein8);
    ndof[model_bernstein8.GetName()] = 9;
	
    sprintf(name,"QCD_expPow_p0_%s", ext.Data());
    RooRealVar QCD_p0_expPow(name,name,1,0.1,10);
    sprintf(name,"QCD_expPow_p1_%s", ext.Data());
    RooRealVar QCD_p1_expPow(name,name,0.1,0,10);
    sprintf(name,"QCD_expPow_p2_%s", ext.Data());
    RooRealVar QCD_p2_expPow(name,name,1,0,3);
    sprintf(name,"QCD_expPow_%s", ext.Data());
    RooGenericPdf model_alternate1(name,"pow(@0-30,@1)*exp(-@2*pow(@0,@3))",RooArgList(*x,QCD_p0_expPow,QCD_p1_expPow,QCD_p2_expPow));
    QCDmodels.push_back(&model_alternate1);
    ndof[model_alternate1.GetName()] = 3;
        
    sprintf(name,"QCD_expPow_ext1_p0_%s", ext.Data());
    RooRealVar QCD_p0_expPow_ext1(name,name,0.7,0.1,10);
    sprintf(name,"QCD_expPow_ext1_p1_%s", ext.Data());
    RooRealVar QCD_p1_expPow_ext1(name,name,1,0,10);
    sprintf(name,"QCD_expPow_ext1_p2_%s", ext.Data());
    RooRealVar QCD_p2_expPow_ext1(name,name,0.4,0,3);
    sprintf(name,"QCD_expPow_ext1_p3_%s", ext.Data());
    RooRealVar QCD_p3_expPow_ext1(name,name,50,5,100);
    sprintf(name,"QCD_expPow_ext1_%s", ext.Data());
    RooGenericPdf model_expPow_ext1(name,"pow(@0-@4,@1)*exp(-@2*pow(@0,@3))",
				RooArgList(*x,QCD_p0_expPow_ext1,QCD_p1_expPow_ext1,QCD_p2_expPow_ext1,QCD_p3_expPow_ext1));
    QCDmodels.push_back(&model_expPow_ext1);
    ndof[model_expPow_ext1.GetName()] = 4;
      
//             sprintf(name,"QCD_expPow_ext2_p0_%s", ext.Data());
//         RooRealVar QCD_p0_expPow_ext2(name,name,0.73,0.1,10);
//         sprintf(name,"QCD_expPow_ext2_p1_%s", ext.Data());
//         RooRealVar QCD_p1_expPow_ext2(name,name,-0.044,-1,1);
//         sprintf(name,"QCD_expPow_ext2_p2_%s", ext.Data());
//         RooRealVar QCD_p2_expPow_ext2(name,name,0.00006,-1,1);
//         sprintf(name,"QCD_expPow_ext2_p3_%s", ext.Data());
//         RooRealVar QCD_p3_expPow_ext2(name,name,42,5,100);
//         sprintf(name,"QCD_expPow_ext2_p4_%s", ext.Data());
//         RooRealVar QCD_p4_expPow_ext2(name,name,-80,-150,-10);

    sprintf(name,"QCD_expPow_ext2_p0_%s", ext.Data());
    RooRealVar QCD_p0_expPow_ext2(name,name,0.7,0.1,10);
    sprintf(name,"QCD_expPow_ext2_p1_%s", ext.Data());
    RooRealVar QCD_p1_expPow_ext2(name,name,0,-1,1);
    sprintf(name,"QCD_expPow_ext2_p2_%s", ext.Data());
    RooRealVar QCD_p2_expPow_ext2(name,name,0,-1,1);
    sprintf(name,"QCD_expPow_ext2_p3_%s", ext.Data());
    RooRealVar QCD_p3_expPow_ext2(name,name,50,5,100);
    sprintf(name,"QCD_expPow_ext2_p4_%s", ext.Data());
    RooRealVar QCD_p4_expPow_ext2(name,name,-80,-150,-10);
    sprintf(name,"QCD_expPow_ext2_%s", ext.Data());
    RooGenericPdf model_expPow_ext2(name,"pow(@0-@4,@1)*exp(@2*@0+@3*pow(@0,2)+@4)",
				    RooArgList(*x,QCD_p0_expPow_ext2,QCD_p1_expPow_ext2,QCD_p2_expPow_ext2,QCD_p3_expPow_ext2,QCD_p4_expPow_ext2));
    QCDmodels.push_back(&model_expPow_ext2);
    ndof[model_expPow_ext2.GetName()] = 5;
    
//     
    sprintf(name,"QCD_expPow_Paolo_p0_%s", ext.Data());
    RooRealVar QCD_p0_expPow_Paolo(name,name,0.1,0.01,5);
    sprintf(name,"QCD_expPow_Paolo_p1_%s", ext.Data());
    RooRealVar QCD_p1_expPow_Paolo(name,name,1,0,3);
    sprintf(name,"QCD_expPow_Paolo_p2_%s", ext.Data());
    RooRealVar QCD_p2_expPow_Paolo(name,name,0.01,0.001,1);
    sprintf(name,"QCD_expPow_Paolo_p3_%s", ext.Data());
    RooRealVar QCD_p3_expPow_Paolo(name,name,0,-0.1,0.1);
    sprintf(name,"QCD_expPow_Paolo_p4_%s", ext.Data());
    RooRealVar QCD_p4_expPow_Paolo(name,name,150,100,300);
    sprintf(name,"QCD_expPow_Paolo_%s", ext.Data());
    RooGenericPdf model_expPow_Paolo(name,"(@0-30)*(@3*@0*@0-2*@3*@4*@0+@3*@4*@4+1)*exp(-@2*pow(@0,@5))",
				    RooArgList(*x,QCD_p0_expPow_Paolo,QCD_p2_expPow_Paolo,QCD_p3_expPow_Paolo,QCD_p4_expPow_Paolo,QCD_p1_expPow_Paolo));
    QCDmodels.push_back(&model_expPow_Paolo);
    ndof[model_expPow_Paolo.GetName()] = 5;
// 	
    sprintf(name,"QCD_expPow_ext2b_p0_%s", ext.Data());
    RooRealVar QCD_p0_expPow_ext2b(name,name,0,0,10);
    sprintf(name,"QCD_expPow_ext2b_p1_%s", ext.Data());
    RooRealVar QCD_p1_expPow_ext2b(name,name,1,0,10);
    sprintf(name,"QCD_expPow_ext2b_p2_%s", ext.Data());
    RooRealVar QCD_p2_expPow_ext2b(name,name,-30,-50,50);
    sprintf(name,"QCD_expPow_ext2b_p3_%s", ext.Data());
    RooRealVar QCD_p3_expPow_ext2b(name,name,0.1,0,10);
    sprintf(name,"QCD_expPow_ext2b_p4_%s", ext.Data());
    RooRealVar QCD_p4_expPow_ext2b(name,name,1,0,3);
    sprintf(name,"QCD_expPow_ext2b_%s", ext.Data());
    RooGenericPdf model_expPow_ext2b(name,"(@1*pow(@0,2)+@2*@0+@3)*exp(-@4*pow(@0,@5))",
				RooArgList(*x,QCD_p0_expPow_ext2b,QCD_p1_expPow_ext2b,QCD_p2_expPow_ext2b,QCD_p3_expPow_ext2b,QCD_p4_expPow_ext2b));
    QCDmodels.push_back(&model_expPow_ext2b);
    ndof[model_expPow_ext2b.GetName()] = 5;


//     sprintf(name,"QCD_GaBe2_mean_%s", ext.Data());
//     RooRealVar m(name,name,120,0,500);
//     sprintf(name,"QCD_GaBe2_sigma_%s", ext.Data());
//     RooRealVar s(name,name,100,0,500);
//     sprintf(name,"QCD_ga_%s", ext.Data());
//     RooGaussian ga(name,name,*x,m,s);
//     sprintf(name,"QCD_GaBe2_p0_%s", ext.Data());
//     RooRealVar e0(name,name,0.1,0,1);
//     sprintf(name,"QCD_GaBe2_p1_%s", ext.Data());
//     RooRealVar e1(name,name,0.1,0,1);
//     sprintf(name,"QCD_GaBe2_p2_%s", ext.Data());
//     RooRealVar e2(name,name,0.1,0,1);
//     sprintf(name,"QCD_Be2_%s", ext.Data());
//     RooBernstein be2(name,name,*x,RooArgSet(e0,e1,e2));
//     sprintf(name,"QCD_GaBe2_%s", ext.Data());
//     RooProdPdf model_gabe2(name,name,RooArgSet(ga,be2));
//     QCDmodels.push_back(&model_gabe2);
//     ndof[model_gabe2.GetName()] = 5;
    
    sprintf(name,"QCD_tanh_p0_%s", ext.Data());
    RooRealVar f0(name,name,1.5,1,10);
    sprintf(name,"QCD_tanh_p1_%s", ext.Data());
    RooRealVar f1(name,name,0.01,0.001,0.1);
    sprintf(name,"QCD_tanh_p2_%s", ext.Data());
    RooRealVar f2(name,name,2,-0.1,50);
    sprintf(name,"QCD_tanh_%s", ext.Data());
    RooGenericPdf model_tanh(name,"@0 - tanh(@1*@2-@3)",RooArgList(f0,f1,*x,f2));
    QCDmodels.push_back(&model_tanh);
    ndof[model_tanh.GetName()] = 3;

    sprintf(name,"QCD_tanh_ext_p0_%s", ext.Data());
    RooRealVar f0_ext(name,name,1.5,-10,10);
    sprintf(name,"QCD_tanh_ext_p3_%s", ext.Data());
    RooRealVar f3_ext(name,name,0,-1,1);
    sprintf(name,"QCD_tanh_ext_p1_%s", ext.Data());
    RooRealVar f1_ext(name,name,0.01,0.001,0.1);
    sprintf(name,"QCD_tanh_ext_p2_%s", ext.Data());
    RooRealVar f2_ext(name,name,2,-0.1,50);
    sprintf(name,"QCD_tanh_ext_%s", ext.Data());
    RooGenericPdf model_tanh_ext(name,"@0+@4*@2 - tanh(@1*@2-@3)",RooArgList(f0_ext,f1_ext,*x,f2_ext,f3_ext));
    QCDmodels.push_back(&model_tanh_ext);
    ndof[model_tanh_ext.GetName()] = 4;
// 	
    sprintf(name,"QCD_tanh_Paolo_p0_%s", ext.Data());
    RooRealVar f0_Paolo(name,name,1,-10,10);
    sprintf(name,"QCD_tanh_Paolo_p1_%s", ext.Data());
    RooRealVar f1_Paolo(name,name,0.01,0.001,0.1);
    sprintf(name,"QCD_tanh_Paolo_p2_%s", ext.Data());
    RooRealVar f2_Paolo(name,name,1.4,-10,50);
    sprintf(name,"QCD_tanh_Paolo_p3_%s", ext.Data());
    RooRealVar f3_Paolo(name,name,0,-0.1,0.1);
    sprintf(name,"QCD_tanh_Paolo_p4_%s", ext.Data());
    RooRealVar f4_Paolo(name,name,200,100,300);
    sprintf(name,"QCD_tanh_Paolo_%s", ext.Data());
    RooGenericPdf model_tanh_Paolo(name,"@0- tanh((@1*@2-@3)*(@4*@2*@2-2*@4*@5*@2+@4*@5*@5+1))",RooArgList(f0_Paolo,f1_Paolo,*x,f2_Paolo,f3_Paolo,f4_Paolo));
    QCDmodels.push_back(&model_tanh_Paolo);
    ndof[model_tanh_Paolo.GetName()] = 5;
// // 	
    sprintf(name,"QCD_modG_p0_%s", ext.Data());
    RooRealVar h0(name,name,0.007,0.0001,0.1);
    sprintf(name,"QCD_modG_p1_%s", ext.Data());
    RooRealVar h1(name,name,0.03,0.001,10);
    sprintf(name,"QCD_modG_p2_%s", ext.Data());
    RooRealVar h2(name,name,0.007,0.0001,0.1);
    sprintf(name,"QCD_modG_%s", ext.Data());
    RooGenericPdf model_modG(name,"exp(-@0*@1) * TMath::Erfc(@2-@3*@1)",RooArgList(h0,*x,h1,h2));
    QCDmodels.push_back(&model_modG);
    ndof[model_modG.GetName()] = 3;
//         
    sprintf(name,"QCD_modG_ext_p0_%s", ext.Data());
    RooRealVar h0_ext(name,name,0.017,-0.1,0.1);
    sprintf(name,"QCD_modG_ext_p1_%s", ext.Data());
    RooRealVar h1_ext(name,name,0.5,0.001,10);
    sprintf(name,"QCD_modG_ext_p2_%s", ext.Data());
    RooRealVar h2_ext(name,name,0.01,0.0001,0.1);
    sprintf(name,"QCD_modG_ext_p3_%s", ext.Data());
    RooRealVar h3_ext(name,name,0,-0.1,0.1);
    sprintf(name,"QCD_modG_ext_%s", ext.Data());
    RooGenericPdf model_modG_ext(name,"exp(-@0*@1+@4) * TMath::Erfc(@2-@3*@1)",RooArgList(h0_ext,*x,h1_ext,h2_ext,h3_ext));
    QCDmodels.push_back(&model_modG_ext);
    ndof[model_modG_ext.GetName()] = 4;

    sprintf(name,"QCD_modG_extb_p0_%s", ext.Data());
    RooRealVar h0_extb(name,name,0.03,-0.1,0.1);
    sprintf(name,"QCD_modG_extb_p1_%s", ext.Data());
    RooRealVar h1_extb(name,name,1.2,0.001,10);
    sprintf(name,"QCD_modG_extb_p2_%s", ext.Data());
    RooRealVar h2_extb(name,name,0.024,0.0001,0.1);
    sprintf(name,"QCD_modG_extb_p3_%s", ext.Data());
    RooRealVar h3_extb(name,name,0.00004,-0.1,0.1);

// 	sprintf(name,"QCD_modG_extb_p0_%s", ext.Data());
// 	RooRealVar h0_extb(name,name,0.007,-0.1,0.1);
// 	sprintf(name,"QCD_modG_extb_p1_%s", ext.Data());
// 	RooRealVar h1_extb(name,name,0.03,0.001,10);
// 	sprintf(name,"QCD_modG_extb_p2_%s", ext.Data());
// 	RooRealVar h2_extb(name,name,0.007,0.0001,0.1);
// 	sprintf(name,"QCD_modG_extb_p3_%s", ext.Data());
// 	RooRealVar h3_extb(name,name,0,-0.1,0.1);
    sprintf(name,"QCD_modG_extb_%s", ext.Data());
    RooGenericPdf model_modG_extb(name,"exp(-@0*@1+@4*pow(@1,2)) * TMath::Erfc(@2-@3*@1)",RooArgList(h0_extb,*x,h1_extb,h2_extb,h3_extb));
    QCDmodels.push_back(&model_modG_extb);
    ndof[model_modG_extb.GetName()] = 4;
// 	
    sprintf(name,"QCD_modG_Paolo_p0_%s", ext.Data());
    RooRealVar h0_Paolo(name,name,0.017,0.001,0.1);
    sprintf(name,"QCD_modG_Paolo_p1_%s", ext.Data());
    RooRealVar h1_Paolo(name,name,0.5,0.1,5);
    sprintf(name,"QCD_modG_Paolo_p2_%s", ext.Data());
    RooRealVar h2_Paolo(name,name,0.01,0.002,0.1);
    sprintf(name,"QCD_modG_Paolo_p3_%s", ext.Data());
    RooRealVar h3_Paolo(name,name,0.001,-0.01,0.01);
    sprintf(name,"QCD_modG_Paolo_p4_%s", ext.Data());
    RooRealVar h4_Paolo(name,name,150,20,250);
    sprintf(name,"QCD_modG_Paolo_%s", ext.Data());
    RooGenericPdf model_modG_Paolo(name, "exp(-@0*@1) * TMath::Erfc((@2-@3*@1)*(@4*@1*@1-2*@4*@5*@1+@4*@5*@5+1))", RooArgList(h0_Paolo,*x,h1_Paolo,h2_Paolo,h3_Paolo,h4_Paolo));
    QCDmodels.push_back(&model_modG_Paolo);
    ndof[model_modG_Paolo.GetName()] = 5;
    
    sprintf(name,"QCD_modG_extc_p0_%s", ext.Data());
    RooRealVar h0_extc(name,name,0.007,-0.1,0.1);
    sprintf(name,"QCD_modG_extc_p1_%s", ext.Data());
    RooRealVar h1_extc(name,name,0.03,0.001,10);
    sprintf(name,"QCD_modG_extc_p2_%s", ext.Data());
    RooRealVar h2_extc(name,name,0.007,0.0001,0.1);
    sprintf(name,"QCD_modG_extc_p3_%s", ext.Data());
    RooRealVar h3_extc(name,name,0,-0.1,0.1);
    sprintf(name,"QCD_modG_extc_%s", ext.Data());
    RooGenericPdf model_modG_extc(name,"exp(-@0*@1) * TMath::Erfc(@2-@3*@1+@4*pow(@1,2))",RooArgList(h0_extc,*x,h1_extc,h2_extc,h3_extc));
    QCDmodels.push_back(&model_modG_extc);
    ndof[model_modG_extc.GetName()] = 4;
    
    RooRealVar QCD_erfPow_0("QCD_erfPow_0_"+ext,"QCD_erfPow_0_"+ext,30,0,60);
    RooRealVar QCD_erfPow_1("QCD_erfPow_1_"+ext,"QCD_erfPow_1_"+ext,10,-50,50);
    RooRealVar QCD_erfPow_2("QCD_erfPow_2_"+ext,"QCD_erfPow_2_"+ext,1,-10,10);
    RooRealVar QCD_erfPow_3("QCD_erfPow_3_"+ext,"QCD_erfPow_3_"+ext,1,-10,10);
    RooGenericPdf model_erfPow("QCD_erfPow_"+ext,"TMath::Erf((@0-@1)/@2)*pow(@0,-@3-@4*log(@0/8000))",RooArgList(*x,QCD_erfPow_0,QCD_erfPow_1,QCD_erfPow_2,QCD_erfPow_3));
    QCDmodels.push_back(&model_erfPow);
    ndof[model_erfPow.GetName()] = 4;
    
    RooRealVar QCD_erfPol_0("QCD_erfPol_0_"+ext,"QCD_erfPol_0_"+ext,30,0,60);
    RooRealVar QCD_erfPol_1("QCD_erfPol_1_"+ext,"QCD_erfPol_1_"+ext,10,-50,50);
    RooRealVar QCD_erfPol_2("QCD_erfPol_2_"+ext,"QCD_erfPol_2_"+ext,-0.005,-0.01,0.01);
    RooRealVar QCD_erfPol_3("QCD_erfPol_3_"+ext,"QCD_erfPol_3_"+ext,-1,-5,5);
    RooRealVar QCD_erfPol_4("QCD_erfPol_4_"+ext,"QCD_erfPol_4_"+ext,500,0,2e+3);
    RooGenericPdf model_erfPol("QCD_erfPol_"+ext,"TMath::Erf((@0-@1)/@2)*(@3*pow(@0,2)+@4*@0+@5)", RooArgList(*x,QCD_erfPol_0,QCD_erfPol_1,QCD_erfPol_2,QCD_erfPol_3,QCD_erfPol_4));
    QCDmodels.push_back(&model_erfPol);
    ndof[model_erfPol.GetName()] = 5;
    
    RooRealVar QCD_tanhPol_0("QCD_tanhPol_0_"+ext,"QCD_tanhPol_0_"+ext,0.15,0.01,1);
    RooRealVar QCD_tanhPol_1("QCD_tanhPol_1_"+ext,"QCD_tanhPol_1_"+ext,53,40,65);
    RooRealVar QCD_tanhPol_2("QCD_tanhPol_2_"+ext,"QCD_tanhPol_2_"+ext,-0.005,-0.01,0.01);
    RooRealVar QCD_tanhPol_3("QCD_tanhPol_3_"+ext,"QCD_tanhPol_3_"+ext,-1,-5,5);
    RooRealVar QCD_tanhPol_4("QCD_tanhPol_4_"+ext,"QCD_tanhPol_4_"+ext,500,0,2e+3);
    RooGenericPdf model_tanhPol("QCD_tanhPol_"+ext,"tanh(@1*(@0-@2))*(@3*pow(@0,2)+@4*@0+@5)", RooArgList(*x,QCD_tanhPol_0,QCD_tanhPol_1,QCD_tanhPol_2,QCD_tanhPol_3,QCD_tanhPol_4));
    QCDmodels.push_back(&model_tanhPol);
    ndof[model_tanhPol.GetName()] = 5;
//     
    //---------- Make Building blocks new models ----------
    const int totOrder = 4;
    RooRealVar *expPar[totOrder], *powPar[totOrder], *sinPar[2*totOrder];
    RooExponential *expPdf[totOrder];
    RooGenericPdf *powPdf[totOrder];
    RooGenericPdf *sinPdf[totOrder];
    
    for( int iOrder = 1; iOrder < totOrder+1; iOrder++) {
        sprintf(name,"QCD_exp_p0_order%d_%s", iOrder, ext.Data());
        expPar[iOrder-1] = new RooRealVar(name,name,0,-1,1);
        sprintf(name,"QCD_exp_order%d_%s", iOrder, ext.Data());
        expPdf[iOrder-1] = new RooExponential(name,name,*x,*expPar[iOrder-1]);
        
        sprintf(name,"QCD_pow_p0_order%d_%s", iOrder, ext.Data());
        powPar[iOrder-1] = new RooRealVar(name,name,0,-1,1);
        sprintf(name,"QCD_pow_order%d_%s", iOrder, ext.Data());
        powPdf[iOrder-1] = new RooGenericPdf(name,name,"pow(@0,@1)",RooArgList(*x,*powPar[iOrder-1]));
    }
    
    QCDmodels.push_back(expPdf[0]);
    QCDmodels.push_back(powPdf[0]);
    ndof[expPdf[0]->GetName()] = 1;
    ndof[powPdf[0]->GetName()] = 1;
    
    
    sprintf(name,"QCD_sin_phase_order%d_%s", 1, ext.Data());
    sinPar[0] = new RooRealVar(name,name,0,-3.14,3.14);
    sprintf(name,"norm_sin_order%d_%s", 1, ext.Data());
    sinPar[1] = new RooRealVar(name,name,0.4,0.01,1);
    sprintf(name,"QCD_sin_phase_order%d_%s", 2, ext.Data());
    sinPar[2] = new RooRealVar(name,name,0,-3.14,3.14);
    sprintf(name,"norm_sin_order%d_%s", 2, ext.Data());
    sinPar[3] = new RooRealVar(name,name,0.4,0.01,1);
    
    sprintf(name,"QCD_sin_freq_order%d_%s", 1, ext.Data());
    RooRealVar *sinFreqpar = new RooRealVar(name,name,0.017,0.005,0.05);
    sprintf(name,"QCD_sin_order%d_%s", 1, ext.Data());
    sinPdf[0] = new RooGenericPdf(name,name,"1+@2*sin(@0*@3+@1)",RooArgList(*x,*sinPar[0],*sinPar[1],*sinFreqpar));
        QCDmodels.push_back(sinPdf[0]);
    ndof[sinPdf[0]->GetName()] = 3;
    sprintf(name,"QCD_sin_order%d_%s", 2, ext.Data());
    sinPdf[1] = new RooGenericPdf(name,name,"1+@2*sin(@0*@3+@1)+@5*sin(@0*@3*2+@4)",RooArgList(*x,*sinPar[0],*sinPar[1],*sinFreqpar,*sinPar[2],*sinPar[3]));
    QCDmodels.push_back(sinPdf[1]);
    ndof[sinPdf[1]->GetName()] = 5;
    
    //---------- Build models ----------------
        RooAddPdf *totExpPdf[totOrder-1];
        RooAddPdf *totPowPdf[totOrder-1];
        RooRealVar *normExpPar[totOrder-1], *normPowPar[totOrder-1];
        
        for( int iOrder = 1; iOrder < totOrder; iOrder++) {
    	sprintf(name,"norm_exp_order%d_%s", iOrder, ext.Data());
    	normExpPar[iOrder-1] = new RooRealVar(name,name,0.2,0,1);
    	sprintf(name,"norm_pow_order%d_%s", iOrder, ext.Data());
    	normPowPar[iOrder-1] = new RooRealVar(name,name,0.2,0,1); //will go crazy if they are allowed to be negative
        }
        
        sprintf(name,"QCD_TotExp_order%d_%s", 2, ext.Data());	 //can't use loop without correlating parameters
        totExpPdf[0] = new RooAddPdf(name,name,*expPdf[0], *expPdf[1],*normExpPar[0]);
        QCDmodels.push_back(totExpPdf[0]);
        ndof[totExpPdf[0]->GetName()] = 3;
        sprintf(name,"QCD_TotExp_order%d_%s", 3, ext.Data());
        totExpPdf[1] = new RooAddPdf(name,name,RooArgList(*expPdf[0],*expPdf[1],*expPdf[2]),RooArgList(*normExpPar[0],*normExpPar[1]));
        QCDmodels.push_back(totExpPdf[1]);
        ndof[totExpPdf[1]->GetName()] = 5;
        sprintf(name,"QCD_TotExp_order%d_%s", 4, ext.Data());
        totExpPdf[2] = new RooAddPdf(name,name,RooArgList(*expPdf[0],*expPdf[1],*expPdf[2],*expPdf[3]),RooArgList(*normExpPar[0],*normExpPar[1],*normExpPar[2]));
        QCDmodels.push_back(totExpPdf[2]);
        ndof[totExpPdf[2]->GetName()] = 7;
//         sprintf(name,"QCD_TotExp_order%d_%s", 4, ext.Data());
//         RooGenericPdf *newTotExpPdf = new RooGenericPdf(name,name, "@1*exp(@2*@0)+@3*exp(@4*@0)+@5*exp(@6*@0)+(1-@1-@3-@5)*exp(@7*@0)", RooArgList(*x, *normExpPar[0], *expPar[0],*normExpPar[1],*expPar[1],*normExpPar[2],*expPar[2],*expPar[3]));
//         QCDmodels.push_back(newTotExpPdf);
//         ndof[newTotExpPdf->GetName()] = 7;
        
        sprintf(name,"QCD_TotPow_order%d_%s", 2, ext.Data());
        totPowPdf[0] = new RooAddPdf(name,name,*powPdf[0], *powPdf[1],*normPowPar[0]);
        QCDmodels.push_back(totPowPdf[0]);
        ndof[totPowPdf[0]->GetName()] = 3;
        sprintf(name,"QCD_TotPow_order%d_%s", 3, ext.Data());
        totPowPdf[1] = new RooAddPdf(name,name,RooArgList(*powPdf[0],*powPdf[1],*powPdf[2]),RooArgList(*normPowPar[0],*normPowPar[1]));
        QCDmodels.push_back(totPowPdf[1]);
        ndof[totPowPdf[1]->GetName()] = 5;
	sprintf(name,"QCD_TotPow_order%d_%s", 4, ext.Data());
        totPowPdf[2] = new RooAddPdf(name,name,RooArgList(*powPdf[0],*powPdf[1],*powPdf[2],*powPdf[3]),RooArgList(*normPowPar[0],*normPowPar[1],*normPowPar[2]));
        QCDmodels.push_back(totPowPdf[2]);
        ndof[totPowPdf[2]->GetName()] = 7;
    
//     if( wsModels ) QCDmodels.clear();
//     wFixed->Print();
    RooAbsPdf *ZPdf = (RooAbsPdf*) w->obj(ZModelStr); 
    RooAbsPdf *topPdf = (RooAbsPdf*) w->obj(TopModelStr); 
    RooRealVar *nZ = (RooRealVar*)w->var(ZYieldStr);
    RooRealVar *nT = (RooRealVar*)w->var(TopYieldStr);
    nZ->setConstant(kTRUE);
    nT->setConstant(kTRUE);
    
    RooAbsPdf *HPdf;
    RooRealVar *nH;
    if( addHiggs) {
        HPdf = (RooAbsPdf*) w->obj(HModelStr); 
        nH = (RooRealVar*)w->var(HYieldStr);
        nH->setConstant(kTRUE);
    }

    double QCD_appr = dataHist->sum(kFALSE)-nZ->getVal()-nT->getVal();
    RooRealVar nQCD("yield_QCD_"+ext,"yield_QCD_"+ext,QCD_appr, 0.5*QCD_appr, 2*QCD_appr);
    
    double chiBern=-1;
    for(vector<RooAbsPdf*>::iterator iModel = QCDmodels.begin(); iModel != QCDmodels.end(); ++iModel) {
		RooAddPdf *totModel;
        if( addHiggs) totModel = new RooAddPdf("totModel","totModel", RooArgList(*HPdf, *ZPdf, *topPdf, *(*iModel)),RooArgList(*nH,*nZ,*nT,nQCD));
        else totModel = new RooAddPdf("totModel","totModel", RooArgList(*ZPdf, *topPdf, *(*iModel)),RooArgList(*nZ,*nT,nQCD));
	// 	RooFitResult* fitResult = (*iModel)->fitTo(*dataHist,RooFit::Save());
		RooFitResult* fitResult = totModel->fitTo(*dataHist,RooFit::Save());
	// 	x->setRange("ZWindow",95.3 - 2*10.6, 95.3 + 2*10.6);
	// 	RooAbsReal* QCD_integral = (*iModel)->createIntegral(*x, NormSet(*x), Range("ZWindow"));
	// 	RooAbsReal* Z_integral = ZPdf->createIntegral(*x, NormSet(*x), Range("ZWindow"));
	// 	cout << "S/B (2 sigma): " << Z_integral->getVal() * expZ/ QCD_integral->getVal() / dataHist->sum(kFALSE) << endl;
	// 	cout << "S (2 sigma): " << Z_integral->getVal() * expZ << endl;
	// 	cout << "B (2 sigma): " << QCD_integral->getVal() * dataHist->sum(kFALSE) << endl;
		if( strstr((*iModel)->GetName(),"xp_order")  == NULL || strstr((*iModel)->GetName(),"TotExp_order4")  != NULL) {
			newWS->import(*(*iModel));
		}
		
		TCanvas *Datacan = new TCanvas((*iModel)->GetName(),(*iModel)->GetName(),600,600);
		RooPlot* Dataframe = x->frame();
		dataHist->plotOn(Dataframe,Name("data"),DataError(RooAbsData::SumW2));
		totModel->plotOn(Dataframe,RooFit::LineWidth(2),LineColor(kBlue),Name("model"));
// 		totModel->plotOn(Dataframe,Components(RooArgSet(*ZPdf)),LineColor(kBlue),LineStyle(kDashed));
// 		totModel->plotOn(Dataframe,Components(RooArgSet(*topPdf)),LineColor(kRed),LineStyle(kDashed));
	// 	    (*iModel)->plotOn(Dataframe,RooFit::VisualizeError(*res,2,kTRUE),RooFit::FillColor(kGreen),RooFit::MoveToBack());
	// 	    (*iModel)->plotOn(Dataframe,RooFit::VisualizeError(*res,1,kTRUE),RooFit::FillColor(kYellow));
		
		RooHist* resid = Dataframe->residHist( "data","model"/*, true*/);
		double xVal = 0,y=0, squaredSum=0, squaredSumPoisson=0;
		int yield = 0;	
	// 	double maxContribution=0;
		for( int i=0; i<resid->GetN(); i++) {
			resid->GetPoint(i,xVal,y);
			dataHist->get(i/*+(mbbCut-75)*2-1*/);
			double error = dataHist->weightError(RooAbsData::SumW2);
			double lo, hi, errorPoisson;
			dataHist->weightError(lo,hi);		
	// 	    if( i < 5) cout << "data: " << dataHist->weight() << ", error: " << error<< " y: " << y<< endl;
	// 	    if( y*y/(error*error) > maxContribution ) maxContribution = y*y/(error*error);
			if( y >= 0 )  errorPoisson = lo;
			else errorPoisson = hi;
			if( error != 0 ) {
			squaredSum += y*y/(error*error);
			squaredSumPoisson += y*y/(errorPoisson*errorPoisson);
			}
			yield += dataHist->weight();
	//     		cout << "Verschil: " << y << " +- " << error << endl;
	//     		cout << "squared sum: " << squaredSum << endl;
		}
	// 	cout << "Maximum contribution: " << maxContribution << endl;
	// 	cout << resid->GetN() << " should be equal to " << dataHist->numEntries() << endl;
	// 	cout << "yield: " << yield << endl;
		RooPlot* Dataframe2 = x->frame();
		Dataframe2->addPlotable(resid,"P");
		Datacan->cd();
		Dataframe2->Draw();
		
		double Nll = fitResult->minNll();
		int nBins = (int)((XMAX-XMIN)/DX);
		double prob = TMath::Prob(squaredSum, (nBins-ndof[(*iModel)->GetName()]));
		bool newModel=false;
		if( strstr((*iModel)->GetName(),"QCD_Bernstein")  != NULL || strstr((*iModel)->GetName(),"QCD_expPow_CAT")  != NULL 
		||  strstr((*iModel)->GetName(),"QCD_modG_CAT")  != NULL  ||  strstr((*iModel)->GetName(),"QCD_tanh_CAT")  != NULL
		||  strstr((*iModel)->GetName(),"QCD_sin_order1")  != NULL ||  strstr((*iModel)->GetName(),"erfPow")  != NULL 
        ||  strstr((*iModel)->GetName(),"tanhPol")  != NULL ) newModel = true;
		
		//Output fit results
		fitResult->Print();
		//cout << "Model name: " << (*iModel)->GetName() << "	" << endl 
		//<< "minimized -log(L): " << Nll << endl
		//<< "Probability NLL: "; 
		double probNll;
		if( (NllNull-Nll)>0)
			probNll = TMath::Prob(2*(NllNull-Nll), ndof[(*iModel)->GetName()] - ndofNull);
		else
			probNll = 1;
		cout << "probNll: " << probNll << endl;
// 		cout << "Chi2: " << squaredSum << endl 
		<< "Reduced chi2: " << (squaredSum/(nBins-ndof[(*iModel)->GetName()])) << "	" << (squaredSumPoisson/(nBins-ndof[(*iModel)->GetName()])) << " (Poisson)" << endl;
		//cout << "chi2/chi2_Bern6: " << (squaredSum/(nBins-ndof[(*iModel)->GetName()])/chiBern) << endl
		<< "Probability chi squared:: " << prob << "	" << TMath::Prob(squaredSumPoisson, (nBins-ndof[(*iModel)->GetName()])) << " (Poisson)" << endl
		<< "------------------------------------------------------------" << endl;	
		if( newModel ) {
			NllNull = Nll;
			ndofNull = ndof[(*iModel)->GetName()];
		}
		if( probNll < 0.05) {
			bestModels += (*iModel)->GetName();
			bestModels += "	";
		}
		sprintf(name,"red chi2: %.2f, Prob (chi^2): %.2f", squaredSum/(nBins-ndof[(*iModel)->GetName()]), prob);
		if( strstr((*iModel)->GetName(),"QCD_Bernstein6")  != NULL )
			chiBern = squaredSum/(nBins-ndof[(*iModel)->GetName()]);
		
		if( strstr((*iModel)->GetName(),"QCD_Bernstein4") != NULL) sprintf(name,"4^{th} order Bernstein polynomial");
		if( strstr((*iModel)->GetName(),"QCD_Bernstein5") != NULL) sprintf(name,"5^{th} order Bernstein polynomial");
		if( strstr((*iModel)->GetName(),"QCD_expPow")  != NULL) sprintf(name,"expPow");
		if( strstr((*iModel)->GetName(),"QCD_modG")  != NULL) sprintf(name,"modG");
		if( strstr((*iModel)->GetName(),"QCD_tanh")  != NULL) sprintf(name,"tanh");
		if( strstr((*iModel)->GetName(),"QCD_sin_order1")  != NULL) sprintf(name,"sine");
		
		Dataframe->SetTitle(name);
		Dataframe->SetXTitle("M_{bb} (GeV)");
		Dataframe->SetTitleOffset(1.7,"Y");
		gPad->SetLeftMargin(0.13);
		Datacan->cd();
		Dataframe->Draw();
		TPaveText *pt = new TPaveText(.6,.6,.85,.85, "NDC");
		pt->SetFillColor(0); 
		pt->SetBorderSize(0); 
		sprintf(name,"reduced #Chi^{2}: %.2f", squaredSum/(nBins-ndof[(*iModel)->GetName()]));
		pt->AddText(name);
		sprintf(name,"Probability: %.2f", prob);
		pt->AddText(name);
		pt->Draw();
		
	// 	Datacan->Print("plots/" + ext+(*iModel)->GetName()+ ".png","png");
			
		//Build other CAT models
        if( isTransfer )
        {
            if( strstr((*iModel)->GetName(),"xp_")  == NULL || strstr((*iModel)->GetName(),"TotExp_order4")  != NULL )  {
                int lastCat;
                if(CAT == 0) lastCat = 3;
                else lastCat = 6;

                for( int iCat = CAT+1; iCat <=lastCat; ++iCat) {
                    TString iCatString = "CAT";
                    iCatString += iCat;
                    
                    RooRealVar *x_CATx = new  RooRealVar(*x,"mbbReg_"+iCatString);
                    RooAbsPdf* transfer = (RooAbsPdf*) w->obj("transfer_"+iCatString);
                    TString baseName = (*iModel)->GetName();
                    baseName.Remove(baseName.Length()-1);
                    baseName += iCat;
                    RooAbsPdf* transferTemp = (RooAbsPdf*) transfer->Clone("transfer_"+baseName);
                    RooAbsPdf* qcdTemp;
                    
                    if( strstr((*iModel)->GetName(),"TotExp_order4")  != NULL ) {
                        RooExponential *expTemp1 = (RooExponential*) expPdf[0]->Clone("QCD_exp_order1_"+iCatString);
                        RooExponential *expTemp2 = (RooExponential*) expPdf[1]->Clone("QCD_exp_order2_"+iCatString);
                        RooExponential *expTemp3 = (RooExponential*) expPdf[2]->Clone("QCD_exp_order3_"+iCatString);
                        RooExponential *expTemp4 = (RooExponential*) expPdf[3]->Clone("QCD_exp_order4_"+iCatString);
                        
                        qcdTemp = new RooAddPdf(baseName+"_aux",baseName+"_aux", RooArgList(*expTemp1, *expTemp2,*expTemp3, *expTemp4), RooArgList(*normExpPar[0],*normExpPar[1],*normExpPar[2]));
                    }
                    else qcdTemp = (RooAbsPdf*) (*iModel)->Clone(baseName+"_aux");
                    
                    RooCustomizer* cust = new RooCustomizer(*qcdTemp, "corr");
                    cust->replaceArg(*x, *x_CATx);
                    RooAbsPdf* new_qcdTemp = (RooAbsPdf*) cust->build(); 
                    RooCustomizer* cust2 = new RooCustomizer(*transferTemp, "test_transfer");
                    cust2->replaceArg(*x, *x_CATx);
                    RooAbsPdf* new_transferTemp = (RooAbsPdf*) cust2->build(); 
                    
                    RooProdPdf *model_CATx = new RooProdPdf(baseName, baseName, *new_transferTemp, *new_qcdTemp);
                    model_CATx->Print();
                    newWS->import(*model_CATx);
                }
            }
        }
	}// end loop over QCD models

    cout << bestModels << endl;
    newWS->writeToFile(outName);
}
