# File:"C:\Users\PSStudies\Desktop\case.py", generated on SAT, FEB 24 2024  14:08, PSS(R)E Xplore release 35.03.03
import os
import sys
import pandas as pd

df = pd.read_csv('FeederModel.csv',header = None,skiprows = 2)
# PCS-21A-8,8,PCS-21A-7,7,21A,34.5,0.00144,0.0024,0.00204,0.018,0.00204
frombus = (df.iloc[:,1]).astype(int)
frombusname = df.iloc[:,0]
tobus = (df.iloc[:,3]).astype(int)
tobusname = df.iloc[:,2]

print(frombus)
print(tobus)
allbus = list(set(frombus.tolist()+tobus.tolist()))

# allbusd = frombus+tobus

# allbus = list(set((allbusd)))

# print(allbus.sort())



binpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSBIN"
libpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSLIB"
pythonpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSPY39"

sys.path.append(binpath)
sys.path.append(libpath)
sys.path.append(pythonpath)

os.environ['Path'] = os.environ['Path']+';'+binpath
os.environ['Path'] = os.environ['Path']+';'+libpath
os.environ['Path'] = os.environ['Path']+';'+pythonpath

import psse35
import psspy
psspy.psseinit(50)
psspy.newcase_2([0,1], 100.0, 60.0,"","")

pmax_MW = 4.0
qmax_MW =2.0


for busnum, busname in zip(frombus,frombusname):

    busnumber = busnum
    busname = busname
    print(busnumber,busname)
    intgarbus = [1,1,1,1]
    realarbus = [34.5, 1.0,0.0, 1.1, 0.9, 1.1, 0.9] #change first input
    psspy.bus_data_4(busnumber, 0, intgarbus, realarbus, busname)
    lvbusrealar = realarbus
    genbusintegar = [2,1,1,1]
    
    lvbusrealar[0] = 0.63
    psspy.bus_data_4(busnumber*10, 0, genbusintegar, lvbusrealar, busname+'Gen')

    psspy.two_winding_data_6(busnumber, busnumber*10,r"""1""",[1,busnumber,1,0,0,0,33,0,busnumber,0,0,1,0,1,1,1],[0.0, 0.07, 4.4, 1.0,0.0,0.0, 1.0,0.0, 1.0, 1.0, 1.0, 1.0,0.0,0.0, 1.1, 0.9, 1.1, 0.9,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
0.0,0.0,0.0],"","")
    # [_f, 0.055, 4.0,_f, 34.5,_f,_f, 0.63,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f]


    # psspy.plant_data_4(busnumber,0,[0,0],[ 1.0, 100.0])
    # psspy.machine_data_4(busnumber,r"""1""",[1,1,0,0,0,0,0],[0.0,0.0, pmax_MW,-pmax_MW, qmax_MW,-qmax_MW, 100.0,0.0, 1.0,0.0,0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],"")

for busnum, busname in zip(tobus,tobusname):

    busnumber = busnum
    busname = busname
    print(busnumber,busname)
    intgarbus = [2,1,1,1]
    realarbus = [34.5, 1.0,0.0, 1.1, 0.9, 1.1, 0.9] #change first input
    psspy.bus_data_4(busnumber, 0, intgarbus, realarbus, busname)
    lvbusrealar = realarbus
    lvbusrealar[0] = 0.63
    psspy.bus_data_4(busnumber*10, 0, intgarbus, lvbusrealar, busname+'Gen')


    psspy.two_winding_data_6(busnumber, busnumber*10,r"""1""",[1,busnumber,1,0,0,0,33,0,busnumber,0,0,1,0,1,1,1],[0.0, 0.07, 4.4, 1.0,0.0,0.0, 1.0,0.0, 1.0, 1.0, 1.0, 1.0,0.0,0.0, 1.1, 0.9, 1.1, 0.9,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
0.0,0.0,0.0],"","")
    # [_f, 0.055, 4.0,_f, 34.5,_f,_f, 0.63,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f]


for busnumber in allbus:

    psspy.plant_data_4(busnumber*10,0,[0,0],[ 1.0, 100.0])
    print("started")
    psspy.machine_data_4(busnumber*10,r"""1""",[1,1,0,0,0,2,0],[pmax_MW,qmax_MW, qmax_MW,-qmax_MW,pmax_MW,-pmax_MW,  100.0,0.0, 1.0,0.0,0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],"")
    print("added")


    # 


branches = range(len(df))
intgarbranch = [1,1,1,0,0,0]
realarbranch = [0.0, 0.0001,0.0,0.0,0.0,0.0,0.0,0.0, 1.0, 1.0, 1.0, 1.0]
ratings = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
for branch,frombus,tobus in zip(branches,frombus,tobus):
    print('in branch creation')
    print(branch, frombus, tobus)
    intgarbranch[1] = frombus
    realarbranch[0]= df.iloc[branch,:][7]
    realarbranch[1]= df.iloc[branch,:][8]
    realarbranch[2]= df.iloc[branch,:][9]
    psspy.branch_data_3(frombus,tobus,'1',intgarbranch,realarbranch,ratings,"")
print(psspy.bus_output())

psspy.save(os.getcwd()+'\\casebuild2.sav')
# psspy.runrspnsfile('mpttoinf.idv')
psspy.save(os.getcwd()+'\\casebuild2.sav')
