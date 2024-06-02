#[ascc_report.py]    Get ASCC fault currents in arrays and create custom report
# =====================================================================================================
'''
This is an example file showing how to use "ascc_currents" function from pssarrays module.

ASCC_CURRENTS function returns ASCC short circuit currents for each faulted bus and
each type of fault applied. They are:
    ia1   = Positive Sequence Current
    ia2   = Negative Sequence Current
    ia0   = Zero Sequence Current
    ia    = Phase A current
    ib    = Phase B current
    ic    = Phase C current

The APIs used in this program are part of python "pssarrays" module.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse34

- call function
    run_ascc_report()

    You may want to change inputs specified in this function.
    run_ascc_report(savfile, fltbuses, rptfile)
    Defaults:
        savfile  = 'savnw.sav'
        fltbuses = [151,154]
        rptfile  = 'ascc_report_savnw.txt'
                   When this script is called from PSSE's Example Folder,
                   report is created in subfolder 'Output_Pyscript'
'''
psseversion = 34

if psseversion==35:

    binpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSBIN"
    libpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSLIB"
    pythonpath = r"C:\Program Files\PTI\PSSE35\35.3\PSSPY39"


if psseversion==34:
    
    binpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSBIN"
    libpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSLIB"
    pythonpath = r"C:\Program Files (x86)\PTI\PSSE34\PSSPY37"
import sys
import os
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
# =====================================================================================================

import os, time, math

# =====================================================================================================

def encode_complex_number_xbyr(cnum):
    r=cnum.real
    x=cnum.imag
    csign='+j'
    if x<0:
        csign='-j'
        x=abs(x)

    if r==0:
        rstr=''
        xbyr=''
    else:
        rstr="%9.6f" % r
        xbyr="%9.6f" % (x/r)

    if x==0:
        xstr=''
        csign=''
    else:
        xstr="%9.6f" % x

    cstr="%(rstr)s%(csign)s%(xstr)s, %(xbyr)s" % vars()

    return cstr

# =====================================================================================================

def get_cplx_mag(fmt, cmplxvalue):
    if fmt == 'rectangular':
        return abs(cmplxvalue)
    else:
        return cmplxvalue.real

# =====================================================================================================

