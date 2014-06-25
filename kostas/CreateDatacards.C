#include <iomanip.h>
void CreateDatacards(float BND1,float BND2,float BND3,int CAT_MIN,int CAT_MAX,int BRN_ORDER)
{
  const int NCAT = 7;
  const int NF = 6;
  //---- uncertainties -------------------------------------
  const float UNC_UEPS[NCAT] = {1.04,1.03,0.97,0.94,1.02,1.03,1.03};
  const float UNC_JES[NCAT]  = {1.06,1.08,1.09,1.10,1.06,1.08,1.10};

  TString TAG(TString::Format("%1.2f_%1.2f_%1.2f",BND1,BND2,BND3));
  TFile *fData = TFile::Open("data_shapes_workspace_"+TAG+"_"+TString::Format("BRN%d",BRN_ORDER)+".root");
  TFile *fSig  = TFile::Open("signal_shapes_workspace_"+TAG+".root");
 
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
    sprintf(name,"datacard_m%d_%s_BRN%d_CAT%d-CAT%d.txt",H_MASS[m],TAG.Data(),BRN_ORDER,CAT_MIN,CAT_MAX);
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
    datacard<<"shapes signal     * "<<fSig->GetName() <<" w:signal_model_m"<<H_MASS[m]<<"_$CHANNEL \n";
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
      sprintf(name,"CAT%d CAT%d CAT%d CAT%d ",i,i,i,i);
      datacard<<name;
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<"signal qcd top zjets ";
    }  
    datacard<<"\n";
    datacard<<"process ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<"0 1 1 1 ";
    }  
    datacard<<"\n";
    datacard<<"rate       ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      cout<<"cat#"<<i<<setw(8)<<nData[i]<<setw(8)<<nSigVBF[m][i]<<setw(8)<<nSigGF[m][i]<<setw(8)<<nTop[i]<<setw(8)<<nZ[i]<<setw(8)<<", S/B = "<<(nSigVBF[m][i]+nSigGF[m][i])/nData[i]<<endl;
      datacard<<nSigVBF[m][i]+nSigGF[m][i]<<" "<<nData[i]<<" "<<nTop[i]<<" "<<nZ[i]<<" ";
    }
    datacard<<"\n";
    datacard<<"----------------"<<"\n";
    datacard<<"lumi                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.026"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_generator  lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.10"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_scale_j_ACCEPT     lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_JES[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"pdf_ACCEPT             lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.05"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }  
    datacard<<"\n";
    datacard<<"CMS_res_j_ACCEPT       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.02"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_trigger    lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.05<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_btag       lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.05<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"CMS_qqH_hbb_qgl        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.05<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"UEPS                   lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<UNC_UEPS[i]<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"QCDscale_qqH           lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.002"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    } 
    datacard<<"\n";
    datacard<<"pdf_qqH                lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<"1.028"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"ggH_xsec               lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.1<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_ggH_hbb_ACCEPT     lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.1<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    datacard<<"CMS_ggH_hbb_MLP        lnN ";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      datacard<<setw(NF)<<1.02<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
    }
    datacard<<"\n";
    for(int i=CAT_MIN;i<=CAT_MAX;i++) {
      sprintf(name,"CMS_vbfbb_qcd_norm_CAT%d    lnU ",i);
      datacard<<name<<setw(NF);
      for(int j=CAT_MIN;j<=CAT_MAX;j++) {      
        if (j == i) {
          datacard<<setw(NF)<<"-"<<setw(NF)<<1.5<<setw(NF)<<"-"<<setw(NF)<<"-";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
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
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"1.2";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
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
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"1.2"<<setw(NF)<<"-";
        }
        else {
          datacard<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-"<<setw(NF)<<"-";
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
