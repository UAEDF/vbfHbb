using namespace RooFit;
void CreateDataTemplates(double dX, float XMIN, float XMAX, int BRN_ORDER_NOM, int BRN_ORDER_VBF, TString OUTPATH, bool withTF==true, int NTFPAR_NOM==1, int NTFPAR_VBF==1)
{
  gROOT->ProcessLineSync(".x ../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  const int NSEL(2);
  const int NCAT[NSEL] = {4,3};
  const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};
  char name[1000];
  TString SELECTION[NSEL] = {"NOM","VBF"};
  TString SELTAG[NSEL]    = {"NOM","PRK"};
  TString MBB[NSEL] = {"mbbReg[1]","mbbReg[2]"};
  TString MVA[NSEL] = {"mvaNOM","mvaVBF"};
  TString PATH("flat/");
  int NTFPAR[NSEL] = {NTFPAR_NOM, NTFPAR_VBF};

  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  TFile *fBKG  = TFile::Open(TString::Format("%s/output/bkg_shapes_workspace.root",OUTPATH.Data()).Data());
  RooWorkspace *wBkg = (RooWorkspace*)fBKG->Get("w");
  RooWorkspace *w = new RooWorkspace("w","workspace");
  //RooRealVar x(*(RooRealVar*)wBkg->var("mbbReg"));
  TTree *tr;
  TH1F *h,*hBlind;
  TCanvas *canFit[5]; 
  RooDataHist *roohist[5],*roohist_blind[5];

  if (withTF) {
		TFile *fTransfer = TFile::Open(TString::Format("%s/output/transferFunctions.root",OUTPATH.Data()).Data());
		TF1 *transFunc;
  }

  int counter(0);
  int NPAR(0);
  TString CATSTRING(""), SELSTRING(""), BRNSTRING("");

  for(int isel=0;isel<NSEL;isel++) {
	 SELSTRING = TString::Format("_sel%s",SELECTION[isel].Data());
	 int BRN_ORDER = (SELECTION[isel]=="NOM" ? BRN_ORDER_NOM : BRN_ORDER_VBF);
	 NPAR = BRN_ORDER;
	 const int NCATSEL=NCAT[isel];
	  
    TFile *fDATA = TFile::Open(PATH+"Fit_data"+SELSTRING+".root");
    RooRealVar *brn[NCATSEL][8];
    RooArgSet brn_params[NCATSEL];
	 RooAbsPdf *qcd_pdf[NCATSEL];
	 RooBernstein *qcd_pdf_aux[NCATSEL];
	 RooBernstein *qcd_pdf_aux1[NCATSEL];
	 RooProdPdf *qcd_pdf_aux2[NCATSEL];
	 RooAddPdf *model[NCATSEL];
	 RooRealVar *nQCD[NCATSEL];
	 RooGenericPdf *transfer[NCATSEL];
	 for (int icat=0; icat<NCAT[isel]; icat++) {
	 	for (int ib=0; ib<8; ib++) brn[icat][ib] = NULL;
		qcd_pdf[icat] = NULL;
		qcd_pdf_aux[icat] = NULL;
		qcd_pdf_aux1[icat] = NULL;
		qcd_pdf_aux2[icat] = NULL;
		model[icat] = NULL;
		nQCD[icat] = NULL;
		transfer[icat] = NULL;
	 }

	 for(int icat=0; icat<NCAT[isel]; icat++) {
	 	 printf("\n\n\033[1;31mCurrent selection: %s\033[m\n",SELECTION[isel].Data());
	 	 printf("\033[1;31mCurrent category: %d(%d)\033[m\n",counter,icat);
		 CATSTRING = TString::Format("_CAT%d",counter);	
		 for(int ib=0;ib<=NPAR;ib++) {
			if (withTF && icat>0) break;
			BRNSTRING = TString::Format("b%d",ib);
	      brn[icat][ib] = new RooRealVar(BRNSTRING+SELSTRING+CATSTRING,BRNSTRING+SELSTRING+CATSTRING,0.5,0,10.);
	      brn_params[icat].add(*brn[icat][ib]);
	    }
      
		 RooRealVar x("mbbReg"+CATSTRING,"mbbReg"+CATSTRING,XMIN,XMAX);
		 const int PARS=NTFPAR[isel]+1;
		 float p[PARS], e[PARS];
		 RooRealVar *trans_p[PARS];

		 if (withTF) {
      	sprintf(name,("fitRatio_sel"+SELTAG[isel]+CATSTRING).Data());
      	transFunc = (TF1*)fTransfer->Get(name);
      	// --- The error on the tranfer function parameters is shrinked because the correlations are ingored. 
      	// --- Must be consistent with TransferFunctions.C
			for (int ipar=0; ipar<PARS; ipar++) {
				p[ipar] = transFunc->GetParameter(ipar);
				e[ipar] = transFunc->GetParError(ipar);

				trans_p[ipar] = new RooRealVar(TString::Format("trans_p%i_CAT%d",ipar,counter),TString::Format("trans_p%i_CAT%d",ipar,counter),p[ipar]);

				if (SELECTION[isel]=="NOM") trans_p[ipar]->setError(0.5*e[ipar]);
				else if (SELECTION[isel]=="VBF") trans_p[ipar]->setError(0.05*e[ipar]);

				trans_p[ipar]->setConstant(kTRUE);
			}

			if (NTFPAR[isel]==1) transfer[icat] = new RooGenericPdf(TString::Format("transfer_CAT%d",counter),"@2*@0+@1",RooArgList(x,*trans_p[0],*trans_p[1])); 
			else if (NTFPAR[isel]==2) transfer[icat] = new RooGenericPdf(TString::Format("transfer_CAT%d",counter),"@3*@0*@0+@2*@0+@1",RooArgList(x,*trans_p[0],*trans_p[1],*trans_p[2])); 
		 }	
            
      sprintf(name,("FitData"+SELSTRING+CATSTRING).Data());
      canFit[icat] = new TCanvas(name,name,900,600);
      canFit[icat]->cd(1)->SetBottomMargin(0.4);
      sprintf(name,"Hbb/events");
      tr = (TTree*)fDATA->Get(name); 
      sprintf(name,("hMbb"+SELSTRING+CATSTRING).Data());
      int NBINS = (XMAX-XMIN)/dX;
      
      h = new TH1F(name,name,NBINS,XMIN,XMAX);

      sprintf(name,("hMbb_blind"+SELSTRING+CATSTRING).Data());
      hBlind = new TH1F(name,name,NBINS,XMIN,XMAX);

      sprintf(name,"%s>%1.2f && %s<=%1.2f",MVA[isel].Data(),MVA_BND[isel][icat],MVA[isel].Data(),MVA_BND[isel][icat+1]);
      TCut cut(name);
      sprintf(name,"%s>%1.2f && %s<=%1.2f && %s>100 && %s<150",MVA[isel].Data(),MVA_BND[isel][icat],MVA[isel].Data(),MVA_BND[isel][icat+1],MBB[isel].Data(),MBB[isel].Data());
      TCut cutBlind(name);
      tr->Draw(MBB[isel]+">>"+h->GetName(),cut); 
      tr->Draw(MBB[isel]+">>"+hBlind->GetName(),cutBlind); 
      sprintf(name,("yield_data"+CATSTRING).Data());
      RooRealVar *Yield = new RooRealVar(name,name,h->Integral());
      
      sprintf(name,("data_hist"+CATSTRING).Data());
      roohist[icat] = new RooDataHist(name,name,x,h);

      sprintf(name,("data_hist_blind"+CATSTRING).Data());
      roohist_blind[icat] = new RooDataHist(name,name,x,hBlind);
        
		if (withTF) {
        if (icat == 0) {
          for(int ib=0;ib<=NPAR;ib++) brn[icat][ib]->setConstant(kFALSE); 
          sprintf(name,("qcd_model"+CATSTRING).Data());
          qcd_pdf_aux[icat] = new RooBernstein(name,name,x,brn_params[icat]);
          qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux[icat]);
     		}
     		else {
           for(int ib=0;ib<=NPAR;ib++) brn[0][ib]->setConstant(kTRUE);
     		  sprintf(name,"qcd_model_aux1_CAT%d",counter);
     		  qcd_pdf_aux1[icat] = new RooBernstein(name,name,x,brn_params[0]);
     		  sprintf(name,"qcd_model_CAT%d",counter);
     		  qcd_pdf_aux2[icat] = new RooProdPdf(name,name,RooArgSet(*transfer[icat],*qcd_pdf_aux1[icat]));
     		  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux2[icat]);
     		} 
		}
		else {
        for(int ib=0;ib<=NPAR;ib++) brn[icat][ib]->setConstant(kFALSE); 
        sprintf(name,("qcd_model"+CATSTRING).Data());
        qcd_pdf_aux[icat] = new RooBernstein(name,name,x,brn_params[icat]);
        qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux[icat]);
		}

      sprintf(name,("Z_model"+CATSTRING).Data());
      RooAbsPdf *z_pdf = (RooAbsPdf*)wBkg->pdf(name);
      sprintf(name,("Top_model"+CATSTRING).Data());
      RooAbsPdf *top_pdf = (RooAbsPdf*)wBkg->pdf(name);

      sprintf(name,("yield_ZJets"+CATSTRING).Data());
      RooRealVar *nZ = (RooRealVar*)wBkg->var(name);
      sprintf(name,("yield_Top"+CATSTRING).Data());
      RooRealVar *nT = (RooRealVar*)wBkg->var(name);
      sprintf(name,("yield_QCD"+CATSTRING).Data());
      nQCD[icat] = new RooRealVar(name,name,1000,0,1e+10);
      nZ->setConstant(kTRUE);
      nT->setConstant(kTRUE);
    
		//qcd_pdf[icat]->Print();
      sprintf(name,("bkg_model"+CATSTRING).Data());
      model[icat] = new RooAddPdf(name,name,RooArgList(*z_pdf,*top_pdf,*qcd_pdf[icat]),RooArgList(*nZ,*nT,*nQCD[icat]));
		model[icat]->Print();
      
      RooFitResult *res = model[icat]->fitTo(*roohist[icat],RooFit::Save());
      res->Print();
      
      RooPlot* frame = x.frame();
      RooPlot* frame1 = x.frame();
      roohist[icat]->plotOn(frame);
      model[icat]->plotOn(frame,LineWidth(2));
      cout<<"chi2/ndof = "<<frame->chiSquare()<<endl;
      RooHist *hresid = frame->residHist(); 
      //model[icat]->plotOn(frame,RooFit::VisualizeError(*res,1,kFALSE),FillColor(kGray)MoveToBack());
      model[icat]->plotOn(frame,Components(*qcd_pdf[icat]),LineWidth(2),LineColor(kBlack),LineStyle(kDashed));
      model[icat]->plotOn(frame,Components(*z_pdf),LineWidth(2),LineColor(kBlue));
      model[icat]->plotOn(frame,Components(*top_pdf),LineWidth(2),LineColor(kGreen+1));
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
		  if (withTF && icat>0) break;
        brn[icat][ib]->setConstant(kFALSE);
      }
      
		if (withTF) {
			for (int ipar=0; ipar<NTFPAR[isel]+1; ipar++) {
//if (icat>0) trans_p[ipar]->setConstant(kFALSE);
				w->import(*trans_p[ipar]);
			}
		}

      w->import(*roohist[icat]);
      w->import(*roohist_blind[icat]);
      w->import(*model[icat]);
      w->import(*Yield);
      counter++; 

		system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
		system(TString::Format("[ ! -d %s/plots ] && mkdir %s/plots",OUTPATH.Data(),OUTPATH.Data()).Data());
		system(TString::Format("[ ! -d %s/plots/datTemplates ] && mkdir %s/plots/datTemplates",OUTPATH.Data(),OUTPATH.Data()).Data());
		canFit[icat]->SaveAs(TString::Format("%s/plots/datTemplates/%s.png",OUTPATH.Data(),h->GetName()));
    }// category loop
  }// selection loop
  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  w->Print();
  w->writeToFile(TString::Format("%s/output/data_shapes_workspace_BRN%d+%d.root",OUTPATH.Data(),BRN_ORDER_NOM,BRN_ORDER_VBF));
}
