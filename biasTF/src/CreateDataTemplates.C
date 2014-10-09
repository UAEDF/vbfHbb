using namespace RooFit;
void CreateDataTemplates(double dX, float XMIN, float XMAX, int BRN_ORDER_NOM, int BRN_ORDER_VBF, TString OUTPATH, bool withTF==true, TString TRNOM, TString TRTAGNOM, TString TRVBF, TString TRTAGVBF, bool MERGE)
{
  gROOT->ProcessLineSync(".x ../common/styleCMSTDR.C");
  gROOT->ForceStyle();
  RooMsgService::instance().setSilentMode(kTRUE);
  for(int i=0;i<2;i++) {
    RooMsgService::instance().setStreamStatus(i,kFALSE);
  }
  const int NSEL(2);
  if (!MERGE) {const int NCAT[NSEL] = {4,3};}
  else {const int NCAT[NSEL] = {4,2};}
  if (!MERGE) {const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,0.8,1}};}
  else {const double MVA_BND[NSEL][NCAT[0]+1] = {{-0.6,0.0,0.7,0.84,1},{-0.1,0.4,1}};}
  char name[1000];
  TString SELECTION[NSEL] = {"NOM","VBF"};
  TString SELTAG[NSEL]    = {"NOM","PRK"};
  TString MBB[NSEL] = {"mbbReg[1]","mbbReg[2]"};
  TString MVA[NSEL] = {"mvaNOM","mvaVBF"};
  TString PATH("flat/");
  TString TR[NSEL] = {TRNOM,TRVBF};
  TString TRTAG[NSEL] = {TRTAGNOM,TRTAGVBF};
  float SCALE[3][NSEL][NCAT[0]] = {
	  {{1.0,0.5,0.62,0.67},{1.0,1.2,1.7}},
	  {{1.0,0.04,0.05,0.07},{1.0,0.085,0.1}},
	  {{1.0,0.01,0.01,0.01},{1.0,0.015,0.022}}
  };
  //float SCALE[3][NSEL][NCAT[0]] = {
  //   {{0.5,0.5,0.5,0.5},{0.5,0.5,0.5}},
  //   {{0.05,0.05,0.05,0.05},{0.05,0.05,0.05}},
  //   {{0.01,0.01,0.01,0.01},{0.02,0.015,0.022}}
  //};
  TString tag="";
  if (TRTAG[0]==TRTAG[1]) tag = TRTAG[0];
  else tag = TRTAG[0]+TRTAG[1];

  if (TRNOM=="-1" && TRVBF=="-1") withTF=false;
  TString tMERGE = MERGE ? "_CATmerge56" : "";
  if (MERGE) { SCALE[0][1][1] = 1.5; SCALE[2][1][1] = 0.02; }

  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  TFile *fBKG  = TFile::Open(TString::Format("%s/output/bkg_shapes_workspace%s.root",OUTPATH.Data(),tMERGE.Data()).Data());
  RooWorkspace *wBkg = (RooWorkspace*)fBKG->Get("w");
  RooWorkspace *w = new RooWorkspace("w","workspace");
  
  //RooRealVar x(*(RooRealVar*)wBkg->var("mbbReg"));
  TTree *tr;
  TH1F *h,*hBlind;
  TCanvas *canFit[5]; 
  RooDataHist *roohist[5],*roohist_blind[5];

  if (withTF) {
		TFile *fTransfer = TFile::Open(TString::Format("%s/output/transferFunctions%s.root",OUTPATH.Data(),tMERGE.Data()).Data());
		TF1 *transFunc;
  }

  int counter(0);
  int NPAR(0);
  TString CATSTRING(""), SELSTRING(""), BRNSTRING("");

  for(int isel=0;isel<NSEL;isel++) {
	 // force boolean TF usage
	 if (SELECTION[isel]=="NOM" && TRNOM=="-1") withTF=false;
	 else if (SELECTION[isel]=="NOM" && TRNOM!="-1") withTF=true;
	 else if (SELECTION[isel]=="VBF" && TRVBF=="-1") withTF=false;
	 else if (SELECTION[isel]=="VBF" && TRVBF!="-1") withTF=true;
	 else withTF=true;

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
		 if (MERGE && SELECTION[isel]=="VBF" && icat==1) counter = 56;
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
		 float p[5], e[5];
		 RooRealVar *trans_p[5];
		 for (int i=0; i<5; i++) {
			 p[i]=0;
			 e[i]=0;
			 trans_p[i]=0;
		 }
		 int NPARS=0;

		 if (withTF) {
      	sprintf(name,"fitRatio_sel%s_CAT%d%s",SELTAG[isel].Data(),counter,TRTAG[isel].Data());
      	transFunc = (TF1*)fTransfer->Get(name);
			NPARS = transFunc->GetNpar();
			cout << "NPARS = " << NPARS << " for function " << TR[isel].Data() << endl;
      	// --- The error on the tranfer function parameters is shrinked because the correlations are ingored. 
      	// --- Must be consistent with TransferFunctions.C
			for (int ipar=0; ipar<NPARS; ipar++) {
				p[ipar] = transFunc->GetParameter(ipar);
				e[ipar] = transFunc->GetParError(ipar);

				trans_p[ipar] = new RooRealVar(TString::Format("trans%s_p%i_CAT%d",TRTAG[isel].Data(),ipar,counter),TString::Format("trans%s_p%i_CAT%d",TRTAG[isel].Data(),ipar,counter),p[ipar]);

				if (TR[isel]=="pol1") trans_p[ipar]->setError(SCALE[0][isel][icat]*e[ipar]);
				else if (TR[isel]=="pol2") trans_p[ipar]->setError(SCALE[1][isel][icat]*e[ipar]);
				else if (TR[isel]=="pol3") trans_p[ipar]->setError(SCALE[2][isel][icat]*e[ipar]);
				else trans_p[ipar]->setError(e[ipar]); // expo, exppow, bern2, ...
				//if (SELECTION[isel]=="NOM") trans_p[ipar]->setError(0.5*e[ipar]);
				//else if (SELECTION[isel]=="VBF") trans_p[ipar]->setError(0.05*e[ipar]);
				printf("Error %s: %.2g x %.2g = %.2g (sel%s,CAT%d)\n",TR[isel].Data(),e[ipar],SCALE[2][isel][icat],SCALE[2][isel][icat]*e[ipar],SELTAG[isel].Data(),icat);

				trans_p[ipar]->setConstant(kTRUE);
			}

			if (TR[isel]=="pol1") transfer[icat] = new RooGenericPdf(TString::Format("transfer%s_CAT%d",TRTAG[isel].Data(),counter),"@2*@0+@1",RooArgList(x,*trans_p[0],*trans_p[1]));
			else if (TR[isel]=="pol2") transfer[icat] = new RooGenericPdf(TString::Format("transfer%s_CAT%d",TRTAG[isel].Data(),counter),"@3*@0*@0+@2*@0+@1",RooArgList(x,*trans_p[0],*trans_p[1],*trans_p[2]));
			else if (TR[isel]=="expo") transfer[icat] = new RooGenericPdf(TString::Format("transfer%s_CAT%d",TRTAG[isel].Data(),counter),"exp(@1+@2*@0)",RooArgList(x,*trans_p[0],*trans_p[1]));
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
          sprintf(name,"qcd_model%s_CAT%d",tag.Data(),counter);
          qcd_pdf_aux[icat] = new RooBernstein(name,name,x,brn_params[icat]);
          qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux[icat]);
     		}
     		else {
           for(int ib=0;ib<=NPAR;ib++) brn[0][ib]->setConstant(kTRUE);
     		  sprintf(name,"qcd_model_aux1%s_CAT%d",tag.Data(),counter);
     		  qcd_pdf_aux1[icat] = new RooBernstein(name,name,x,brn_params[0]);
     		  sprintf(name,"qcd_model%s_CAT%d",tag.Data(),counter);
     		  qcd_pdf_aux2[icat] = new RooProdPdf(name,name,RooArgSet(*transfer[icat],*qcd_pdf_aux1[icat]));
     		  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux2[icat]);
     		} 
		}
		else {
        for(int ib=0;ib<=NPAR;ib++) brn[icat][ib]->setConstant(kFALSE); 
        sprintf(name,"qcd_model%s_CAT%d",tag.Data(),counter);
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
      sprintf(name,"bkg_model%s_CAT%d",tag.Data(),counter);
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
        brn[icat][ib]->setConstant((TRTAG[isel]=="" || TR[isel]=="-1" || TRTAG[isel]=="_POL3" || TRTAG[isel]=="_LIN" || TRTAG[isel]=="_POL2" || TRTAG[isel]=="_POL1") ? kFALSE : kTRUE);//kFALSE);
      }
      
		if (withTF) {
			for (int ipar=0; ipar<NPARS; ipar++) {
				if (icat>0) trans_p[ipar]->setConstant((TRTAG[isel]=="" || TR[isel]=="-1" || TRTAG[isel]=="_POL3" || TRTAG[isel]=="_LIN" || TRTAG[isel]=="_POL2" || TRTAG[isel]=="_POL1") ? kFALSE : kTRUE);
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
	 withTF=false;
  }// selection loop
  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  w->Print();
  w->writeToFile(TString::Format("%s/output/data_shapes_workspace_BRN%d+%d%s%s.root",OUTPATH.Data(),BRN_ORDER_NOM,BRN_ORDER_VBF,tMERGE.Data(),tag.Data()));
}