def create_report(fltbuses,flt3ph,fltlg,fltllg,fltll,linout,linend,voltop,genxop,
                  tpunty,dcload,zcorec,lnchrg,shntop,loadop,machpq,volts,
                  savfile,relfile,fcdfile,scfile,rptfile,rprtyp,rprlvl):

    import psspy, arrbox.ascc

    # open case
    if savfile: psspy.case(savfile)

    # Save pre-fault voltages
    sid  = -1
    flag = 2
    ierr, (buslst,)           = psspy.abusint(sid,  flag, ['NUMBER'])
    ierr, (busvltlst_preflt,) = psspy.abuscplx(sid, flag, ['VOLTAGE'])
    ierr, (busvltlst_base,)   = psspy.abusreal(sid, flag, ['BASE'])
    busdata_dict = {}
    for n, vpf, vnm in zip(buslst, busvltlst_preflt, busvltlst_base):
        busdata_dict[n] = {'prefltv': vpf, 'basekv': vnm}

    # set sc units and format
    psspy.short_circuit_units(1)         # 0=PU, 1=Physical
    psspy.short_circuit_coordinates(1)   # 0=rectangular, 1=polar

    sid = 3
    if fltbuses:
        psspy.bsys(sid,0,[0.0,0.0],0,[],len(fltbuses),fltbuses,0,[],0,[])
        busall = 0
    else:
        busall = 1

    # call pssarrays routine
    rlst = arrbox.ascc.ascc_currents(sid, busall, flt3ph=flt3ph, fltlg=fltlg, fltllg=fltllg,
           fltll=fltll, linout=linout, linend=linend, voltop=voltop, genxop=genxop, tpunty=tpunty,
           dcload=dcload, zcorec= zcorec, lnchrg=lnchrg, shntop=shntop, loadop=loadop, machpq=machpq,
           volts=volts, relfile=relfile, fcdfile=fcdfile, scfile=scfile, rprtyp=rprtyp, rprlvl=rprlvl)

    if rlst.ierr!=0:
        raise Exception("arrbox.ascc.ascc_currents error= %d\n" % rlst.ierr)

    if rptfile:
        p, nx = os.path.split(rptfile)
        n, x = os.path.splitext(nx)
        if not x:
            x = '.txt'
            nx = n + x
        if p:
            rptfile = os.path.join(p, nx)
        else:
            rptfile = os.path.join(os.getcwd(), nx)
        rptfile_h = open(rptfile,'w')
        report    = rptfile_h.write
    else:
        psspy.beginreport()
        report = psspy.report

    nfbus=len(rlst.fltbus)

    ttlstr="PSS(R)E ASCC SHORT CIRCUIT CURRENTS" + 10*' ' + time.ctime()
    ln1str,ln2str=psspy.titldt()
    maxlen=max(len(ttlstr),len(ln1str),len(ln2str))
    report(ttlstr.center(maxlen))
    report("\n")
    report(ln1str.center(maxlen))
    report("\n")
    report(ln2str.center(maxlen))
    report("\n\n")

    sbase  = psspy.sysmva()

    scunit = rlst.scunit
    scfmt  = rlst.scfmt

    if scunit == 'pu':
        units = 'PU'
    else:
        units = 'AMP'
    unitstr   = units.center(10)
    clnhdr    = "   BUS     " + 6*unitstr + "\n"
    report("           <-SCMVA-> <--ia1--> <--ia2--> <--ia0--> <--ia---> <--ib---> <--ic--->\n")
    for i in range(nfbus):
       
        # report(clnhdr)
        fbus   = rlst.fltbus[i]
        basekv = busdata_dict[fbus]['basekv']
        baseamp = (1000.0 * sbase) / (math.sqrt(3.0) * basekv)

        if flt3ph:
            ttxt   = "%6d" % fbus
            spc    = '3PH'

            ia1    = get_cplx_mag(scfmt,rlst.flt3ph[i].ia1)
            ia2    = get_cplx_mag(scfmt,rlst.flt3ph[i].ia2)
            ia0    = get_cplx_mag(scfmt,rlst.flt3ph[i].ia0)
            ia     = get_cplx_mag(scfmt,rlst.flt3ph[i].ia)
            ib     = get_cplx_mag(scfmt,rlst.flt3ph[i].ib)
            ic     = get_cplx_mag(scfmt,rlst.flt3ph[i].ic)

            scmva  = math.sqrt(3.0) * basekv * rlst.flt3ph[i].ia1 / 1000.0
            if scunit == 'pu': scmva = scmva*baseamp
            scmva  = get_cplx_mag(scfmt,scmva)

            tmptxt = "%(ttxt)s %(spc)s %(scmva)9.2f %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f \n" % vars()
            report(tmptxt)

        if fltlg:
            if flt3ph:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            ttxt   = "%6d" % fbus
            spc    = ' LG'
            ia1    = get_cplx_mag(scfmt,rlst.fltlg[i].ia1)
            ia2    = get_cplx_mag(scfmt,rlst.fltlg[i].ia2)
            ia0    = get_cplx_mag(scfmt,3*rlst.fltlg[i].ia0)
            ia     = get_cplx_mag(scfmt,rlst.fltlg[i].ia)
            ib     = get_cplx_mag(scfmt,rlst.fltlg[i].ib)
            ic     = get_cplx_mag(scfmt,rlst.fltlg[i].ic)

            scmva  = math.sqrt(3.0) * basekv * 3 * rlst.fltlg[i].ia0 / 1000.0
            if scunit == 'pu': scmva = scmva*baseamp
            scmva  = get_cplx_mag(scfmt,scmva)

            tmptxt = "%(ttxt)s %(spc)s %(scmva)9.2f %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f \n" % vars()
            report(tmptxt)

        if fltllg:
            if flt3ph or fltlg:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            ttxt   = "%6d" % fbus
            spc    = 'LLG'
            ia1    = get_cplx_mag(scfmt,rlst.fltllg[i].ia1)
            ia2    = get_cplx_mag(scfmt,rlst.fltllg[i].ia2)
            ia0    = get_cplx_mag(scfmt,3*rlst.fltllg[i].ia0)
            ia     = get_cplx_mag(scfmt,rlst.fltllg[i].ia)
            ib     = get_cplx_mag(scfmt,rlst.fltllg[i].ib)
            ic     = get_cplx_mag(scfmt,rlst.fltllg[i].ic)

            scmva  = math.sqrt(3.0) * basekv * 3 * rlst.fltllg[i].ia0 / 1000.0
            if scunit == 'pu': scmva = scmva*baseamp
            scmva  = get_cplx_mag(scfmt,scmva)

            tmptxt = "%(ttxt)s %(spc)s %(scmva)9.2f %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f \n" % vars()
            report(tmptxt)

        if fltll:
            if flt3ph or fltlg or fltllg:
                ttxt = 6*' '
            else:
                ttxt = "%6d" % fbus
            ttxt   = "%6d" % fbus
            spc     = ' LL'
            ia1    = get_cplx_mag(scfmt,rlst.fltll[i].ia1)
            ia2    = get_cplx_mag(scfmt,rlst.fltll[i].ia2)
            ia0    = get_cplx_mag(scfmt,rlst.fltll[i].ia0)
            ia     = get_cplx_mag(scfmt,rlst.fltll[i].ia)
            ib     = get_cplx_mag(scfmt,rlst.fltll[i].ib)
            ic     = get_cplx_mag(scfmt,rlst.fltll[i].ic)

            scmva  = math.sqrt(3.0) * basekv * rlst.fltll[i].ib / 1000.0
            if scunit == 'pu': scmva = scmva*baseamp
            scmva  = get_cplx_mag(scfmt,scmva)

            tmptxt = "%(ttxt)s %(spc)s %(scmva)9.2f %(ia1)9.2f %(ia2)9.2f %(ia0)9.2f %(ia)9.2f %(ib)9.2f %(ic)9.2f \n" % vars()
            report(tmptxt)

        # report("\nTHEVENIN IMPEDANCE (pu), X/R\n")
        # z1str = encode_complex_number_xbyr(rlst.thevzpu[i].z1)
        # z1str ="Z1: " + z1str
        # if fltlg or fltllg or fltll:
        #     z2str = encode_complex_number_xbyr(rlst.thevzpu[i].z2)
        #     z2str ="Z2: " + z2str
        #     z0str = encode_complex_number_xbyr(rlst.thevzpu[i].z0)
        #     z0str ="Z0: " + z0str
        #     tmptxt="%(z1str)s    %(z2str)s    %(z0str)s\n" % vars()
        # else:
        #     tmptxt="%(z1str)s\n" % vars()
        # report(tmptxt)

        # if scunit != 'pu':
        #     report("\nTHEVENIN IMPEDANCE (ohms), X/R\n")
        #     z1str = encode_complex_number_xbyr(rlst.thevz[i].z1)
        #     z1str ="Z1: " + z1str
        #     if fltlg or fltllg or fltll:
        #         z2str = encode_complex_number_xbyr(rlst.thevz[i].z2)
        #         z2str ="Z2: " + z2str
        #         z0str = encode_complex_number_xbyr(rlst.thevz[i].z0)
        #         z0str ="Z0: " + z0str
        #         tmptxt="%(z1str)s    %(z2str)s    %(z0str)s\n" % vars()
        #     else:
        #         tmptxt="%(z1str)s\n" % vars()
        #     report(tmptxt)

        # tmptxt=110*'-'
        # report(tmptxt)
        # report("\n")

    # Maximum Fault Currents
    inam = ['ia1', 'ia2', 'ia0', 'ia', 'ib', 'ic']
    unitstr   = units.center(11)
    unitstr = ''
    for each in ['ia1', 'ia2', 'ia0', ' ia', ' ib', ' ic']:
        t = each+'('+units+')'
        t = ' ' + t.center(9) + ' '
        unitstr += t

    clnhdr    = "   BUS  " + unitstr + "  Description\n"
    report("\nBREAKER DUTY CURRENTS\n")
    report(clnhdr)
    for i in range(nfbus):
        fbus   = rlst.fltbus[i]
        ia1    = get_cplx_mag(scfmt,rlst.maxflt[i].ia1)
        ia2    = get_cplx_mag(scfmt,rlst.maxflt[i].ia2)
        ia0    = get_cplx_mag(scfmt,rlst.maxflt[i].ia0)
        ia     = get_cplx_mag(scfmt,rlst.maxflt[i].ia)
        ib     = get_cplx_mag(scfmt,rlst.maxflt[i].ib)
        ic     = get_cplx_mag(scfmt,rlst.maxflt[i].ic)
        dsc    = rlst.maxfltdsc[i]
        tmptxt = "%(fbus)6d   %(ia1)9.2f  %(ia2)9.2f  %(ia0)9.2f  %(ia)9.2f  %(ib)9.2f  %(ic)9.2f   %(dsc)s\n" % vars()
        report(tmptxt)

    # ------------------------------------------------------------------------------------------------
    if rptfile:
        rptfile_h.close()
        print('\n Done .... ASCC FAULT Report saved to file %s' % rptfile)
    else:
        print('\n Done .... ASCC FAULT Report created in Report window.')

