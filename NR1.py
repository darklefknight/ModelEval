from netCDF4 import Dataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
#    NC_FILE = "/home/mpim/m300517/Downloads/modeleval_2016.nc"
    NC_FILE = "/data/share/lehre/unix/edvprak/Evaluat/modeleval_2016.nc"

    nc = Dataset(NC_FILE)

    heights = nc.variables["z"][:].copy()
    times = nc.variables["time"][:].copy()
    temp = nc.variables["t"][0,:,:].copy()
    rh = nc.variables["rh"][0,:,:].copy()
    q = nc.variables["q"][0,:,:].copy()
    windSpeed = nc.variables["ff"][0,:,:].copy()
    windDirect = nc.variables["dd"][0,:,:].copy()

    windDirect = pd.DataFrame(windDirect.transpose())
    windSpeed = pd.DataFrame(windSpeed.transpose())
    temp = pd.DataFrame(temp.transpose())

    variables = [temp,windSpeed,windDirect]
    variable_names = ["temp","Windspeed","Winddirection"]
    deviations = [0.5, ]

    # Hit Rates:
    print("HIT RATES")

    for variable,name in zip(variables,variable_names):

        for i,height in enumerate(heights):
            rates = []
            lefts = []
            AbsDev = abs(variable[i] - variable[i].median())
            AbsDev = AbsDev.median()
            if name == "temp":
                AbsDev = 0.5
            elif name == "Windspeed":
                AbsDev = 0.5
            elif name == "Winddirection":
                AbsDev = 23
            for t,time in enumerate(times):
                left = abs(variable[i][t] - variable[5][t])
#                print(left)
                if not np.isnan(left):
                    lefts.append(variable[i][t] - variable[5][t])
                # print(AbsDev)
                if left<=AbsDev:
                    rates.append(1)
                else:
                    rates.append(0)
            
            

#            lefts = pd.DataFrame(lefts)
            plt.hist(lefts)
            plt.xlim=(-15,15)
            plt.savefig("%s%i.png"%(name,height))
            plt.close()
            hit_rate = sum(rates)/len(rates)
            try:
                print(name,height,hit_rate, np.percentile(lefts,0.05),np.percentile(lefts,0.5),np.percentile(lefts,0.95))
            except:
                pass
