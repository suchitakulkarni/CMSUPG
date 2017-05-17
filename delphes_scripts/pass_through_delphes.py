# Run the decayed lhe files thorugh delphes
# script can take any delphes installation path
# input directory contained decayed pythia files (FILES SHOULD NOT BE HADRONISED)
# IMPORTANT FOR DELPHES INSTLATION
# The delphes installation should be done at the same level where your eos is installaed
# for me the folders look like
# eos/	delphes/   cms_exercises/

 
import os, glob, sys
import commands, shutil
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--dir", dest="decayed_dir", default="./",
                      help="location of decayed LHE files")

parser.add_option("-n", "--nevents", dest="nevents", default=10,
                      help="number of events to decay")

parser.add_option("-s", "--delphesdir", dest="delphesdir", 
		     default="/afs/cern.ch/user/s/sukulkar/delphes/",
		     help="location where delphes is installed")

parser.add_option("-o", "--outdir", dest="outdir",
                     default="./",
                     help="location where outputs including the delphised root, python cmnd and log files are stored")

parser.add_option("-i", "--tempdir", dest="tempdir",
                     default="./",
                     help="location where outputs will be temperorily stored, I envisage this to be your /tmp directory")

parser.add_option("-t", "--testmode", dest="testmode",
                     default="n",
                     help="run in testmode, only one lhe file will be passed through delphes in this case, input y or n")
(options, args) = parser.parse_args()

print "your delphes is installed at ", options.delphesdir
print "Location of your decayed LHE file is", options.decayed_dir
# select all the files you want to decay
# These files need to have the proper SLHA block in the header 
# It is also assumed that the string "undecayed" is part of the name
files_to_run = glob.glob(options.decayed_dir+"*.lhe")
print "total number of files to process are ", len(files_to_run)

# make some directories to keep things organized
if not os.path.isdir(options.outdir):
    os.mkdir(options.outdir)

if not os.path.isdir(options.outdir+"/substructure_cfgs"):
    os.mkdir(options.outdir+"/substructure_cfgs")

if not os.path.isdir(options.outdir+"/substructure_logs"):
    os.mkdir(options.outdir+"/substructure_logs")

if not os.path.isdir(options.outdir+"/delphised_substructure_0PU"):
    os.mkdir(options.outdir+"/delphised_substructure_0PU")

if not os.path.isdir(options.outdir+"/delphised_substructure_200PU"):
    os.mkdir(options.outdir+"/delphised_substructure_200PU")

if not os.path.isdir(options.tempdir):
    os.mkdir(options.tempdir)

if not os.path.isdir(options.tempdir+"/delphised_substructure_0PU"):
    os.mkdir(options.tempdir+"/delphised_substructure_0PU")

if not os.path.isdir(options.tempdir+"/delphised_substructure_200PU"):
    os.mkdir(options.tempdir+"/delphised_substructure_200PU")

pythia_template = "pythia_cmnd.template"

templatelines = open(pythia_template,'r').read().split('\n')

currentdir = os.getcwd()

def run_delphes(outfilename = "test.root", cmndfile_name = "test.txt", PU = 200):
    currentdir = os.getcwd()
    #change to delphes installation directory
    os.chdir(options.delphesdir)
    if PU == 0:
        out = commands.getoutput("./DelphesPythia8 cards/CMS_PhaseII/CMS_PhaseII_Substructure_PIX4022_0PU.tcl %s  %s" %(cmndfile_name, outfilename))
	os.chdir(currentdir)
        #create log files containing delphes log
        logfile = open(options.outdir+"/substructure_logs/"+outfilename.split('/')[-1].replace("root","_0PU.txt"),'w')
	print out
        print >> logfile, out
        logfile.close()

    if PU == 200:
        out = commands.getoutput("./DelphesPythia8 cards/CMS_PhaseII/CMS_PhaseII_Substructure_PIX4022_200PU.tcl %s  %s" %(cmndfile_name, outfilename))
        #create log files containing delphes log
        logfile = open(options.outdir+"/substructure_logs/"+outfilename.split('/')[-1].replace("root","_200PU.txt"),'w')
	os.chdir(currentdir)
	print out
        print >> logfile, out
        logfile.close()
    return

def create_cmnd(cmndfile_name = "test.txt"):

    currentdir = os.getcwd()
    os.chdir(currentdir)

    #create the pythia cmnd file
    if os.path.exists(cmndfile_name): os.remove(cmndfile_name)

    new_cmndfile = open(cmndfile_name, 'w')
    for line in templatelines:
        if "Beams:LHEF = filepath" in line:
            line = "Beams:LHEF = "+ file
        if "Main:numberOfEvents = NEVTS         ! number of events to generate" in line:
            line = "Main:numberOfEvents = %s         ! number of events to generate"%(str(options.nevents))
        print >> new_cmndfile, line
    new_cmndfile.close()

for file in files_to_run:

    # Delphes root file name for 0PU sample
    delphesfile_name = options.tempdir+"/delphised_substructure_0PU/"+file.split('/')[-1].replace("lhe","root")
    print "checking for file  ", options.outdir+"/delphised_substructure_0PU/"+file.split('/')[-1].replace("lhe","root")
    if os.path.exists(options.outdir+"/delphised_substructure_0PU/"+file.split('/')[-1].replace("lhe","root")): 
       print "file exists, will skip"
    else:
       cmndfile_name = options.outdir+"/substructure_cfgs/"+file.split('/')[-1].replace("lhe","cmnd")
       create_cmnd(cmndfile_name = cmndfile_name)
       run_delphes(outfilename = delphesfile_name,cmndfile_name = cmndfile_name, PU = 0)
       shutil.move(delphesfile_name, options.outdir+"/delphised_substructure_0PU/"+file.split('/')[-1].replace("lhe","root"))

    # Delphes root file name for 200PU sample
    delphesfile_200PU_name = options.tempdir+"/delphised_substructure_200PU/"+file.split('/')[-1].replace("lhe","root")
    print "checking for file  ", options.outdir+"/delphised_substructure_200PU/"+file.split('/')[-1].replace("lhe","root")
    # if the root file is already created skip it, BE CAREFUL currupt root files are not checked for
    if os.path.exists(options.outdir+"/delphised_substructure_200PU/"+file.split('/')[-1].replace("lhe","root")): 
        print "file exists, will skip"
        continue
    else:
       cmndfile_name = options.outdir+"/substructure_cfgs/"+file.split('/')[-1].replace("lhe","cmnd")
       create_cmnd(cmndfile_name = cmndfile_name)
       run_delphes(outfilename = delphesfile_200PU_name,cmndfile_name = cmndfile_name, PU = 200)
       shutil.move(delphesfile_200PU_name, options.outdir+"/delphised_substructure_200PU/"+file.split('/')[-1].replace("lhe","root"))
    #sys.exit()
    os.chdir(currentdir)   
    if options.outdir == "y": sys.exit()
