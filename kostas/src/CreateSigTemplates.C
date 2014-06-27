using namespace RooFit;
void CreateSigTemplates(double dX,float BND1,float BND2,float BND3)
{
  gROOT->ForceStyle();
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  double XMIN = 80;
  double XMAX = 200;
  int NBINS = (XMAX-XMIN)/dX;
  float LUMI[2] = {19784,18281};
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,BND1,BND2,BND3,1},{-0.1,0.4,0.8,1}};
  TString TAG(TString::Format("%1.2f_%1.2f_%1.2f",BND1,BND2,BND3));
  TString SELECTION[NSEL] = {"NOM","VBF"};
  TString MASS_VAR[NSEL] = {"mbbReg[1]","mbbReg[2]"};
  TString TRIG_WT[NSEL] = {"trigWtNOM[1]","trigWtVBF"};
  const int NMASS(5);
  int   H_MASS[NMASS]   = {115,120,125,130,135};
  float XSEC_VBF[NMASS] = {1.215,1.069,0.911,0.746,0.585};
  float XSEC_GF[NMASS]  = {16.14,13.69,11.26,8.93,6.78};
  char name[1000];
  TFile *fVBF[NMASS],*fGF[NMASS];
  TTree *trVBF,*trGF;
  TH1F  *hGF[NMASS][NCAT[0]],*hVBF[NMASS][NCAT[0]],*hTOT[NMASS][5],*hPassGF,*hPassVBF;
  RooDataHist *RooHistFit[NMASS][NCAT[0]],*RooHistScaled[NMASS][5];
  RooAddPdf *model[NMASS][NCAT[0]];
  RooRealVar *YieldVBF[NMASS][NCAT[0]],*YieldGF[NMASS][NCAT[0]];
  
  TCanvas *can[NMASS];
  TString PATH("");
  
  RooWorkspace *w = new RooWorkspace("w","workspace");
  
  //RooRealVar x("mbbReg","mbbReg",XMIN,XMAX);

  RooRealVar kJES("CMS_scale_j","CMS_scale_j",1,0.9,1.1);
  RooRealVar kJER("CMS_res_j","CMS_res_j",1,0.8,1.2);
  kJES.setConstant(kTRUE);
  kJER.setConstant(kTRUE);

  TString ss("");

  for(int iMass=0;iMass<NMASS;iMass++) {
    cout<<"Mass = "<<H_MASS[iMass]<<" GeV"<<endl;
    int counter(0);
    for(int isel=0;isel<NSEL;isel++) {
      sprintf(name,"flat/Fit_VBFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[isel].Data());
      fVBF[iMass]  = TFile::Open(PATH+TString(name));
      hPassVBF = (TH1F*)fVBF[iMass]->Get("TriggerPass");
      sprintf(name,"flat/Fit_GFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[isel].Data());
      fGF[iMass]  = TFile::Open(PATH+TString(name)); 
      hPassGF = (TH1F*)fGF[iMass]->Get("TriggerPass");
      sprintf(name,"HMassTemplate_%d_sel%s",H_MASS[iMass],SELECTION[isel].Data());
      can[iMass] = new TCanvas(name,name,900,600);
      can[iMass]->Divide(2,2);
      for(int icat=0;icat<NCAT[isel];icat++) {       
        sprintf(name,"Hbb/events",icat);
        trVBF = (TTree*)fVBF[iMass]->Get(name);
        trGF  = (TTree*)fGF[iMass]->Get(name);
        can[iMass]->cd(icat+1);
        sprintf(name,"mass_VBF%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[isel].Data(),icat);
        hVBF[iMass][icat] = new TH1F(name,name,NBINS,XMIN,XMAX);
        hVBF[iMass][icat]->Sumw2();  
        sprintf(name,"puWt[0]*%s*(mva%s>%1.2f && mva%s<=%1.2f)",TRIG_WT[isel].Data(),SELECTION[isel].Data(),MVA_BND[isel][icat],SELECTION[isel].Data(),MVA_BND[isel][icat+1]);
        TCut cut(name); 
        trVBF->Draw(MASS_VAR[isel]+">>"+TString(hVBF[iMass][icat]->GetName()),cut);
        sprintf(name,"mass_GF%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[isel].Data(),icat);
        hGF[iMass][icat] = new TH1F(name,name,NBINS,XMIN,XMAX);
        hGF[iMass][icat]->Sumw2();
        trGF->Draw(MASS_VAR[isel]+">>"+TString(hGF[iMass][icat]->GetName()),cut);
        delete trVBF;
        delete trGF;
        
        RooRealVar x("mbbReg_"+TString::Format("CAT%d",counter),"mbbReg_"+TString::Format("CAT%d",counter),XMIN,XMAX);

        sprintf(name,"roohist_fit_mass%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[isel].Data(),icat);
        RooHistFit[iMass][icat] = new RooDataHist(name,name,x,hVBF[iMass][icat]);

        hGF[iMass][icat]->Scale(LUMI[isel]*XSEC_GF[iMass]/hPassGF->GetBinContent(1));
        hVBF[iMass][icat]->Scale(LUMI[isel]*XSEC_VBF[iMass]/hPassVBF->GetBinContent(1));
        
        sprintf(name,"mass_Total%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[isel].Data(),icat);
        hTOT[iMass][icat] = (TH1F*)hVBF[iMass][icat]->Clone(name);
        hTOT[iMass][icat]->Add(hGF[iMass][icat]);
             
        sprintf(name,"yield_signalVBF_mass%d_CAT%d",H_MASS[iMass],counter);
        YieldVBF[iMass][icat] = new RooRealVar(name,name,hVBF[iMass][icat]->Integral());
        sprintf(name,"yield_signalGF_mass%d_CAT%d",H_MASS[iMass],counter);
        YieldGF[iMass][icat]  = new RooRealVar(name,name,hGF[iMass][icat]->Integral());
        
        sprintf(name,"roohist_demo_mass%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[isel].Data(),icat);
        RooHistScaled[iMass][icat] = new RooDataHist(name,name,x,hTOT[iMass][icat]);

        sprintf(name,"mean_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar m(name,name,H_MASS[iMass],H_MASS[iMass]-5,H_MASS[iMass]+5);
        sprintf(name,"sigma_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar s(name,name,12,3,30);
        sprintf(name,"fwhm_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar width(name,name,25,0,100);
        
        sprintf(name,"mean_shifted_m%d_CAT%d",H_MASS[iMass],counter);
        RooFormulaVar mShift(name,"@0*@1",RooArgList(m,kJES));
        sprintf(name,"sigma_shifted_m%d_CAT%d",H_MASS[iMass],counter);
        RooFormulaVar sShift(name,"@0*@1",RooArgList(s,kJER)); 
      
        sprintf(name,"alpha_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar a(name,name,1,-10,10);
        sprintf(name,"exp_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar n(name,name,1,0,100);
        
        sprintf(name,"b0_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar b0(name,name,0.5,0.,1.);
        sprintf(name,"b1_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar b1(name,name,0.5,0.,1.);
        sprintf(name,"b2_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar b2(name,name,0.5,0.,1.);
        sprintf(name,"b3_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar b3(name,name,0.5,0.,1.);
        
        sprintf(name,"signal_bkg_m%d_CAT%d",H_MASS[iMass],counter);
        RooBernstein bkg(name,name,x,RooArgSet(b0,b1,b2));
        
        sprintf(name,"fsig_m%d_CAT%d",H_MASS[iMass],counter);
        RooRealVar fsig(name,name,0.7,0.,1.);

        sprintf(name,"signal_gauss_m%d_CAT%d",H_MASS[iMass],counter);
        RooCBShape sig(name,name,x,mShift,sShift,a,n);
        
        ss = TString::Format("signal_model_m%d_CAT%d",H_MASS[iMass],counter); 
        model[iMass][icat] = new RooAddPdf(ss,ss,RooArgList(sig,bkg),fsig);
         
        model[iMass][icat]->fitTo(*RooHistFit[iMass][icat],SumW2Error(kFALSE),"q");

        RooPlot* frame = x.frame();
        RooHistScaled[iMass][icat]->plotOn(frame);
        model[iMass][icat]->plotOn(frame);
        double chi2 = frame->chiSquare(); 
        model[iMass][icat]->plotOn(frame,RooFit::Components(bkg),LineColor(kBlue),LineWidth(2),LineStyle(kDashed)); 
        frame->GetXaxis()->SetNdivisions(505); 
        frame->GetXaxis()->SetTitle("M_{bb} (GeV)");
        frame->GetYaxis()->SetTitle("Events");
        frame->Draw();
        hGF[iMass][icat]->SetFillColor(kGreen-8); 
        hVBF[iMass][icat]->SetFillColor(kRed-10); 
        THStack *hs = new THStack("hs","hs");
        hs->Add(hGF[iMass][icat]);
        hs->Add(hVBF[iMass][icat]);
        hs->Draw("same hist");
        frame->Draw("same");
        gPad->RedrawAxis();
        
        TF1 *tmp_func = model[iMass][icat]->asTF(x,fsig,x);
        double y0 = tmp_func->GetMaximum();
        double x0 = tmp_func->GetMaximumX();
        double x1 = tmp_func->GetX(y0/2,XMIN,x0);
        double x2 = tmp_func->GetX(y0/2,x0,XMAX);
        double FWHM = x2-x1;
        width.setVal(FWHM);
        double y1 = dX*0.5*y0*(YieldVBF[iMass][icat]->getVal()+YieldGF[iMass][icat]->getVal())/tmp_func->Integral(XMIN,XMAX); 
        TLine *ln = new TLine(x1,y1,x2,y1);
        ln->SetLineColor(kMagenta+3);
        ln->SetLineStyle(7);
        ln->SetLineWidth(2);
        ln->Draw(); 

        TLegend *leg = new TLegend(0.65,0.35,0.9,0.45);  
        leg->AddEntry(hVBF[iMass][icat],"VBF","F");
        leg->AddEntry(hGF[iMass][icat],"GF","F");
        leg->SetFillColor(0);
        leg->SetBorderSize(0);
        leg->SetTextFont(42);
        leg->SetTextSize(0.05);
        leg->Draw("same");
      
        TPaveText *pave = new TPaveText(0.65,0.55,0.9,0.92,"NDC");
        sprintf(name,"M_{H} = %d GeV",H_MASS[iMass]);
        pave->AddText(name);
        sprintf(name,"%s selection",SELECTION[isel].Data());
        pave->AddText(name);
        sprintf(name,"CAT%d",counter);
        pave->AddText(name);
        sprintf(name,"m = %1.1f #pm %1.1f",m.getVal(),m.getError());
        pave->AddText(name);
        sprintf(name,"#sigma = %1.1f #pm %1.1f",s.getVal(),s.getError());
        pave->AddText(name);
        sprintf(name,"FWHM = %1.2f",FWHM);
        pave->AddText(name);
        
        pave->SetFillColor(0);
        pave->SetBorderSize(0);
        pave->SetTextFont(42);
        pave->SetTextSize(0.05);
        pave->SetTextColor(kBlue);
        pave->Draw();
        
        b0.setConstant(kTRUE);
        b1.setConstant(kTRUE);
        b2.setConstant(kTRUE);
        b3.setConstant(kTRUE);
         
        m.setConstant(kTRUE);
        s.setConstant(kTRUE); 
        a.setConstant(kTRUE);
        n.setConstant(kTRUE);
        fsig.setConstant(kTRUE);
      
        w->import(*model[iMass][icat]);
        w->import(*RooHistScaled[iMass][icat]);
        //w->import(*res); 
        w->import(width);
        w->import(*YieldVBF[iMass][icat]);   
        w->import(*YieldGF[iMass][icat]);  
        
        counter++;
      }// categories loop
	 	can[iMass]->SaveAs(TString::Format("plots/fitsig/%s_%s.png",can[iMass]->GetName(),SELECTION[isel].Data()));
    }// selection loop 
  }// mass loop
  //w->Print();
  //x.Print();
  w->writeToFile("workspace/signal_shapes_workspace_"+TAG+".root");
}
