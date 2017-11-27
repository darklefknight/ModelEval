from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def calcVeryfy(mod,obs):
    hitRates = []
    falseAlarmRates = []
    baseRates = []
    FARs = []
    BIASs = []
    GSSs = []
    HSSs = []
    PSSs = []
    for speed in range(17):
        a = 0
        b = 0
        c = 0
        d = 0
        for i in range(len(mod)):
            try:
                m =  int(round(mod[i],0))
                o = int(round(obs[i],0))
            except: # if nan then continue
                continue
            if (m == speed) and (o==speed):
                a += 1

            elif (m == speed) and (o != speed):
                b += 1

            elif (m != speed) and (o==speed):
                c+=1

            elif (m != speed) and (o != speed):
                d += 1
            else:
                print("Error!")

        if (a+b+c+d) != 0:
            a_r = (a+b)*(a+c)/(a+b+c+d) # random_hits
            d_r = (b + d) * (c + d) / (a + b + c + d)
        else:
            a_r = 9e99
            d_r = 9e99


        # Base rate:
        if a+b+c+d != 0:
            baserate = (a+c)/(a+b+c+d)
        else:
            baserate = 0
        baseRates.append(baserate)

        # hit rate:
        if a+c != 0:
            hitrate = a/(a+c)
        else:
            hitrate = 0
        hitRates.append(hitrate)

        # falseAlarmRate:
        if b+d != 0:
            falseAlarmRate = b/(b+d)
        else:
            falseAlarmRate = 0
        falseAlarmRates.append(falseAlarmRate)

        #FAR:
        if a+b != 0:
            FAR = a/(a+b)
        else:
            FAR = 0
        FARs.append(FAR)

        # BIAS:
        if a+c != 0:
            BIAS = (a+b)/(a+c)
        else:
            BIAS = 0
        BIASs.append(BIAS)

        # Gilbert Skill score:
        if (a+b+c-a_r) != 0:
            GSS = (a-a_r)/(a+b+c-a_r)
        else:
            GSS = 0
        GSSs.append(GSS)

        # Heidke Skill score:
        if (a+b+c+d-a_r-d_r) != 0:
            HSS = (a+d-a_r-d_r)/(a+b+c+d-a_r-d_r)
        else:
            HSS = 0
        HSSs.append(HSS)

        # Peirce skill score:
        if ((d+b)*(a+c)) != 0:
            PSS = (a*d-b*c)/((b+d)*(a+c))
        else:
            PSS = 0
        PSSs.append(PSS)


    df = pd.DataFrame({"H":hitRates,"F":falseAlarmRates,"FAR":FARs,"BIAS":BIASs,"GSS":GSSs,"HSS":HSSs,"PSS":PSSs,"s":baseRates})
    return df



def RV(mod,obs):
    threshold = 10
    a,b,c,d = 0,0,0,0
    COST = 0
    LOSS = 0
    for i in range(len(mod)):
        if (obs[i] > threshold) and (mod[i] > threshold):
            COST +=1
            a += 1
        elif (obs[i] <= threshold) and (mod[i] > threshold):
            COST += 1
            b += 1
        elif (obs[i] > threshold) and (mod[i] <= threshold):
            LOSS += 1
            c += 1
        elif (obs[i] <= threshold) and (mod[i] <= threshold):
            d += 1

    base_rate = (a+c)/(a+b+c+d)

    if COST/LOSS < base_rate:
        E_clim = COST
    else:
        E_clim = np.multiply(base_rate,LOSS)

    E_real = np.add(np.multiply(a+b,COST),np.multiply(COST,LOSS))
    E_perf = np.multiply(base_rate,COST)

    RV_ret = np.divide(np.subtract(E_real,E_perf),np.subtract(E_clim,E_perf))
    C_L = np.divide(COST,LOSS)
    return RV_ret,C_L













if __name__ == "__main__":
    font = 24

    PATH = "/home/mpim/m300517/Downloads/"
    FILE = "modeleval_2016.nc"

    nc = Dataset(PATH + FILE)
    ff_mod24 = nc.variables["ff"][-1,:,:]
    ff_obs = nc.variables["ff"][0,:,:]
    heights = nc.variables["z"][:]
    nc.close()

    # ff_obs[np.where(np.isnan(ff_obs))] = 999
    # ff_mod24[np.where(np.isnan(ff_mod24))] = 999

    # ===========================================================================
    # Aufgabe 1:
    # ===========================================================================

    fig = plt.figure(figsize=(16,9))
    ax1 = fig.add_subplot(111)
    ax1.set_title("Quantile-Quantile plot for observed vs. 24h forecast windspeeds", fontsize=font)


    for i in range(6):
        ff_m = np.sort(ff_mod24[i,:])
        ff_o = np.sort(ff_obs[i,:])

        ax1.plot(ff_o,np.subtract(ff_m,ff_o), lw=3 ,label=str(heights[i]))
    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(18)
    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(18)

    ax1.legend(loc="upper right",fontsize=font)
    ax1.set_xlabel("v$_{OBS}$ (m/s)",fontsize=font)
    ax1.set_ylabel("v$_{MOD}$-v$_{OBS}$ (m/s)",fontsize=font)
    ax1.grid()
    plt.tight_layout()
    plt.savefig("q_q_plot.png")

    # ===========================================================================
    # Aufgabe 2:
    # ===========================================================================

    height= 3
    fig2, (ax1,ax2) = plt.subplots(nrows=1,ncols=2,figsize=(16,9))
    fig2.suptitle("Different Scores for Windspeeds at %4.0f hight"%heights[height],fontsize=font)

    axes = [ax1,ax2]

    speeds = [x for x in range(17)]

    df = calcVeryfy(ff_mod24[height], ff_obs[height])
    ax1.plot(speeds, df["BIAS"],label="BIAS",lw=2)
    ax1.plot(speeds,df["H"],label="Hit Rate",lw=2)
    ax1.plot(speeds,df["F"],label="False Alarm Rate",lw=2)
    ax1.plot(speeds,df["FAR"],label="False Alarm Ratio",lw=2)

    ax2.plot(speeds,df["GSS"],label="GSS",lw=2)
    ax2.plot(speeds,df["HSS"],label="HSS",lw=2)
    ax2.plot(speeds,df["PSS"],label="PSS",lw=2)

    for ax in axes:
        ax.grid()
        ax.legend(loc="best",fontsize=font)
        ax.set_xlabel("wind threshold (m/s)",fontsize=font)
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(18)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(18)

    plt.savefig("Scores_at_%im.png"%int(heights[height]))

    # ===========================================================================
    # Aufgabe 2:
    # ===========================================================================

    RV_plot,C_L = RV(ff_mod24[height],ff_obs[height])

    fig3, ax1 = plt.subplots(ncols=1,nrows=1,figsize=(16,9))

    ax1.plot(C_L,RV_plot)





