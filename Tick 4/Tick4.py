import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import pickle 

def Mobility(v,w):
    assert(len(v) == len(w))
    OldBins = np.percentile(v, np.array([20, 40, 60, 80, 100]))
    OldQuintiles = np.digitize(v, OldBins, True)
    NewBins = np.percentile(w, np.array([20, 40, 60, 80, 100]))
    NewQuintiles = np.digitize(w, NewBins, True)
    Delta = np.subtract(NewQuintiles, OldQuintiles)    
    MovedMultipleQuintilesCount = np.sum(np.where(abs(Delta) >= 2, 1, 0))
    return MovedMultipleQuintilesCount / len(v)

def Pairs(N):
    assert(N%2 == 0)
    SourceArray = np.arange(0, N)
    np.random.shuffle(SourceArray)    
    return (SourceArray[:N//2], SourceArray[N//2:])

def KineticExchange(v, w):
    R = np.random.rand(len(v))
    Sum = np.add(v, w)
    return (np.multiply(R, Sum), np.multiply(1 - R, Sum))

def ValueTransferTheorem(v, w):
    Rands = np.random.rand(len(v)) * 2 - 1
    RMins = np.minimum(v, w) * Rands
    return (v + RMins, w - RMins)

def Gini(w):
    Top = np.cumsum(np.multiply(np.arange(1, len(w)+1), np.sort(w)))[len(w) - 1]
    Bottom = np.cumsum(w)[len(w) - 1]
    return (2 / len(w)) *  (Top / Bottom) - 1 - 1 / len(w)

def SimPeriod(StartWealths, Incomes, TimeSteps, WealthGrowthMult):
    assert(len(StartWealths)%2 == 0)

    #Remember this is by ref
    Wealths = StartWealths    
    N = len(StartWealths)
    
    GiniCoefficients = np.empty(TimeSteps)
    
    for i in range(TimeSteps):
        Pairings = Pairs(N)
        V = np.take(Wealths, Pairings[0])
        W = np.take(Wealths, Pairings[1])
        #Sim expenses/trade
        newV, newW = ValueTransferTheorem(V, W)
        np.put(Wealths, Pairings[0], newV)
        np.put(Wealths, Pairings[1], newW) 
        #Capital gains
        #Change to do mean of old wealth + new to simualte bank interest? Take minimums instead?
        np.multiply(Wealths, WealthGrowthMult, out=Wealths)     
        #Income
        np.add(Wealths, Incomes, out=Wealths)       
        #Normalise
        np.divide(Wealths, np.max(Wealths), out=Wealths)
        if (i % 200 == 0 and i > 0):
            print("Completed 200 loops!")
        GiniCoefficients[i] = Gini(Wealths)
        
    return (Wealths, GiniCoefficients)

def SimPeriodNoGini(StartWealths, Incomes, TimeSteps, WealthGrowthMult):
    assert(len(StartWealths)%2 == 0)

    Wealths = StartWealths    
    N = len(StartWealths)
    
    for i in range(TimeSteps):
        Pairings = Pairs(N)
        V = np.take(Wealths, Pairings[0])
        W = np.take(Wealths, Pairings[1])
        #Sim expenses/trade
        newV, newW = ValueTransferTheorem(V, W)#KineticExchange(V, W)
        np.put(Wealths, Pairings[0], newV)
        np.put(Wealths, Pairings[1], newW) 
        #Capital gains
        #Change to do mean of old wealth + new to simualte bank interest? Take minimums instead?
        np.multiply(Wealths, WealthGrowthMult, out=Wealths)     
        #Income
        np.add(Wealths, Incomes, out=Wealths)       
        #Normalise
        np.divide(Wealths, np.max(Wealths), out=Wealths)
        if (i % 1000 == 0 and i > 0):
            print("Completed 1000 loops!")
        
    return Wealths

def DrawTestData(N, T, Mult, MobilityDays):    
    print("Started Sim!")
    
    Incomes = np.random.rand(N)    
    Wealths, Ginis = SimPeriod(np.ones(N), Incomes, T, Mult)
    Mobilities = np.empty(MobilityDays)
    
    print("Finished Sim!")
    
    FurtherWealths = np.copy(Wealths)    
    for i in range(0, len(Mobilities)):
        FurtherWealths, G = SimPeriod(FurtherWealths, Incomes, 1, Mult)
        Mobilities[i] = Mobility(Wealths, FurtherWealths)
        
    print("Finished Mobility Calcs!")
    
    Fig, Axes = plt.subplots(3, figsize=(8, 6))      

    plt.subplots_adjust(hspace = 0.5)
    Fig.suptitle("Wealths & Ginis")

    Barchart = {"color": "blue", "alpha" : 1}
    Linegraph = {"color": "blue", "alpha" : 1}

    Axes[0].bar(np.arange(1, N + 1), Wealths, **Barchart)
    Axes[0].set_xlabel("Person ID")
    Axes[0].set_ylabel("Wealth")  

    Axes[1].plot(np.arange(1, T + 1), Ginis, **Linegraph)
    Axes[1].set_xlabel("Time")
    Axes[1].set_ylabel("Gini")  

    Axes[2].plot(np.arange(1, MobilityDays + 1), Mobilities, **Linegraph)
    Axes[2].set_xlabel("Time")
    Axes[2].set_ylabel("Mobility")  

    plt.show()

def CalculateData(N, T, Mult, MobilityDays, Reruns):
    AllGinis = np.empty([Reruns, MobilityDays])
    AllMobilities = []
    for i in range(0, Reruns):
        print("Started Sim!")
        
        Incomes = np.random.rand(N)    
        Wealths = SimPeriodNoGini(np.ones(N), Incomes, T, Mult)
        AllGinis[i] = Gini(Wealths)
        
        Mobilities = np.empty(MobilityDays)
        FurtherWealths = np.copy(Wealths)
        
        for j in range(0, MobilityDays):
            SimPeriodNoGini(FurtherWealths, Incomes, 1, Mult)
            Mobilities[j] = Mobility(Wealths, FurtherWealths)

        AllMobilities.append(Mobilities)
    
    return (AllGinis, AllMobilities)

def CalculateDataMultiThread(N, T, Mult, MobilityDays, Reruns, OutputList):
    AllGinis = np.empty([Reruns, MobilityDays])
    AllMobilities = []
    for i in range(0, Reruns):
        print("Started Sim!")
        
        Incomes = np.random.rand(N)    
        Wealths = SimPeriodNoGini(np.ones(N), Incomes, T, Mult)
        AllGinis[i] = Gini(Wealths)
        
        Mobilities = np.empty(MobilityDays)
        FurtherWealths = np.copy(Wealths)
        
        for j in range(0, MobilityDays):
            SimPeriodNoGini(FurtherWealths, Incomes, 1, Mult)
            Mobilities[j] = Mobility(Wealths, FurtherWealths)

        AllMobilities.append(Mobilities)
    
    OutputList.append((Mult, AllGinis, AllMobilities))

N = 100000
T = 3000
MobilityDays = 200
MobilityMeanFromDay = 100
Reruns = 15
CapitalGainsMults = [1, 1.01, 1.025, 1.05, 1.1, 1.15, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0]

StartTime = time.time()

MeanGinis = np.empty(len(CapitalGainsMults))
MeanMobilities = np.empty(len(CapitalGainsMults))

Threads = []
OutputList = []
for i, Mult in enumerate(CapitalGainsMults):
    Threads.append(threading.Thread(target=CalculateDataMultiThread, args=(N, T, Mult, MobilityDays, Reruns, OutputList)))
    Threads[i].start()

for i in range(0, len(Threads)):
    Threads[i].join()
    
print("--- %s seconds ---" % (time.time() - StartTime))

F = open('SimData.data', 'wb')
pickle.dump((N, T, MobilityDays, MobilityMeanFromDay, Reruns, CapitalGainsMults, OutputList), F)
F.close()
