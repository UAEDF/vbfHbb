#include <iostream>
#include <string.h>
#include <fstream>
#include <iomanip>
#include "Settings.h"

void FitData(TString MASS_VAR, int BRN_ORDER)
{
  gROOT->ForceStyle();
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  char name[1000];
  const int NCAT(5);
  double TRIG_SF_AVE = 0.85;
  double TRIG_SF[5][NCAT] = {
      {0.830,0.844,0.850,0.852,0.849},
      {0.832,0.845,0.851,0.854,0.847},
      {0.832,0.845,0.851,0.855,0.846},
      {0.831,0.844,0.850,0.854,0.846},
      {0.831,0.845,0.851,0.853,0.845} 
  };
  TString PATH("/afs/cern.ch/work/k/kkousour/private/data/vbfhbb/");

  TFile *fdat = TFile::Open(PATH+"flatTree_data_preselect_hard_PAPER_tmva_fit.root");
  TTree *tdat[NCAT];
  
  TFile *fzj = TFile::Open(PATH+"flatTree_ZJets_preselect_hard_PAPER_tmva.root");
  TTree *tzj = (TTree*)fzj->Get("Hbb/events");

  TFile *fwj = TFile::Open(PATH+"flatTree_WJets_preselect_hard_PAPER_tmva.root");
  TTree *twj = (TTree*)fwj->Get("Hbb/events");
  
  TFile *fttj = TFile::Open(PATH+"flatTree_TTJets_preselect_hard_PAPER_tmva.root");
  TTree *tttj = (TTree*)fttj->Get("Hbb/events");
  
  TFile *ft = TFile::Open(PATH+"flatTree_T_preselect_hard_PAPER_tmva.root");
  TTree *tt = (TTree*)ft->Get("Hbb/events");
  
  TFile *ftbar = TFile::Open(PATH+"flatTree_Tbar_preselect_hard_PAPER_tmva.root");
  TTree *ttbar = (TTree*)ftbar->Get("Hbb/events");
  
  TFile *fgluglu = TFile::Open(PATH+"flatTree_GluGlu-Powheg125_preselect_hard_PAPER_tmva.root");
  TTree *tgluglu = (TTree*)fgluglu->Get("Hbb/events");
  
  TFile *fZTemplates = TFile::Open("Z_"+MASS_VAR+"_shapes_hard_PAPER_workspace.root");
  RooWorkspace *wZ = (RooWorkspace*)fZTemplates->Get("w");

  TFile *fTopTemplates = TFile::Open("Top_"+MASS_VAR+"_shapes_hard_PAPER_workspace.root");
  RooWorkspace *wT = (RooWorkspace*)fTopTemplates->Get("w");

  double XMIN = 70;
  double XMAX = 250;
  if (MASS_VAR == "mbbParton" || MASS_VAR == "mbbParton2") {
    XMIN = 75;
    XMAX = 255;
  }
  double dX   = 0.5;
  int NBINS   = (XMAX-XMIN)/dX;

  TCut CUT_TRIGGER("triggerResult[0]==1 || triggerResult[1]==1");
  sprintf(name,"%s>%d && %s<%d",MASS_VAR.Data(),XMIN,MASS_VAR.Data(),XMAX);
  TCut CUT_MASS(name); 
  TCut CUT_PUID("puId[0]==1");
  TCut CUT_ELE("jetElf[0]<0.7 && jetElf[1]<0.7 && jetElf[2]<0.7 && jetElf[3]<0.7"); 
  TCut CUT_MUO("jetMuf[0]<0.7 && jetMuf[1]<0.7 && jetMuf[2]<0.7 && jetMuf[3]<0.7");
  
  TString SEL[5] = {
    "dPhibb<2.0 && MLP<0.52",
    "dPhibb<2.0 && MLP>=0.52 && MLP<0.76",
    "dPhibb<2.0 && MLP>=0.76 && MLP<0.90",
    "dPhibb<2.0 && MLP>=0.90 && MLP<0.96",
    "dPhibb<2.0 && MLP>=0.96"
  };
  /*
  TString SEL[5] = {
    "dPhibb<2.0 && MLP<0.50",
    "dPhibb<2.0 && MLP>=0.50 && MLP<0.74",
    "dPhibb<2.0 && MLP>=0.74 && MLP<0.88",
    "dPhibb<2.0 && MLP>=0.88 && MLP<0.94",
    "dPhibb<2.0 && MLP>=0.94"
  };
  */
  RooRealVar x(MASS_VAR,MASS_VAR,XMIN,XMAX);
  //x.setBins(NBINS,"default");
  RooDataSet *data[NCAT];
  TH1F *hdata[NCAT];
  //TH1F *hzj[NCAT];
 
  TH1F *hsgn[NCAT][5];
  TH1F *hgluglu[NCAT][5];
  TFile *fsgn[5];
  TTree *tsgn[5];
  RooDataHist *data_hist[NCAT],*RooHistSig[NCAT][5];
  RooPlot *frame1[NCAT];
  RooPlot *frame2[NCAT];
  TCanvas *can[NCAT],*can1[NCAT];
  RooHist *hresid[NCAT];
  RooBernstein *bkg_model[NCAT];
  RooAddPdf *model[NCAT];
  RooAbsPdf *z_pdf[NCAT];
  RooAbsPdf *top_pdf[NCAT];
  RooFitResult *res[NCAT];
  RooWorkspace *w = new RooWorkspace("w","workspace");
  int COLOR[5] = {kBlack,kRed,kGreen+1,kBlue,kMagenta};
  for(int j=0;j<5;j++) {
    sprintf(name,"flatTree_VBF-Powheg%d-ext_preselect_hard_PAPER_tmva.root",H_MASS[j]);
    fsgn[j] = TFile::Open(PATH+TString(name));
    tsgn[j] = (TTree*)fsgn[j]->Get("Hbb/events");
  }
  for(int i=0;i<NCAT;i++) {
    sprintf(name,"can1%d",i);
    can1[i] = new TCanvas(name,name,900,600);
    sprintf(name,"HbbCAT%d/events",i);
    tdat[i] = (TTree*)fdat->Get(name);
    sprintf(name,"data_CAT%d",i);
    data[i] = new RooDataSet(name,name,tdat[i],x);
    
    sprintf(name,"hdata_CAT%d",i);
    hdata[i] = new TH1F(name,name,NBINS,XMIN,XMAX);
    tdat[i]->Draw(MASS_VAR+">>"+TString(name));
    sprintf(name,"data_hist_CAT%d",i);
    data_hist[i] = new RooDataHist(name,name,x,hdata[i]);
    
    TCut CUT_SEL(SEL[i]);
    
    float NZ    = (TRIG_SF_AVE*LUMI*XSEC_ZJETS/N_ZJETS)*tzj->GetEntries(CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_MASS+CUT_ELE+CUT_MUO);
    float NW    = (TRIG_SF_AVE*LUMI*XSEC_WJETS/N_WJETS)*twj->GetEntries(CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_MASS+CUT_ELE+CUT_MUO);
    float NTT   = (TRIG_SF_AVE*LUMI*XSEC_TTJETS/N_TTJETS)*tttj->GetEntries(CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_MASS+CUT_ELE+CUT_MUO);
    float NT    = (TRIG_SF_AVE*LUMI*XSEC_T/N_T)*tt->GetEntries(CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_MASS+CUT_ELE+CUT_MUO);
    float NTBAR = (TRIG_SF_AVE*LUMI*XSEC_TBAR/N_TBAR)*ttbar->GetEntries(CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_MASS+CUT_ELE+CUT_MUO);

    cout<<"======== CATEGORY #"<<i<<" ======================"<<endl;
    cout<<"data events: "<<hdata[i]->Integral()<<endl;
    cout<<"Z events:    "<<NZ<<endl;
    cout<<"W events:    "<<NW<<endl;
    cout<<"TT events:   "<<NTT<<endl;
    cout<<"T events:    "<<NT<<endl;
    cout<<"Tbar events: "<<NTBAR<<endl;
    for(int j=0;j<5;j++) {
      sprintf(name,"hgluglu_CAT%d_%d",i,H_MASS[j]);
      hgluglu[i][j] = new TH1F(name,name,NBINS,XMIN,XMAX);
      sprintf(name,"%d*%s/125>>hgluglu_CAT%d_%d",H_MASS[j],MASS_VAR.Data(),i,H_MASS[j]);
      tgluglu->Draw(name,CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_ELE+CUT_MUO);
      hgluglu[i][j]->Scale(TRIG_SF_AVE*LUMI*XSEC_GLUGLU[j]/N_GLUGLU[j]);
      sprintf(name,"hsgn_CAT%d_%d",i,H_MASS[j]);
      hsgn[i][j] = new TH1F(name,name,NBINS,XMIN,XMAX);
      tsgn[j]->Draw(MASS_VAR+">>"+TString(name),CUT_SEL+CUT_PUID+CUT_TRIGGER+CUT_ELE+CUT_MUO);
      hsgn[i][j]->Scale(TRIG_SF[j][i]*LUMI*XSEC_SIGNAL[j]/N_SIGNAL[j]);
      hsgn[i][j]->SetLineColor(COLOR[j]);
      hsgn[i][j]->SetLineWidth(2);

      float Ngg = hgluglu[i][j]->Integral();
      float Nvbf = hsgn[i][j]->Integral();
      cout<<"----------------------------"<<endl;
      cout<<"Mass = "<<H_MASS[j]<<" GeV"<<endl;
      cout<<"----------------------------"<<endl;
      cout<<"VBF events: "<<hsgn[i][j]->Integral()<<endl;
      cout<<"GluGlu events: "<<Ngg<<" ("<<Ngg/Nvbf<<")"<<endl;
      hsgn[i][j]->Add(hgluglu[i][j]);
      sprintf(name,"hist_CAT%d_sgn%d",i,H_MASS[j]);
      RooHistSig[i][j] = new RooDataHist(name,name,x,hsgn[i][j]);
    }

    sprintf(name,"bkg_par0_CAT%d",i);
    RooRealVar a0(name,name,0.1,0,10);
    sprintf(name,"bkg_par1_CAT%d",i);
    RooRealVar a1(name,name,0.1,0,10);
    sprintf(name,"bkg_par2_CAT%d",i);
    RooRealVar a2(name,name,0.1,0,10);
    sprintf(name,"bkg_par3_CAT%d",i);
    RooRealVar a3(name,name,0.1,0,10);
    sprintf(name,"bkg_par4_CAT%d",i);
    RooRealVar a4(name,name,0.1,0,10);
    sprintf(name,"bkg_par5_CAT%d",i);
    RooRealVar a5(name,name,0.1,0,10);
    
    sprintf(name,"bkg_CAT%d",i);
    if (BRN_ORDER == 3) {
      bkg_model[i] = new RooBernstein(name,name,x,RooArgSet(a0,a1,a2,a3)); 
    }
    else if (BRN_ORDER == 4) {
      bkg_model[i] = new RooBernstein(name,name,x,RooArgSet(a0,a1,a2,a3,a4));
    }
    else if (BRN_ORDER == 5) {
      bkg_model[i] = new RooBernstein(name,name,x,RooArgSet(a0,a1,a2,a3,a4,a5));
    }
    else {
      cout<<"Bernstein order out of range [3,5]. Proceeding with 4th order."<<endl; 
      bkg_model[i] = new RooBernstein(name,name,x,RooArgSet(a0,a1,a2,a3,a4));
      BRN_ORDER = 4;
    }
      
    sprintf(name,"Z_model_CAT%d",i);
    z_pdf[i] = (RooAbsPdf*)wZ->pdf(name);

    sprintf(name,"Top_model_CAT%d",i);
    top_pdf[i] = (RooAbsPdf*)wT->pdf(name);
    
    sprintf(name,"nzjet_CAT%d",i);
    RooRealVar nzjet(name,name,NZ+NW,0*(NZ+NW),2.0*(NZ+NW));
    sprintf(name,"ntop_CAT%d",i);
    RooRealVar ntop(name,name,NTT+NT+NTBAR,0*(NTT+NT+NTBAR),2*(NTT+NT+NTBAR));
    sprintf(name,"nqcd_CAT%d",i);
    RooRealVar nqcd(name,name,500,0.,1e+12.);
    
    nzjet.setConstant(kTRUE);
    ntop.setConstant(kTRUE);

    sprintf(name,"model_CAT%d",i);
    model[i] = new RooAddPdf(name,name,RooArgList(*top_pdf[i],*z_pdf[i],*bkg_model[i]),RooArgList(ntop,nzjet,nqcd));
     
    res[i] = model[i]->fitTo(*data_hist[i],RooFit::Save());
    //res[i]->Print("v");
  
    
    //----- drawing ------------------
    frame1[i] = x.frame(RooFit::Bins(NBINS));  
    //data[i]->plotOn(frame1[i]);
    //model[i]->plotOn(frame1[i],RooFit::VisualizeError(*res[i],1,kTRUE),RooFit::FillColor(kGray));
    data[i]->plotOn(frame1[i]);
    model[i]->plotOn(frame1[i],RooFit::LineWidth(2));
    double chi2 = frame1[i]->chiSquare();
    cout<<"chi2/ndof = "<<chi2<<endl;
    model[i]->plotOn(frame1[i],RooFit::Components(*bkg_model[i]),RooFit::LineWidth(2),RooFit::LineStyle(2));
    hresid[i] = frame1[i]->residHist();
    //cout<<"chi2/ndof = "<<frame1[i]->chiSquare()<<endl;
    model[i]->plotOn(frame1[i],RooFit::Components(*z_pdf[i]),RooFit::LineWidth(2),RooFit::LineColor(kRed));
    model[i]->plotOn(frame1[i],RooFit::Components(*top_pdf[i]),RooFit::LineWidth(2),RooFit::LineColor(kGreen+2));
    //data[i]->plotOn(frame1[i]);
    
    
    sprintf(name,"Residual Distribution CAT%d",i);
    frame2[i] = x.frame(RooFit::Title(name));
    frame2[i]->addPlotable(hresid[i],"P");
    z_pdf[i]->plotOn(frame2[i],RooFit::LineWidth(2),RooFit::LineColor(kRed));
    top_pdf[i]->plotOn(frame2[i],RooFit::LineWidth(2),RooFit::LineColor(kGreen+2));
    
    sprintf(name,"DataFit_BRN%d_CAT%d",BRN_ORDER,i);
    can[i] = new TCanvas(name,name,900,600);
    can[i]->Divide(1,2,-1,-1);
    can[i]->cd(1);  
    gPad->SetLeftMargin(0.1); 
    gPad->SetRightMargin(0.01);
    gPad->SetTopMargin(0.02);
    frame1[i]->GetYaxis()->SetTitle("Events");
    frame1[i]->GetYaxis()->SetTitleSize(0.12);
    frame1[i]->GetYaxis()->SetTitleOffset(0.4);
    frame1[i]->GetYaxis()->SetLabelSize(0.07);
    frame1[i]->Draw();
    
    TPaveText *pave = new TPaveText(0.5,0.7,0.9,0.9,"NDC");
    sprintf(name,"fitted Z = (%1.2f #pm %1.2f) #sigma_{SM}",nzjet.getVal()/(NZ+NW),nzjet.getError()/(NZ+NW));
    pave->AddText(name);
    sprintf(name,"fitted Top = (%1.2f #pm %1.2f) #sigma_{SM}",ntop.getVal()/(NTT+NT+NTBAR),ntop.getError()/(NTT+NT+NTBAR));
    pave->AddText(name);
    sprintf(name,"#chi^{2}/ndof = %1.3f",chi2);
    pave->AddText(name);
    pave->SetFillColor(0);
    pave->SetBorderSize(0);
    pave->SetTextFont(42);
    pave->Draw("same");
  
    can[i]->cd(2); 
  
    //gPad->SetBorderSize(0);
    gPad->SetLeftMargin(0.1); 
    gPad->SetRightMargin(0.01); 
    gPad->SetBottomMargin(0.3);
    frame2[i]->GetXaxis()->SetTitle("M_{bb} (GeV)");
    frame2[i]->GetYaxis()->SetLabelSize(0.05);
    frame2[i]->GetXaxis()->SetTitleSize(0.1);
    frame2[i]->GetXaxis()->SetTitleOffset(1.0);
    frame2[i]->GetXaxis()->SetLabelSize(0.07);
    sprintf(name,"Z_model_CAT%d",i);
    frame2[i]->Draw();
    //hzj[i]->Draw("same");
    //httj[i]->Draw("same");
    //ht[i]->Draw("same");
    //htbar[i]->Draw("same");
    for(int j=0;j<5;j++) {
      hsgn[i][j]->Draw("same ][");
    }  
    w->import(*model[i]);
    w->import(*data_hist[i]);
    w->import(*data[i]);
    w->import(*res[i]);
    for(int j=0;j<5;j++) {
      w->import(*RooHistSig[i][j]);
    } 
    
  }
  //w->Print();
  sprintf(name,"%s_BRN%d_hard_PAPER_workspace.root",MASS_VAR.Data(),BRN_ORDER);
  cout<<"Writing file "<<name<<endl;
  w->writeToFile(name);
  // Workspace will remain in memory after macro finishes
  gDirectory->Add(w);
}
