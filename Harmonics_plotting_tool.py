import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import datetime

df = pd.read_clipboard(sep = '\t',header = 0)

headers = list(df.columns.values)
thdword = "TDD"

h_order = df.iloc[1:,0]
fundamental_a  = df.iloc[0,2]
fundamental_b  = df.iloc[0,3]
fundamental_c  = df.iloc[0,4]

a = df.iloc[1:,2].to_numpy()

b = df.iloc[1:,3].to_numpy()

c = df.iloc[1:,4].to_numpy()

sum_of_squares_a = np.sum([num**2 for num in a])

thd = thdword + ' = '+str(np.round(np.sqrt(sum_of_squares_a)/fundamental_a*100,2))+r'%'

plt.figure(1,figsize=[10,4])

width = 0.2

plt.bar(h_order,a/fundamental_a*100,width=width)
plt.bar(h_order+width,b/fundamental_b*100,width=width)
plt.bar(h_order+2*width,c/fundamental_c*100,width=width)

plt.xticks(np.arange(2,len(df)+1,2))

plt.grid(axis = 'y',linestyle = '--')
plt.legend(headers[2:])
# plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

plt.xlabel('Harmonic Order')
plt.ylabel('Distortion (%)')

plt.annotate(thd,xy = (46,np.max(a/fundamental_a*50)))

import os

cwd = os.getcwd()

plt.savefig(cwd+'\\'+'Cap_off_MPT_HV_Current_harm.svg')
plt.show()