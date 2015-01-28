using namespace RooFit;
void CreateDataTemplates(double dX,float BND1,float BND2,float BND3,int BRN_ORDER)
{
  gROOT->ForceStyle();
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  double XMIN = 80;
  double XMAX = 200;
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,BND1,BND2,BND3,1},{-0.1,0.4,0.8,1}};
  TString TAG(TString::Format("%1.2f_%1.2f_%1.2f",BND1,BND2,BND3));
  char name[1000];
  TString SELECTION[2] = {"NOM","VBF"};
  TString MASS_VAR[2] = {"mbbReg[1]","mbbReg[2]"};

  TFile *fBKG  = TFile::Open("workspace/bkg_shapes_workspace_"+TAG+".root");
  RooWorkspace *wBkg = (RooWorkspace*)fBKG->Get("w");
  RooWorkspace *w = new RooWorkspace("w","workspace");
  //RooRealVar x(*(RooRealVar*)wBkg->var("mbbReg"));
  TTree *tr;
  TH1F *h;
  TCanvas *canFit[5]; 
  RooDataHist *roohist[5];

  TFile *fTransfer = TFile::Open("transfer/TransferFunction_"+TAG+".root");
  TF1 *transFunc;

  int counter(0);
  int NPAR = BRN_ORDER;

  for(int isel=0;isel<NSEL;isel++) {
    TFile *fDATA = TFile::Open("flat/Fit_data_sel"+SELECTION[isel]+".root");
    RooRealVar *brn[8];
    RooArgSet brn_params;
    if (isel == 1) {
      NPAR = BRN_ORDER-1;
    } 
    for(int ib=0;ib<=NPAR;ib++) {
      brn[ib] = new RooRealVar("b"+TString::Format("%d",ib)+"_sel"+SELECTION[isel],"b"+TString::Format("%d",ib)+"_sel"+SELECTION[isel],0.5,0,1.);
      brn_params.add(*brn[ib]);
    }
    for(int icat=0;icat<NCAT[isel];icat++) {
      RooRealVar x("mbbReg_"+TString::Format("CAT%d",counter),"mbbReg_"+TString::Format("CAT%d",counter),XMIN,XMAX);

      sprintf(name,"fitRatio_sel%s_CAT%d",SELECTION[isel].Data(),icat);
      transFunc = (TF1*)fTransfer->Get(name);
      float p0 = transFunc->GetParameter(0);
      float e0 = transFunc->GetParError(0);
      float p1 = transFunc->GetParameter(1);
      float e1 = transFunc->GetParError(1);
      
      RooRealVar trans_p1(TString::Format("trans_p1_CAT%d",counter),TString::Format("trans_p1_CAT%d",counter),p1,p1-e1,p1+e1);
      RooRealVar trans_p0(TString::Format("trans_p0_CAT%d",counter),TString::Format("trans_p0_CAT%d",counter),p0,p0-e0,p0+e0);
      trans_p1.setError(e1);
      trans_p0.setError(e0);
      trans_p1.setConstant(kTRUE);
      trans_p0.setConstant(kTRUE);
      RooGenericPdf transfer(TString::Format("transfer_CAT%d",counter),"@2*@0+@1",RooArgList(x,trans_p0,trans_p1));

      sprintf(name,"FitData_sel%s_CAT%d",SELECTION[isel].Data(),icat);
      canFit[icat] = new TCanvas(name,name,900,600);
      canFit[icat]->cd(1)->SetBottomMargin(0.4);
      sprintf(name,"Hbb/events");
      tr = (TTree*)fDATA->Get(name); 
      sprintf(name,"hMbb_%s_CAT%d",SELECTION[isel].Data(),icat);
      int NBINS = (XMAX[isel][icat]-XMIN[isel][icat])/dX;
      
      h = new TH1F(name,name,NBINS,XMIN[isel][icat],XMAX[isel][icat]);

      sprintf(name,"mva%s>%1.2f && mva%s<=%1.2f",SELECTION[isel].Data(),MVA_BND[isel][icat],SELECTION[isel].Data(),MVA_BND[isel][icat+1]);
      TCut cut(name);
      tr->Draw(MASS_VAR[isel]+">>"+h->GetName(),cut); 
      sprintf(name,"yield_data_CAT%d",counter);
      RooRealVar *Yield = new RooRealVar(name,name,h->Integral());
      
      sprintf(name,"data_hist_CAT%d",counter);
      roohist[icat] = new RooDataHist(name,name,x,h);
        
      RooAbsPdf *qcd_pdf;
      if (icat == 0) {
        for(int ib=0;ib<=NPAR;ib++) {
          brn[ib]->setConstant(kFALSE);
        }
        sprintf(name,"qcd_model_CAT%d",counter);
        RooBernstein *qcd_pdf_aux = new RooBernstein(name,name,x,brn_params);
        qcd_pdf = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux);
      }
      else {
        for(int ib=0;ib<=NPAR;ib++) {
          brn[ib]->setConstant(kTRUE);
        }
        sprintf(name,"qcd_model_aux1_CAT%d",counter);
        RooBernstein *qcd_pdf_aux1 = new RooBernstein(name,name,x,brn_params);
        sprintf(name,"qcd_model_CAT%d",counter);
        RooProdPdf *qcd_pdf_aux2 = new RooProdPdf(name,name,RooArgSet(transfer,*qcd_pdf_aux1));
        qcd_pdf = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux2);
      } 

      sprintf(name,"Z_model_CAT%d",counter);
      RooAbsPdf *z_pdf = (RooAbsPdf*)wBkg->pdf(name);
      sprintf(name,"Top_model_CAT%d",counter);
      RooAbsPdf *top_pdf = (RooAbsPdf*)wBkg->pdf(name);

      sprintf(name,"yield_ZJets_CAT%d",counter);
      RooRealVar *nZ = (RooRealVar*)wBkg->var(name);
      sprintf(name,"yield_Top_CAT%d",counter);
      RooRealVar *nT = (RooRealVar*)wBkg->var(name);
      sprintf(name,"yield_QCD_CAT%d",counter);
      RooRealVar nQCD(name,name,1000,0,1e+10);
      nZ->setConstant(kTRUE);
      nT->setConstant(kTRUE);
    
      sprintf(name,"bkg_model_CAT%d",counter);
      RooAddPdf model(name,name,RooArgList(*z_pdf,*top_pdf,*qcd_pdf),RooArgList(*nZ,*nT,nQCD));
      
      RooFitResult *res = model.fitTo(*roohist[icat],RooFit::Save());
      res->Print();
      
      RooPlot* frame = x.frame();
      RooPlot* frame1 = x.frame();
      roohist[icat]->plotOn(frame);
      model.plotOn(frame,LineWidth(2));
      RooHist *hresid = frame->residHist(); 
      //model.plotOn(frame,RooFit::VisualizeError(*res,1,kFALSE),FillColor(kGray)MoveToBack());
      model.plotOn(frame,Components(*qcd_pdf),LineWidth(2),LineColor(kBlack),LineStyle(kDashed));
      model.plotOn(frame,Components(*z_pdf),LineWidth(2),LineColor(kBlue));
      model.plotOn(frame,Components(*top_pdf),LineWidth(2),LineColor(kGreen+1));
      frame->Draw(); 
      gPad->Update();
      TPad* pad = new TPad("pad", "pad", 0., 0., 1., 1.);
      pad->SetTopMargin(0.6);
      pad->SetFillColor(0);
      pad->SetFillStyle(0);
      pad->Draw();
      pad->cd(0);
      frame1->addPlotable(hresid,"p");
      frame1->Draw();

      for(int ib=0;ib<=NPAR;ib++) {
        brn[ib]->setConstant(kFALSE);
      }

      if (icat > 0) {
        trans_p1.setConstant(kFALSE);
        trans_p0.setConstant(kFALSE);
      }
      w->import(trans_p1);
      w->import(trans_p0);
      w->import(*roohist[icat]);
      w->import(model);
      w->import(*Yield);
      counter++; 
		canFit[icat]->SaveAs(TString::Format("plots/fitdat/%s.png",canFit[icat]->GetName()));
    }// category loop
  }// selection loop
  //w->Print();
  w->writeToFile("workspace/data_shapes_workspace_"+TAG+"_"+TString::Format("BRN%d",BRN_ORDER)+".root");
}
