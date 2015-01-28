using namespace RooFit;
void DrawBestFit(float BIN_SIZE,bool BLIND,int BRN_ORDER)
{
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  gROOT->ForceStyle();

  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  float XMIN = 80;
  float XMAX = 200; 

  TFile *f1 = TFile::Open("output/datacard_m125_"+TString::Format("BRN%d",BRN_ORDER)+"_CAT0-CAT6.root");
  TFile *f2 = TFile::Open("output/mlfit_m125_"+TString::Format("BRN%d",BRN_ORDER)+"_CAT0-CAT6.root");
  TFile *f3 = TFile::Open("output/signal_shapes_workspace.root");
  TFile *f4 = TFile::Open("output/data_shapes_workspace_"+TString::Format("BRN%d",BRN_ORDER)+".root");

  RooWorkspace *w = (RooWorkspace*)f1->Get("w");
  //w->Print();
  RooAbsPdf *bkg_model;
  RooFitResult *res; 
  RooRealVar *rFit(0);
  if (BLIND) {
    bkg_model = (RooAbsPdf*)w->pdf("model_b");
    res = (RooFitResult*)f2->Get("fit_b");
  }
  else {
    bkg_model = (RooAbsPdf*)w->pdf("model_s");
    res = (RooFitResult*)f2->Get("fit_s");
    rFit = dynamic_cast<RooRealVar *>(res->floatParsFinal()).find("r");
  }
  RooDataSet *data     = (RooDataSet*)w->data("data_obs");
  
  res->Print();
  
  w->allVars().assignValueOnly(res->floatParsFinal());
  //w->Print();
  
  RooWorkspace *wSig = (RooWorkspace*)f3->Get("w"); 
  RooWorkspace *wDat = (RooWorkspace*)f4->Get("w"); 

  const RooSimultaneous *sim = dynamic_cast<const RooSimultaneous *> (bkg_model);
  const RooAbsCategoryLValue &cat = (RooAbsCategoryLValue &) sim->indexCat();
  TList *datasets = data->split(cat,true);
  TIter next(datasets);
  for(RooAbsData *ds = (RooAbsData*)next();ds != 0; ds= (RooAbsData*)next()) {
    RooAbsPdf *pdfi = sim->getPdf(ds->GetName());
    RooArgSet *obs = (RooArgSet*)pdfi->getObservables(ds);
    RooRealVar *x = dynamic_cast<RooRealVar *>(obs->first());

    RooRealVar *yield_vbf = (RooRealVar*)wSig->var("yield_signalVBF_mass125_"+TString(ds->GetName()));
    RooRealVar *yield_gf  = (RooRealVar*)wSig->var("yield_signalGF_mass125_"+TString(ds->GetName()));

    //----- get the QCD normalization -----------
    RooRealVar *qcd_norm_final = dynamic_cast<RooRealVar *>(res->floatParsFinal()).find("CMS_vbfbb_qcd_norm_"+TString(ds->GetName()));
    RooRealVar *qcd_yield      = (RooRealVar*)wDat->var("yield_data_"+TString(ds->GetName()));

    float Nqcd  = exp(log(1.5)*qcd_norm_final->getVal())*qcd_yield->getVal();
    float eNqcd = log(1.5)*qcd_norm_final->getError()*Nqcd;
    cout<<Nqcd<<" +/- "<<eNqcd<<endl;
    
    TH1 *hCoarse = (TH1*)ds->createHistogram("coarseHisto_"+TString(ds->GetName()),*x);
    float norm = hCoarse->Integral();
  
    int rebin = BIN_SIZE/hCoarse->GetBinWidth(1);
    hCoarse->Rebin(rebin);

    float MIN_VAL = TMath::Max(0.9*hCoarse->GetBinContent(hCoarse->GetMinimumBin()),1.0);
    RooDataHist ds_coarse("ds_coarse_"+TString(ds->GetName()),"ds_coarse_"+TString(ds->GetName()),*x,hCoarse);

    TH1F *hBlind = (TH1F*)hCoarse->Clone("blindHisto_"+TString(ds->GetName()));
    for(int i=0;i<hBlind->GetNbinsX();i++) {
      double x0 = hBlind->GetBinCenter(i+1);
      if (x0 > 100 && x0 < 150) {
        hBlind->SetBinContent(i+1,0);
        hBlind->SetBinError(i+1,0);
      }
    }
    
    RooDataHist ds_blind("ds_blind_"+TString(ds->GetName()),"ds_blind_"+TString(ds->GetName()),*x,hBlind); 
    
    RooHist *hresid;
    RooPlot *frame1 = x->frame();
    RooPlot *frame2 = x->frame();
    
    if (BLIND) {
      ds_coarse.plotOn(frame1,LineColor(0),MarkerColor(0));
      pdfi->plotOn(frame1,VisualizeError(*res,1,kTRUE),FillColor(0),MoveToBack());
      pdfi->plotOn(frame1);
      ds_blind.plotOn(frame1);
      hresid = frame1->residHist();
      frame2->addPlotable(hresid,"p");
    }
    else {    
      ds_coarse.plotOn(frame1);
      pdfi->plotOn(frame1);
      cout<<"chi2/ndof = "<<frame1->chiSquare()<<endl;
      pdfi->plotOn(frame1,VisualizeError(*res,1,kTRUE),FillColor(kGray),MoveToBack());
      pdfi->plotOn(frame1,Components("shapeBkg_qcd_"+TString(ds->GetName())),LineWidth(2),LineStyle(2),LineColor(kGreen+1));
      pdfi->plotOn(frame1,Components("shapeBkg_qcd_"+TString(ds->GetName())+",shapeBkg_top_"+TString(ds->GetName())+",shapeBkg_zjets_"+TString(ds->GetName())),LineWidth(2),LineStyle(2)); 
      hresid = frame1->residHist();
      frame2->addPlotable(hresid,"p");
    
      float yield_sig = rFit->getValV()*(yield_vbf->getValV()+yield_gf->getValV());
      RooAbsPdf *signal_pdf = (RooAbsPdf*)w->pdf("shapeSig_qqH_"+TString(ds->GetName()));
      signal_pdf->plotOn(frame2,LineWidth(2),LineColor(kRed),Normalization(yield_sig,RooAbsReal::NumEvent));
    }
    
    TCanvas* canFit = new TCanvas("Higgs_fit_"+TString(ds->GetName()),"Higgs_fit_"+TString(ds->GetName()),900,600);
    canFit->cd(1)->SetBottomMargin(0.4);
    frame1->SetMinimum(MIN_VAL);
    frame1->GetYaxis()->SetNdivisions(510);
    frame1->GetXaxis()->SetTitleSize(0);
    frame1->GetXaxis()->SetLabelSize(0);
    frame1->GetYaxis()->SetTitle(TString::Format("Events / %1.1f GeV",BIN_SIZE));
    frame1->Draw();
    gPad->Update();
    
    TList *list = (TList*)gPad->GetListOfPrimitives();
    list->Print();
    TH1F *hUncH = new TH1F("hUncH"+TString(ds->GetName()),"hUncH"+TString(ds->GetName()),(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUncL = new TH1F("hUncL"+TString(ds->GetName()),"hUncL"+TString(ds->GetName()),(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUnc2H = new TH1F("hUnc2H"+TString(ds->GetName()),"hUnc2H"+TString(ds->GetName()),(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUnc2L = new TH1F("hUnc2L"+TString(ds->GetName()),"hUnc2L"+TString(ds->GetName()),(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX); 
    
    RooCurve *errorBand,*gFit;
    
    if (BLIND) {
      errorBand = (RooCurve*)list->FindObject("pdf_bin"+TString(ds->GetName())+"_bonly_Norm[mbbReg_"+TString(ds->GetName())+"]_errorband");
      gFit = (RooCurve*)list->FindObject("pdf_bin"+TString(ds->GetName())+"_bonly_Norm[mbbReg_"+TString(ds->GetName())+"]");
    }
    else {
      errorBand = (RooCurve*)list->FindObject("pdf_bin"+TString(ds->GetName())+"_Norm[mbbReg_"+TString(ds->GetName())+"]_errorband");
      gFit = (RooCurve*)list->FindObject("pdf_bin"+TString(ds->GetName())+"_Norm[mbbReg_"+TString(ds->GetName())+"]");
    }  
    for(int i=0;i<hUncH->GetNbinsX();i++) {
      double x0 = hUncH->GetBinCenter(i+1);
      double e1 = fabs(errorBand->Eval(x0)-gFit->Eval(x0));
      double e2 = eNqcd/hUncH->GetNbinsX();
      hUncH->SetBinContent(i+1,sqrt(pow(e2,2)+pow(e1,2)));
      hUnc2H->SetBinContent(i+1,2*sqrt(pow(e2,2)+pow(e1,2)));
      hUncL->SetBinContent(i+1,-sqrt(pow(e2,2)+pow(e1,2)));
      hUnc2L->SetBinContent(i+1,-2*sqrt(pow(e2,2)+pow(e1,2)));
    }
   
    TPad* pad = new TPad("pad", "pad", 0., 0., 1., 1.);
    pad->SetTopMargin(0.63);
    pad->SetFillColor(0);
    pad->SetFillStyle(0);
    pad->Draw();
    pad->cd(0);
    hUnc2H->GetXaxis()->SetTitle("M_{bb} (GeV)");
    hUnc2H->GetYaxis()->SetTitle("Data - Fit");
    double YMAX = frame2->GetMaximum();
    double YMIN = -frame2->GetMaximum();
    hUnc2H->GetYaxis()->SetRangeUser(YMIN,YMAX);
    hUnc2H->GetYaxis()->SetNdivisions(505);
    hUnc2H->GetXaxis()->SetTitleOffset(0.9);
    hUnc2H->GetYaxis()->SetTitleOffset(1.0);
    hUnc2H->GetYaxis()->SetTickLength(0.0);
    hUnc2H->GetYaxis()->SetTitleSize(0.05);
    hUnc2H->GetYaxis()->SetLabelSize(0.04);
    hUnc2H->GetYaxis()->CenterTitle(kTRUE);
    hUnc2H->SetFillColor(kGreen);
    hUnc2L->SetFillColor(kGreen);
    hUncH->SetFillColor(kYellow);
    hUncL->SetFillColor(kYellow);
    hUnc2H->Draw("HIST");
    hUnc2L->Draw("same HIST");
    hUncH->Draw("same HIST");
    hUncL->Draw("same HIST");
    frame2->Draw("same");

    TList *list1 = (TList*)gPad->GetListOfPrimitives();
    list1->Print();
    RooCurve *gSigFit = (RooCurve*)list1->FindObject("shapeSig_zjets_"+TString(ds->GetName())+"_Norm[mbbReg[1]]");

    TLegend *leg = new TLegend(0.7,0.62,0.9,0.92);
    leg->SetHeader(TString(ds->GetName()));
    leg->AddEntry(hBlind,"Data","P");
    if (!BLIND) {
      leg->AddEntry(gSigFit,"Fitted signal","L");
    }
    leg->AddEntry(gFit,"Total fit","L");
    //leg->AddEntry(gBkgFit,"QCD + Top","L");
    leg->AddEntry(hUnc2H,"2-#sigma uncertainty","F");
    leg->AddEntry(hUncH,"1-#sigma uncertainty","F");
    leg->SetFillColor(0);
    leg->SetBorderSize(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.04);
    leg->Draw(); 
     
    delete ds;
  }
  delete datasets; 
}
