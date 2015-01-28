using namespace RooFit;
using namespace std;

void CreateDataTemplatesTest(double dX, float XMIN, float XMAX, int CATMIN, int CATMAX, int BRN_ORDER_NOM, int BRN_ORDER_VBF, TString OUTPATH, TString TR, TString BR, bool FitWithSignal, int NdXchi=1)
{
  gROOT->ProcessLineSync(".x ../../common/styleCMSTDR.C");
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

  float SCALE[3][NSEL][NCAT[0]] = {
	  {{1.0,0.5,0.62,0.67},{1.0,1.2,1.7}},
	  {{1.0,0.04,0.05,0.07},{1.0,0.085,0.1}},
	  {{1.0,0.01,0.01,0.01},{1.0,0.015,0.022}}
  };
  
  float pset[4][3] = {{1,0.1,1},{1.5,0.01,2},{0.007,0.03,0.007},{0,0.4,0.017}} ;
  float pmin[4][3] = {{0.1,0,0},{1,0.001,-0.1},{0.0001,0.001,0.0001},{-3.1416,0.01,0.005}};
  float pmax[4][3] = {{10,10,3},{10,0.1,50},{0.1,10,0.1},{3.1416,1,0.05}};

  const int BRNdsize(4);
  TString BRNKEYS[BRNdsize] = {"expPow","tanh","modG","sine1"};
  TString BRNVALS[BRNdsize] = {"pow(@0-30,@1) * exp(-@2*pow(@0,@3))","@1 - tanh(@2*@0 - @3)","exp(-@1*@0) * TMath::Erfc(@2 - @3*@0)","1.0 + @2*sin(@3*@0 + @1)"};

  const int TRFdsize(6);
  TString TRFKEYS[TRFdsize] = {"POL1","POL2","POL3","FixedPOL1","FixedPOL2","FixedPOL3"};
  TString TRFVALS[TRFdsize] = {"@1*@0+1","@2*@0*@0+@1*@0+1","@3*@0*@0*@0+@2*@0*@0+@1*@0+1","@2*@0+@1","@3*@0*@0+@2*@0+@1","@4*@0*@0*@0+@3*@0*@0+@2*@0+@1"};

  makeDirs(OUTPATH);
  makeDirs(OUTPATH+"/output/");
  if (XMAXDIFF==0) TFile *fBKG  = TFile::Open(TString::Format("%s/output/bkg_shapes_workspace_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX).Data());
  else             TFile *fBKG  = TFile::Open(TString::Format("%s/output/bkg_shapes_workspace_B%.f-%.f%.f.root",OUTPATH.Data(),XMIN,XMAX,XMAX+XMAXDIFF).Data());
  RooWorkspace *wBkg = (RooWorkspace*)fBKG->Get("w");
  if (XMAXDIFF==0) TFile *fSIG  = TFile::Open(TString::Format("%s/output/signal_shapes_workspace_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX).Data());
  else             TFile *fSIG  = TFile::Open(TString::Format("%s/output/signal_shapes_workspace_B%.f-%.f%.f.root",OUTPATH.Data(),XMIN,XMAX,XMAX+XMAXDIFF).Data());
  RooWorkspace *wSig = (RooWorkspace*)fSIG->Get("w");
  RooWorkspace *w = new RooWorkspace("w","workspace");

  //RooRealVar x(*(RooRealVar*)wBkg->var("mbbReg"));
  TTree *tr;
  TH1F *h,*hBlind,*hB1;
  TCanvas *canFit[5]; 
  RooDataHist *roohist[5],*roohist_blind[5],*roohistB1[5];

  bool withTRF=false, withBRN=false;
  if (TR=="") withTRF=false;
  else if (TR=="BRN") withTRF=false;
  else withTRF=true;
  if (BR=="") withBRN=false;
  else withBRN=true;

  TString tTRF="", tBRN="", sTRF="";
  if (withTRF || TR=="BRN") { tTRF=TString::Format("_Fit%s",TR.Data()); }
  if (withTRF && TR(0,5)=="Fixed") { sTRF=TString::Format("%s",TR(5,4).Data()); }
  else if (withTRF && TR(0,5)!="Fixed") { sTRF=TR; }
  if (withBRN) { tBRN=TString::Format("_Alt%s",BR.Data()); }

  if (withTRF) {
		TFile *fTransfer = TFile::Open(TString::Format("%s/output/transferFunctions_B%.f-%.f.root",OUTPATH.Data(),XMIN,XMAX).Data());
		TF1 *transFunc;
  }

  int counter(CATMIN);
  int NPAR(0);
  TString CATSTRING(""), SELSTRING(""), BRNSTRING("");

  int TRFmatch(-1),BRNmatch(-1);
  for (int im=0; im<TRFdsize; im++) {
     if (TRFKEYS[im]==TR) { TRFmatch=im; break; }
  }
  for (int im=0; im<BRNdsize; im++) {
     if (BRNKEYS[im]==BR) { BRNmatch=im; break; }
  }
  
  for(int isel=0;isel<NSEL;isel++) {
	 SELSTRING = TString::Format("_sel%s",SELECTION[isel].Data());
	 int BRN_ORDER = (SELECTION[isel]=="NOM" ? BRN_ORDER_NOM : BRN_ORDER_VBF);
	 if (BR == "" || TR == "BRN") NPAR = BRN_ORDER;
	 else if (BR(0,3)=="brn") NPAR = atoi(BR(3,1).Data())+1;
	 else NPAR = 2; 
	 const int NCATSEL=NCAT[isel];
	  
    TFile *fDATA = TFile::Open(PATH+"Fit_data"+SELSTRING+".root");
    RooRealVar *brn[NCATSEL][8];
    RooArgSet brn_params[NCATSEL];
	 RooAbsPdf *qcd_pdf[NCATSEL];
	 RooBernstein *qcd_pdf_Baux[NCATSEL];
	 RooBernstein *qcd_pdf_Baux1[NCATSEL];
	 RooGenericPdf *qcd_pdf_Gaux[NCATSEL];
	 RooGenericPdf *qcd_pdf_Gaux1[NCATSEL];
	 RooProdPdf *qcd_pdf_aux2[NCATSEL];
	 RooAddPdf *model[NCATSEL];
	 RooRealVar *nQCD[NCATSEL];
	 RooGenericPdf *transfer[NCATSEL];

	 for (int icat=0; icat<NCAT[isel]; icat++) {
	 	for (int ib=0; ib<8; ib++) brn[icat][ib] = NULL;
		qcd_pdf[icat] = NULL;
		qcd_pdf_Baux[icat] = NULL;
		qcd_pdf_Baux1[icat] = NULL;
		qcd_pdf_Gaux[icat] = NULL;
		qcd_pdf_Gaux1[icat] = NULL;
		qcd_pdf_aux2[icat] = NULL;
		model[icat] = NULL;
		nQCD[icat] = NULL;
		transfer[icat] = NULL;
	 }
	 
	 if (isel==0 && NCAT[0]<=CATMIN) continue;
	 if (isel==1 && CATMAX<NCAT[0]) continue;

	 for(int icat=0; icat<NCAT[isel]; icat++) {
		 if (counter>CATMAX) break;
	 	 printf("\n\n\033[1;31mCurrent selection: %s\033[m\n",SELECTION[isel].Data());
	 	 printf("\033[1;31mCurrent category: %d(%d)\033[m\n",counter,icat);
		 CATSTRING = TString::Format("_CAT%d",counter);	
		 for(int ib=0;ib<=NPAR;ib++) {
			if (withTRF && icat>0) break;
			if (BR=="" || BR(0,3)=="brn") {
				BRNSTRING = TString::Format("b%d",ib);
		      brn[icat][ib] = new RooRealVar(BRNSTRING+SELSTRING+CATSTRING,BRNSTRING+SELSTRING+CATSTRING,0.5,0,10.);
	   	   brn_params[icat].add(*brn[icat][ib]);
			}
			else {
				BRNSTRING = TString::Format("p%d",ib);
				//cout << NPAR << " " << BRNmatch << " " << ib << endl;
				//cout << pset[BRNmatch][ib] << " " << pmin[BRNmatch][ib] << " " << pmax[BRNmatch][ib] << endl; 
		      brn[icat][ib] = new RooRealVar(BRNSTRING+SELSTRING+CATSTRING,BRNSTRING+SELSTRING+CATSTRING,pset[BRNmatch][ib],pmin[BRNmatch][ib],pmax[BRNmatch][ib]);
	   	   brn_params[icat].add(*brn[icat][ib]);
			}
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

		 if (icat!=0 && withTRF) {
      	sprintf(name,"fitRatio_sel%s_CAT%d_%s",SELTAG[isel].Data(),counter,sTRF.Data());
      	transFunc = (TF1*)fTransfer->Get(name);
			NPARS = transFunc->GetNpar();
      	// --- The error on the tranfer function parameters is shrinked because the correlations are ingored. 
      	// --- Must be consistent with TransferFunctions.C
			for (int ipar=0; ipar<NPARS; ipar++) {
				p[ipar] = transFunc->GetParameter(ipar);
				e[ipar] = transFunc->GetParError(ipar);

				trans_p[ipar] = new RooRealVar(TString::Format("trans_%s_p%i_CAT%d",sTRF.Data(),ipar,counter),TString::Format("trans_%s_p%i_CAT%d",sTRF.Data(),ipar,counter),p[ipar],-1000.,1000.);

				if (TR=="FixedPOL1") trans_p[ipar]->setError(SCALE[0][isel][icat]*e[ipar]);
				if (TR=="FixedPOL2") trans_p[ipar]->setError(SCALE[1][isel][icat]*e[ipar]);
				if (TR=="FixedPOL3") trans_p[ipar]->setError(SCALE[2][isel][icat]*e[ipar]);
				else trans_p[ipar]->setError(e[ipar]); // expo, exppow, brn4, ...
				printf("\033[1;31mError %s: %.2g x %.2g = %.2g (sel%s,CAT%d)\033[m\n",TR.Data(),e[ipar],SCALE[2][isel][icat],SCALE[2][isel][icat]*e[ipar],SELTAG[isel].Data(),icat);

				trans_p[ipar]->setConstant(kTRUE);
			}
			
     	   if (TR=="POL1")  { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[1])); }
	      if (TR=="POL2")  { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[1],*trans_p[2])); }
         if (TR=="POL3")  { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[1],*trans_p[2],*trans_p[3])); }
         if (TR=="FixedPOL1") { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[0],*trans_p[1])); }
         if (TR=="FixedPOL2") { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[0],*trans_p[1],*trans_p[2])); }
         if (TR=="FixedPOL3") { transfer[icat] = new RooGenericPdf(TString::Format("transfer_%s_CAT%d",TR.Data(),counter).Data(),TRFVALS[TRFmatch].Data(),RooArgList(x,*trans_p[0],*trans_p[1],*trans_p[2],*trans_p[3])); }
		}

      sprintf(name,("FitData"+SELSTRING+CATSTRING).Data());
      canFit[icat] = new TCanvas(name,name,900,600);
      canFit[icat]->cd(1)->SetBottomMargin(0.4);
      sprintf(name,"Hbb/events");
      tr = (TTree*)fDATA->Get(name); 
      
		sprintf(name,("hMbb"+SELSTRING+CATSTRING).Data());
      int NBINS = (XMAX-XMIN)/dX;
      int NBINSB1 = (XMAX-XMIN)/dX/NdXchi;
      h = new TH1F(name,name,NBINS,XMIN,XMAX);
      
		sprintf(name,("hMbb_B1"+SELSTRING+CATSTRING).Data());
      hB1 = new TH1F(name,name,NBINSB1,XMIN,XMAX);

      sprintf(name,("hMbb_blind"+SELSTRING+CATSTRING).Data());
      hBlind = new TH1F(name,name,NBINS,XMIN,XMAX);

      sprintf(name,"%s>%1.2f && %s<=%1.2f",MVA[isel].Data(),MVA_BND[isel][icat],MVA[isel].Data(),MVA_BND[isel][icat+1]);
      TCut cut(name);
      sprintf(name,"%s>%1.2f && %s<=%1.2f && %s>100 && %s<150",MVA[isel].Data(),MVA_BND[isel][icat],MVA[isel].Data(),MVA_BND[isel][icat+1],MBB[isel].Data(),MBB[isel].Data());
      TCut cutBlind(name);
      tr->Draw(MBB[isel]+">>"+h->GetName(),cut); 
      tr->Draw(MBB[isel]+">>"+hBlind->GetName(),cutBlind); 
      tr->Draw(MBB[isel]+">>"+hB1->GetName(),cut); 
      sprintf(name,("yield_data"+CATSTRING).Data());
      RooRealVar *Yield = new RooRealVar(name,name,h->Integral());
      
      sprintf(name,("data_hist"+CATSTRING).Data());
      roohist[icat] = new RooDataHist(name,name,x,h);

      sprintf(name,("data_hist_blind"+CATSTRING).Data());
      roohist_blind[icat] = new RooDataHist(name,name,x,hBlind);
        
      sprintf(name,("data_hist_B1"+CATSTRING).Data());
      roohistB1[icat] = new RooDataHist(name,name,x,hB1);
        
		if (withTRF) {
        if (icat == 0) {
           for(int ib=0;ib<=NPAR;ib++) brn[icat][ib]->setConstant(kFALSE); 
           sprintf(name,"qcd_model%s%s_CAT%d",tTRF.Data(),tBRN.Data(),counter);
			  if (BR=="" || BR(0,3)=="brn") {
				  qcd_pdf_Baux[icat] = new RooBernstein(name,name,x,brn_params[icat]);
   	     	  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_Baux[icat]);
			  }
			  else {
				  qcd_pdf_Gaux[icat] = new RooGenericPdf(name,ALTS[BRNi],RooArgSet(x,*brn[icat][0],*brn[icat][1],*brn[icat][2]));
   	     	  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_Gaux[icat]);
			  }
     		}
     		else {
           for(int ib=0;ib<=NPAR;ib++) brn[0][ib]->setConstant(kTRUE);
     		  sprintf(name,"qcd_model_aux1%s%s_CAT%d",tTRF.Data(),tBRN.Data(),counter);
			  if (BR=="" || BR(0,3)=="brn") qcd_pdf_Baux1[icat] = new RooBernstein(name,name,x,brn_params[0]);
			  else qcd_pdf_Gaux1[icat] = new RooGenericPdf(name,BRNVALS[BRNmatch],RooArgSet(x,*brn[0][0],*brn[0][1],*brn[0][2]));
     		  sprintf(name,"qcd_model%s%s_CAT%d",tTRF.Data(),tBRN.Data(),counter);
     		  if (BR=="" || BR(0,3)=="brn") qcd_pdf_aux2[icat] = new RooProdPdf(name,name,RooArgSet(*transfer[icat],*qcd_pdf_Baux1[icat]));
			  else qcd_pdf_aux2[icat] = new RooProdPdf(name,name,RooArgSet(*transfer[icat],*qcd_pdf_Gaux1[icat]));
     		  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_aux2[icat]);
     		} 
		}
		else {
        for(int ib=0;ib<=NPAR;ib++) brn[icat][ib]->setConstant(kFALSE); 
        sprintf(name,"qcd_model%s%s_CAT%d",tTRF.Data(),tBRN.Data(),counter);
		  if (BR=="" || BR(0,3)=="brn") {
			  qcd_pdf_Baux[icat] = new RooBernstein(name,name,x,brn_params[icat]);
        	  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_Baux[icat]);
		  }
		  else {
			  qcd_pdf_Gaux[icat] = new RooGenericPdf(name,BRNVALS[BRNmatch],RooArgSet(x,*brn[icat][0],*brn[icat][1],*brn[icat][2]));
        	  qcd_pdf[icat] = dynamic_cast<RooAbsPdf*> (qcd_pdf_Gaux[icat]);
		  }
		}

		TString MSTRING="_m125";
		TString MASSSTRING="_mass125";

      sprintf(name,("Z_model"+CATSTRING).Data());
      RooAbsPdf *z_pdf = (RooAbsPdf*)wBkg->pdf(name);
      sprintf(name,("Top_model"+CATSTRING).Data());
      RooAbsPdf *top_pdf = (RooAbsPdf*)wBkg->pdf(name);
      sprintf(name,("signal_model"+MSTRING+CATSTRING).Data());
  	   RooAbsPdf *sig_pdf = (RooAbsPdf*)wSig->pdf(name);

      sprintf(name,("yield_ZJets"+CATSTRING).Data());
      RooRealVar *nZ = (RooRealVar*)wBkg->var(name);
      sprintf(name,("yield_Top"+CATSTRING).Data());
      RooRealVar *nT = (RooRealVar*)wBkg->var(name);
      sprintf(name,("yield_QCD"+CATSTRING).Data());
      nQCD[icat] = new RooRealVar(name,name,1000,0,1e+10);
      nZ->setConstant(kTRUE);
      nT->setConstant(kTRUE);
      sprintf(name,("yield_signalVBF"+MASSSTRING+CATSTRING).Data());
      RooRealVar *nSigVBF = (RooRealVar*)wSig->var(name);
      sprintf(name,("yield_signalGF"+MASSSTRING+CATSTRING).Data());
      RooRealVar *nSigVBF = (RooRealVar*)wSig->var(name);
      RooRealVar *nSigGF = (RooRealVar*)wSig->var(name);
		sprintf(name,("yield_signal"+MSTRING+CATSTRING).Data());
		RooRealVar *nSig = new RooRealVar(name,name,nSigVBF->getValV()+nSigGF->getValV(),0.,400.);
		nSig->setConstant(kTRUE);

   	//sig_pdf->Print();
	  	//nSig->Print();

		//qcd_pdf[icat]->Print();
      sprintf(name,"bkg_model%s%s_CAT%d",tTRF.Data(),tBRN.Data(),counter);
		if (FitWithSignal) { 
        model[icat] = new RooAddPdf(name,name,RooArgList(*z_pdf,*top_pdf,*qcd_pdf[icat],*sig_pdf),RooArgList(*nZ,*nT,*nQCD[icat],*nSig));
		} else {    
        model[icat] = new RooAddPdf(name,name,RooArgList(*z_pdf,*top_pdf,*qcd_pdf[icat]),RooArgList(*nZ,*nT,*nQCD[icat]));
		}   
		//model[icat]->Print();
		//qcd_pdf[icat]->Print();
      
      RooFitResult *res = model[icat]->fitTo(*roohist[icat],RooFit::Save());
      res->Print();
      
      RooPlot* frame = x.frame();
      RooPlot* frame1 = x.frame();
      //roohist[icat]->plotOn(frame);
      roohistB1[icat]->plotOn(frame);
      model[icat]->plotOn(frame,LineWidth(2));
		cout<<"chi2/ndof = "<<frame->chiSquare()<<endl;
		
		RooHist *hresid = frame->residHist(); 

		double xVal=0, y=0, Sum2=0, Sum2Poisson=0;
		int yield = 0;	
		for( int i=0; i<hresid->GetN(); i++) {
			hresid->GetPoint(i,xVal,y);
			//roohist[icat]->get(i);
			roohistB1[icat]->get(i);
			//double error = roohist[icat]->weightError(RooAbsData::SumW2);
			double error = roohistB1[icat]->weightError(RooAbsData::SumW2);
			double lo, hi, errorPoisson;
			//roohist[icat]->weightError(lo,hi);		
			roohistB1[icat]->weightError(lo,hi);		
			if( y >= 0 )  errorPoisson = lo;
			else errorPoisson = hi;
			if( error != 0 ) {
			  Sum2 += y*y/(error*error);
			  Sum2Poisson += y*y/(errorPoisson*errorPoisson);
			}
			//yield += roohist[icat]->weight();
			yield += roohistB1[icat]->weight();
		}
		if ( TR=="" || icat==0 ) {
		cout << "\033[0;38;5;22m";
	 	//cout << "[ERROR CALC] " << BR.Data() << "  " << dX << "  " << hresid->GetN() << " should be equal to " << roohist[icat]->numEntries() << endl;
	 	cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << hresid->GetN() << " should be equal to " << roohistB1[icat]->numEntries() << endl;
		//cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "NBINS: " << NBINS << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "chi2 binenlarge: " << NdXchi << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "NBINS: " << NBINSB1 << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "NPARS: " << NPAR+1 << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2:  " << Sum2 << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2P: " << Sum2Poisson << endl;
	//	cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2 / NDOF: " << Sum2 / (NBINS - (NPAR+1)) << endl;
	//	cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2P / NDOF: " << Sum2Poisson / (NBINS - (NPAR+1)) << endl;
	//	cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "Probability chi squared: " << TString::Format("%.6f",TMath::Prob(Sum2,        (NBINS-(NPAR+1))))                 << endl;
	//	cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "                         " << TString::Format("%.6f",TMath::Prob(Sum2Poisson, (NBINS-(NPAR+1)))) << " (Poisson)" << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2 / NDOF: " << Sum2 / (NBINSB1 - (NPAR+1)) << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "CHI2P / NDOF: " << Sum2Poisson / (NBINSB1 - (NPAR+1)) << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "Probability chi squared: " << TString::Format("%.6f",TMath::Prob(Sum2,        (NBINSB1-(NPAR+1))))                 << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "                         " << TString::Format("%.6f",TMath::Prob(Sum2Poisson, (NBINSB1-(NPAR+1)))) << " (Poisson)" << endl;
		cout << "[ERROR CALC] " << BR.Data() << "  " << dX*NdXchi << "  " << "Minimized -log(L): " << res->minNll() << "\033[m" << endl << endl;
		}

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
		  if (withTRF && icat>0) break;
        brn[icat][ib]->setConstant((TR!="") ? kFALSE : kTRUE);//kFALSE);
      }
      
		if (withTRF) {
			for (int ipar=0; ipar<NPARS; ipar++) {
				if (icat>0) trans_p[ipar]->setConstant((TR(0,5)!="Fixed") ? kFALSE : kTRUE);
				w->import(*trans_p[ipar]);
			}
		}

      w->import(*roohist[icat]);
      w->import(*roohist_blind[icat]);
      w->import(*model[icat]);
      w->import(*Yield);
      counter++; 

		makeDirs(OUTPATH);
		makeDirs(OUTPATH+"/plots");
		makeDirs(OUTPATH+"/plots/datTemplates/");
		canFit[icat]->SaveAs(TString::Format("%s/plots/datTemplates/%s.png",OUTPATH.Data(),h->GetName()));
    }// category loop
  }// selection loop
  makeDirs(OUTPATH+"/output/");
//  w->Print();
  if (XMAXDIFF==0) w->writeToFile(TString::Format("%s/output/data_shapes_workspace_BRN%dp%d_B%.f-%.f%s%s%s.root",OUTPATH.Data(),BRN_ORDER_NOM,BRN_ORDER_VBF,XMIN,XMAX,tTRF.Data(),tBRN.Data(),FitWithSignal ? "_withSignal" : ""));
  else             w->writeToFile(TString::Format("%s/output/data_shapes_workspace_BRN%dp%d_B%.f-%.f%.f%s%s%s.root",OUTPATH.Data(),BRN_ORDER_NOM,BRN_ORDER_VBF,XMIN,XMAX,XMAX+XMAXDIFF,tTRF.Data(),tBRN.Data(),FitWithSignal ? "_withSignal" : ""));
} 

void makeDirs(TString dirName) {
	 system(TString::Format("[ ! -d %s ] && mkdir %s",dirName.Data(),dirName.Data()).Data());
}
