using namespace RooFit;
void CreateBkgTemplates(float XMIN, float XMAX, TString OUTPATH, float XMAXDIFF=0.)
{
  gROOT->ProcessLineSync(".x ../../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  gStyle->SetPadRightMargin(0.04);
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  float LUMI[2] = {19784.,18281.};
  TString SELECTION[2] = {"NOM","VBF"};
  TString SELNAME[2] = {"Set A","Set B"};
  TString MASS_VAR[2] = {"mbbReg[1]","mbbReg[2]"};
  TString TRIG_WT[2] = {"trigWtNOM[1]","trigWtVBF"};
  TString PATH("flat/");
  TFile *inf[9];
  TTree *tr;
  TH1F *hMbb[9],*hMbbYield[9],*hPass;
  TH1F *hZ,*hW,*hTT,*hST,*hTop;
  TH1F *hZYield,*hWYield,*hTTYield,*hSTYield,*hTopYield;
  char name[1000];
  float LUMI;
  float XSEC[9] = {56.4,11.1,3.79,30.7,11.1,1.76,245.8,650,1.2*1205};
  RooDataHist *roohist_Z[5],*roohist_T[5];
  RooRealVar *kJES[10],*kJER[10];
  RooWorkspace *w = new RooWorkspace("w","workspace");
  makeDirs(OUTPATH);
  makeDirs(OUTPATH+"/plots");
  makeDirs(OUTPATH+"/plots/bkgTemplates/");
  TString FULLPATH(OUTPATH+"/plots/bkgTemplates");
  
  int counter(0);
  for(int isel=0;isel<NSEL;isel++) {
    inf[0] = TFile::Open(PATH+"Fit_T_t-channel_sel"+SELECTION[isel]+".root");
    inf[1] = TFile::Open(PATH+"Fit_T_tW-channel_sel"+SELECTION[isel]+".root");
    inf[2] = TFile::Open(PATH+"Fit_T_s-channel_sel"+SELECTION[isel]+".root");
    inf[3] = TFile::Open(PATH+"Fit_Tbar_t-channel_sel"+SELECTION[isel]+".root");
    inf[4] = TFile::Open(PATH+"Fit_Tbar_tW-channel_sel"+SELECTION[isel]+".root");
    inf[5] = TFile::Open(PATH+"Fit_Tbar_s-channel_sel"+SELECTION[isel]+".root");
    inf[6] = TFile::Open(PATH+"Fit_TTJets_sel"+SELECTION[isel]+".root");
    inf[7] = TFile::Open(PATH+"Fit_ZJets_sel"+SELECTION[isel]+".root");
    inf[8] = TFile::Open(PATH+"Fit_WJets_sel"+SELECTION[isel]+".root");
     
    TCanvas *canZ = new TCanvas("canZ_"+SELECTION[isel],"canZ_"+SELECTION[isel],900,600); 
    TCanvas *canT = new TCanvas("canT_"+SELECTION[isel],"canT_"+SELECTION[isel],900,600);  
    canZ->Divide(2,2);
    canT->Divide(2,2);
    TCanvas *can = new TCanvas("c","c",900,600); 
    
    sprintf(name,"CMS_vbfbb_scale_mbb_sel%s",SELECTION[isel].Data()); 
    kJES[isel] = new RooRealVar(name,name,1.0);
    sprintf(name,"CMS_vbfbb_res_mbb_sel%s",SELECTION[isel].Data()); 
    kJER[isel] = new RooRealVar(name,name,1.0);
    kJES[isel]->setConstant(kTRUE);
    kJER[isel]->setConstant(kTRUE);
  
    for(int icat=0;icat<NCAT[isel];icat++) {
		if (isel==1 && icat==0) { XMAX += XMAXDIFF; }
		cout << endl << endl;
      for(int i=0;i<9;i++) {
        hPass = (TH1F*)inf[i]->Get("TriggerPass");
        sprintf(name,"Hbb/events",icat);
        tr = (TTree*)inf[i]->Get(name); 
        sprintf(name,"puWt[0]*%s*(mva%s>%1.2f && mva%s<=%1.2f)",TRIG_WT[isel].Data(),SELECTION[isel].Data(),MVA_BND[isel][icat],SELECTION[isel].Data(),MVA_BND[isel][icat+1]);
        TCut cut(name); 
        int NBINS(20);
        //if (icat > 1 && icat<=2) NBINS = 20; 
        if (icat > 2) NBINS = 12;
        sprintf(name,"hMbb%d_sel%s_CAT%d",i,SELECTION[isel].Data(),icat);
        hMbb[i] = new TH1F(name,name,NBINS,XMIN,XMAX);
        hMbb[i]->Sumw2();
        can->cd();        
        tr->Draw(MASS_VAR[isel]+">>"+hMbb[i]->GetName(),cut);
        sprintf(name,"hMbbYield%d_sel%s_CAT%d",i,SELECTION[isel].Data(),icat);
        hMbbYield[i] = new TH1F(name,name,NBINS,XMIN,XMAX);
        hMbbYield[i]->Sumw2();
        tr->Draw(MASS_VAR[isel]+">>"+hMbbYield[i]->GetName(),cut);
        hMbbYield[i]->Scale(LUMI[isel]*XSEC[i]/hPass->GetBinContent(1)); 
		  printf("%-50s | CAT%d | sel%s | %d\n",inf[i]->GetName(),icat,SELECTION[isel].Data(),hMbb[i]->GetEntries());
      }
		cout << endl << endl;
      hZ  = (TH1F*)hMbb[7]->Clone("Z");
      hW  = (TH1F*)hMbb[8]->Clone("W");
      hTT = (TH1F*)hMbb[6]->Clone("TT");
      hST = (TH1F*)hMbb[0]->Clone("ST");
      hST->Add(hMbb[1]);
      hST->Add(hMbb[2]);
      hST->Add(hMbb[3]);
      hST->Add(hMbb[4]);
      hST->Add(hMbb[5]);
      hTop = (TH1F*)hTT->Clone("Top");
      hTop->Add(hST);
      //hZ->Add(hW);
      hZYield  = (TH1F*)hMbbYield[7]->Clone("ZYield");
      hWYield  = (TH1F*)hMbbYield[8]->Clone("WYield");
      hTTYield = (TH1F*)hMbbYield[6]->Clone("TTYield");
      hSTYield = (TH1F*)hMbbYield[0]->Clone("STYield");
      hSTYield->Add(hMbbYield[1]);
      hSTYield->Add(hMbbYield[2]);
      hSTYield->Add(hMbbYield[3]);
      hSTYield->Add(hMbbYield[4]);
      hSTYield->Add(hMbbYield[5]);
      hTopYield = (TH1F*)hTTYield->Clone("TopYield");
      hTopYield->Add(hSTYield);
      hZYield->Add(hWYield); 

		if (isel==0 && icat==0) TFile *fout = TFile::Open("tmp.root","recreate");
		else TFile *fout = TFile::Open("tmp.root","update");
		hTopYield->Write(TString::Format("hTop_CAT%d",isel==0 ? icat : icat+NCAT[0]));
		hZ->Write(TString::Format("hZ_CAT%d",isel==0 ? icat : icat+NCAT[0]));
		fout->Close();

      RooRealVar x("mbbReg_"+TString::Format("CAT%d",counter),"mbbReg_"+TString::Format("CAT%d",counter),XMIN,XMAX);

      sprintf(name,"yield_ZJets_CAT%d",counter);
      RooRealVar *YieldZ = new RooRealVar(name,name,hZYield->Integral());
      sprintf(name,"yield_WJets_CAT%d",counter);
      RooRealVar *YieldW = new RooRealVar(name,name,hWYield->Integral());
      sprintf(name,"yield_Top_CAT%d",counter);
      RooRealVar *YieldT = new RooRealVar(name,name,hTopYield->Integral());
      sprintf(name,"yield_TT_CAT%d",counter);
      RooRealVar *YieldTT = new RooRealVar(name,name,hTTYield->Integral());
      sprintf(name,"yield_ST_CAT%d",counter);
      RooRealVar *YieldST = new RooRealVar(name,name,hSTYield->Integral());

      sprintf(name,"roohist_Z_CAT%d",counter);
      roohist_Z[icat] = new RooDataHist(name,name,x,hZ);

      sprintf(name,"Z_mean_CAT%d",counter);
      RooRealVar mZ(name,name,95,80,110);
      sprintf(name,"Z_sigma_CAT%d",counter);
      RooRealVar sZ(name,name,12,9,20);

      sprintf(name,"Z_mean_shifted_CAT%d",counter);
      RooFormulaVar mZShift(name,"@0*@1",RooArgList(mZ,*(kJES[isel])));
      sprintf(name,"Z_sigma_shifted_CAT%d",counter);
      RooFormulaVar sZShift(name,"@0*@1",RooArgList(sZ,*(kJER[isel])));

      sprintf(name,"Z_a_CAT%d",counter);
      RooRealVar aZ(name,name,-1,-10,10);
      sprintf(name,"Z_n_CAT%d",counter);
      RooRealVar nZ(name,name,1,0,10);

      RooRealVar Zb0("Z_b0_CAT"+TString::Format("%d",counter),"Z_b0_CAT"+TString::Format("%d",counter),0.5,0,1.);
      RooRealVar Zb1("Z_b1_CAT"+TString::Format("%d",counter),"Z_b1_CAT"+TString::Format("%d",counter),0.5,0,1.);
      RooRealVar Zb2("Z_b2_CAT"+TString::Format("%d",counter),"Z_b2_CAT"+TString::Format("%d",counter),0.5,0,1.);
      RooBernstein Zbkg("Z_bkg_CAT"+TString::Format("%d",counter),"Z_bkg_CAT"+TString::Format("%d",counter),x,RooArgSet(Zb0,Zb1,Zb2));
      
      RooRealVar fZsig("fZsig_CAT"+TString::Format("%d",counter),"fZsig_CAT"+TString::Format("%d",counter),0.7,0.,1.);
      RooCBShape Zcore("Zcore_CAT"+TString::Format("%d",counter),"Zcore_CAT"+TString::Format("%d",counter),x,mZShift,sZShift,aZ,nZ);
    
      RooAddPdf modelZ("Z_model_CAT"+TString::Format("%d",counter),"Z_model_CAT"+TString::Format("%d",counter),RooArgList(Zcore,Zbkg),fZsig);
    
      RooFitResult *resZ = modelZ.fitTo(*roohist_Z[icat],RooFit::Save(),"q"); 
		
      canZ->cd(icat+1);
      RooPlot* frame = x.frame();
      roohist_Z[icat]->plotOn(frame);
      modelZ.plotOn(frame,RooFit::LineWidth(2));
      frame->GetXaxis()->SetTitle("M_{bb} (GeV)");
      frame->Draw();
		frame->GetYaxis()->SetRangeUser(0.,(hZ->GetBinContent(hZ->GetMaximumBin())+hZ->GetBinError(hZ->GetMaximumBin()))*1.05);
      TPaveText *pave = new TPaveText(0.7,0.76,0.9,0.9,"NDC");
		pave->SetTextAlign(11);
      pave->SetFillColor(0);
      pave->SetBorderSize(0);
      pave->SetTextFont(62);
      pave->SetTextSize(0.045);
      pave->AddText(TString::Format("%s selection",SELNAME[isel].Data()));
		pave->AddText(TString::Format("CAT%d",counter));
		TText *lastline = pave->AddText("Z template");
		pave->SetY1NDC(pave->GetY2NDC()-0.055*3);
		TPaveText *paveorig = (TPaveText*)pave->Clone();
      paveorig->Draw();
    
		TPaveText *paveZ = new TPaveText(0.70,0.58,0.95,0.60,"NDC");
		paveZ->SetTextAlign(11);
      paveZ->SetFillColor(0);
      paveZ->SetBorderSize(0);
      paveZ->SetTextFont(82);
      paveZ->SetTextSize(0.030);
		paveZ->AddText(TString::Format("mZ: %.2f #pm %.2f",mZ.getValV(),mZ.getError()));
		paveZ->AddText(TString::Format("sZ: %.2f #pm %.2f",sZ.getValV(),sZ.getError()));
		//paveZ->Draw();
		gPad->Update();
		paveZ->SetY2NDC(paveZ->GetY1NDC()+paveZ->GetListOfLines()->GetSize()*0.032);
		
		can->cd();
		frame->Draw();
		pave->Draw();
		//paveZ->Draw();
		//gPad->Update();
		//paveZ->SetY2NDC(paveZ->GetY1NDC()+paveZ->GetListOfLines()->GetSize()*0.032);
		can->SaveAs(TString::Format("%s/bkg_Z_CAT%d.pdf",FULLPATH.Data(),counter).Data());
		can->SaveAs(TString::Format("%s/bkg_Z_CAT%d.png",FULLPATH.Data(),counter).Data());

      sprintf(name,"roohist_T_CAT%d",counter);
      if (icat < 3) { 
        roohist_T[icat] = new RooDataHist(name,name,x,hTopYield);
      }
      else {
        roohist_T[icat] = new RooDataHist(name,name,x,hSTYield);
      }

      sprintf(name,"Top_mean_CAT%d",counter);
      RooRealVar mT(name,name,130,0,200);
      sprintf(name,"Top_sigma_CAT%d",counter);
      RooRealVar sT(name,name,50,0,200);

      sprintf(name,"Top_mean_shifted_CAT%d",counter);
      RooFormulaVar mTShift(name,"@0*@1",RooArgList(mT,*(kJES[isel])));
      sprintf(name,"Top_sigma_shifted_CAT%d",counter);
      RooFormulaVar sTShift(name,"@0*@1",RooArgList(sT,*(kJER[isel])));

      sprintf(name,"Top_model_CAT%d",counter);

      RooGaussian *modelT = new RooGaussian(name,name,x,mTShift,sTShift); 
    
      RooFitResult *resT = modelT->fitTo(*roohist_T[icat],RooFit::Save(),SumW2Error(kTRUE),"q");

		modelT->Print();
		resT->Print();

      /*
      TF1 *tmp_func = new TF1("tmpFunc","gaus",XMIN,XMAX);
      tmp_func->SetParameters(1,a0.getVal(),a1.getVal());
      if (icat < 3) {
        float norm = tmp_func->Integral(XMIN,XMAX)/hTopYield->GetBinWidth(1);
        tmp_func->SetParameter(0,hTopYield->Integral()/norm);
      }
      else {
        float norm = tmp_func->Integral(XMIN,XMAX)/hSTYield->GetBinWidth(1);
        tmp_func->SetParameter(0,hSTYield->Integral()/norm);
      }  
      */
      canT->cd(icat+1);
      RooPlot* frame = x.frame();
		frame->GetYaxis()->SetRangeUser(0.,hTopYield->GetBinContent(hTopYield->GetMaximumBin())*1.1);
      roohist_T[icat]->plotOn(frame);
      modelT->plotOn(frame,RooFit::LineWidth(2));
      //modelT->plotOn(frame,VisualizeError(*resT,1,kTRUE),FillColor(kGray),MoveToBack());
      frame->GetXaxis()->SetTitle("M_{bb} (GeV)");
      frame->Draw();
      //tmp_func->Draw("sameL");
		lastline->SetTitle("Top template");
		pave->Draw();

		TPaveText *paveT = new TPaveText(0.2,0.18,0.4,0.30,"NDC");
		paveT->SetTextAlign(11);
      paveT->SetFillColor(0);
      paveT->SetBorderSize(0);
      paveT->SetTextFont(82);
      paveT->SetTextSize(0.030);
		paveT->AddText(TString::Format("mT: %.2f #pm %.2f",mT.getValV(),mT.getError()));
		paveT->AddText(TString::Format("sT: %.2f #pm %.2f",sT.getValV(),sT.getError()));
		//paveT->AddText(TString::Format("mTShift: %.2f %.2f",mTShift.getValV(),mTShift.getValV()));
		//paveT->AddText(TString::Format("sTShift: %.2f %.2f",sTShift.getValV(),sTShift.getValV()));
		//paveT->Draw();
		gPad->Update();
		paveT->SetY2NDC(paveT->GetY1NDC()+paveT->GetListOfLines()->GetSize()*0.032);

		can->cd();
		frame->Draw();
		pave->Draw();
		//paveT->Draw();
		//gPad->Update();
		//paveT->SetY2NDC(paveT->GetY1NDC()+paveT->GetListOfLines()->GetSize()*0.032);
		can->SaveAs(TString::Format("%s/bkg_T_CAT%d.pdf",FULLPATH.Data(),counter).Data());
		can->SaveAs(TString::Format("%s/bkg_T_CAT%d.png",FULLPATH.Data(),counter).Data());

      mZ.setConstant(kTRUE);
      sZ.setConstant(kTRUE);
      aZ.setConstant(kTRUE);
      nZ.setConstant(kTRUE);
      Zb0.setConstant(kTRUE);
      Zb1.setConstant(kTRUE);
      Zb2.setConstant(kTRUE);
      fZsig.setConstant(kTRUE);
      
      mT.setConstant(kTRUE);
      sT.setConstant(kTRUE);

      w->import(modelZ);
      w->import(*modelT);
      w->import(*YieldZ);
      w->import(*YieldT);
      w->import(*YieldTT);
      w->import(*YieldST);
      YieldZ->Print();
      YieldW->Print();
      YieldT->Print();
      YieldTT->Print();
      YieldST->Print();
      counter++;
    }// category loop
	 canT->SaveAs(TString::Format("%s/%s.png",FULLPATH.Data(),canT->GetName()));
	 canZ->SaveAs(TString::Format("%s/%s.png",FULLPATH.Data(),canZ->GetName()));
	 canT->SaveAs(TString::Format("%s/%s.pdf",FULLPATH.Data(),canT->GetName()));
	 canZ->SaveAs(TString::Format("%s/%s.pdf",FULLPATH.Data(),canZ->GetName()));
	 delete can;
  }// selection loop
  XMAX -= XMAXDIFF;
  makeDirs(OUTPATH+"/output/");
  w->Print();
  if (XMAXDIFF==0) w->writeToFile(TString::Format("%s/output/bkg_shapes_workspace_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX).Data());
  else             w->writeToFile(TString::Format("%s/output/bkg_shapes_workspace_B%.f-%.f%.f.root",OUTPATH.Data(),XMIN,XMAX,XMAX+XMAXDIFF).Data());
}

void makeDirs(TString dirName) {
	 system(TString::Format("[ ! -d %s ] && mkdir %s",dirName.Data(),dirName.Data()).Data());
}

