#ifndef VbfHbbFlatTreeProducer_h
#define VbfHbbFlatTreeProducer_h

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionData.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionEvaluator.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionParser.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "TTree.h"
#include "TH1.h"
#include "TH2.h"
#include "KKousour/CMGAnalysis/plugins/QGLCalculator.h"
#include "KKousour/CMGAnalysis/plugins/JetRegressor.h"
#include "KKousour/CMGAnalysis/plugins/BJetLikelihood.h"
#include "KKousour/CMGAnalysis/plugins/DiscriminatorMVA.h"

class VbfHbbFlatTreeProducer : public edm::EDAnalyzer 
{
  public:
    typedef reco::Particle::LorentzVector LorentzVector;
    explicit VbfHbbFlatTreeProducer(edm::ParameterSet const& cfg);
    virtual void beginJob();
    virtual void analyze(edm::Event const& iEvent, edm::EventSetup const& iSetup);
    virtual void endJob();
    virtual ~VbfHbbFlatTreeProducer();

  private:  
    void initialize();
    void fillWeights();
    void order(std::vector<float> const& v, std::vector<int>* idx, int Nmax);
    float getSF(TH2 *h, float x, float y, bool interpolate);
    float shiftCSV(float value);
    float shiftQGL(float value);
    //---- configurable parameters --------   
    edm::InputTag srcJets_,srcSoftJets_,srcGenJets_,srcMET_,srcRho_,srcGenParticles_;
    std::string srcBtag_,srcPU_,puTag_,jetReg_xml_;
    double shiftJES_;
    double ptMin_;
    double etaMax_;
    double dEtaMin_;
    double dPhiMax_;
    bool   saveSoftJets_,savePartons_,saveJetProperties_;
    bool   forceNOM_,forceVBF_,jetReg_massless_;
    bool   correctCSV_,correctQGL_;
    std::vector<double> btagThresholds_;
    edm::Service<TFileService> fs_;
    TTree *outTree_; 
    //---- TRIGGER -------------------------
    triggerExpression::Data triggerCache_;
    std::vector<triggerExpression::Evaluator*> vtriggerSelector_;
    std::vector<std::string> vtriggerAlias_,vtriggerSelection_;
    TH1F *triggerPassHisto_,*triggerNamesHisto_,*puHisto_;
    //---- output TREE variables ------
    //---- global event variables -----
    bool  selNOM_,selNOMsoft_,selVBF_,selVBFsoft_;
    int   run_,evt_,nVtx_,lumi_,nSoftJets_,nSoftJets2_,nSoftJets5_,nSoftJets2noLep_,nJets_,nLeptons_,nBJets_;
    int   b1_[4],b2_[4],q1_[4],q2_[4];
	 int   pdfID1_, pdfID2_;
	 float pdfX1_, pdfX2_, pdfQ_;
    float rho_,met_,metPhi_,metSig_,ht_,sphericity_,aplanarity_,softHt_,softHtnoLep_,mjjTrig_,dEtaTrig_;
    float mqq_[4],mbb_[4],mbbReg_[4],dEtaqq_[4],dEtabb_[4],dPhiqq_[4],dPhibb_[4],ptbb_[4],etabb_[4];
    float x1_,x2_,cosTheta_[4],etaRatio_[4],ptRatio_[4];
    float mvaNOM_,mvaVBF_,mvaNOMnoLep_,mvaVBFnoLep_;
    std::vector<bool> *triggerResult_;
    //---- jet variables --------------
    std::vector<bool>  *puIdL_,*puIdM_,*puIdT_,*idL_,*idM_,*idT_,*btagL_,*btagM_,*btagT_;
    std::vector<int>   *btagIdx_,*etaIdx_,*blikNOMIdx_,*blikVBFIdx_;
    std::vector<int>   *part_,*nChg_QC_,*nChg_ptCut_,*nNeutral_ptCut_,*softLepId_;
    std::vector<float> *pt_,*jec_,*regPt_,*regE_,*unc_,*eta_,*phi_,*mass_,*energy_,*chf_,*nhf_,*phf_,*elf_,*muf_,*jetMetPhi_;
    std::vector<float> *ptD_,*ptD_QC_,*btag_,*puMva_,*qgl_,*blikNOM_,*blikVBF_;
    std::vector<float> *vtxMass_,*vtxPt_,*vtx3dL_,*vtx3deL_,
                       *softLepPt_,*softLepPtRel_,*softLepDR_,*softLepSigDB3D_,*leadTrkPt_;
    std::vector<float> *axisMinor_,*axisMajor_,*axisMinor_QC_,*axisMajor_QC_,*pull_,*pull_QC_,*jetR_,*jetRChg_QC_;
    //---- lepton variables -----------
    std::vector<int>   *lepChId_;
    std::vector<float> *lepPt_,*lepEta_,*lepPhi_,*lepE_,*lepIso_;
    //---- soft activity --------------
    std::vector<float> *softJetPt_,*softJetEta_,*softJetPhi_,*softJetE_;
    //---- MC variables ---------------
    int npu_;
    std::vector<int>   *partonId_,*partonSt_,*partonMatchIdx_;
    std::vector<float> *partonPt_,*partonEta_,*partonPhi_,*partonE_,*partonMatchDR_;
    std::vector<float> *genjetPt_,*genjetEta_,*genjetPhi_,*genjetE_;
     
    //---- QGL tagger -----------------
    QGLCalculator *qglCalc_;
    //---- Jet regressor -----------------
    JetRegressor *jetReg_;
    //---- BJet likelihood ---------------
    BJetLikelihood *bjetLikNOM_,*bjetLikVBF_;
    //---- MVA discriminators ------------
    DiscriminatorMVA *discrNOM_,*discrVBF_;
};

#endif
