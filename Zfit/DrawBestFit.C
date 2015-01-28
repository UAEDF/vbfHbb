using namespace RooFit;

void DrawBestFit(float BIN_SIZE)
{
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  gROOT->ForceStyle();
  gROOT->LoadMacro("CMS_lumi.C");
  TGaxis::SetMaxDigits(3);
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  float XMIN = 60;
  float XMAX = 170; 

  TFile *f1 = TFile::Open("datacard_Z.root");
  TFile *f2 = TFile::Open("mlfitZ.root");
  TFile *f3 = TFile::Open("bkgForZ_shapes_workspace_m0.02_0.02.root");
  TFile *f4 = TFile::Open(TString::Format("dataZ_shapes_workspace_BRN8_dM0.1_m0.02_0.02.root"));

  RooWorkspace *w = (RooWorkspace*)f1->Get("w");
  //w->Print();
  RooAbsPdf *bkg_model = (RooAbsPdf*)w->pdf("model_s");
  RooFitResult *res_s  = (RooFitResult*)f2->Get("fit_s"); 
  RooFitResult *res_b  = (RooFitResult*)f2->Get("fit_b");
  RooRealVar *rFit     = dynamic_cast<RooRealVar *>(res_s->floatParsFinal()).find("r");
  RooDataSet *data     = (RooDataSet*)w->data("data_obs");
  
  res_s->Print();
   
  w->allVars().assignValueOnly(res_s->floatParsFinal());
  //w->Print();
  
  cout<<"Fitted signal = "<<rFit->getVal()<<" - "<<rFit->getErrorLo()<<" + "<<rFit->getErrorHi()<<endl;

  RooWorkspace *wSig = (RooWorkspace*)f3->Get("w"); 
  RooWorkspace *wDat = (RooWorkspace*)f4->Get("w"); 

  const RooSimultaneous *sim = dynamic_cast<const RooSimultaneous *> (bkg_model);
  const RooAbsCategoryLValue &cat = (RooAbsCategoryLValue &) sim->indexCat();
  TList *datasets = data->split(cat,true);
  TIter next(datasets);
  for(RooAbsData *ds = (RooAbsData*)next();ds != 0; ds = (RooAbsData*)next()) {
    RooAbsPdf *pdfi = sim->getPdf(ds->GetName());
    RooArgSet *obs = (RooArgSet*)pdfi->getObservables(ds);
    RooRealVar *x = dynamic_cast<RooRealVar *>(obs->first());

    RooRealVar *yield_signal = (RooRealVar*)wSig->var("yield_ZJets_"+TString(ds->GetName()));
    TString ds_name(ds->GetName());
    //----- get the QCD normalization -----------
    RooRealVar *qcd_norm_final = dynamic_cast<RooRealVar *>(res_s->floatParsFinal()).find("qcd_norm_"+ds_name);
    RooRealVar *qcd_yield      = (RooRealVar*)wDat->var("yield_data_"+ds_name);

    float Nqcd  = exp(log(1.5)*qcd_norm_final->getVal())*qcd_yield->getVal();
    float eNqcd = log(1.5)*qcd_norm_final->getError()*Nqcd;
    cout<<"QCD normalization = "<<Nqcd<<" +/- "<<eNqcd<<endl;
    
    TH1 *hCoarse = (TH1*)ds->createHistogram("coarseHisto_"+ds_name,*x);
    float norm = hCoarse->Integral();
  
    int rebin = BIN_SIZE/hCoarse->GetBinWidth(1);
    hCoarse->Rebin(rebin);

    float MIN_VAL = TMath::Max(0.9*hCoarse->GetBinContent(hCoarse->GetMinimumBin()),1.0);
    float MAX_VAL = 1.3*hCoarse->GetBinContent(hCoarse->GetMaximumBin());
    RooDataHist ds_coarse("ds_coarse_"+ds_name,"ds_coarse_"+ds_name,*x,hCoarse);

    RooHist *hresid;
    RooPlot *frame1 = x->frame();
    RooPlot *frame2 = x->frame();
    
    ds_coarse.plotOn(frame1);
    pdfi->plotOn(frame1);
    cout<<"chi2/ndof = "<<frame1->chiSquare()<<endl;
    //pdfi->plotOn(frame1,VisualizeError(*res_s,1,kTRUE),FillColor(0),MoveToBack());
    //pdfi->plotOn(frame1,Components("shapeBkg_qcd_"+ds_name),LineWidth(2),LineStyle(5),LineColor(kGreen+2)); 
    pdfi->plotOn(frame1,Components("shapeBkg_qcd_"+ds_name+",shapeBkg_top_"+ds_name),LineWidth(2),LineStyle(2),LineColor(kBlack));
    pdfi->plotOn(frame1,Components("shapeBkg_qcd_"+ds_name+",shapeBkg_top_"+ds_name),LineWidth(2),LineStyle(2),LineColor(kBlack),VisualizeError(*res_s,1,kTRUE),FillColor(0),MoveToBack());
    hresid = frame1->residHist();
    frame2->addPlotable(hresid,"pE1");
    
    float yield_sig = rFit->getValV()*(yield_signal->getValV());
    RooAbsPdf *signal_pdf = (RooAbsPdf*)w->pdf("shapeSig_zjets_"+ds_name);
    signal_pdf->plotOn(frame2,LineWidth(2),LineColor(kRed),Normalization(yield_sig,RooAbsReal::NumEvent),MoveToBack());
    
    TCanvas* canFit = new TCanvas("Z_fit_"+ds_name,"Z_fit_"+ds_name,900,750);
    canFit->cd(1)->SetBottomMargin(0.4);
    frame1->SetMinimum(MIN_VAL);
    frame1->SetMaximum(MAX_VAL);
    frame1->GetYaxis()->SetNdivisions(510);
    frame1->GetXaxis()->SetTitleSize(0);
    frame1->GetXaxis()->SetLabelSize(0);
    frame1->GetYaxis()->SetTitle(TString::Format("Events / %1.1f GeV",BIN_SIZE));
    frame1->Draw();
    gPad->Update();
    
    TList *list = (TList*)gPad->GetListOfPrimitives();
    //list->Print();
    TH1F *hUncH  = new TH1F("hUncH"+ds_name,"hUncH"+ds_name,(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUncL  = new TH1F("hUncL"+ds_name,"hUncL"+ds_name,(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUnc2H = new TH1F("hUnc2H"+ds_name,"hUnc2H"+ds_name,(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX);
    TH1F *hUnc2L = new TH1F("hUnc2L"+ds_name,"hUnc2L"+ds_name,(XMAX-XMIN)/BIN_SIZE,XMIN,XMAX); 
    
    RooCurve *errorBand,*gFit,*gQCDFit,*gBkgFit;
    
    //errorBand = (RooCurve*)list->FindObject("pdf_bin"+ds_name+"_Norm[mbbReg_"+ds_name+"]_errorband");
    errorBand = (RooCurve*)list->FindObject("pdf_bin"+ds_name+"_Norm[mbbReg[1]]_errorband_Comp[shapeBkg_qcd_"+ds_name+",shapeBkg_top_"+ds_name+"]");
    gFit = (RooCurve*)list->FindObject("pdf_bin"+ds_name+"_Norm[mbbReg[1]]"); 
    //gQCDFit = (RooCurve*)list->FindObject("pdf_bin"+ds_name+"_Norm[mbbReg[1]]"+"_Comp[shapeBkg_qcd_"+ds_name+"]");  
    gBkgFit = (RooCurve*)list->FindObject("pdf_bin"+ds_name+"_Norm[mbbReg[1]]"+"_Comp[shapeBkg_qcd_"+ds_name+",shapeBkg_top_"+ds_name+"]");
    for(int i=0;i<hUncH->GetNbinsX();i++) {
      double x0 = hUncH->GetBinCenter(i+1);
      double e1 = fabs(errorBand->Eval(x0)-gBkgFit->Eval(x0));
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
    hUnc2H->GetYaxis()->SetTitle("Data - Bkg");
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
    gPad->Update();
    TLine *ln = new TLine(gPad->GetFrame()->GetX1(),0,gPad->GetFrame()->GetX2(),0);
    ln->SetLineColor(kBlack);
    ln->SetLineStyle(2);
    ln->SetLineWidth(1);
    ln->Draw();

    TList *list1 = (TList*)gPad->GetListOfPrimitives();
    //list1->Print();
    RooCurve *gSigFit = (RooCurve*)list1->FindObject("shapeSig_zjets_"+ds_name+"_Norm[mbbReg[1]]");

    TLegend *leg = new TLegend(0.65,0.6,0.9,0.92);
    leg->SetHeader(ds_name);
    leg->AddEntry(hCoarse,"Data","P");
    leg->AddEntry(gSigFit,"Fitted signal","L");
    leg->AddEntry(gFit,"Bkg + sig","L");
    leg->AddEntry(gBkgFit,"Bkg","L");
    //leg->AddEntry(gQCDFit,"QCD","L");
    leg->AddEntry(hUnc2H,"2-#sigma bkg. unc.","F");
    leg->AddEntry(hUncH,"1-#sigma bkg. unc.","F");
    leg->SetFillColor(0);
    leg->SetBorderSize(0);
    leg->SetTextFont(42);
    leg->SetTextSize(0.04);
    leg->Draw(); 
     
    CMS_lumi(canFit,2,10);

    canFit->Print(TString(canFit->GetName())+".pdf");
    delete ds;
  }
  delete datasets; 
}
