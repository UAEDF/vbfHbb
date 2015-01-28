using namespace RooFit;
void CreateSigTemplates(double dX, float XMIN, float XMAX, TString OUTPATH, TString MASS, float XMAXDIFF=0.)
{
  gROOT->ProcessLineSync(".x ../../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  gStyle->SetPadTopMargin(0.05);
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  int NBINS = (XMAX-XMIN)/dX;
  float LUMI[2] = {19784.,18281.};
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  TString SELECTION[NSEL] = {"NOM","VBF"};
  TString SELTAG[NSEL] = {"Set A","Set B"};
  TString MASS_VAR[NSEL] = {"mbbReg[1]","mbbReg[2]"};
  TString TRIG_WT[NSEL] = {"trigWtNOM[1]","trigWtVBF"};
  const int NMASS(5);
  int   H_MASS[NMASS]   = {115,120,125,130,135};
  float XSEC_VBF[NMASS] = {1.215,1.069,0.911,0.746,0.585};
  float XSEC_GF[NMASS]  = {15.93,13.52,11.12,8.82,6.69};//{16.14,13.69,11.26,8.93,6.78};
  char name[1000];
  TFile *fVBF[NMASS],*fGF[NMASS];
  TTree *trVBF,*trGF;
  TH1F  *hGF[NMASS][NCAT[0]],*hVBF[NMASS][NCAT[0]],*hTOT[NMASS][5],*hPassGF,*hPassVBF;
  RooDataHist *RooHistFit[NMASS][NCAT[0]],*RooHistScaled[NMASS][5];
  RooAddPdf *model[NMASS][NCAT[0]];
  RooRealVar *YieldVBF[NMASS][NCAT[0]],*YieldGF[NMASS][NCAT[0]];
  RooRealVar *kJES[10],*kJER[10];
  TCanvas *can[NMASS];
  TCanvas *canvas = new TCanvas("c","c",900,750);
  TString PATH("flat/");
  TString ss("");

  vector<int> MASSasked = splitString(MASS);
  cout << MASSasked[0] << endl;
  RooWorkspace *w = new RooWorkspace("w","workspace");

  makeDirs(OUTPATH);
  makeDirs(OUTPATH+"/plots/");
  makeDirs(OUTPATH+"/plots/sigTemplates/");

  int counter(0);
  for(int isel=0;isel<NSEL;isel++) {
    sprintf(name,"CMS_vbfbb_scale_mbb_sel%s",SELECTION[isel].Data()); 
    kJES[isel] = new RooRealVar(name,name,1.0);
    sprintf(name,"CMS_vbfbb_res_mbb_sel%s",SELECTION[isel].Data()); 
    kJER[isel] = new RooRealVar(name,name,1.0);
    kJES[isel]->setConstant(kTRUE);
    kJER[isel]->setConstant(kTRUE);
  }
  for(int iMass=0;iMass<NMASS;iMass++) {
	 bool go=false;
	 for (int iv=0; iv<(int)MASSasked.size(); iv++) {
		 if (H_MASS[iMass]==MASSasked[iv]) { go=true; break; }
	 }
	 if (!go) continue;
    cout<<"Mass = "<<H_MASS[iMass]<<" GeV"<<endl;
    counter = 0;
    for(int isel=0;isel<NSEL;isel++) {
      sprintf(name,"Fit_VBFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[isel].Data());
      fVBF[iMass]  = TFile::Open(PATH+TString(name));
      hPassVBF = (TH1F*)fVBF[iMass]->Get("TriggerPass");
      sprintf(name,"Fit_GFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[isel].Data());
      fGF[iMass]  = TFile::Open(PATH+TString(name)); 
      hPassGF = (TH1F*)fGF[iMass]->Get("TriggerPass");
      sprintf(name,"HMassTemplate_%d_sel%s",H_MASS[iMass],SELECTION[isel].Data());
      can[iMass] = new TCanvas(name,name,900,600);
      can[iMass]->Divide(2,2);
      for(int icat=0;icat<NCAT[isel];icat++) {       
			if (isel==1 && icat==0) { XMAX += XMAXDIFF; }
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
        
        sprintf(name,"mbbReg_CAT%d",counter);
        RooRealVar x(name,name,XMIN,XMAX);

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
        RooFormulaVar mShift(name,"@0*@1",RooArgList(m,*(kJES[isel])));
        sprintf(name,"sigma_shifted_m%d_CAT%d",H_MASS[iMass],counter);
        RooFormulaVar sShift(name,"@0*@1",RooArgList(s,*(kJER[isel]))); 
      
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
			
		  hGF[iMass][icat]->Rebin(25);
		  hVBF[iMass][icat]->Rebin(25);
		  hTOT[iMass][icat]->Rebin(25);
        RooHistScaled[iMass][icat] = new RooDataHist(name,name,x,hTOT[iMass][icat]);

        RooPlot* frame = x.frame();
        RooHistScaled[iMass][icat]->plotOn(frame);
        model[iMass][icat]->plotOn(frame);
        double chi2 = frame->chiSquare(); 
        model[iMass][icat]->plotOn(frame,RooFit::Components(bkg),LineColor(kBlue),LineWidth(2),LineStyle(kDashed)); 
        frame->GetXaxis()->SetNdivisions(505); 
        frame->GetXaxis()->SetTitle("M_{bb} (GeV)");
        frame->GetYaxis()->SetTitle(TString::Format("Events / (%.1f)",hTOT[iMass][icat]->GetBinWidth(1)).Data());
		  frame->GetYaxis()->SetRangeUser(0.,hTOT[iMass][icat]->GetBinContent(hTOT[iMass][icat]->GetMaximumBin())*1.1);
        frame->Draw();
        hGF[iMass][icat]->SetFillColor(kGreen-8); 
        hVBF[iMass][icat]->SetFillColor(kRed-10); 
        THStack *hs = new THStack("hs","hs");
        hs->Add(hGF[iMass][icat]);
        hs->Add(hVBF[iMass][icat]);
        hs->Draw("same hist");
        frame->Draw("same");
        gPad->RedrawAxis();
        
		  //TF1 *tmp_func = model[iMass][icat]->asTF(x,fsig);
        //double y0 = tmp_func->GetMaximum();
		  //cout << y0 << endl;
        tmp_func = model[iMass][icat]->asTF(x,fsig,x);
		  double y0b = tmp_func->GetMaximum();
        double x0 = tmp_func->GetMaximumX();
        double x1 = tmp_func->GetX(y0b/2,XMIN,x0);
        double x2 = tmp_func->GetX(y0b/2,x0,XMAX);
        double FWHM = x2-x1;
        width.setVal(FWHM);
        double y1 = dX*25*0.5*y0b*(YieldVBF[iMass][icat]->getVal()+YieldGF[iMass][icat]->getVal())/tmp_func->Integral(XMIN,XMAX); 
		  cout << y1 << endl;
        TLine *ln = new TLine(x1,y1,x2,y1);
        ln->SetLineColor(kMagenta+3);
        ln->SetLineStyle(7);
        ln->SetLineWidth(2);
        ln->Draw(); 

        TLegend *leg = new TLegend(0.71,0.35,0.9,0.45);  
        leg->AddEntry(hVBF[iMass][icat],"VBF","F");
        leg->AddEntry(hGF[iMass][icat],"GF","F");
        leg->SetFillColor(0);
        leg->SetBorderSize(0);
        leg->SetTextFont(42);
        leg->SetTextSize(0.05);
        leg->Draw("same");
      
        TPaveText *pave = new TPaveText(0.67,1.-(6*1.2+1)*gStyle->GetPadTopMargin()-0.02,1.-gStyle->GetPadRightMargin()-0.02,1.-gStyle->GetPadTopMargin()-0.02,"NDC");
        sprintf(name,"M_{H} = %d GeV",H_MASS[iMass]);
        pave->AddText(name);
        sprintf(name,"%s selection",SELTAG[isel].Data());
        pave->AddText(name);
        sprintf(name,"CAT%d",counter);
        pave->AddText(name);
        sprintf(name,"m = %1.1f #pm %1.1f",m.getVal(),m.getError());
        pave->AddText(name);
        sprintf(name,"#sigma = %1.1f #pm %1.1f",s.getVal(),s.getError());
        pave->AddText(name);
        sprintf(name,"FWHM = %1.2f",width.getVal());//FWHM);
        pave->AddText(name);
        
        pave->SetFillColor(0);
        pave->SetBorderSize(0);
        pave->SetTextFont(42);
        pave->SetTextSize(gStyle->GetPadTopMargin()*3.75/4.);
        pave->SetTextColor(kBlue);
        pave->Draw();

		  canvas->cd();
		  frame->Draw();
		  hs->Draw("hist,same");
		  frame->Draw("same");
		  ln->Draw();
		  leg->Draw("same");
		  pave->Draw();
		  gPad->SetRightMargin(0.05);
		  gPad->Update();
		  pave->SetX2(1.-gPad->GetRightMargin()-0.02);
		  gPad->Modified();
		  gPad->Update();
		  gPad->RedrawAxis();
		  canvas->SaveAs(TString::Format("%s/plots/sigTemplates/sig_m%d_CAT%d.png",OUTPATH.Data(),H_MASS[iMass],counter).Data());
		  canvas->SaveAs(TString::Format("%s/plots/sigTemplates/sig_m%d_CAT%d.pdf",OUTPATH.Data(),H_MASS[iMass],counter).Data());
        
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
        
		  gPad->RedrawAxis();
        counter++;
      }// categories loop
		can[iMass]->SaveAs(TString::Format("%s/plots/sigTemplates/%s.png",OUTPATH.Data(),can[iMass]->GetName()));
		can[iMass]->SaveAs(TString::Format("%s/plots/sigTemplates/%s.pdf",OUTPATH.Data(),can[iMass]->GetName()));
    }// selection loop 
  }// mass loop
  XMAX -= XMAXDIFF;
  makeDirs(OUTPATH+"/output/");
  w->Print();
  if (XMAXDIFF==0) w->writeToFile(TString::Format("%s/output/signal_shapes_workspace_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX).Data());
  else             w->writeToFile(TString::Format("%s/output/signal_shapes_workspace_B%.f-%.f%.f.root",OUTPATH.Data(),XMIN,XMAX,XMAX+XMAXDIFF).Data());
}

void makeDirs(TString dirName) {
	 system(TString::Format("[ ! -d %s ] && mkdir %s",dirName.Data(),dirName.Data()).Data());
}

vector<int> splitString(TString s) {
    TObjArray *t = s.Tokenize(",");
    const int n = t->GetEntries();
	 vector<int> out;
	 out.clear();
	 for (int i=0; i<n; i++) {
	     out.push_back(((TObjString*)t->At(i))->String().Atoi());
	 }
	 return out; 
}

