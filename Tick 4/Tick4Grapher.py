import numpy as np
import matplotlib.pyplot as plt
import pickle 

F = open('SimData.data', 'rb')
(N, T, MobilityDays, MobilityMeanFromDay, Reruns, CapitalGainsMults, OutputList) = pickle.load(F)
F.close()

MeanGinis = np.empty(len(CapitalGainsMults))
VarianceGinis = np.empty(len(CapitalGainsMults))
MeanMobilities = np.empty(len(CapitalGainsMults))
VarianceMobilities = np.empty(len(CapitalGainsMults))

for (Mult, AllGinis, AllRunMobilities) in OutputList:
    
    WantedMobilities = np.empty(Reruns)
    for i, MobilityForRun in enumerate(AllRunMobilities):  
        WantedMobilities[i] = MobilityForRun[MobilityMeanFromDay - 1]

    i = CapitalGainsMults.index(Mult)
    MeanGinis[i] = np.mean(AllGinis)
    VarianceGinis[i] = np.std(AllGinis) / np.sqrt(len(AllGinis))
    MeanMobilities[i] = np.mean(WantedMobilities)
    VarianceMobilities[i] = np.std(WantedMobilities) / np.sqrt(len(WantedMobilities))
    
Fig, Axes = plt.subplots(figsize=(8, 6))
Axes.set_title("Impact of capital gains rate on inequality and mobility")
Axes.set_xlabel("Gini coefficient")
Axes.set_ylabel("Mobility after {fromVal} steps".format(fromVal=MobilityMeanFromDay))  

Axes.errorbar(MeanGinis, MeanMobilities, VarianceMobilities, VarianceGinis, color = (1, 0, 0), zorder = 0)
Axes.plot(MeanGinis, MeanMobilities, zorder = 1)
Axes.scatter(MeanGinis, MeanMobilities, color = (0, 0.75, 0.75), zorder = 2)

if (len(MeanGinis) > 0):
    OffsetX = MeanGinis[0] * 0.00055
    OffsetY = - MeanMobilities[0] * 0.018
    for i, (x, y) in enumerate(zip(MeanGinis, MeanMobilities)):
        plt.text(x + OffsetX, y + OffsetY, CapitalGainsMults[i], fontsize = 9)

plt.text(0.04,0.88, "N = {nVal}\nTimesteps = {tVal}\nRuns per CGR = {runVal}".format(nVal=N, tVal=T, runVal=Reruns), fontsize = 7, color = 'r', transform=Axes.transAxes)

plt.show()
