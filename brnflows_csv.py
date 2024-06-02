#[brnflows_csv.py]  Export BRANCH FLOWS to COMMA SEPARATED FILE (CSV)
# ====================================================================================================
'''
This is an example file showing how to use "subsystem data retrieval APIs
from Python to save branch flows to Comma Separated File.
    Input : Solved PSS(R)E saved case file name
    Output: CSV file name to save
    When 'savfile' is provided, FNSL with default options is used to solve the case.
    When 'savfile' is not provided, it uses solved Case from PSS(R)E memory.
    When 'csvfile' is provided, branch flows is saved in ASCII text file 'csvfile'.
    When 'csvfile' is not provided, it produces report in PSS(R)E report window.

The subsystem data retrieval APIs return values as List of Lists. For example:
When "abusint" API is called with "istrings" as defined below:
    istrings = ['number','type','area','zone','owner','dummy']
    ierr, idata = psspy.abusint(sid, flag_bus, istrings)
The returned list will have format:
    idata=[[list of 'number'],[list of 'type'],[],[],[],[list of 'dummy']]

This example is written such that, such returned lists are converted into dictionary with
keys as strings specified in "istrings". This makes it easier to refer and use these lists.
    ibuses = array2dict(istrings, idata)

So ibuses['number'] gives the bus numbers returned by "abusint".

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse34

- call function
    run_brnflowscsv()
    You may want to change input arguments when you call this function.
    run_brnflowscsv(savfile, csvfile)

'''
# ----------------------------------------------------------------------------------------------------
import os


import os,sys
psseversion = 34
#from tkinter import filedialog 
if psseversion==35:

    binpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSBIN"
    libpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSLIB"
    pythonpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSPY39"


if psseversion==34:
    
    binpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSBIN"
    libpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSLIB"
    pythonpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSPY37"

sys.path.append(binpath)
sys.path.append(libpath)
sys.path.append(pythonpath)

os.environ['Path'] = os.environ['Path']+';'+binpath
os.environ['Path'] = os.environ['Path']+';'+libpath
os.environ['Path'] = os.environ['Path']+';'+pythonpath
if psseversion==35:
    import psse35
if psseversion==34:
    print("version 34")
    import psse34  
import psspy
import pssarrays

psspy.psseinit(1000000)


psspy.case('CaseLF_lag_0.95hunp.sav')

# ----------------------------------------------------------------------------------------------------
def array2dict(dict_keys, dict_values):
    '''Convert array to dictionary of arrays.
    Returns dictionary as {dict_keys:dict_values}
    '''
    tmpdict = {}
    for i in range(len(dict_keys)):
        tmpdict[dict_keys[i].lower()] = dict_values[i]
    return tmpdict

# ----------------------------------------------------------------------------------------------------
def busindexes(busnum, busnumlist):
    '''Find indexes of a bus in list of buses.
    Returns list with indexes of 'busnum' in 'busnumlist'.
    '''
    busidxes = []
    startidx = 0
    buscounts = busnumlist.count(busnum)
    if buscounts:
        for i in range(buscounts):
            tmpidx = busnumlist.index(busnum,startidx)
            busidxes.append(tmpidx)
            startidx = tmpidx+1
    return busidxes

# ----------------------------------------------------------------------------------------------------
def splitstring_commaspace(tmpstr):
    '''Split string first at comma and then by space. Example:
    Input  tmpstr = a1       a2,  ,a4 a5 ,,,a8,a9
    Output strlst = ['a1', 'a2', ' ', 'a4', 'a5', ' ', ' ', 'a8', 'a9']
    '''
    strlst = []
    commalst = tmpstr.split(',')
    for each in commalst:
        eachlst = each.split()
        if eachlst:
            strlst.extend(eachlst)
        else:
            strlst.extend(' ')

    return strlst

