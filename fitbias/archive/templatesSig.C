void templatesSig(double XMIN,double XMAX,double dX,TString cutstring) {
	gROOT->ForceStyle();
	RooMsgService::instance().setSilentMode(kTRUE);
	for(int i=0;i<2;i++) RooMsgService::instance().setStreamStatus(i,kFALSE);

	const int NMASS(1);
	char name[1000];

	TFile *fVBF[NMASS];//,*fGF[NMASS];
	TH1F  *hVBF[NMASS][5],*hPassVBF;
	int H_MASS[1] = {125};
	TString SELECTION[1] = {"jetPt[0]>80 && jetPt[1]>70"};
	int NCAT[1] = {4};
	int LUMI[1] = {19281};
	int XSEC_VBF[1] = {0.911};

//	TH1F  *hGF[NMASS][5],*hVBF[NMASS][5],*hTOT[NMASS][5],*hPassGF,*hPassVBF;
	RooDataHist *RooHistFit[NMASS][5],*RooHistScaled[NMASS][5];
	RooAddPdf *model[NMASS][5];

	TCanvas *can[NMASS];
	TString PATH("rootfiles/");

	RooWorkspace *w = new RooWorkspace("w","workspace");
	int NBINS   = (XMAX-XMIN)/dX;

	RooRealVar x("mbbReg","mbbReg",XMIN,XMAX);
	RooRealVar kJES("CMS_scale_j","CMS_scale_j",1,0.9,1.1);
	RooRealVar kJER("CMS_res_j","CMS_res_j",1,0.8,1.2);
	kJES.setConstant(kTRUE);
	kJER.setConstant(kTRUE);

	TString TRIG_WT[2] = {"trigWtNOM[1]","trigWtVBF"};
	for(int iMass=0;iMass<NMASS;iMass++) {
		cout<<"Mass = "<<H_MASS[iMass]<<" GeV"<<endl;
		int counter(0);
		for(int iSEL=0;iSEL<2;iSEL++) {
//			sprintf(name,"Fit_VBFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[iSEL].Data());
			sprintf(name,"vbfHbb_uncertainties_JEx.root");
			cout << name << endl;
			fVBF[iMass]  = TFile::Open(PATH+TString(name));
//			hPassVBF = (TH1F*)fVBF[iMass]->Get("TriggerPass");

//			sprintf(name,"Fit_GFPowheg%d_sel%s.root",H_MASS[iMass],SELECTION[iSEL].Data());
//			fGF[iMass]  = TFile::Open(PATH+TString(name)); 
//			hPassGF = (TH1F*)fGF[iMass]->Get("TriggerPass");

			sprintf(name,"HMassTemplate_%d_sel%s",H_MASS[iMass],SELECTION[iSEL].Data());

			can[iMass] = new TCanvas(name,name,1200,800);
			can[iMass]->Divide(2,2);

			for(int icat=0;icat<NCAT[iSEL];icat++) { 
				sprintf(name,"Hbb%d/events",icat);
//				trVBF = (TTree*)fVBF[iMass]->Get(name);
//				trGF  = (TTree*)fGF[iMass]->Get(name);
				can[iMass]->cd(icat+1);
				sprintf(name,"mass_VBF%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[iSEL].Data(),icat);
				
				hVBF[iMass][icat] = (TH1F*)fVBF[iMass]->Get("histos/VBF125/h_NOM_VBF125_Hbb_mbbReg1;1");//new TH1F(name,name,NBINS,XMIN,XMAX);
//				hVBF[iMass][icat]->Sumw2();
//				TCut cut("puWt[0]*"+TRIG_WT[iSEL]+"*(mva"+SELECTION[iSEL]+">-1)");
//				TCut cut(cutstring.Data());
//				trVBF->Draw(MASS_VAR[iSEL]+">>"+TString(name),cut);

//				sprintf(name,"mass_GF%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[iSEL].Data(),icat);
//				hGF[iMass][icat] = new TH1F(name,name,NBINS,XMIN,XMAX);
//				hGF[iMass][icat]->Sumw2();
//				trGF->Draw(MASS_VAR[iSEL]+">>"+TString(name),cut);
//
		//		delete trVBF;
//				delete trGF;
				
				sprintf(name,"roohist_fit_mass%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[iSEL].Data(),icat);
				RooHistFit[iMass][icat] = new RooDataHist(name,name,x,hVBF[iMass][icat]);
				
//				hGF[iMass][icat]->Scale(LUMI[iSEL]*XSEC_GF[iMass]/hPassGF->GetBinContent(1));
				hVBF[iMass][icat]->Scale(LUMI[iSEL]*XSEC_VBF[iMass]/4794398.);//hPassVBF->GetBinContent(1));

//				sprintf(name,"mass_Total%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[iSEL].Data(),icat);
				hTOT[iMass][icat] = (TH1F*)hVBF[iMass][icat]->Clone(name);
//				hTOT[iMass][icat]->Add(hGF[iMass][icat]);
				
				sprintf(name,"yield_signalVBF_mass%d_CAT%d",H_MASS[iMass],counter);
				RooRealVar *YieldVBF = new RooRealVar(name,name,hVBF[iMass][icat]->Integral());
        		
				sprintf(name,"roohist_demo_mass%d_sel%s_CAT%d",H_MASS[iMass],SELECTION[iSEL].Data(),icat);
		        RooHistScaled[iMass][icat] = new RooDataHist(name,name,x,hTOT[iMass][icat]);

      			sprintf(name,"mean_m%d_CAT%d",H_MASS[iMass],counter);
	        	RooRealVar m(name,name,125,100,150);
	        	sprintf(name,"sigma_m%d_CAT%d",H_MASS[iMass],counter);
	        	RooRealVar s(name,name,12,3,30);

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
				
				
				// model(x) = fsig*sig(x) + (1-fsig)*bkg(x)
				sprintf(name,"signal_model_m%d_CAT%d",H_MASS[iMass],counter);
				model[iMass][icat] = new RooAddPdf(name,name,RooArgList(sig,bkg),fsig);
				
				RooFitResult *res = model[iMass][icat]->fitTo(*RooHistFit[iMass][icat],RooFit::Save(),RooFit::SumW2Error(kFALSE),"q");
				//res->Print();
				
				RooPlot* frame = x.frame();
				RooHistScaled[iMass][icat]->plotOn(frame);
				//model[iMass][icat]->plotOn(frame,RooFit::VisualizeError(*res,1,kFALSE),RooFit::FillColor(kGray));
				//RooHist[iMass][icat]->plotOn(frame);
				model[iMass][icat]->plotOn(frame);
				double chi2 = frame->chiSquare(); 
				//model[iMass][icat]->plotOn(frame,RooFit::LineWidth(2));
				model[iMass][icat]->plotOn(frame,RooFit::Components(bkg),RooFit::LineColor(kBlue),RooFit::LineWidth(2),RooFit::LineStyle(kDashed)); 
				frame->GetXaxis()->SetNdivisions(505); 
				frame->GetXaxis()->SetTitle("M_{bb} (GeV)");
				frame->GetYaxis()->SetTitle("Events");
				frame->Draw();
//				hGF[iMass][icat]->SetFillColor(kGreen-8); 
				hVBF[iMass][icat]->SetFillColor(kRed-10); 
				THStack *hs = new THStack("hs","hs");
//				hs->Add(hGF[iMass][icat]);
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
				//cout<<"Int = "<<tmp_func->Integral(XMIN,XMAX)<<", Yield = "<<Yield->getVal()<<", y0 = "<<y0<<", x0 = "<<x0<<", x1 = "<<x1<<", x2 = "<<x2<<", FWHM = "<<FWHM<<endl;
				//delete tmp_func;
				double y1 = dX*0.5*y0*(YieldVBF->getVal()+YieldGF->getVal())/tmp_func->Integral(XMIN,XMAX); 
				TLine *ln = new TLine(x1,y1,x2,y1);
				ln->SetLineColor(kMagenta+3);
				ln->SetLineStyle(7);
				ln->SetLineWidth(2);
				ln->Draw(); 
				
				TLegend *leg = new TLegend(0.65,0.35,0.9,0.45);  
				leg->AddEntry(hVBF[iMass][icat],"VBF","F");
//				leg->AddEntry(hGF[iMass][icat],"GF","F");
				leg->SetFillColor(0);
				leg->SetBorderSize(0);
				leg->SetTextFont(42);
				leg->SetTextSize(0.05);
				leg->Draw("same");
				
				TPaveText *pave = new TPaveText(0.65,0.55,0.9,0.92,"NDC");
				sprintf(name,"M_{H} = %d GeV",H_MASS[iMass]);
				TLegend *leg = new TLegend(0.65,0.35,0.9,0.45);  
				leg->AddEntry(hVBF[iMass][icat],"VBF","F");
//				leg->AddEntry(hGF[iMass][icat],"GF","F");
				leg->SetFillColor(0);
				leg->SetBorderSize(0);
				leg->SetTextFont(42);
				leg->SetTextSize(0.05);
				leg->Draw("same");
				
				TPaveText *pave = new TPaveText(0.65,0.55,0.9,0.92,"NDC");
				sprintf(name,"M_{H} = %d GeV",H_MASS[iMass]);
				pave->AddText(name);
				sprintf(name,"%s selection",SELECTION[iSEL].Data());
				pave->AddText(name);
				sprintf(name,"CAT%d",icat);
				pave->AddText(name);
				sprintf(name,"m = %1.1f #pm %1.1f",m.getVal(),m.getError());
				pave->AddText(name);
				sprintf(name,"#sigma = %1.1f #pm %1.1f",s.getVal(),s.getError());
				pave->AddText(name);
				sprintf(name,"FWHM = %1.2f",FWHM);
				pave->AddText(name);
				/*
				sprintf(name,"a = %1.2f #pm %1.2f",a.getVal(),a.getError());
				pave->AddText(name);
				sprintf(name,"n = %1.2f #pm %1.2f",n.getVal(),n.getError());
				pave->AddText(name);
				sprintf(name,"f = %1.2f #pm %1.2f",fsig.getVal(),fsig.getError());
				pave->AddText(name);
				*/
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
				
				//m2.setConstant(kTRUE);
				//s2.setConstant(kTRUE); 
				m.setConstant(kTRUE);
				s.setConstant(kTRUE); 
				a.setConstant(kTRUE);
				n.setConstant(kTRUE);
				fsig.setConstant(kTRUE);
				
				w->import(*model[iMass][icat]);
				w->import(*RooHistScaled[iMass][icat]);
				w->import(*res); 
				w->import(*YieldVBF);   
				w->import(*YieldGF);  
				
				counter++;
			}// categories loop
		}// selection loop 
	}// mass loop
	w->Print();
	//x.Print();
	TString selName = "_";
	selName += XMIN;    
	selName += "-";
	selName += XMAX;
	w->writeToFile("signal_shapes_workspace"+selName+".root");
}
