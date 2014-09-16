#include <iomanip.h>
void CreateDatacards(int CAT_MIN,int CAT_MAX,int BRN_ORDER)
{
  const int NCAT = 7;
  const int NF = 6;
  //---- uncertainties -------------------------------------
  const float UNC_UEPS_VBF[NCAT]  = {1.04,1.02,0.97,0.93,1.02,1.03,1.04};
  const float UNC_JES_VBF[NCAT]   = {1.06,1.08,1.09,1.10,1.06,1.08,1.10};
  const float UNC_JER_VBF[NCAT]   = {0.97,0.96,0.97,0.98,0.99,0.98,0.99};
  const float UNC_TRIG_VBF[NCAT]  = {1.03,1.04,1.05,1.06,1.01,1.01,1.02};
  const float UNC_CSV_VBF[NCAT]   = {1.03,0.99,0.97,0.94,1.01,0.94,0.91};
  const float UNC_QGL_VBF[NCAT]   = {1.03,1.01,1.00,0.98,1.03,1.01,0.98};
  const float UNC_SCALE_VBF[NCAT] = {1.00,1.00,1.01,1.02,1.03,1.03,1.05};
  const float UNC_PDF_VBF[NCAT]   = {1.02,1.02,1.02,1.02,1.03,1.03,1.03};

  const float UNC_UEPS_GF[NCAT]   = {1.25,1.10,0.80,0.90,0.65,1.65,1.45};
  const float UNC_JES_GF[NCAT]    = {1.08,1.10,1.12,1.12,1.04,1.09,1.10};
  const float UNC_JER_GF[NCAT]    = {0.99,0.99,0.95,0.96,0.91,0.99,0.95};
  const float UNC_TRIG_GF[NCAT]   = {1.05,1.05,1.10,1.15,1.09,1.09,1.19};
  const float UNC_CSV_GF[NCAT]    = {0.99,0.97,0.93,0.93,0.93,0.97,0.90};
  const float UNC_QGL_GF[NCAT]    = {1.03,1.01,1.00,0.98,1.03,1.01,0.98};
  const float UNC_SCALE_GF[NCAT]  = {1.00,1.00,1.01,1.02,1.03,1.03,1.05};
  const float UNC_PDF_GF[NCAT]    = {1.04,1.04,1.04,1.04,1.05,1.04,1.04};

  TFile *fData = TFile::Open("output/data_shapes_workspace_"+TString::Format("BRN%d",BRN_ORDER)+".root");
  TFile *fSig  = TFile::Open("output/signal_shapes_workspace.root");
 
  RooWorkspace *wData = (RooWorkspace*)fData->Get("w");
  RooWorkspace *wSig  = (RooWorkspace*)fSig->Get("w");

  char name[1000];
  int H_MASS[5] = {115,120,125,130,135};
  float nData[NCAT],nZ[NCAT],nTop[NCAT],nSigVBF[5][NCAT],nSigGF[5][NCAT];
  for(int i=CAT_MIN;i<=CAT_MAX;i++) {
    sprintf(name,"yield_data_CAT%d",i);
    nData[i] = float((RooRealVar*)wData->var(name)->getValV());
    sprintf(name,"yield_ZJets_CAT%d",i);
    nZ[i]  = ((RooRealVar*)wData->var(name))->getValV();
    sprintf(name,"yield_Top_CAT%d",i);
    nTop[i]  = ((RooRealVar*)wData->var(name))->getValV(); 
    for(int m=0;m<5;m++) {
      sprintf(name,"yield_signalVBF_mass%d_CAT%d",H_MASS[m],i);
      nSigVBF[m][i] = ((RooRealVar*)wSig->var(name))->getValV();
      sprintf(name,"yield_signalGF_mass%d_CAT%d",H_MASS[m],i);
      nSigGF[m][i]  = ((RooRealVar*)wSig->var(name))->getValV();
    }
  }

  for(int m=0;m<5;m++) {
    ofstream datacard;
    sprintf(name,"datacard_m%d_BRN%d_CAT%d-CAT%d.txt",H_MASS[m],BRN_ORDER,CAT_MIN,CAT_MAX);
    cout<<"======================================="<<endl; 
    cout<<"Creating datacard: "<<name<<endl;
    cout<<"======================================="<<endl; 
    datacard.open(name);
    datacard.setf(ios::right);
    datacard<<"imax "<<CAT_MAX-CAT_MIN+1<<"\n";
    datacard<<"jmax *"<<"\n";
    datacard<<"kmax *"<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"shapes data_obs   * "<<fData->GetName()<<" w:data_hist_$CHANNEL"<<"\n";
    datacard<<"shapes qcd        * "<<fData->GetName()<<" w:qcd_model_$CHANNEL"<<"\n";
    datacard<<"shapes top        * "<<fData->GetName()<<" w:Top_model_$CHANNEL"<<"\n";
    datacard<<"shapes zjets      * "<<fData->GetName()<<" w:Z_model_$CHANNEL"<<"\n";
    datacard<<"shapes qqH        * "<<fSig->GetName() <<" w:signal_model_m"<<H_MASS[m]<<"_$CHANNEL \n";
    datacard<<"shapes ggH        * "<<fSig->GetName() <<" w:signal_model_m"<<H_MASS[m]<<"_$CHANNEL \n";
    datacard<<"----------------"<<"\n";
    datacard<<"bin         ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) { 
      sprintf(name,"CAT%d ",i);
      datacard<<name;
    }
    datacard<<"\n";
    datacard<<"observation ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<"-1 ";
    }  
    datacard<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"bin  ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      sprintf(name,"CAT%d CAT%d CAT%d CAT%d CAT%d ",i,i,i,i,i);
      datacard<<name;
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<"qqH ggH qcd top zjets ";
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<"0 -1 1 1 1 ";
    }  
    datacard<<"\n";
    datacard<<"rate       ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      cout<<"cat#"<<i<<setw(8)<<nData[i]<<setw(8)<<nSigVBF[m][i]<<setw(8)<<nSigGF[m][i]<<setw(8)<<nTop[i]<<setw(8)<<nZ[i]<<setw(8)<<", S/B = "<<(nSigVBF[m][i]+nSigGF[m][i])/nData[i]<<endl;
      datacard<<nSigVBF[m][i]<<" "<<nSigGF[m][i]<<" "<<nData[i]<<" "<<nTop[i]<<" "<<nZ[i]<<" ";
    }
    datacard<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"lumi                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.026"<<setw(NF)<<"1.026"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_scale_j_ACCEPT     lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_JES_VBF[i]<<setw(NF)<<UNC_JES_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"pdf_ACCEPT             lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.05"<<setw(NF)<<"1.05"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_res_j_ACCEPT       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_JER_VBF[i]<<setw(NF)<<UNC_JER_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_trigger    lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_TRIG_VBF[i]<<setw(NF)<<UNC_TRIG_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_btag       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_CSV_VBF[i]<<setw(NF)<<UNC_CSV_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_qgl        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_QGL_VBF[i]<<setw(NF)<<UNC_QGL_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"UEPS                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_UEPS_VBF[i]<<setw(NF)<<UNC_UEPS_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"QCDscale_qqH           lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_SCALE_VBF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"QCDscale_ggH           lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_SCALE_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"pdf_qqH                lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_PDF_VBF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"pdf_ggH                lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"-"<<setw(NF)<<UNC_PDF_GF[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"qqH_xsec               lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.03<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"ggH_xsec               lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"-"<<setw(NF)<<1.1<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      sprintf(name,"CMS_vbfbb_qcd_norm_CAT%d    lnU ",i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {      
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
      sprintf(name,"CMS_vbfbb_zjets_norm_CAT%d  lnN ",i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {
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
      sprintf(name,"CMS_vbfbb_top_norm_CAT%d    lnN ",i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {
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
    datacard<<"CMS_scale_j        param 1.0 0.04 \n";
    datacard<<"CMS_res_j          param 1.0 0.1 \n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      //if ((i == 0) || (i == 5)) continue;
      //float mZ  = mzjet[icat]->getValV();
      //float emZ = mzjet[icat]->getError();
      //float emZ = sqrt(pow(mzjet[icat]->getError(),2)+pow(0.015*mZ,2));
      //float sZ  = szjet[icat]->getValV();
      //float esZ = szjet[icat]->getError();
      //float esZ = sqrt(pow(szjet[icat]->getError(),2)+pow(0.1*sZ,2));
     
      //datacard<<mzjet[icat]->GetName()<<"   param "<<mZ<<" "<<emZ<<"\n";
      //datacard<<szjet[icat]->GetName()<<"  param "<<sZ<<" "<<esZ<<"\n";
      
      sprintf(name,"mean_m%d_CAT%d",H_MASS[m],i);
      RooRealVar *vmass = (RooRealVar*)wSig->var(name);
      double mass  = vmass->getValV();
      double emass = vmass->getError();
      //float em = sqrt(pow(mean[imass][icat]->getError(),2)+pow(0.015*m,2));
      datacard<<name<<"     param "<<mass<<" "<<emass<<"\n";
      sprintf(name,"sigma_m%d_CAT%d",H_MASS[m],i);
      RooRealVar *vsigma = (RooRealVar*)wSig->var(name);
      double sigma  = vsigma->getValV();
      double esigma = vsigma->getError(); 
      //float es = sqrt(pow(sigma[imass][icat]->getError(),2)+pow(0.1*s,2));
      //cout<<m<<" "<<sigma<<" "<<esigma<<endl;
      datacard<<name<<"    param "<<sigma<<" "<<esigma<<"\n";
      
      if (i != 0 && i != 4) {
        sprintf(name,"trans_p2_CAT%d",i); 
        datacard<<name<<"      param "<<((RooRealVar*)wData->var(name))->getVal()<<" "<<((RooRealVar*)wData->var(name))->getError()<<"\n";
        sprintf(name,"trans_p1_CAT%d",i); 
        datacard<<name<<"      param "<<((RooRealVar*)wData->var(name))->getVal()<<" "<<((RooRealVar*)wData->var(name))->getError()<<"\n";
        sprintf(name,"trans_p0_CAT%d",i); 
        datacard<<name<<"      param "<<((RooRealVar*)wData->var(name))->getVal()<<" "<<((RooRealVar*)wData->var(name))->getError()<<"\n"; 
      }
      
    }
    datacard.close();
  }
  fData->Close();
  fSig->Close();
}