# =====================================================================================================

def check_psse_example_folder(rptfile):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'
    rptpath, rptfnam = os.path.split(rptfile)
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
        rptfile  = os.path.join(outdir, rptfnam)

    return rptfile

# =====================================================================================================

def run_ascc_report(savfile="Reactive_Power_Requirement_WETC_20GF.sav", fltbuses=[], rptfile='ShortCircuit_WETC1_20GF.txt'):

    import psspy

    psspy.psseinit()

    # Inputs, change as required

    flt3ph  = 1       #
    fltlg   = 1       #
    fltllg  = 1       #
    fltll   = 1       #
    linout  = 0       #
    linend  = 0       #
    voltop  = 0       #
    genxop  = 0       #
    tpunty  = 0       #
    dcload  = 1       #
    zcorec  = 1       #
    lnchrg  = 1       #
    shntop  = 0       #
    loadop  = 0       #
    machpq  = 0       #

    volts   = 1.01     #

    rptfile = check_psse_example_folder(rptfile)

    relfile = ""
    fcdfile = ""
    scfile  = ""

    rprtyp  = -1      # no report
    rprlvl  = 0       # number of contribution levels

    create_report(fltbuses,flt3ph,fltlg,fltllg,fltll,linout,linend,voltop,genxop,
                  tpunty,dcload,zcorec,lnchrg,shntop,loadop,machpq,volts,
                  savfile,relfile,fcdfile,scfile,rptfile,rprtyp,rprlvl)

# ====================================================================================================
if __name__ == '__main__':

    import psse34
    run_ascc_report()

# ====================================================================================================

