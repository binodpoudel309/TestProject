import os,sys
psseversion = 35
#from tkinter import filedialog 
if psseversion==35:

    binpath = r"C:\Program Files\PTI\PSSE35\35.6\PSSBIN"
    libpath = r"C:\Program Files\PTI\PSSE35\35.6\PSSLIB"
    pythonpath = r"C:\Program Files\PTI\PSSE35\35.6\PSSPY311"


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

psspy.psseinit(50)


# psspy.case('BocanovaII_cha_lag.sav')
# psspy.case('BocanovaII_cha_lead.sav')
# psspy.case('BocanovaII_cha_unity.sav')
# psspy.case('BocanovaII_dis_lag.sav')
# psspy.case('BocanovaII_dis_lead.sav')
psspy.case('BocanovaII_dis_unity.sav')

# base = 'cha_lag'
# base = 'cha_lead'
# base = 'cha_unity'
# base = 'dis_lag'
# base = 'dis_lead'
# base = 'dis_unity'
# outfile_base = "LVRT_Pref_"+ base
# outfile_base = "LVRT_Legacy_"+base
savfilnam, snpfilnam = psspy.sfiles()
case_base = os.path.splitext(os.path.basename(savfilnam))[0]
base = "_".join(case_base.split("_")[-2:])

outfile_base = f"HVRT_Legacy_{base}"

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

psspy.fdns([1,0,1,1,1,0,0,0])
psspy.save(os.getcwd()+r"\testsavedcase.sav")

psspy.cong()
psspy.conl(1,1,1,[0,0],[100,0,0,100])
psspy.conl(1,1,2,[0,0],[100,0,0,100])
psspy.conl(1,1,3,[0,0],[100,0,0,100])


# Solve for dynamics initialization (ordering, factoring, switching to Y-bus)
psspy.ordr(0)
psspy.fact()
psspy.tysl(0)
psspy.save(os.getcwd()+r"\converted_case.sav")
# Save converted case (optional)
# psspy.save(case_root + "_C.sav") 


psspy.progress_output(2,'logs.txt',[0,0])
psspy.prompt_output(2,'logs.txt',[0,0])
psspy.report_output(2,'logs.txt',[0,0])
psspy.alert_output(4,'logs.txt',[0,0])


# 3. Add dynamics data
DYRFILE = os.getcwd()+r"\bocanova2.dyr" # Example dyr file
psspy.dyre_new(dyrefile=DYRFILE)

sid = 0

# 4. Set up channels for output
# Add bus voltage channel (example for bus 3001)
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,1,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,2,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,3,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,4,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,7,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,12,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,25,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,26,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,14,0]) 
psspy.chsb(sid=0, all=1, status=[-1,-1,-1,1,16,0]) 

# Save snapshot
psspy.snap([-1,-1,-1,-1,-1],os.getcwd()+r"\snapshot_case.snp") 

psspy.case("converted_case.sav")
psspy.rstr("snapshot_case.snp")
# 5. Run the simulation

def get_unique_filename(base_name,extension):
    counter = 0
    
    new_filename = f"{base_name}{extension}"
    print("Here")
    while os.path.isfile(new_filename):
        counter +=1 
        new_filename = f"{base_name}_{counter}{extension}"
        print(f"File already exists. Trying: {new_filename}")
    return new_filename
file_extension = ".out"   
outfilename = get_unique_filename(outfile_base,file_extension)
print(outfilename)
psspy.strt_2([0,0],outfile=outfilename) # Initialize simulation with output file

# Run flat for a few seconds (e.g., 1 second)
# psspy.run(0, 1.0, 1, 1, 1) 
psspy.run(0,20,0,0,0)
psspy.pssehalt_2()