# ----------------------------------------------------------------------------------------------------
def brnflows_csv(savfile,csvfile):
    '''Generates power flow result report.
    When 'savfile' is provided, FNSL with default options is used to solve the case.
    When 'savfile' is not provided, it uses solved Case from PSS(R)E memory.
    When 'csvfile' is provided, report is saved in ASCII text file 'csvfile'.
    When 'csvfile' is not provided, it produces report in PSS(R)E report window.
    '''

    import psspy
    psspy.psseinit()

    # Set Save and CSV files according to input file names
    if savfile:
        ierr = psspy.case(savfile)
        if ierr != 0: return
        fpath, fext = os.path.splitext(savfile)
        if not fext: savfile = fpath + '.sav'
    else:   # saved case file not provided, check if working case is in memory
        ierr, nbuses = psspy.abuscount(-1,2)
        if ierr != 0:
            print('\n No working case in memory.')
            print(' Either provide a Saved case file name or open Saved case in PSSE.')
            return
        savfile, snapfile = psspy.sfiles()

    if csvfile:  # open CSV file to write
        csvfile_h = open(csvfile,'w')
        report    = csvfile_h.write
    else:        # send results to PSS(R)E report window
        psspy.beginreport()
        report = psspy.report

    # ================================================================================================
    # PART 1: Get the required results data
    # ================================================================================================

    # Select what to report
    if psspy.bsysisdef(0):
        sid = 0
    else:   # Select subsytem with all buses
        sid = -1

    flag_brflow  = 1    # in-service
    owner_brflow = 1    # use bus ownership, ignored if sid is -ve
    ties_brflow  = 5    # ignored if sid is -ve

    # ------------------------------------------------------------------------------------------------
    # Branch Flow Data
    # Branch Flow Data - Integer
    istrings = ['fromnumber','tonumber','status','nmeternumber','owners','own1','own2','own3','own4']
    ierr, idata = psspy.aflowint(sid, owner_brflow, ties_brflow, flag_brflow, istrings)
    if ierr != 0: return
    iflow = array2dict(istrings, idata)
    # Branch Flow Data - Real
    rstrings = ['amps','pucur','pctrate','pctratea','pctrateb','pctratec','pctmvarate',
                'pctmvaratea','pctmvarateb',#'pctmvaratec','fract1','fract2','fract3',
                'fract4','rate','ratea','rateb','ratec',
                'p','q','mva','ploss','qloss',
                'o_p','o_q','o_mva','o_ploss','o_qloss'
                ]
    ierr, rdata = psspy.aflowreal(sid, owner_brflow, ties_brflow, flag_brflow, rstrings)
    if ierr != 0: return
    rflow = array2dict(rstrings, rdata)
    # Branch Flow Data - Complex
    xstrings = ['pq','pqloss','o_pq','o_pqloss']
    ierr, xdata = psspy.aflowcplx(sid, owner_brflow, ties_brflow, flag_brflow, xstrings)
    if ierr != 0: return
    xflow = array2dict(xstrings, xdata)
    # Branch Flow Data - Character
    cstrings = ['id','fromname','fromexname','toname','toexname','nmetername','nmeterexname']
    ierr, cdata = psspy.aflowchar(sid, owner_brflow, ties_brflow, flag_brflow, cstrings)
    if ierr != 0: return
    cflow = array2dict(cstrings, cdata)

    # ================================================================================================
    # PART 2: Write acquired results to Report file
    # ================================================================================================

    report("Branch flows from Saved case: %s\n" %savfile)

    clnttls = "%6s,%18s,%18s,%6s,%18s,%18s,%3s,%3s,%9s,%9s,%9s,%6s,%8s,%8s\n" %('FRMBUS',
             'FROMBUSEXNAME','Frombusvoltage','TOBUS','TOBUSEXNAME','Tobusvoltage','CKT','STS','MW','MVAR','MVA','%I','MWLOSS','MVARLOSS')
    report(clnttls)
    for i in range(len(iflow['fromnumber'])):
        fromnum    = iflow['fromnumber'][i]
        fromexname = cflow['fromexname'][i]
        tonum      = iflow['tonumber'][i]
        toexname   = cflow['toexname'][i]
        ckt        = cflow['id'][i]
        status     = iflow['status'][i]
        p          = rflow['p'][i]
        q          = rflow['q'][i]
        mva        = rflow['mva'][i]
        ploss      = rflow['ploss'][i]
        qloss      = rflow['qloss'][i]
        pcti       = rflow['pctrate'][i]

        
        buses = [fromnum,tonum]
       
        psspy.bsys(0,0,[0.0,0.0],0,[],len(buses),buses,0,[],0,[])
        bus_voltage = psspy.abusreal(sid=0, flag=2, string=["PU"], busnum=buses)
        print("bus voltages ",bus_voltage)

        if fromnum<tonum:
            k = 1
        else:
            k = 2

        print('K is ',k)
        frombusvoltage=0
        tobusvoltage = 0
        if len(bus_voltage[1][0])==2 and k==1:
            frombusvoltage = bus_voltage[1][0][0]
            tobusvoltage = bus_voltage[1][0][1]
        if len(bus_voltage[1][0])==2 and k==2:
            frombusvoltage = bus_voltage[1][0][1]
            tobusvoltage = bus_voltage[1][0][0]
       
        
        print("this is frombusvoltage",fromnum, frombusvoltage)
        # print("this is tobusvoltage",tonum,  tobusvoltage)
        report("%(fromnum)6d,%(fromexname)18s,%(frombusvoltage)1.3F,%(tonum)6d,%(toexname)18s,%(tobusvoltage)1.3F,%(ckt)3s,%(status)3d,\
%(p)9.2F,%(q)9.2F,%(mva)9.2F,%(pcti)6.2F,%(ploss)8.2F,%(qloss)8.2F\n" %vars())
    # ------------------------------------------------------------------------------------------------
    if csvfile:
        csvfile_h.close()
        print('\n Done .... Power Flow Results Report saved to file %s' % csvfile)
    else:
        print('\n Done .... Power Flow Results Report created in Report window.')

# =====================================================================================================

def check_psse_example_folder(csvfile):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'
    rptpath, rptfnam = os.path.split(csvfile)
    if not rptpath:
        rptpath = os.getcwd()
        cwd = rptpath.lower()
        i = cwd.find('pti')
        j = cwd.find('psse')
        k = cwd.find('example')
        if i>0 and j>i and k>j:     # called from Example folder
            outdir = os.path.join(os.getcwd(), 'Output_Pyscript')
            if not os.path.exists(outdir): os.mkdir(outdir)
        else:
            outdir = os.getcwd()
        csvfile  = os.path.join(outdir, rptfnam)

    return csvfile

# =====================================================================================================

def run_brnflows_csv(savfile='CaseLF_lag_0.95hunp.sav', csvfile='brnflows_csv_savnw.csv'):

    csvfile  = check_psse_example_folder(csvfile)

    brnflows_csv(savfile, csvfile)

# ====================================================================================================
# ====================================================================================================
if __name__ == '__main__':

    import psse34
    run_brnflows_csv()

# ====================================================================================================
