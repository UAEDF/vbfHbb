void PrepareDataForFit()
{
  TFile *inf = TFile::Open("/data/UAData/fromKostas/paper2012/flatTree_data_preselect_hard_tmva.root");
  TTree *tIN = (TTree*)inf->Get("Hbb/events");
  
  tIN->SetBranchStatus("*",0);
  tIN->SetBranchStatus("MLP",1);
  tIN->SetBranchStatus("dPhibb",1);
  tIN->SetBranchStatus("mbbCor",1);
  tIN->SetBranchStatus("mbbParton",1);
//  tIN->SetBranchStatus("mbbParton2",1);
  tIN->SetBranchStatus("mbb",1);
  tIN->SetBranchStatus("puId",1);
  tIN->SetBranchStatus("jetElf",1);
  tIN->SetBranchStatus("jetMuf",1);
  tIN->SetBranchStatus("triggerResult",1);
  
  TCut CUT_TRIGGER("(triggerResult[0]==1 || triggerResult[1]==1)");
  TCut CUT_PUID("puId[0]==1");
  TCut CUT_ELE("jetElf[0]<0.7 && jetElf[1]<0.7 && jetElf[2]<0.7 && jetElf[3]<0.7"); 
  TCut CUT_MUO("jetMuf[0]<0.7 && jetMuf[1]<0.7 && jetMuf[2]<0.7 && jetMuf[3]<0.7");
  
  TString SEL[5] = {
    "dPhibb<2.0 && MLP<0.52",
    "dPhibb<2.0 && MLP>=0.52 && MLP<0.76",
    "dPhibb<2.0 && MLP>=0.76 && MLP<0.90",
    "dPhibb<2.0 && MLP>=0.90 && MLP<0.96",
    "dPhibb<2.0 && MLP>=0.96"
  };
  /*
  TString SEL[5] = {
    "dPhibb<2.0 && MLP<0.50",
    "dPhibb<2.0 && MLP>=0.50 && MLP<0.74",
    "dPhibb<2.0 && MLP>=0.74 && MLP<0.88",
    "dPhibb<2.0 && MLP>=0.88 && MLP<0.94",
    "dPhibb<2.0 && MLP>=0.94"
  };
  */
  TFile *outf = TFile::Open("/data/UAData/fromKostas/paper2012/flatTree_data_preselect_hard_tmva_fit.root","RECREATE");
  
  char name[1000];
  for(int icat=0;icat<5;icat++) {
    cout<<"Categroy #"<<icat<<endl;
    sprintf(name,"HbbCAT%d",icat);
    TDirectoryFile *dir = (TDirectoryFile*)outf->mkdir(name);
    dir->cd();
    TCut CUT_SEL(SEL[icat]);
    TTree *tOUT = (TTree*)tIN->CopyTree(CUT_TRIGGER+CUT_PUID+CUT_SEL+CUT_ELE+CUT_MUO);
    cout<<"Events: "<<tOUT->GetEntries()<<endl;
    tOUT->Write("events");
    dir->Close();
  }  
  
  outf->Close();
  inf->Close();
}
