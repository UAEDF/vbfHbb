#include <iomanip.h>
void CreateDatacards(int CAT_MIN,int CAT_MAX,int BRN_ORDER_NOM,int BRN_ORDER_VBF, int TRORDER_NOM, int TRORDER_VBF, TString OUTPATH, TString TRTAG, TString BRTAG, TString CATVETO="", bool MERGE, int FREETF=-1)
{
  TString PATH(TString::Format("%s/output/",OUTPATH.Data()).Data());
  const int NCAT = 7;
  const int NF = 6;
  const int NMASS = 5;
  //---- uncertainties -------------------------------------
  const float UNC_BR[NMASS]       = {1.024,1.028,1.032,1.037,1.043};

  const float UNC_UEPS_VBF[NCAT]  = {1.04,1.02,0.97,0.93,1.02,1.03,1.04};
  const float UNC_JES_VBF[NCAT]   = {1.06,1.08,1.09,1.10,1.06,1.08,1.10};
  const float UNC_JER_VBF[NCAT]   = {0.97,0.96,0.97,0.98,0.99,0.98,0.99};
  const float UNC_TRIG_VBF[NCAT]  = {1.03,1.04,1.05,1.06,1.01,1.01,1.02};
  const float UNC_CSV_VBF[NCAT]   = {1.03,0.99,0.97,0.94,1.01,0.94,0.91};
  const float UNC_QGL_VBF[NCAT]   = {1.03,1.01,1.00,0.98,1.03,1.01,0.98};
  const float UNC_SCALE_VBF[NCAT] = {1.00,1.00,1.01,1.02,1.03,1.03,1.05};
  const float UNC_PDF_VBF[NCAT]   = {1.02,1.02,1.02,1.02,1.03,1.03,1.03};
  const float UNC_PDFGlobal_VBF[NMASS]   = {1.028,1.028,1.028,1.027,1.027};
  const float UNC_SCALEGlobal_VBF[NMASS] = {1.002,1.002,1.002,1.002,1.002};

  const float UNC_UEPS_GF[NCAT]   = {1.25,1.10,0.80,0.90,0.65,1.65,1.45};
  const float UNC_JES_GF[NCAT]    = {1.08,1.10,1.12,1.12,1.04,1.09,1.10};
  const float UNC_JER_GF[NCAT]    = {0.99,0.99,0.95,0.96,0.91,0.99,0.95};
  const float UNC_TRIG_GF[NCAT]   = {1.05,1.05,1.10,1.15,1.09,1.09,1.19};
  const float UNC_CSV_GF[NCAT]    = {0.99,0.97,0.93,0.93,0.93,0.97,0.90};
  const float UNC_QGL_GF[NCAT]    = {1.03,1.01,1.00,0.98,1.03,1.01,0.98};
  const float UNC_SCALE_GF[NCAT]  = {1.00,1.00,1.01,1.02,1.03,1.03,1.05};
  const float UNC_PDF_GF[NCAT]    = {1.04,1.04,1.04,1.04,1.05,1.04,1.04};
  const float UNC_PDFGlobal_GF[NMASS]    = {1.076,1.075,1.075,1.075,1.074};
  const float UNC_SCALEGlobal_GF[NMASS]  = {1.081,1.079,1.078,1.077,1.077};

  vector<int> vCATVETO = tokenize(CATVETO);
  TString tCATVETO = tag(CATVETO);

  TString TRTAG_NOM = TRTAG(0,5);
  TString TRTAG_VBF = TRTAG(5,5);
  TString TRTAGsplit[2] = {TRTAG_NOM,TRTAG_VBF};
  if (TRTAG_VBF=="_BIDP" && BRTAG!="") TRTAG_VBF = "";
  TRTAG = TRTAG_NOM+TRTAG_VBF;
  if (CAT_MAX<4) TRTAG = TRTAG_NOM;
  if (CAT_MIN>3 && TRTAG_VBF!="") TRTAG = TRTAG_VBF;
  else if (CAT_MIN>3) {
	  TRTAG = TRTAG_NOM;
	  TRTAG_VBF = TRTAG_NOM;
  }
  if (CAT_MIN==0 && CAT_MAX==6 && TRTAG_VBF=="") TRTAG_VBF = TRTAG_NOM;

  int CAT_MAX_TAG = 0;
  if (MERGE && CAT_MAX==6) {
	  CAT_MAX = 5;
	  CAT_MAX_TAG = 6;
  }
  else CAT_MAX_TAG = CAT_MAX;

  TString tMERGE = MERGE ? "_CATmerge56" : "";

  TFile *fData = TFile::Open(PATH+"data_shapes_workspace_"+TString::Format("BRN%d+%d%s",BRN_ORDER_NOM,BRN_ORDER_VBF,tMERGE.Data())+TRTAG+BRTAG+".root");
  TFile *fSig  = TFile::Open(PATH+"signal_shapes_workspace"+tMERGE+".root");
 
  RooWorkspace *wData = (RooWorkspace*)fData->Get("w");
  RooWorkspace *wSig  = (RooWorkspace*)fSig->Get("w");
  
  TString nameData = fData->GetName();
  TString nameDataShort = nameData(nameData.Last('/')+1,nameData.Length());
  TString nameSig  = fSig->GetName();
  TString nameSigShort = nameSig(nameSig.Last('/')+1,nameSig.Length());

  char name[1000];
  int H_MASS[5] = {115,120,125,130,135};
  float nData[NCAT],nZ[NCAT],nTop[NCAT],nSigVBF[5][NCAT],nSigGF[5][NCAT];
  for(int i=CAT_MIN;i<=CAT_MAX;i++) {
	 int j = i;
	 if (MERGE) j = merge(i);
    sprintf(name,"yield_data_CAT%d",j);
    nData[i] = float((RooRealVar*)wData->var(name)->getValV());
    sprintf(name,"yield_ZJets_CAT%d",j);
    nZ[i]  = ((RooRealVar*)wData->var(name))->getValV();
    sprintf(name,"yield_Top_CAT%d",j);
    nTop[i]  = ((RooRealVar*)wData->var(name))->getValV(); 
    for(int m=0;m<5;m++) {
      sprintf(name,"yield_signalVBF_mass%d_CAT%d",H_MASS[m],j);
      nSigVBF[m][i] = ((RooRealVar*)wSig->var(name))->getValV();
      sprintf(name,"yield_signalGF_mass%d_CAT%d",H_MASS[m],j);
      nSigGF[m][i]  = ((RooRealVar*)wSig->var(name))->getValV();
    }
  }
  
  system(TString::Format("[ ! -d %s ] && mkdir %s",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output ] && mkdir %s/output",OUTPATH.Data(),OUTPATH.Data()).Data());
  system(TString::Format("[ ! -d %s/output/datacards ] && mkdir %s/output/datacards",OUTPATH.Data(),OUTPATH.Data()).Data());
  for(int m=0;m<5;m++) {
	  cout << m << endl;
    ofstream datacard;
	 TString tFREETF = "";
    if (FREETF > 0 && (TRTAGsplit[0]=="" || TRTAGsplit[0]=="_BIDP" || TRTAGsplit[0]=="_POL3" || TRTAGsplit[0]=="_LIN" || TRTAGsplit[0]=="_POL2" || TRTAGsplit[0]=="_POL1" || TRTAGsplit[1]=="" || TRTAGsplit[1]=="_BIDP" || TRTAGsplit[1]=="_POL3" || TRTAGsplit[1]=="_LIN" || TRTAGsplit[1]=="_POL2" || TRTAGsplit[1]=="_POL1")) { tFREETF = TString::Format("_freeTF%d",FREETF); }
	 else if (FREETF == 0) { tFREETF = "_Free"; }
    sprintf(name,"%s/output/datacards/datacard_m%d_BRN%d+%d_CAT%d-CAT%d%s%s%s%s%s.txt",OUTPATH.Data(),H_MASS[m],BRN_ORDER_NOM,BRN_ORDER_VBF,CAT_MIN,CAT_MAX_TAG,tCATVETO.Data(),tMERGE.Data(),TRTAG.Data(),BRTAG.Data(),tFREETF.Data());
    cout<<"======================================="<<endl; 
    cout<<"Creating datacard: "<<name<<endl;
    cout<<"======================================="<<endl; 
    datacard.open(name);
    datacard.setf(ios::right);
    datacard<<"imax "<<CAT_MAX-CAT_MIN+1-vCATVETO.size()<<"\n";
    datacard<<"jmax *"<<"\n";
    datacard<<"kmax *"<<"\n";
    datacard<<"----------------"<<"\n";

    datacard<<"shapes data_obs   * "<<nameDataShort<<" w:data_hist_$CHANNEL"<<"\n";
    datacard<<"shapes qcd        * "<<nameDataShort<<" w:qcd_model"<<TRTAG.Data()<<BRTAG.Data()<<"_$CHANNEL"<<"\n";
    datacard<<"shapes top        * "<<nameDataShort<<" w:Top_model_$CHANNEL"<<"\n";
    datacard<<"shapes zjets      * "<<nameDataShort<<" w:Z_model_$CHANNEL"<<"\n";
    datacard<<"shapes qqH        * "<<nameSigShort<<" w:signal_model_m"<<H_MASS[m]<<"_$CHANNEL \n";
    datacard<<"shapes ggH        * "<<nameSigShort<<" w:signal_model_m"<<H_MASS[m]<<"_$CHANNEL \n";
    datacard<<"----------------"<<"\n";
    datacard<<"bin         ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) { 
		if (veto(vCATVETO, i)) continue;
		if (MERGE) i = merge(i);
      sprintf(name,"CAT%d ",i);
      datacard<<name;
    }
    datacard<<"\n";
    datacard<<"observation ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<"-1 ";
    }  
    datacard<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"bin  ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
		if (MERGE) i = merge(i);
      sprintf(name,"CAT%d CAT%d CAT%d CAT%d CAT%d ",i,i,i,i,i);
      datacard<<name;
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<"qqH ggH qcd top zjets ";
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<"0 -1 1 1 1 ";
    }  
    datacard<<"\n";
    datacard<<"rate       ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      cout<<"cat#"<<i<<setw(8)<<nData[i]<<setw(8)<<nSigVBF[m][i]<<setw(8)<<nSigGF[m][i]<<setw(8)<<nTop[i]<<setw(8)<<nZ[i]<<setw(8)<<", S/B = "<<(nSigVBF[m][i]+nSigGF[m][i])/nData[i]<<endl;
      datacard<<nSigVBF[m][i]<<" "<<nSigGF[m][i]<<" "<<nData[i]<<" "<<nTop[i]<<" "<<nZ[i]<<" ";
    }
    datacard<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"BR                     lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_BR[m]<<setw(NF)<<UNC_BR[m]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"QCDscale_qqh           lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_SCALEGlobal_GF[m]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"QCDscale_ggh           lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_SCALEGlobal_VBF[m]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"pdf_qqbar              lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_PDFGlobal_VBF[m]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"pdf_gg                 lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_PDFGlobal_GF[m]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"lumi                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"1.026"<<setw(NF)<<"1.026"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_scale_j_ACCEPT     lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_JES_VBF[i]<<setw(NF)<<UNC_JES_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"pdf_ACCEPT             lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"1.05"<<setw(NF)<<"1.05"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_res_j_ACCEPT       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_JER_VBF[i]<<setw(NF)<<UNC_JER_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_trigger    lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_TRIG_VBF[i]<<setw(NF)<<UNC_TRIG_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_btag       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_CSV_VBF[i]<<setw(NF)<<UNC_CSV_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_qgl        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_QGL_VBF[i]<<setw(NF)<<UNC_QGL_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"UEPS                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_UEPS_VBF[i]<<setw(NF)<<UNC_UEPS_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_QCDscale   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_SCALE_VBF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_ggH_hbb_QCDscale   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_SCALE_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_pdf        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<UNC_PDF_VBF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_ggH_hbb_pdf        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_PDF_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      sprintf(name,"CMS_vbfbb_qcd_norm_CAT%d    lnU ",MERGE ? merge(i) : i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {      
		  if (veto(vCATVETO, j)) continue;
        if (j == i) {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<1.5<<setw(NF)<<"-"<<setw(NF)<<"-";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
        }
      }
      datacard<<"\n";
    }  
    datacard<<"\n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      sprintf(name,"CMS_vbfbb_zjets_norm_CAT%d  lnN ",MERGE ? merge(i) : i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {
		  if (veto(vCATVETO, j)) continue;
        if (j == i) {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"1.2";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
        }
      }
      datacard<<"\n";
    }
    datacard<<"\n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
      sprintf(name,"CMS_vbfbb_top_norm_CAT%d    lnN ",MERGE ? merge(i) : i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {
		  if (veto(vCATVETO, j)) continue;
        if (j == i) {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"1.2"<<setw(NF)<<"-";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
        }
      }
      datacard<<"\n";
    }


    datacard<<"\n";
    datacard<<"#--- signal and Z shape parameters ------ \n";
    datacard<<"\n";
    datacard<<"CMS_vbfbb_scale_mbb_selNOM   param 1.0 0.02"<<"\n";
    datacard<<"CMS_vbfbb_scale_mbb_selVBF   param 1.0 0.02"<<"\n";
    datacard<<"CMS_vbfbb_res_mbb_selNOM     param 1.0 0.1"<<"\n";
    datacard<<"CMS_vbfbb_res_mbb_selVBF     param 1.0 0.1"<<"\n";
	 

    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
		if (veto(vCATVETO, i)) continue;
		if (MERGE) i = merge(i);
		cout << "CAT" << i << endl;
      /*
      sprintf(name,"CMS_vbfbb_scale_mbb_CAT%d",i); 
      datacard<<name<<"     param 1.0 0.02"<<"\n";
      sprintf(name,"CMS_vbfbb_res_mbb_CAT%d",i);
      datacard<<name<<"       param 1.0 0.1"<<"\n";
      */      
      sprintf(name,"mean_m%d_CAT%d",H_MASS[m],i);
      RooRealVar *vmass = (RooRealVar*)wSig->var(name);
      double mass  = vmass->getValV();
      double emass = vmass->getError();
      datacard<<name<<"               param "<<mass<<" "<<emass<<"\n";
      sprintf(name,"sigma_m%d_CAT%d",H_MASS[m],i);
      RooRealVar *vsigma = (RooRealVar*)wSig->var(name);
      double sigma  = vsigma->getValV();
      double esigma = vsigma->getError(); 
      
      datacard<<name<<"              param "<<sigma<<" "<<esigma<<"\n";
      
		for(int j=5; j>=0; j--){

  	 	  float enlarge = 1.0;

		  if (i>0 && i < 4 && TRORDER_NOM>j-1 && FREETF!=0) {
	   	  if (FREETF > 0 && (TRTAGsplit[0]=="" || TRTAGsplit[0]=="_BIDP" || TRTAGsplit[0]=="_POL3" || TRTAGsplit[0]=="_LIN" || TRTAGsplit[0]=="_POL2" || TRTAGsplit[0]=="_POL1")) { enlarge = FREETF; cout << "FreeTF: enlarged error x" << FREETF << endl; }
	        sprintf(name,"trans%s_p%d_CAT%d",TRTAG_NOM.Data(),j,i); 
   	     datacard<<name<<"                param "<<((RooRealVar*)wData->var(name))->getVal()<<" "<<((RooRealVar*)wData->var(name))->getError()*enlarge<<"\n";
		  }
		  if (i > 4 && TRORDER_VBF>j-1 && FREETF!=0) { 
	   	  if (FREETF > 0 && (TRTAGsplit[1]=="" || TRTAGsplit[1]=="_BIDP" || TRTAGsplit[1]=="_POL3" || TRTAGsplit[1]=="_LIN" || TRTAGsplit[1]=="_POL2" || TRTAGsplit[1]=="_POL1")) { enlarge = FREETF; cout << "FreeTF: enlarged error x" << FREETF << endl; }
	        sprintf(name,"trans%s_p%d_CAT%d",TRTAG_VBF.Data(),j,i); 
   	     datacard<<name<<"                param "<<((RooRealVar*)wData->var(name))->getVal()<<" "<<((RooRealVar*)wData->var(name))->getError()*enlarge<<"\n";
		  }

		} 
      
    }
    datacard.close();
  }
  fData->Close();
  fSig->Close();
}

bool veto(vector<int> vetos, int i) {
	bool vetoVal = false;
	for (int j=0; j<(int)vetos.size(); j++) {
		if (vetos[j]==i) {
			vetoVal = true;
			break;
		}
	}
	return vetoVal;
}

vector<int> tokenize(TString s) {
    TObjArray *t = s.Tokenize(",");
    const int n = t->GetEntries();
    vector<int> CATVETO;
	 CATVETO.clear();
	 for (int i=0; i<n; i++) {
	     CATVETO.push_back(((TObjString*)t->At(i))->String().Atoi());
	 }
	 return CATVETO; 
}
                                                                      
TString tag(TString s) {
    TObjArray *t = s.Tokenize(",");
    const int n = t->GetEntries();
	 TString tCATVETO = "";
	 for (int i=0; i<n; i++) {
	     tCATVETO += TString::Format("%d",((TObjString*)t->At(i))->String().Atoi());
	 }
	 if (n>0): tCATVETO = "_CATveto"+tCATVETO;
	 return tCATVETO; 
}

int merge(int i) {
	if (i==5) {return 56;}
	else {return i;}
}
