#include <iostream>
#include <sstream>
#include <istream>
#include <fstream>
#include <iomanip>
#include <string>
#include <cmath>
#include <functional>
#include <vector>
#include <cassert>
#include "TFile.h"
#include "TBranch.h"
#include "TH1D.h"
#include "TH2F.h"
#include "TMath.h"
#include "TVector3.h"
#include "TVectorD.h"
#include "TLorentzVector.h"
#include "TMatrixDSym.h"
#include "TMatrixDSymEigen.h"

#include "KKousour/CMGAnalysis/plugins/VbfHbbFlatTreeProducer.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/JetReco/interface/JetCollection.h"
#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "AnalysisDataFormats/CMGTools/interface/PFJet.h"
#include "AnalysisDataFormats/CMGTools/interface/BaseMET.h"
#include "AnalysisDataFormats/CMGTools/interface/Electron.h"
#include "AnalysisDataFormats/CMGTools/interface/Muon.h"
#include "CMGTools/External/interface/PileupJetIdentifier.h"

using namespace std;
using namespace reco;

VbfHbbFlatTreeProducer::VbfHbbFlatTreeProducer(edm::ParameterSet const& cfg) 
{
  srcJets_            = cfg.getParameter<edm::InputTag>             ("jets");
  srcSoftJets_        = cfg.getParameter<edm::InputTag>             ("softJets");
  srcMET_             = cfg.getParameter<edm::InputTag>             ("met");
  srcRho_             = cfg.getParameter<edm::InputTag>             ("rho"); 
  srcBtag_            = cfg.getParameter<std::string>               ("btagger");
  puTag_              = cfg.getParameter<std::string>               ("putag");
  shiftJES_           = cfg.getParameter<double>                    ("shiftJES");
  etaMax_             = cfg.getParameter<double>                    ("etaMax");
  ptMin_              = cfg.getParameter<double>                    ("ptMin");
  dEtaMin_            = cfg.getParameter<double>                    ("dEtaMin");
  dPhiMax_            = cfg.getParameter<double>                    ("dPhiMax");
  btagThresholds_     = cfg.getParameter<vector<double> >           ("btagThresholds");
  jetReg_xml_         = cfg.getUntrackedParameter<std::string>      ("jetRegXML","factory_JetReg_BDT_final.weights.xml");
  jetReg_massless_    = cfg.getUntrackedParameter<bool>             ("jetRegMassless",false);
  saveJetProperties_  = cfg.getUntrackedParameter<bool>             ("saveJetProperties",false);
  saveSoftJets_       = cfg.getUntrackedParameter<bool>             ("saveSoftJets",false);
  savePartons_        = cfg.getUntrackedParameter<bool>             ("savePartons",false);
  forceNOM_           = cfg.getUntrackedParameter<bool>             ("forceNOM",false);
  forceVBF_           = cfg.getUntrackedParameter<bool>             ("forceVBF",false);
  correctCSV_         = cfg.getUntrackedParameter<bool>             ("correctCSV",false);
  correctQGL_         = cfg.getUntrackedParameter<bool>             ("correctQGL",false);
  
  srcPU_              = cfg.getUntrackedParameter<std::string>      ("pu","");
  srcGenJets_         = cfg.getUntrackedParameter<edm::InputTag>    ("genjets",edm::InputTag(""));
  srcGenParticles_    = cfg.getUntrackedParameter<edm::InputTag>    ("genparticles",edm::InputTag(""));

  triggerCache_       = triggerExpression::Data(cfg.getParameterSet("triggerConfiguration"));
  vtriggerAlias_      = cfg.getParameter<std::vector<std::string> > ("triggerAlias");
  vtriggerSelection_  = cfg.getParameter<std::vector<std::string> > ("triggerSelection");

  if (vtriggerAlias_.size() != vtriggerSelection_.size()) {
    cout<<"ERROR: the number of trigger aliases does not match the number of trigger names !!!"<<endl;
    return;
  }

  for(unsigned i=0;i<vtriggerSelection_.size();i++) {
    vtriggerSelector_.push_back(triggerExpression::parse(vtriggerSelection_[i]));
  }
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::beginJob() 
{
  //--- book the trigger histograms ---------
  triggerNamesHisto_ = fs_->make<TH1F>("TriggerNames","TriggerNames",1,0,1);
  triggerNamesHisto_->SetBit(TH1::kCanRebin);
  for(unsigned i=0;i<vtriggerSelection_.size();i++) {
    triggerNamesHisto_->Fill(vtriggerSelection_[i].c_str(),1);
  }
  triggerPassHisto_ = fs_->make<TH1F>("TriggerPass","TriggerPass",1,0,1);
  triggerPassHisto_->SetBit(TH1::kCanRebin);
  //--- book the pileup histogram -----------
  puHisto_ = fs_->make<TH1F>("pileup","pileup",40,0,40);
  //--- book the tree -----------------------
  outTree_ = fs_->make<TTree>("events","events");
  outTree_->Branch("runNo"                ,&run_               ,"run_/I");
  outTree_->Branch("evtNo"                ,&evt_               ,"evt_/I");
  outTree_->Branch("lumi"                 ,&lumi_              ,"lumi_/I");
  outTree_->Branch("nvtx"                 ,&nVtx_              ,"nVtx_/I");
  outTree_->Branch("selVBF"               ,&selVBF_            ,"selVBF_/O");
  outTree_->Branch("selVBFsoft"           ,&selVBFsoft_        ,"selVBFsoft_/O");
  outTree_->Branch("selNOM"               ,&selNOM_            ,"selNOM_/O");
  outTree_->Branch("selNOMsoft"           ,&selNOMsoft_        ,"selNOMsoft_/O");
  outTree_->Branch("nSoftJets"            ,&nSoftJets_         ,"nSoftJets_/I");
  outTree_->Branch("nSoftJets2"           ,&nSoftJets2_        ,"nSoftJets2_/I");
  outTree_->Branch("nSoftJets5"           ,&nSoftJets5_        ,"nSoftJets5_/I");
  outTree_->Branch("nSoftJets2noLep"      ,&nSoftJets2noLep_   ,"nSoftJets2noLep_/I");
  outTree_->Branch("nJets"                ,&nJets_             ,"nJets_/I");
  outTree_->Branch("nBJets"               ,&nBJets_            ,"nBJets_/I");
  outTree_->Branch("nLeptons"             ,&nLeptons_          ,"nLeptons_/I");
  outTree_->Branch("b1"                   ,&b1_                ,"b1_[4]/I");
  outTree_->Branch("b2"                   ,&b2_                ,"b2_[4]/I");
  outTree_->Branch("q1"                   ,&q1_                ,"q1_[4]/I");
  outTree_->Branch("q2"                   ,&q2_                ,"q2_[4]/I");
  outTree_->Branch("mvaNOM"               ,&mvaNOM_            ,"mvaNOM_/F");
  outTree_->Branch("mvaVBF"               ,&mvaVBF_            ,"mvaVBF_/F");
  outTree_->Branch("mvaNOMnoLep"          ,&mvaNOMnoLep_       ,"mvaNOMnoLep_/F");
  outTree_->Branch("mvaVBFnoLep"          ,&mvaVBFnoLep_       ,"mvaVBFnoLep_/F"); 
  outTree_->Branch("softHt"               ,&softHt_            ,"softHt_/F");
  outTree_->Branch("softHtnoLep"          ,&softHtnoLep_       ,"softHtnoLep_/F");
  outTree_->Branch("rho"                  ,&rho_               ,"rho_/F");
  outTree_->Branch("ht"                   ,&ht_                ,"ht_/F");
  outTree_->Branch("met"                  ,&met_               ,"met_/F");
  outTree_->Branch("metPhi"               ,&metPhi_            ,"metPhi_/F");
  outTree_->Branch("metSig"               ,&metSig_            ,"metSig_/F");
  outTree_->Branch("sphericity"           ,&sphericity_        ,"sphericity_/F");
  outTree_->Branch("aplanarity"           ,&aplanarity_        ,"aplanarity_/F");
  outTree_->Branch("x1"                   ,&x1_                ,"x1_/F");
  outTree_->Branch("x2"                   ,&x2_                ,"x2_/F");
  outTree_->Branch("mjjTrig"              ,&mjjTrig_           ,"mjjTrig_/F");
  outTree_->Branch("dEtaTrig"             ,&dEtaTrig_          ,"dEtaTrig_/F");
  outTree_->Branch("cosTheta"             ,&cosTheta_          ,"cosTheta_[4]/F");
  outTree_->Branch("mqq"                  ,&mqq_               ,"mqq_[4]/F");
  outTree_->Branch("mbb"                  ,&mbb_               ,"mbb_[4]/F");
  outTree_->Branch("mbbReg"               ,&mbbReg_            ,"mbbReg_[4]/F");
  outTree_->Branch("dEtaqq"               ,&dEtaqq_            ,"dEtaqq_[4]/F");
  outTree_->Branch("dEtabb"               ,&dEtabb_            ,"dEtabb_[4]/F");
  outTree_->Branch("ptbb"                 ,&ptbb_              ,"ptbb_[4]/F");
  outTree_->Branch("etabb"                ,&etabb_             ,"etabb_[4]/F");
  outTree_->Branch("dPhiqq"               ,&dPhiqq_            ,"dPhiqq_[4]/F");
  outTree_->Branch("dPhibb"               ,&dPhibb_            ,"dPhibb_[4]/F");
  outTree_->Branch("etaRatio"             ,&etaRatio_          ,"etaRatio_[4]/F"); 
  outTree_->Branch("ptRatio"              ,&ptRatio_           ,"ptRatio_[4]/F"); 
  //------------------------------------------------------------------
  btagIdx_        = new std::vector<int>;
  etaIdx_         = new std::vector<int>;
  blikNOMIdx_     = new std::vector<int>;
  blikVBFIdx_     = new std::vector<int>;
  btagL_          = new std::vector<bool>;
  btagM_          = new std::vector<bool>;
  btagT_          = new std::vector<bool>;
  puIdL_          = new std::vector<bool>;
  puIdM_          = new std::vector<bool>;
  puIdT_          = new std::vector<bool>;
  idL_            = new std::vector<bool>;
  idM_            = new std::vector<bool>;
  idT_            = new std::vector<bool>;
  pt_             = new std::vector<float>;
  btag_           = new std::vector<float>;
  blikNOM_        = new std::vector<float>;
  blikVBF_        = new std::vector<float>;
  puMva_          = new std::vector<float>;
  jec_            = new std::vector<float>;
  regPt_          = new std::vector<float>;
  regE_           = new std::vector<float>;
  unc_            = new std::vector<float>;
  qgl_            = new std::vector<float>;
  eta_            = new std::vector<float>;
  phi_            = new std::vector<float>;
  jetMetPhi_      = new std::vector<float>;
  mass_           = new std::vector<float>;
  energy_         = new std::vector<float>;
  chf_            = new std::vector<float>;
  nhf_            = new std::vector<float>;
  phf_            = new std::vector<float>;
  muf_            = new std::vector<float>;
  elf_            = new std::vector<float>;
  lepChId_        = new std::vector<int>;
  lepIso_         = new std::vector<float>; 
  lepPt_          = new std::vector<float>;
  lepEta_         = new std::vector<float>;
  lepPhi_         = new std::vector<float>;
  lepE_           = new std::vector<float>;
  outTree_->Branch("lepChId"              ,"vector<int>"       ,&lepChId_);
  outTree_->Branch("lepIso"               ,"vector<float>"     ,&lepIso_);
  outTree_->Branch("lepPt"                ,"vector<float>"     ,&lepPt_);
  outTree_->Branch("lepEta"               ,"vector<float>"     ,&lepEta_);
  outTree_->Branch("lepPhi"               ,"vector<float>"     ,&lepPhi_);
  outTree_->Branch("lepE"                 ,"vector<float>"     ,&lepE_);
  outTree_->Branch("btagIdx"              ,"vector<int>"       ,&btagIdx_);
  outTree_->Branch("blikNOMIdx"           ,"vector<int>"       ,&blikNOMIdx_);
  outTree_->Branch("blikVBFIdx"           ,"vector<int>"       ,&blikVBFIdx_);
  outTree_->Branch("etaIdx"               ,"vector<int>"       ,&etaIdx_);
  outTree_->Branch("jetPuIdL"             ,"vector<bool>"      ,&puIdL_);
  outTree_->Branch("jetPuIdM"             ,"vector<bool>"      ,&puIdM_);
  outTree_->Branch("jetPuIdT"             ,"vector<bool>"      ,&puIdT_);
  outTree_->Branch("jetIdL"               ,"vector<bool>"      ,&idL_);
  outTree_->Branch("jetIdM"               ,"vector<bool>"      ,&idM_);
  outTree_->Branch("jetIdT"               ,"vector<bool>"      ,&idT_); 
  outTree_->Branch("jetBtagL"             ,"vector<bool>"      ,&btagL_);
  outTree_->Branch("jetBtagM"             ,"vector<bool>"      ,&btagM_);
  outTree_->Branch("jetBtagT"             ,"vector<bool>"      ,&btagT_);
  outTree_->Branch("jetPt"                ,"vector<float>"     ,&pt_);
  outTree_->Branch("jetBtag"              ,"vector<float>"     ,&btag_); 
  outTree_->Branch("jetBlikNOM"           ,"vector<float>"     ,&blikNOM_); 
  outTree_->Branch("jetBlikVBF"           ,"vector<float>"     ,&blikVBF_); 
  outTree_->Branch("jetPuMva"             ,"vector<float>"     ,&puMva_);
  outTree_->Branch("jetJec"               ,"vector<float>"     ,&jec_);
  outTree_->Branch("jetRegPt"             ,"vector<float>"     ,&regPt_);
  outTree_->Branch("jetRegE"              ,"vector<float>"     ,&regE_);
  outTree_->Branch("jetUnc"               ,"vector<float>"     ,&unc_);
  outTree_->Branch("jetQGL"               ,"vector<float>"     ,&qgl_);
  outTree_->Branch("jetEta"               ,"vector<float>"     ,&eta_);
  outTree_->Branch("jetPhi"               ,"vector<float>"     ,&phi_);
  outTree_->Branch("jetMetPhi"            ,"vector<float>"     ,&jetMetPhi_);
  outTree_->Branch("jetMass"              ,"vector<float>"     ,&mass_);
  outTree_->Branch("jetEnergy"            ,"vector<float>"     ,&energy_);
  outTree_->Branch("jetChf"               ,"vector<float>"     ,&chf_);
  outTree_->Branch("jetNhf"               ,"vector<float>"     ,&nhf_);
  outTree_->Branch("jetPhf"               ,"vector<float>"     ,&phf_);
  outTree_->Branch("jetMuf"               ,"vector<float>"     ,&muf_);
  outTree_->Branch("jetElf"               ,"vector<float>"     ,&elf_);
  //------------------------------------------------------------------- 
  if (saveJetProperties_) {
    ptD_            = new std::vector<float>;
    ptD_QC_         = new std::vector<float>;
    axisMinor_      = new std::vector<float>;
    axisMajor_      = new std::vector<float>;
    axisMinor_QC_   = new std::vector<float>;
    axisMajor_QC_   = new std::vector<float>;
    pull_           = new std::vector<float>;
    pull_QC_        = new std::vector<float>;
    leadTrkPt_      = new std::vector<float>; 
    jetR_           = new std::vector<float>;
    jetRChg_QC_     = new std::vector<float>;
    vtxMass_        = new std::vector<float>;
    vtx3dL_         = new std::vector<float>;
    vtx3deL_        = new std::vector<float>;
    vtxPt_          = new std::vector<float>;
    softLepPt_      = new std::vector<float>;
    softLepDR_      = new std::vector<float>;
    softLepPtRel_   = new std::vector<float>;
    softLepSigDB3D_ = new std::vector<float>;
    softLepId_      = new std::vector<int>;
    part_           = new std::vector<int>;
    nChg_QC_        = new std::vector<int>;
    nChg_ptCut_     = new std::vector<int>;
    nNeutral_ptCut_ = new std::vector<int>; 
    outTree_->Branch("jetPtD"               ,"vector<float>"     ,&ptD_);
    outTree_->Branch("jetPtD_QC"            ,"vector<float>"     ,&ptD_QC_);
    outTree_->Branch("jetAxisMinor"         ,"vector<float>"     ,&axisMinor_);
    outTree_->Branch("jetAxisMajor"         ,"vector<float>"     ,&axisMajor_);
    outTree_->Branch("jetAxisMinor_QC"      ,"vector<float>"     ,&axisMinor_QC_);
    outTree_->Branch("jetAxisMajor_QC"      ,"vector<float>"     ,&axisMajor_QC_);
    outTree_->Branch("jetPull"              ,"vector<float>"     ,&pull_);
    outTree_->Branch("jetPull_QC"           ,"vector<float>"     ,&pull_QC_);
    outTree_->Branch("jetR"                 ,"vector<float>"     ,&jetR_);
    outTree_->Branch("jetLeadTrkPt"         ,"vector<float>"     ,&leadTrkPt_);
    outTree_->Branch("jetRChg_QC"           ,"vector<float>"     ,&jetRChg_QC_);
    outTree_->Branch("jetVtx3dL"            ,"vector<float>"     ,&vtx3dL_);
    outTree_->Branch("jetVtx3deL"           ,"vector<float>"     ,&vtx3deL_);
    outTree_->Branch("jetVtxPt"             ,"vector<float>"     ,&vtxPt_);
    outTree_->Branch("jetVtxMass"           ,"vector<float>"     ,&vtxMass_);
    outTree_->Branch("jetSoftLepPt"         ,"vector<float>"     ,&softLepPt_);
    outTree_->Branch("jetSoftLepPtRel"      ,"vector<float>"     ,&softLepPtRel_);
    outTree_->Branch("jetSoftLepDR"         ,"vector<float>"     ,&softLepDR_);
    outTree_->Branch("jetSoftLepSigDB3D"    ,"vector<float>"     ,&softLepSigDB3D_);
    outTree_->Branch("jetSoftLepId"         ,"vector<int>"       ,&softLepId_);
    outTree_->Branch("jetPart"              ,"vector<int>"       ,&part_); 
    outTree_->Branch("jetnChg_QC"           ,"vector<int>"       ,&nChg_QC_);
    outTree_->Branch("jetnChg_ptCut"        ,"vector<int>"       ,&nChg_ptCut_);
    outTree_->Branch("jetnNeutral_ptCut"    ,"vector<int>"       ,&nNeutral_ptCut_);
  }
  //------------------------------------------------------------------
  triggerResult_ = new std::vector<bool>;
  outTree_->Branch("triggerResult","vector<bool>",&triggerResult_);
  //------------------------------------------------------------------
  if (saveSoftJets_) { 
    softJetPt_  = new std::vector<float>;
    softJetEta_ = new std::vector<float>;
    softJetPhi_ = new std::vector<float>;
    softJetE_   = new std::vector<float>;
    outTree_->Branch("softJetPt" ,"vector<float>" ,&softJetPt_);
    outTree_->Branch("softJetEta","vector<float>" ,&softJetEta_);
    outTree_->Branch("softJetPhi","vector<float>" ,&softJetPhi_);
    outTree_->Branch("softJetE"  ,"vector<float>" ,&softJetE_);
  }
  //------------------- MC ---------------------------------
  outTree_->Branch("npu"           ,&npu_          ,"npu_/I");
  if (savePartons_) {
    partonId_       = new std::vector<int>;
    partonSt_       = new std::vector<int>;
    partonMatchIdx_ = new std::vector<int>;
    partonMatchDR_  = new std::vector<float>;
    partonPt_       = new std::vector<float>;
    partonEta_      = new std::vector<float>;
    partonPhi_      = new std::vector<float>;
    partonE_        = new std::vector<float>;
    outTree_->Branch("partonId"       ,"vector<int>"   ,&partonId_);
    outTree_->Branch("partonSt"       ,"vector<int>"   ,&partonSt_);
    outTree_->Branch("partonMatchIdx" ,"vector<int>"   ,&partonMatchIdx_);
    outTree_->Branch("partonMatchDR"  ,"vector<float>" ,&partonMatchDR_);
    outTree_->Branch("partonPt"       ,"vector<float>" ,&partonPt_);
    outTree_->Branch("partonEta"      ,"vector<float>" ,&partonEta_);
    outTree_->Branch("partonPhi"      ,"vector<float>" ,&partonPhi_);
    outTree_->Branch("partonE"        ,"vector<float>" ,&partonE_);
    genjetPt_       = new std::vector<float>;
    genjetEta_      = new std::vector<float>;
    genjetPhi_      = new std::vector<float>;
    genjetE_        = new std::vector<float>; 
    outTree_->Branch("genjetPt"       ,"vector<float>" ,&genjetPt_);
    outTree_->Branch("genjetEta"      ,"vector<float>" ,&genjetEta_);
    outTree_->Branch("genjetPhi"      ,"vector<float>" ,&genjetPhi_);
    outTree_->Branch("genjetE"        ,"vector<float>" ,&genjetE_);
	 outTree_->Branch("pdfX1"          ,&pdfX1_         ,"pdfX1_/F");
	 outTree_->Branch("pdfX2"          ,&pdfX2_         ,"pdfX2_/F");
	 outTree_->Branch("pdfID1"         ,&pdfID1_        ,"pdfID1_/I");
	 outTree_->Branch("pdfID2"         ,&pdfID2_        ,"pdfID2_/I");
	 outTree_->Branch("pdfQ"           ,&pdfQ_          ,"pdfQ_/F");

  }  
  qglCalc_    = new QGLCalculator();
  jetReg_     = new JetRegressor("KKousour/CMGAnalysis/data/"+jetReg_xml_);
  bjetLikNOM_ = new BJetLikelihood("KKousour/CMGAnalysis/data/factory_BCanditate_NOM_BDT_GRAD.weights.xml");
  bjetLikVBF_ = new BJetLikelihood("KKousour/CMGAnalysis/data/factory_BCanditate_VBF_BDT_GRAD.weights.xml");
  discrNOM_   = new DiscriminatorMVA("KKousour/CMGAnalysis/data/factory_mvaNOM_BDT_GRAD.weights.xml");
  discrVBF_   = new DiscriminatorMVA("KKousour/CMGAnalysis/data/factory_mvaVBF_BDT_GRAD.weights.xml");
  cout<<"Begin job finished"<<endl;
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::endJob() 
{  
  if (puHisto_->GetEntries() > 0) {
    fillWeights();
  }
  delete qglCalc_;
  delete jetReg_;
  delete bjetLikNOM_;
  delete bjetLikVBF_;
  delete discrNOM_;
  delete discrVBF_;
  if (savePartons_) {
    delete partonSt_;
    delete partonId_;
    delete partonMatchIdx_;
    delete partonMatchDR_;
    delete partonPt_;
    delete partonEta_;
    delete partonPhi_;
    delete partonE_;
    delete genjetPt_;
    delete genjetEta_;
    delete genjetPhi_;
    delete genjetE_; 
  }
  if (saveSoftJets_) {
    delete softJetPt_;
    delete softJetEta_;
    delete softJetPhi_;
    delete softJetE_;
  }
  delete triggerResult_;
  delete btagIdx_;
  delete blikNOMIdx_;
  delete blikVBFIdx_; 
  delete etaIdx_;
  delete puIdL_;
  delete puIdM_;
  delete puIdT_;
  delete idL_;
  delete idM_;
  delete idT_;
  delete btagL_;
  delete btagM_;
  delete btagT_;
  delete pt_;
  delete btag_;
  delete blikNOM_;
  delete blikVBF_;
  delete puMva_;
  delete jec_;
  delete regPt_;
  delete regE_;
  delete unc_;
  delete qgl_;
  delete eta_;
  delete phi_;
  delete jetMetPhi_;
  delete mass_;
  delete energy_;
  delete chf_;
  delete nhf_;
  delete phf_;
  delete muf_;
  delete elf_;
  delete lepChId_;
  delete lepIso_;
  delete lepPt_;
  delete lepEta_;
  delete lepPhi_;
  delete lepE_;
  if (saveJetProperties_) {
    delete ptD_;
    delete ptD_QC_;
    delete axisMinor_;
    delete axisMajor_;
    delete axisMinor_QC_;
    delete axisMajor_QC_;
    delete pull_;
    delete pull_QC_;
    delete jetR_;
    delete jetRChg_QC_;
    delete leadTrkPt_;
    delete vtx3dL_;
    delete vtx3deL_;
    delete vtxPt_;
    delete vtxMass_;
    delete softLepPt_;
    delete softLepPtRel_;
    delete softLepDR_;
    delete softLepSigDB3D_;
    delete softLepId_;
    delete part_;
    delete nChg_QC_;
    delete nChg_ptCut_;
    delete nNeutral_ptCut_;
  }
  for(unsigned i=0;i<vtriggerSelector_.size();i++) {
    delete vtriggerSelector_[i];
  }
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::analyze(edm::Event const& iEvent, edm::EventSetup const& iSetup) 
{
  initialize();

  edm::Handle<edm::View<cmg::PFJet> > jets;
  iEvent.getByLabel(srcJets_,jets);
  edm::View<cmg::PFJet> cmg_jets = *jets;

  edm::Handle<edm::View<reco::Jet> > softJets;
  iEvent.getByLabel(srcSoftJets_,softJets);

  edm::Handle<edm::View<cmg::Muon> > muons;
  iEvent.getByLabel("cmgMuonSel",muons);
 
  edm::Handle<edm::View<cmg::Electron> > electrons;
  iEvent.getByLabel("cmgElectronSel",electrons);

  edm::Handle<edm::View<cmg::BaseMET> >  met;
  iEvent.getByLabel(srcMET_,met);

  edm::Handle<double> rho;
  iEvent.getByLabel(srcRho_,rho);

  edm::Handle<reco::VertexCollection> recVtxs;
  iEvent.getByLabel("offlinePrimaryVertices",recVtxs);

  edm::Handle<GenEventInfoProduct> hEventInfo;
  iEvent.getByLabel("generator",hEventInfo);

  edm::Handle<GenParticleCollection> genParticles;
  
  edm::Handle<std::vector<cmg::PhysicsObjectWithPtr<edm::Ptr<reco::GenJet> > > > cmggenjets;
  edm::Handle<reco::GenJetCollection> genjets;
  //---------- pu -----------------------
  edm::Handle<std::vector<PileupSummaryInfo> > PupInfo;
  if (!iEvent.isRealData()) {
    if (srcPU_ != "") {
      iEvent.getByLabel(srcPU_,PupInfo);
      std::vector<PileupSummaryInfo>::const_iterator PUI;
      for(PUI = PupInfo->begin(); PUI != PupInfo->end(); ++PUI) {
        if (PUI->getBunchCrossing() == 0) {
          npu_ = PUI->getTrueNumInteractions();
        }
      }
    }
    puHisto_->Fill(npu_); 
  }
  //-------------- Trigger Info -----------------------------------
  triggerPassHisto_->Fill("totalEvents",1);
  if (triggerCache_.setEvent(iEvent,iSetup)) {
    for(unsigned itrig=0;itrig<vtriggerSelector_.size();itrig++) {
      bool result(false);
      if (vtriggerSelector_[itrig]) {
        if (triggerCache_.configurationUpdated()) {
          vtriggerSelector_[itrig]->init(triggerCache_);
        }
        result = (*(vtriggerSelector_[itrig]))(triggerCache_);
      }
      if (result) {
        triggerPassHisto_->Fill(vtriggerAlias_[itrig].c_str(),1);
      }
      triggerResult_->push_back(result);
    }
  }
     
  //----- at least one good vertex -----------
  bool cut_vtx = (recVtxs->size() > 0);
  
  if (cut_vtx) {
    //---- muons block --------------------------------------------  
    nLeptons_ = 0;
    for(edm::View<cmg::Muon>::const_iterator imu = muons->begin();imu != muons->end(); ++imu) { 
      if (imu->pt() < 20 || fabs(imu->eta()) > 2.5) continue;
      if (!(imu->isGlobalMuon() && 
            imu->isPF() &&
            fabs(imu->normalizedChi2()) < 10 &&
            imu->numberOfValidMuonHits() > 0 &&
            imu->numberOfMatches() > 1 && 
            fabs(imu->dxy()) < 0.2 &&
            fabs(imu->dz()) < 0.5 &&
            imu->numberOfValidPixelHits() > 0 && 
            imu->numberOfValidTrackerHits() > 5
           )) continue;
      if (imu->relIso(0.5,0,0.4) > 0.15) continue;
      lepPt_ ->push_back(imu->pt());
      lepEta_->push_back(imu->eta());
      lepPhi_->push_back(imu->phi());	
      lepE_  ->push_back(imu->energy());
      lepIso_->push_back(imu->relIso(0.5,0,0.4));	
      lepChId_->push_back(imu->charge());      
      nLeptons_++;
    }// muons loop
    //---- electrons block --------------------------------------------  
    for(edm::View<cmg::Electron>::const_iterator iel = electrons->begin();iel != electrons->end(); ++iel) { 
      if (iel->pt() < 20 || fabs(iel->eta()) > 2.5) continue;
      float ecalE                          = iel->sourcePtr()->get()->ecalEnergy();
      float trkP                           = ecalE/iel->sourcePtr()->get()->eSuperClusterOverP(); 
      float dxy                            = iel->dxy();
      float dz                             = iel->dz();
      float fep                            = fabs(1./ecalE-1./trkP);                              
      float sigmaIetaIeta                  = iel->sigmaIetaIeta();
      float hadronicOverEm                 = iel->hadronicOverEm();
      float deltaPhiSuperClusterTrackAtVtx = iel->deltaPhiSuperClusterTrackAtVtx();
      float deltaEtaSuperClusterTrackAtVtx = iel->deltaEtaSuperClusterTrackAtVtx();
      float etaSC = fabs(iel->sourcePtr()->get()->superCluster()->eta());
      bool id(false);
      if (etaSC < 1.442) {
        if (hadronicOverEm < 0.1 && sigmaIetaIeta < 0.03 && dxy < 0.02 && fep < 0.05) { 
          if (deltaPhiSuperClusterTrackAtVtx < 0.03 && deltaEtaSuperClusterTrackAtVtx < 0.004 && dz < 0.1)  {
            id = true;
          }
        }
      }// if EB
      if (etaSC > 1.566) {
        if (hadronicOverEm < 0.1 && sigmaIetaIeta < 0.03 && dxy < 0.02 && fep < 0.05) {
          if (deltaPhiSuperClusterTrackAtVtx < 0.02 && deltaEtaSuperClusterTrackAtVtx < 0.005 && dz < 0.1)  {
            id = true;
          }
        }
      }// if EE	
      if (!id) continue;
      float Aeff;
      if (etaSC < 1.0) Aeff = 0.13;
      else if (etaSC >= 1.0 && etaSC < 1.479) Aeff = 0.14;
      else if (etaSC >= 1.479 && etaSC < 2.0) Aeff = 0.07;
      else if (etaSC >= 2.0 && etaSC < 2.2) Aeff = 0.09;
      else if (etaSC >= 2.2 && etaSC < 2.3) Aeff = 0.11;
      else if (etaSC >= 2.3 && etaSC < 2.5) Aeff = 0.11;
      else Aeff = 0.14;
      float iso = iel->chargedHadronIso(0.3)+max((iel->neutralHadronIso(0.3)+iel->photonIso(0.3)-(*rho)*Aeff),0.0);
      if (iso > 0.15) continue;
      lepPt_ ->push_back(iel->pt());
      lepEta_->push_back(iel->eta());
      lepPhi_->push_back(iel->phi());	
      lepE_  ->push_back(iel->energy());
      lepIso_->push_back(iso/iel->pt());
      lepChId_->push_back(2*iel->charge());
      nLeptons_++;
    }// electrons loop
    //----- soft jets ----------------------
    softHt_          = 0;
    nSoftJets_       = 0; 
    nSoftJets2_      = 0; 
    nSoftJets5_      = 0;
    softHtnoLep_     = 0; 
    nSoftJets2noLep_ = 0; 
    for(int it=0;it<int(softJets->size());it++) {
      softHt_ += (*softJets)[it].pt();
      if (saveSoftJets_) {
        if (nSoftJets_ < 3) {
          softJetPt_ ->push_back((*softJets)[it].pt());
          softJetEta_->push_back((*softJets)[it].eta());
          softJetPhi_->push_back((*softJets)[it].phi());
          softJetE_  ->push_back((*softJets)[it].energy());
        }  
      }
      nSoftJets_++;
      if ((*softJets)[it].pt() > 2) {
        nSoftJets2_++;
        if ((*softJets)[it].pt() > 5) {
          nSoftJets5_++;
        }
      }
      //---- cross clean with isolated leptons --
      bool matched(false);
      for(int ilep=0;ilep<nLeptons_;ilep++) {
        double dR = deltaR((*softJets)[it].eta(),(*softJets)[it].phi(),(*lepEta_)[ilep],(*lepPhi_)[ilep]);
        if (dR < 0.5) {
          matched = true;
          break;
        }
      }
      if (matched) continue;
      softHtnoLep_ += (*softJets)[it].pt();
      if ((*softJets)[it].pt() > 5) {
        nSoftJets2noLep_++;
      }
    }
    //----- PF jets ------------------------------
    nJets_ = 0;
    nBJets_ = 0;
    float ht(0.0);
    float sumP2(0.0),sumPxx(0.0),sumPxy(0.0),sumPxz(0.0),sumPyy(0.0),sumPyz(0.0),sumPzz(0.0);
    vector<float> vaJES;
    vector<TLorentzVector> vP4;
    for(edm::View<cmg::PFJet>::const_iterator ijet = cmg_jets.begin();ijet != cmg_jets.end(); ++ijet) {  
      //---- cross clean with isolated leptons --
      bool matched(false);
      for(int ilep=0;ilep<nLeptons_;ilep++) {
        double dR = deltaR(ijet->eta(),ijet->phi(),(*lepEta_)[ilep],(*lepPhi_)[ilep]);
        if (dR < 0.5) {
          matched = true;
          break;
        }
      }
      if (matched) continue;
      float chf = ijet->component(1).fraction();
      float nhf = ijet->component(5).fraction();
      float phf = ijet->component(4).fraction();
      float muf = ijet->component(3).fraction();
      float elf = ijet->component(2).fraction();
      int chm   = ijet->component(1).number();
      int npr   = ijet->nConstituents();
      float eta = fabs(ijet->eta());
      float pt  = ijet->pt();
      float btag = ijet->bDiscriminator(srcBtag_.c_str());
      if (correctCSV_) {
        btag = shiftCSV(btag);
      }
      float qgl = qglCalc_->getQGL(*ijet,*rho);
      if (correctQGL_) {
        qgl = shiftQGL(qgl);
      }
      bool puIdL = ijet->passPuJetId(puTag_.c_str(),PileupJetIdentifier::kLoose);
      bool puIdM = ijet->passPuJetId(puTag_.c_str(),PileupJetIdentifier::kMedium);
      bool puIdT = ijet->passPuJetId(puTag_.c_str(),PileupJetIdentifier::kTight);
      bool idL = (npr>1 && phf<0.99 && nhf<0.99);
      bool idM = (idL && ((eta<=2.4 && nhf<0.9 && phf<0.9 && elf<0.99 && muf<0.99 && chf>0 && chm>0) || eta>2.4));
      bool idT = (idL && ((eta<=2.4 && nhf<0.9 && phf<0.9 && elf<0.7 && muf<0.7 && chf>0 && chm>0) || eta>2.4));   
      bool btagL = (btag > btagThresholds_[0]);
      bool btagM = (btag > btagThresholds_[1]);
      bool btagT = (btag > btagThresholds_[2]);
      if (idL && puIdL && (pt > ptMin_) && (eta < etaMax_)) {
        vP4.push_back(TLorentzVector(ijet->px(),ijet->py(),ijet->pz(),ijet->energy()));
        sumP2  += ijet->p()  * ijet->p();
        sumPxx += ijet->px() * ijet->px();
        sumPxy += ijet->px() * ijet->py();
        sumPxz += ijet->px() * ijet->pz();
        sumPyy += ijet->py() * ijet->py();
        sumPyz += ijet->py() * ijet->pz();
        sumPzz += ijet->pz() * ijet->pz();   
        double aJES = 1.+shiftJES_*ijet->uncOnFourVectorScale();
        vaJES.push_back(aJES);
        chf_           ->push_back(chf);
        nhf_           ->push_back(nhf);
        phf_           ->push_back(phf);
        elf_           ->push_back(elf);
        muf_           ->push_back(muf);
        unc_           ->push_back(ijet->uncOnFourVectorScale());
        jec_           ->push_back(aJES/ijet->rawFactor());
        float dphiJetMet = fabs(deltaPhi(ijet->phi(),(*met)[0].phi()));
        jetMetPhi_     ->push_back(dphiJetMet);
        pt_            ->push_back(aJES*pt);
        phi_           ->push_back(ijet->phi());
        eta_           ->push_back(ijet->eta());
        mass_          ->push_back(aJES*ijet->mass());
        energy_        ->push_back(aJES*ijet->energy());
        btag_          ->push_back(btag); 
        qgl_           ->push_back(qgl);  
        puMva_         ->push_back(ijet->puMva(puTag_.c_str()));
        puIdL_         ->push_back(puIdL);
        puIdM_         ->push_back(puIdM);
        puIdT_         ->push_back(puIdT);
        idL_           ->push_back(idL);
        idM_           ->push_back(idM);
        idT_           ->push_back(idT);
        btagL_         ->push_back(btagL);
        btagM_         ->push_back(btagM);
        btagT_         ->push_back(btagT);
        float softLepPt(0.0),softLepPtRel(0.0),softLepDR(0.0),softLepId(-1),softLepPtRelMax(0.0),softLepSigDB3D(0.0);
        //---- identify muons that match the jet ------
        for(edm::View<cmg::Muon>::const_iterator imuon = muons->begin();imuon != muons->end(); ++imuon) {
          if (imuon->pt() < 2) continue;
          float dR    = deltaR(imuon->eta(),imuon->phi(),ijet->eta(),ijet->phi()); 
          float ptRel = ((ijet->p4().Vect()-imuon->p4().Vect()).Cross(imuon->p4().Vect())).R()/ijet->p4().Vect().R();
          if (dR < 0.5 && ptRel > softLepPtRelMax) {
            softLepPt       = imuon->pt();
            softLepDR       = dR;
            softLepPtRel    = ptRel; 
            softLepId       = 0;
            softLepPtRelMax = ptRel;
            softLepSigDB3D  = 0;
            if (imuon->dB3D() != 0) {
              softLepSigDB3D  = imuon->edB3D()/imuon->dB3D();
            } 
          }
        }
        //---- identify electrons that match the jet ------
        for(edm::View<cmg::Electron>::const_iterator ielectron = electrons->begin();ielectron != electrons->end(); ++ielectron) {
          if ((ielectron->mva() < -0.1) || (ielectron->pt() < 2)) continue;
          float dR    = deltaR(ielectron->eta(),ielectron->phi(),ijet->eta(),ijet->phi()); 
          float ptRel = ((ijet->p4().Vect()-ielectron->p4().Vect()).Cross(ielectron->p4().Vect())).R()/ijet->p4().Vect().R();
          if (dR < 0.5 && ptRel > softLepPtRelMax) {
            softLepPt       = ielectron->pt();
            softLepDR       = dR;
            softLepPtRel    = ptRel; 
            softLepId       = 1;
            softLepPtRelMax = ptRel;
            softLepSigDB3D  = 0;
            if (ielectron->dB3D() != 0) {
              softLepSigDB3D = ielectron->edB3D()/ielectron->dB3D();
            } 
          }
        }
        regPt_->push_back((jetReg_->getTarget(*ijet,dphiJetMet,*rho,(*met)[0].et(),softLepPt,softLepPtRel))[0]/ijet->pt());
        regE_ ->push_back((jetReg_->getTarget(*ijet,dphiJetMet,*rho,(*met)[0].et(),softLepPt,softLepPtRel))[0]/ijet->pt());
        if (saveJetProperties_) {
          softLepPt_     ->push_back(softLepPt);
          softLepDR_     ->push_back(softLepDR); 
          softLepPtRel_  ->push_back(softLepPtRel);
          softLepSigDB3D_->push_back(softLepSigDB3D);
          softLepId_     ->push_back(softLepId);
          ptD_           ->push_back(ijet->ptd());
          ptD_QC_        ->push_back(ijet->ptdQC());
          vtx3dL_        ->push_back(ijet->vtx3dL());
          vtx3deL_       ->push_back(ijet->vtx3deL());
          vtxPt_         ->push_back(ijet->vtxPt());
          vtxMass_       ->push_back(ijet->secvtxMass());
          part_          ->push_back(npr);
          axisMajor_     ->push_back(ijet->axisMajor());
          axisMinor_     ->push_back(ijet->axisMinor());
          axisMajor_QC_  ->push_back(ijet->axisMajorQC());
          axisMinor_QC_  ->push_back(ijet->axisMinorQC());
          pull_          ->push_back(ijet->pull());
          pull_QC_       ->push_back(ijet->pullQC());
          leadTrkPt_     ->push_back(ijet->fmaxCharged()*ijet->pt()*ijet->rawFactor());
          jetR_          ->push_back(ijet->fmax());
          jetRChg_QC_    ->push_back(ijet->fmaxCharged());
          nChg_ptCut_    ->push_back(ijet->nChargedPtCut());
          nNeutral_ptCut_->push_back(ijet->nNeutralPtCut());
          nChg_QC_       ->push_back(ijet->nChargedQC());
        }
        ht += aJES*pt;
        nJets_++;
        if (btagM) {
          nBJets_++; 
        }
      }
    }// jet loop
    // ------- MC -----------------------------------------
    if (!iEvent.isRealData()) {
      //---------- genjets ------------------
      if (savePartons_) {
        if (srcGenJets_ == edm::InputTag("ak5GenJets")) {
          iEvent.getByLabel(srcGenJets_, genjets);
          for(reco::GenJetCollection::const_iterator igen = genjets->begin();igen != genjets->end(); ++igen) {
            genjetPt_ ->push_back(igen->pt());
            genjetEta_->push_back(igen->eta());
            genjetPhi_->push_back(igen->phi());
            genjetE_  ->push_back(igen->energy());
          }
        }
        else {
          iEvent.getByLabel(srcGenJets_, cmggenjets);
          for(std::vector<cmg::PhysicsObjectWithPtr<edm::Ptr<reco::GenJet> > >::const_iterator igen = cmggenjets->begin();igen != cmggenjets->end(); ++igen) {
            genjetPt_ ->push_back(igen->pt());
            genjetEta_->push_back(igen->eta());
            genjetPhi_->push_back(igen->phi());
            genjetE_  ->push_back(igen->energy()); 
          }
        }// genjet loop
        //---------- partons ------------------
        iEvent.getByLabel(srcGenParticles_, genParticles);
        for(unsigned ip = 0; ip < genParticles->size(); ++ ip) {
          const GenParticle &p = (*genParticles)[ip];
          if (p.status() != 3) continue;
          int ndst3(0);
	  for(unsigned k = 0; k < p.numberOfDaughters(); k++) {
	    if (p.daughter(k)->status() == 3) {
              ndst3++; 
            }
	  }
          if (ndst3 > 0) continue; 
          partonId_ ->push_back(p.pdgId());
			 partonSt_ ->push_back(p.status()); 
          partonPt_ ->push_back(p.pt());
          partonEta_->push_back(p.eta());
          partonPhi_->push_back(p.phi());
          partonE_  ->push_back(p.energy()); 
          //----- match partons with jets ------------
          float dRmin(1000);  
          int imatch(0);
          for(int j=0;j<nJets_;j++) {
            float dR = deltaR(p.eta(),p.phi(),(*eta_)[j],(*phi_)[j]);
            if (dR < dRmin) {
              imatch = j;
              dRmin = dR;
            }
          }   
          partonMatchIdx_->push_back(imatch);
          partonMatchDR_->push_back(dRmin);
        }// parton loop
      }
		pdfX1_  = hEventInfo->pdf()->x.first;
		pdfX2_  = hEventInfo->pdf()->x.second;
		pdfID1_ = hEventInfo->pdf()->id.first;
		pdfID2_ = hEventInfo->pdf()->id.second;
		pdfQ_   = hEventInfo->pdf()->scalePDF;
    }// if MC
    //---- compute sphericity -----------------------
    if (sumP2 > 0) {
      float Txx = sumPxx/sumP2;
      float Tyy = sumPyy/sumP2;
      float Tzz = sumPzz/sumP2;  
      float Txy = sumPxy/sumP2; 
      float Txz = sumPxz/sumP2; 
      float Tyz = sumPyz/sumP2;
      TMatrixDSym T(3);
      T(0,0) = Txx;
      T(0,1) = Txy;
      T(0,2) = Txz;
      T(1,0) = Txy;
      T(1,1) = Tyy;
      T(1,2) = Tyz;
      T(2,0) = Txz;
      T(2,1) = Tyz;
      T(2,2) = Tzz;
      TMatrixDSymEigen TEigen(T);
      TVectorD eigenValues(TEigen.GetEigenValues());
      sphericity_ = 1.5*(eigenValues(1)+eigenValues(2));
      aplanarity_ = 1.5*eigenValues(2); 
    }   
    ht_     = ht;
    rho_    = *rho;
    met_    = (*met)[0].et();
    metPhi_ = (*met)[0].phi();
    if ((*met)[0].sumEt() > 0) {
      metSig_ = (*met)[0].et()/(*met)[0].sumEt();
    }
    nVtx_   = recVtxs->size();
    run_    = iEvent.id().run();
    evt_    = iEvent.id().event();
    lumi_   = iEvent.id().luminosityBlock();
    if (nJets_ > 3) {
      //----- order jets according to the btag value -----
      order(*btag_,btagIdx_,4);
      //----- order jets according to the eta value -----
      order(*eta_,etaIdx_,4);
      //----- compute the blikelihood -------------------
      for(int j=0;j<4;j++) {
        blikNOM_->push_back(bjetLikNOM_->eval((*btagIdx_)[j],(*etaIdx_)[j],(*btag_)[j],(*eta_)[j]));
        blikVBF_->push_back(bjetLikVBF_->eval((*btagIdx_)[j],(*etaIdx_)[j],(*btag_)[j],(*eta_)[j])); 
      } 
      //----- order jets according to the blik value -----
      order(*blikNOM_,blikNOMIdx_,4);
      order(*blikVBF_,blikVBFIdx_,4); 
      //----- loop over all jet pairs that pass the VBF trigger logic and find the one with the largest mass ---
      float mjjmax = 0;
      for(int j1=0;j1<4;j1++) {
        for(int j2=j1+1;j2<4;j2++) {
          if ((*pt_)[j1] > 35 && (*pt_)[j2] > 35) {
            float mjj = (vaJES[j1]*vP4[j1]+vaJES[j2]*vP4[j2]).M();
            if (mjj > mjjmax) {
              mjjmax = mjj;
              mjjTrig_ = mjjmax;
              dEtaTrig_ = fabs((*eta_)[j1]-(*eta_)[j2]);
            }
          }
        }
      }
      //------------------------------------------------------------------------ 
      b1_[0] = (*btagIdx_)[0]; 
      b2_[0] = (*btagIdx_)[1];
      q1_[0] = (*btagIdx_)[2];
      q2_[0] = (*btagIdx_)[3];
      b1_[1] = (*blikNOMIdx_)[0]; 
      b2_[1] = (*blikNOMIdx_)[1];
      q1_[1] = (*blikNOMIdx_)[2];
      q2_[1] = (*blikNOMIdx_)[3]; 
      b1_[2] = (*blikVBFIdx_)[0]; 
      b2_[2] = (*blikVBFIdx_)[1];
      q1_[2] = (*blikVBFIdx_)[2];
      q2_[2] = (*blikVBFIdx_)[3];
      b1_[3] = (*etaIdx_)[1]; 
      b2_[3] = (*etaIdx_)[2];
      q1_[3] = (*etaIdx_)[0];
      q2_[3] = (*etaIdx_)[3];
      float sumE(0.0),sumPz(0.0);
      vector<TLorentzVector> vRegP4;
      for(int i=0;i<4;i++) {
        sumE  += vaJES[i]*vP4[i].Energy();
        sumPz += vaJES[i]*vP4[i].Pz();
        TLorentzVector p4(0,0,0,0);
        if (jetReg_massless_) {
          p4.SetPtEtaPhiM((*regPt_)[i]*(*pt_)[i],(*eta_)[i],(*phi_)[i],0);
        } 
        else {
          p4.SetPtEtaPhiE((*regPt_)[i]*(*pt_)[i],(*eta_)[i],(*phi_)[i],(*regE_)[i]*(*energy_)[i]);
        }
        vRegP4.push_back(p4);
      }
      x1_ = (sumE+sumPz)/8000;
      x2_ = (sumE-sumPz)/8000;
      for(int k=0;k<4;k++) {
        dEtabb_[k]     = fabs((*eta_)[b1_[k]]-(*eta_)[b2_[k]]);
        dEtaqq_[k]     = fabs((*eta_)[q1_[k]]-(*eta_)[q2_[k]]);
        mbb_[k]        = (vaJES[b1_[k]]*vP4[b1_[k]]+vaJES[b2_[k]]*vP4[b2_[k]]).M();
        mbbReg_[k]     = (vaJES[b1_[k]]*vRegP4[b1_[k]]+vaJES[b2_[k]]*vRegP4[b2_[k]]).M();   
        mqq_[k]        = (vaJES[q1_[k]]*vP4[q1_[k]]+vaJES[q2_[k]]*vP4[q2_[k]]).M();
        ptbb_[k]       = (vaJES[b1_[k]]*vP4[b1_[k]]+vaJES[b2_[k]]*vP4[b2_[k]]).Pt();
        etabb_[k]      = (vaJES[b1_[k]]*vP4[b1_[k]]+vaJES[b2_[k]]*vP4[b2_[k]]).Eta();
        dPhibb_[k]     = fabs(deltaPhi((*phi_)[b1_[k]],(*phi_)[b2_[k]]));
        dPhiqq_[k]     = fabs(deltaPhi((*phi_)[q1_[k]],(*phi_)[q2_[k]])); 
        etaRatio_[k]   = etabb_[k]/TMath::Max(fabs((*eta_)[q1_[k]]),fabs((*eta_)[q2_[k]]));
        ptRatio_[k]    = ptbb_[k]/TMath::Max(fabs((*pt_)[q1_[k]]),fabs((*pt_)[q2_[k]]));
        //----- plane angle at the qqbb rest frame ------
        TLorentzVector cmP4 = vP4[b1_[k]]+vP4[b2_[k]]+vP4[q1_[k]]+vP4[q2_[k]];
        TVector3 vb = cmP4.BoostVector();
        TLorentzVector cmP4b1 = vP4[b1_[k]];
        TLorentzVector cmP4b2 = vP4[b2_[k]];
        TLorentzVector cmP4q1 = vP4[q1_[k]];
        TLorentzVector cmP4q2 = vP4[q2_[k]];
        cmP4b1.Boost(-vb);
        cmP4b2.Boost(-vb);
        cmP4q1.Boost(-vb);
        cmP4q2.Boost(-vb);
        cosTheta_[k] = cos(((cmP4q1.Vect()).Cross(cmP4q2.Vect())).Angle((cmP4b1.Vect()).Cross(cmP4b2.Vect())));
      }
      mvaNOM_ = discrNOM_->eval(mqq_[1],dEtaqq_[1],dPhiqq_[1],(*btag_)[b1_[0]],(*btag_)[b2_[0]],(*qgl_)[b1_[1]],(*qgl_)[b2_[1]],(*qgl_)[q1_[1]],(*qgl_)[q2_[1]],softHt_,nSoftJets2_,cosTheta_[1],x1_,x2_,sphericity_,aplanarity_,etaRatio_[1],ptRatio_[1]);

      mvaVBF_ = discrVBF_->eval(mqq_[2],dEtaqq_[2],dPhiqq_[2],(*btag_)[b1_[0]],(*btag_)[b2_[0]],(*qgl_)[b1_[2]],(*qgl_)[b2_[2]],(*qgl_)[q1_[2]],(*qgl_)[q2_[2]],softHt_,nSoftJets2_,cosTheta_[2],x1_,x2_,sphericity_,aplanarity_,etaRatio_[2],ptRatio_[2]);

      mvaNOMnoLep_ = discrNOM_->eval(mqq_[1],dEtaqq_[1],dPhiqq_[1],(*btag_)[b1_[0]],(*btag_)[b2_[0]],(*qgl_)[b1_[1]],(*qgl_)[b2_[1]],(*qgl_)[q1_[1]],(*qgl_)[q2_[1]],softHtnoLep_,nSoftJets2noLep_,cosTheta_[1],x1_,x2_,sphericity_,aplanarity_,etaRatio_[1],ptRatio_[1]);

      mvaVBFnoLep_ = discrVBF_->eval(mqq_[2],dEtaqq_[2],dPhiqq_[2],(*btag_)[b1_[0]],(*btag_)[b2_[0]],(*qgl_)[b1_[2]],(*qgl_)[b2_[2]],(*qgl_)[q1_[2]],(*qgl_)[q2_[2]],softHtnoLep_,nSoftJets2noLep_,cosTheta_[2],x1_,x2_,sphericity_,aplanarity_,etaRatio_[2],ptRatio_[2]);

      bool cut_Btag_NOM = ((*btagL_)[b1_[0]] && (*btagL_)[b2_[0]]);
      bool cut_Btag_VBF = ((*btagM_)[b1_[0]] && (*btagL_)[b2_[0]]);

      if (cut_Btag_NOM && dPhibb_[1]<dPhiMax_) {
        if ((*pt_)[0]>70 && (*pt_)[1]>55 && (*pt_)[2]>40 && (*pt_)[3]>30 && dEtaqq_[1]>2.0 && mqq_[1]>200) {
          selNOMsoft_ = true;
          if ((*pt_)[0]>80 && (*pt_)[1]>70 && (*pt_)[2]>50 && (*pt_)[3]>40 && dEtaqq_[1]>2.5 && mqq_[1]>250) {
            selNOM_ = true;
          }
        }
      } 
      if (cut_Btag_VBF && dPhibb_[2]<dPhiMax_ && (*pt_)[3]>30 && 0.5*((*pt_)[0]+(*pt_)[1])>80) {
        if (dEtaqq_[2] > 3.0 && mqq_[2] > 300 && dEtaTrig_ > 3.0 && mjjTrig_ > 300) {
          selVBFsoft_ = true;
          if (dEtaqq_[2] > 3.5 && mqq_[2] > 700 && dEtaTrig_ > 3.5 && mjjTrig_ > 700) {
            selVBF_ = true;
          } 
        }
      }
      //--------------------------------------------------------------
      bool SELECTION(false);
      if (forceNOM_) {
        SELECTION = selNOMsoft_;
      }
      if (forceVBF_) {
        SELECTION = selVBFsoft_;
      }
      if (!forceNOM_ && !forceVBF_) {
        SELECTION = cut_Btag_NOM && ((dEtaqq_[1]>dEtaMin_ && dPhibb_[1]<dPhiMax_) || (dEtaqq_[2]>dEtaMin_ && dPhibb_[2]<dPhiMax_));
      }
      if (SELECTION) { 
        outTree_->Fill();     
      }
    }// if nJets > 3
  }// if vtx
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::order(vector<float> const& v, vector<int>* idx, int Nmax)
{
  vector<float> tmp;
  int N = min(int(v.size()),Nmax);
  for(int i=0;i<N;i++) {
    idx->push_back(i);
    tmp.push_back(v[i]); 
  }
  for(int i=0;i<N;i++) {
    for(int j=i+1;j<N;j++) {
      if (tmp[j] > tmp[i]) {
        int k = (*idx)[i];
        (*idx)[i] = (*idx)[j];
        (*idx)[j] = k;
        float x = tmp[i]; 
        tmp[i] = tmp[j];
        tmp[j] = x;
      }
    } 
  }
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::initialize()
{
  selVBF_     = false;
  selVBFsoft_ = false;
  selNOM_     = false;   
  selNOMsoft_ = false;
  for(int i=0;i<4;i++) {
    cosTheta_[i]   = -999;
    mbb_[i]        = -999;
    mbbReg_[i]     = -999;
    dEtaqq_[i]     = -999;
    dEtabb_[i]     = -999;
    dPhiqq_[i]     = -999;
    dPhibb_[i]     = -999;
    ptbb_[i]       = -999;
    etabb_[i]      = -999;
    etaRatio_[i]   = -999;
    ptRatio_[i]    = -999;
    b1_[i]         = -999;
    b2_[i]         = -999;
    q1_[i]         = -999;
    q2_[i]         = -999;
  } 
  run_            = -999;
  evt_            = -999;
  lumi_           = -999;
  nVtx_           = -999;
  nSoftJets_      = -999;
  nSoftJets2_     = -999;
  nSoftJets5_     = -999;
  nSoftJets2noLep_= -999;
  nJets_          = -999;
  nBJets_         = -999;
  nLeptons_       = -999;
  rho_            = -999;
  met_            = -999;
  metPhi_         = -999;
  metSig_         = -999;
  ht_             = -999;
  softHt_         = -999;
  softHtnoLep_    = -999;
  sphericity_     = -999;
  aplanarity_     = -999;
  x1_             = -999;
  x2_             = -999;
  mvaNOM_         = -999;
  mvaVBF_         = -999;
  mvaNOMnoLep_    = -999;
  mvaVBFnoLep_    = -999;
  mjjTrig_        = -999; 
  dEtaTrig_       = -999; 
  lepChId_        ->clear();
  lepIso_         ->clear();
  lepPt_          ->clear();
  lepEta_         ->clear();
  lepPhi_         ->clear();
  lepE_           ->clear();
  pt_             ->clear();
  eta_            ->clear();
  phi_            ->clear();
  jetMetPhi_      ->clear();
  mass_           ->clear();
  energy_         ->clear();
  chf_            ->clear();
  nhf_            ->clear();
  phf_            ->clear();
  elf_            ->clear();
  muf_            ->clear();
  jec_            ->clear();
  regPt_          ->clear();
  regE_           ->clear();
  btag_           ->clear();
  btagIdx_        ->clear();
  blikNOM_        ->clear();
  blikVBF_        ->clear();
  blikNOMIdx_     ->clear();
  blikVBFIdx_     ->clear();
  etaIdx_         ->clear();
  qgl_            ->clear();
  puMva_          ->clear();
  unc_            ->clear();
  puIdL_          ->clear();
  puIdM_          ->clear();
  puIdT_          ->clear();
  idL_            ->clear();
  idM_            ->clear();
  idT_            ->clear();
  btagL_          ->clear();
  btagM_          ->clear();
  btagT_          ->clear();
  triggerResult_  ->clear();
  if (saveJetProperties_) {
    ptD_            ->clear();
    ptD_QC_         ->clear();
    vtx3dL_         ->clear();
    vtx3deL_        ->clear();
    vtxPt_          ->clear();
    vtxMass_        ->clear();
    softLepPt_      ->clear();
    softLepPtRel_   ->clear();
    softLepDR_      ->clear();
    softLepSigDB3D_ ->clear();
    softLepId_      ->clear();
    part_           ->clear();
    axisMinor_      ->clear();
    axisMajor_      ->clear();
    axisMinor_QC_   ->clear();
    axisMajor_QC_   ->clear();
    pull_           ->clear(); 
    pull_QC_        ->clear();
    jetR_           ->clear();
    leadTrkPt_      ->clear();
    jetRChg_QC_     ->clear();
    nChg_QC_        ->clear();
    nChg_ptCut_     ->clear();
    nNeutral_ptCut_ ->clear();
  }
  if (saveSoftJets_) {
    softJetPt_      ->clear(); 
    softJetEta_     ->clear();
    softJetPhi_     ->clear();
    softJetE_       ->clear();
  }
  //----- MC -------
  npu_ = -999;
  if (savePartons_) {
    partonSt_      ->clear();
    partonId_      ->clear();
    partonMatchIdx_->clear();
    partonMatchDR_ ->clear();
    partonPt_      ->clear();
    partonEta_     ->clear();
    partonPhi_     ->clear();
    partonE_       ->clear();
    genjetPt_      ->clear();
    genjetEta_     ->clear();
    genjetPhi_     ->clear();
    genjetE_       ->clear();
  }
  pdfX1_  = -999.;
  pdfX2_  = -999.;
  pdfID1_ = -999;
  pdfID2_ = -999;
  pdfQ_   = -999.;
}
//////////////////////////////////////////////////////////////////////////////////////////
float VbfHbbFlatTreeProducer::shiftCSV(float value)
{
  float x1,x2,y1,y2,result(-1.0);
  if (value >=0 && value < 0.1875) {
    x1 = 0;
    x2 = 0.1875;
    y1 = 0;
    y2 = 0.244;
  }
  else if (value >= 0.1875 && value < 0.7125) {
    y1 = 0.244;
    y2 = 0.679;
    x1 = 0.1875;
    x2 = 0.7125;
  }
  else if (value >= 0.7125 && value < 0.8875) {
    y1 = 0.679;
    y2 = 0.898;
    x1 = 0.7125;
    x2 = 0.8875;
  }
  else if (value >= 0.8875) {
    y1 = 0.898;
    y2 = 1.0;
    x1 = 0.8875;
    x2 = 1.0;
  }
  else {
    return value;
  }
  float z1 = y1*(x2-value)/(x2-x1);
  float z2 = y2*(value-x1)/(x2-x1);
  result = z1+z2;
  return result;
}
//////////////////////////////////////////////////////////////////////////////////////////
float VbfHbbFlatTreeProducer::shiftQGL(float value)
{
  float result = 0.5*(tanh(0.98*TMath::ATanH(2*value-1)+0.02)+1);
  return result;
}
//////////////////////////////////////////////////////////////////////////////////////////
float VbfHbbFlatTreeProducer::getSF(TH2 *h, float x, float y, bool interpolate)
{
  float result(1.0);
  if (interpolate) {
    float x_1 = h->GetXaxis()->GetBinCenter(1);
    float x_2 = h->GetXaxis()->GetBinCenter(h->GetNbinsX());
    float y_1 = h->GetYaxis()->GetBinCenter(1);
    float y_2 = h->GetYaxis()->GetBinCenter(h->GetNbinsY());
    float x0 = x;
    float y0 = y;
    if (x < x_1) {
      x0 = x_1; 
    } 
    if (x > x_2) {
      x0 = x_2;
    }
    if (y < y_1) {
      y0 = y_1; 
    } 
    if (y > y_2) {
      y0 = y_2;
    }
    result = h->Interpolate(x0,y0);
  }
  else {
    int bin = h->FindBin(x,y);
    result = h->GetBinContent(bin);
  }
  return result;
}
//////////////////////////////////////////////////////////////////////////////////////////
void VbfHbbFlatTreeProducer::fillWeights()
{
  char name[1000];
  //------ pu weights ----------------------
  puHisto_->Scale(1./puHisto_->Integral());
  edm::FileInPath fPu[5] = {
    edm::FileInPath("KKousour/CMGAnalysis/data/pu2012DCONLY.root"),
    edm::FileInPath("KKousour/CMGAnalysis/data/pileUp_DiJet35.root"),
    edm::FileInPath("KKousour/CMGAnalysis/data/pileUp_DiPFJetAve40.root"),
    edm::FileInPath("KKousour/CMGAnalysis/data/pileUp_DiPFJetAve80.root"),
    edm::FileInPath("KKousour/CMGAnalysis/data/pileUp_PFJet80.root")
  };
  TFile *puf[5];
  TH1D *puRef[5],*puWeightHisto[5];
  for(int i=0;i<5;i++) {
    puf[i]   = new TFile(TString(fPu[i].fullPath()));
    puRef[i] = (TH1D*)puf[i]->Get("pileup_trunc");
    puRef[i]->Sumw2();
    puRef[i]->Rebin(25);
    puRef[i]->Scale(1./puRef[i]->Integral());
    sprintf(name,"puWeight%d",i);
    puWeightHisto[i] = (TH1D*)puRef[i]->Clone(name);
    puWeightHisto[i]->Divide(puHisto_);
  }
  //------ trigger weights -----------------
  edm::FileInPath fNOM("KKousour/CMGAnalysis/data/TriggerScaleFactorNOM.root");
  edm::FileInPath fVBF("KKousour/CMGAnalysis/data/TriggerScaleFactorVBF.root");
  TFile *trigNOMf = new TFile(TString(fNOM.fullPath()));
  TFile *trigVBFf = new TFile(TString(fVBF.fullPath()));
  TH2F *trigMapNOMHisto1 = (TH2F*)trigNOMf->Get("SF1");
  TH2F *trigMapNOMHisto2 = (TH2F*)trigNOMf->Get("SF2");
  TH2F *trigMapVBFHisto  = (TH2F*)trigVBFf->Get("SF");
  int npu,b1[4],b2[4];
  float puWt[5] = {1.0,1.0,1.0,1.0,1.0};
  float trigWtNOM[2],trigWtVBF,mqq[4],dEtaqq[4];
  vector<float> *btag(0);
  TBranch *br1 = outTree_->Branch("puWt"     ,&puWt     ,"puWt[5]/F");
  TBranch *br2 = outTree_->Branch("trigWtVBF",&trigWtVBF,"trigWtVBF/F");
  TBranch *br3 = outTree_->Branch("trigWtNOM",&trigWtNOM,"trigWtNOM[2]/F");
  outTree_->SetBranchAddress("npu"    ,&npu);
  outTree_->SetBranchAddress("mqq"    ,&mqq);
  outTree_->SetBranchAddress("dEtaqq" ,&dEtaqq);
  outTree_->SetBranchAddress("jetBtag",&btag);
  outTree_->SetBranchAddress("b1"     ,&b1);
  outTree_->SetBranchAddress("b2"     ,&b2);
  cout<<"Filling tree with weights"<<endl;
  for(int i=0;i<outTree_->GetEntries();i++) {
    outTree_->GetEvent(i);
    for(int j=0;j<5;j++) {
      puWt[j] = puWeightHisto[j]->GetBinContent(puWeightHisto[j]->FindBin(npu));
    }
    trigWtNOM[0] = getSF(trigMapNOMHisto1,(*btag)[b1[0]],(*btag)[b2[0]],false);
    trigWtNOM[1] = getSF(trigMapNOMHisto2,(*btag)[b1[0]],mqq[1],false);
    trigWtVBF    = getSF(trigMapVBFHisto,dEtaqq[2],mqq[2],true);
    br1->Fill();
    br2->Fill();
    br3->Fill();
  }
  for(int i=0;i<5;i++) {
    puf[i]->Close();
    delete puf[i]; 
  }
  trigNOMf->Close();
  trigVBFf->Close();
  delete trigNOMf;
  delete trigVBFf;
  cout<<"Ended weights"<<endl;
}
//////////////////////////////////////////////////////////////////////////////////////////
VbfHbbFlatTreeProducer::~VbfHbbFlatTreeProducer() 
{
}

DEFINE_FWK_MODULE(VbfHbbFlatTreeProducer);
















