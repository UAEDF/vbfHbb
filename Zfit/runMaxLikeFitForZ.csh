#!/bin/csh

#combine -M MaxLikelihoodFit --saveNormalizations --plots --stepSize=0.05 --preFitValue=1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.01 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=2 --minimizerTolerance=0.05 --rMin=-10 --rMax=10 datacard_Z.txt -n "Z"

#combine -M MultiDimFit --points 50 --rMin -1 --rMax 3 --algo grid datacard_Z.txt -n "Z"
combine -M MultiDimFit --points 50 --rMin -1 --rMax 3 --algo grid datacard_Z.txt -n "ExpectedZ" -t -1 --expectSignal=1 --toysFreq

#combine -M ChannelCompatibilityCheck --saveFitResult --stepSize=0.05 --preFitValue=1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --minimizerAlgoForMinos=Minuit2 --minimizerToleranceForMinos=0.01 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --minimizerAlgo=Minuit2 --minimizerStrategy=2 --minimizerTolerance=0.05 --rMin=-10 --rMax=10 datacard_Z.txt -n "Z"

#combine -M ProfileLikelihood --significance datacard_Z.txt -n "ExpectedZ" -t -1 --expectSignal=1 --toysFreq

#combine -M ProfileLikelihood --signif datacard_Z.txt -n "ObservedZ"

#text2workspace.py datacard_Z.txt


