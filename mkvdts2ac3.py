#!/usr/bin/env python

import sys
import os
import subprocess
import time
import glob

starttime = time.time()

fileordir  = sys.argv[1]
#~ nzbname   = sys.argv[2]
#~ cleanname = sys.argv[3]
#~ reportnum = int(sys.argv[4])
#~ category  = sys.argv[5]
#~ group     = sys.argv[6]
#~ status    = int(sys.argv[7])

# SABnzbd argv: 
# 1  The final directory of the job (full path) 
# 2  The original name of the NZB file 
# 3  Clean version of the job name (no path info and ".nzb" removed) 
# 4  Indexer's report number (if supported) 
# 5  User-defined category 
# 6  Group that the NZB was posted in e.g. alt.binaries.x 
# 7  Status of post processing. 0 = OK, 1=failed verification, 2=failed unpack, 3=1+2

newdir = "C:\Users\Thomson\Downloads\sab\complete\movies"
newdir = os.path.join(newdir, os.path.basename(os.path.normpath(fileordir)))

#~ set up temp dir
from os.path import expanduser
home = expanduser("~")
tempdir = os.path.join(home, 'temp')
tempdir = os.path.join(tempdir, 'mkvdts2ac3')
if not os.path.exists(tempdir):
    os.makedirs(tempdir)

mkvfiles = []
    
#~ find mkvfile in dir (cuz sabnzbd gives us the entire directory)
if os.path.isdir(fileordir):
    dirList=os.listdir(fileordir)
    mkvsize=0
    for fname in dirList:
        if fname.endswith('.mkv'):
            fnamesize = os.path.getsize(os.path.join(fileordir, fname))
            if fnamesize > mkvsize:
                mkvsize = fnamesize
                mkvfiles.append(fname)
else:
    for f in glob.glob(fileordir):
        if not os.path.isdir(f):
            if f.endswith('.mkv'):
                mkvfiles.append(f)
    

if not mkvfiles:
    print "No MKV files found"
else:
    for mkvfilename in mkvfiles:
        name = os.path.splitext(mkvfilename)[0]
        mkvfile = os.path.join(fileordir, mkvfilename)
        dtsfile = os.path.join(tempdir, name + '.dts')
        ac3file = os.path.join(tempdir, name + '.ac3')
        tcfile = os.path.join(tempdir, name + '.tc')
        newmkvfile = os.path.join(tempdir, name + '.mkv')
        
        #~ get dts track id and video track id
        stuff = subprocess.check_output(["mkvmerge", "-i", mkvfile])
        lines = stuff.split("\n")
        dtstrackid = False
        videotrackid = False
        alreadygotac3 = False
        for line in lines:
            if ': audio (A_DTS)' in line:
                linelist = line.split(' ')
                dtstrackid = linelist[2]
                linelist = dtstrackid.split(':')
                dtstrackid = linelist[0]
            elif 'video (V_' in line:
                linelist = line.split(' ')
                videotrackid = linelist[2]
                linelist = videotrackid.split(':')
                videotrackid = linelist[0]
            elif ': audio (A_AC3)' in line:
                alreadygotac3 = True
        
        if not dtstrackid:
            print "No DTS track found"
        elif alreadygotac3:
            print "Already has AC3 track"
        else:
            
            #~ extract timecodes
            print "Extracting Timecodes..."
            subprocess.call(["mkvextract", "timecodes_v2", mkvfile, dtstrackid + ':' + tcfile])
        
            delay = False
            fp = open(tcfile)
            for i, line in enumerate(fp):
                if i == 1:
                    delay = line
                    break
            fp.close()
            
            #~ extract dts track
            print "Extracting DTS track..."
            subprocess.call(["mkvextract", "tracks", mkvfile, dtstrackid + ':' + dtsfile])
            
            #~ convert DTS to AC3
            print "Converting DTS to AC3..."
            subprocess.call(["ffmpeg", "-y", "-i", dtsfile, "-acodec", "ac3", "-ac", "6", "-ab", "448k", ac3file])
        
            #~ remux
            print "Remuxing AC3 into MKV..."
            remux = ["mkvmerge"]
            remux.append("-o")
            remux.append(newmkvfile)
            remux.append("--compression")
            remux.append(videotrackid + ":none")
            remux.append(mkvfile)
            if delay:
                remux.append("--sync")
                remux.append("0:" + delay)
            remux.append("--compression")
            remux.append("0:none")
            remux.append(ac3file)
            
            subprocess.call(remux)
        
            #~ replace old mkv with new mkv
            os.remove(mkvfile)
            os.rename(newmkvfile, mkvfile)
            
            #~ clean up temp folder
            os.remove(dtsfile)
            os.remove(ac3file)
            os.remove(tcfile)
            os.rmdir(tempdir)
        
            #~ print out time taken
            elapsed = (time.time() - starttime)
            minutes = int(elapsed / 60)
            seconds = int(elapsed) % 60
            print "Total Time: " + str(minutes) + " minutes " + str(seconds) + " seconds"

#~ move all files in original dir to the dir couch potato looks for
if os.path.isdir(fileordir):
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    for filename in os.listdir(fileordir):
        os.rename(os.path.join(fileordir, filename), os.path.join(newdir, filename))
    os.rmdir(fileordir)
