#!/usr/bin/env python

#Copyright (C) 2012  Drew Thomson
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import subprocess
import time
import glob
import re
import tempfile
import sys
import ConfigParser
import shutil

version = "1.0"

# check if from sabnzbdplus
sab = False
if len(sys.argv) == 8:
    nzbgroup = sys.argv[6]
    ppstatus = sys.argv[7]
    if int(ppstatus) >= 0 and int(ppstatus) <= 3 and "." in nzbgroup:
        sab = True

parser = argparse.ArgumentParser(description='convert matroska (.mkv) video files audio portion from dts to ac3')

config = ConfigParser.SafeConfigParser()
configFilename = os.path.join(os.path.dirname(sys.argv[0]), "mkvdts2ac3.cfg")

if not os.path.isfile(configFilename):
    print "ERROR: You need a mkvdts2ac3.cfg file - did you rename and edit the .sample?"
    sys.exit(-1)

config.read(configFilename)
defaults = dict(config.items("mkvdts2ac3"))
for key in defaults:
    if key == "version":
        defaults[version] = int(defaults[version])

parser.set_defaults(**defaults)
parser.add_argument('fileordir', metavar='ForD', nargs='+', help='a file or directory (wildcards may be used)')

parser.add_argument("-c", "--custom", metavar="TITLE", help="Custom AC3 track title")
parser.add_argument("-d", "--default", help="Mark AC3 track as default", action="store_true")
parser.add_argument("--destdir", metavar="DIRECTORY", help="Destination Directory")
parser.add_argument("-e", "--external", action="store_true",
                    help="Leave AC3 track out of file. Does not modify the original matroska file. This overrides '-n' and '-d' arguments")
parser.add_argument("-f", "--force", help="Force processing when AC3 track is detected", action="store_true")
parser.add_argument("-i", "--initial", help="New AC3 track will be first in the file", action="store_true")
parser.add_argument("-k", "--keepdts", help="Keep external DTS track (implies '-n')", action="store_true")
parser.add_argument("--moveonlyifsab", help="Only move to destination directory --destdir if called from sabnzbd", action="store_true")
parser.add_argument("-n", "--nodts", help="Do not retain the DTS track", action="store_true")
parser.add_argument("--new", help="Do not copy over original. Create new adjacent file", action="store_true")
parser.add_argument("-r", "--recursive", help="Recursively descend into directories", action="store_true")
parser.add_argument("-s", "--compress", metavar="MODE", help="Apply header compression to streams (See mkvmerge's --compression)")
parser.add_argument("-t", "--track", metavar="TRACKID", help="Specify alternate DTS track. If it is not a DTS track it will default to the first DTS track found")
parser.add_argument("-w", "--wd", metavar="FOLDER", help="Specify alternate temporary working directory")
parser.add_argument("-v", "--verbose", help="Turn on verbose output", action="count")
parser.add_argument("-V", "--version", help="Print script version information", action='version', version='%(prog)s ' + version + ' by Drew Thomson')
parser.add_argument("--test", help="Print commands only, execute nothing", action="store_true")
parser.add_argument("--debug", help="Print commands and pause before executing each", action="store_true")

args = parser.parse_args()

if sab:
    args.fileordir = [args.fileordir[0]]

def doprint(mystr):
    if args.test or args.debug or args.verbose:
        sys.stdout.write(mystr)
    
def runcommand(cmdlist):
    if args.test or args.debug or args.verbose >= 1:
        cmdstr = ''
        for e in cmdlist:
            cmdstr += e + ' '
        print "\n" + cmdstr.rstrip()
    if args.debug:
        raw_input("Press Enter to continue...")
    if not args.test:
        if args.verbose >= 2:
            subprocess.call(cmdlist)
        else:
            subprocess.call(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def process(ford):
    if os.path.isdir(ford):
        if args.recursive:
            for f in os.listdir(ford):
                process(os.path.join(ford, f))
    else:
        # check if file is an mkv file
        child = subprocess.Popen(["mkvmerge", "-i", ford], stdout=subprocess.PIPE)
        child.communicate()[0]
        if child.returncode == 0:
            starttime = time.time()
            
            # set up temp dir
            tempdir = False
            if args.wd:
                tempdir = args.wd
                if not os.path.exists(tempdir):
                    os.makedirs(tempdir)
            else:
                tempdir = tempfile.gettempdir()
                tempdir = os.path.join(tempdir, "mkvdts2ac3")
                
            (dirName, fileName) = os.path.split(ford)
            fileBaseName = os.path.splitext(fileName)[0]
            
            doprint("filename: " + fileName + "\n")
            
            dtsfile = fileBaseName + '.dts'
            tempdtsfile = os.path.join(tempdir, dtsfile)
            ac3file = fileBaseName + '.ac3'
            tempac3file = os.path.join(tempdir, ac3file)
            tcfile = fileBaseName + '.tc'
            temptcfile = os.path.join(tempdir, tcfile)
            newmkvfile = fileBaseName + '.mkv'
            tempnewmkvfile = os.path.join(tempdir, newmkvfile)
            adjacentmkvfile = os.path.join(dirName, fileBaseName + '.new.mkv')
            fname = fileName
            
            # get dts track id and video track id
            output = subprocess.check_output(["mkvmerge", "-i", ford])
            lines = output.split("\n")
            altdtstrackid = False
            dtstrackid = False
            videotrackid = False
            alreadygotac3 = False
            audiotracks = []
            for line in lines:
                linelist = line.split(' ')
                trackid = False
                if len(linelist) > 2:
                    trackid = linelist[2]
                    linelist = trackid.split(':')
                    trackid = linelist[0]
                if 'audio (A_' in line:
                    audiotracks.append(trackid)
                if ': audio (A_DTS)' in line:
                    dtstrackid = trackid
                elif 'video (V_' in line:
                    videotrackid = trackid
                elif ': audio (A_AC3)' in line:
                    alreadygotac3 = True
                elif args.track:
                    if "Track ID " + args.track + ": audio (A_DTS)" in line:
                        altdtstrackid = args.track
            if altdtstrackid:
                dtstrackid = altdtstrackid
            
            if not dtstrackid:
                doprint("  No DTS track found\n")
            elif alreadygotac3 and not args.force:
                doprint("  Already has AC3 track\n")
            else:
                # get dtstrack info
                output = subprocess.check_output(["mkvinfo", ford])
                lines = output.split("\n")
                dtstrackinfo = []
                startcount = 0
                for line in lines:
                    match = re.search(r'^\|( *)\+', line)
                    linespaces = startcount
                    if match:
                        linespaces = len(match.group(1))
                    if startcount == 0:
                        if "track ID for mkvmerge & mkvextract:" in line:
                            if "track ID for mkvmerge & mkvextract: " + dtstrackid in line:
                                startcount = linespaces
                        elif "+ Track number: " + dtstrackid in line:
                            startcount = linespaces
                    if linespaces < startcount:
                        break
                    if startcount != 0:
                        dtstrackinfo.append(line)
                
                # get dts language
                dtslang = "eng"
                for line in dtstrackinfo:
                    if "Language" in line:
                        dtslang = line.split()[-1]
                
                # get dts name
                dtsname = False
                if args.custom:
                    dtsname = args.custom
                else:
                    for line in dtstrackinfo:
                        if "+ Name: " in line:
                            dtsname = line.split("+ Name: ")[-1]
                            dtsname = dtsname.replace("DTS", "AC3")
                            dtsname = dtsname.replace("dts", "ac3")
                
                # extract timecodes
                tctime = time.time()
                doprint("  Extracting Timecodes...")
                tccmd = ["mkvextract", "timecodes_v2", ford, dtstrackid + ":" + temptcfile]
                runcommand(tccmd)
                elapsed = (time.time() - tctime)
                minutes = int(elapsed / 60)
                seconds = int(elapsed) % 60
                doprint(str(minutes) + "min " + str(seconds) + " sec\n")
                
                delay = False
                if not args.test:
                    # get the delay if there is any
                    fp = open(temptcfile)
                    for i, line in enumerate(fp):
                        if i == 1:
                            delay = line
                            break
                    fp.close()
                
                # extract dts track
                extracttime = time.time()
                doprint("  Extracting DTS track...")
                extractcmd = ["mkvextract", "tracks", ford, dtstrackid + ':' + tempdtsfile]
                runcommand(extractcmd)
                elapsed = (time.time() - extracttime)
                minutes = int(elapsed / 60)
                seconds = int(elapsed) % 60
                doprint(str(minutes) + "min " + str(seconds) + " sec\n")
                
                # convert DTS to AC3
                converttime = time.time()
                doprint("  Converting DTS to AC3...")
                convertcmd = ["ffmpeg", "-y", "-i", tempdtsfile, "-acodec", "ac3", "-ac", "6", "-ab", "448k", tempac3file]
                runcommand(convertcmd)
                elapsed = (time.time() - converttime)
                minutes = int(elapsed / 60)
                seconds = int(elapsed) % 60
                doprint(str(minutes) + "min " + str(seconds) + " sec\n")
                if args.external:
                    if not args.test:
                        os.rename(ac3file, os.path.join(dirName, fileBaseName + '.ac3'))
                        fname = ac3file
                else:
                    # remux
                    remuxtime = time.time()
                    doprint("  Remuxing AC3 into MKV...")
                    # Start to "build" command
                    remux = ["mkvmerge"]
                    
                    # Puts the AC3 track as the second in the file if indicated as initial
                    if args.initial:
                        remux.append("--track-order")
                        remux.append("0:1,1:0")
                        
                    # Declare output file
                    remux.append("-o")
                    remux.append(tempnewmkvfile)
                    
                    # If user doesn't want the original DTS track drop it
                    comp = "none"
                    if args.nodts or args.keepdts:
                        if len(audiotracks) == 1:
                            remux.append("-A")
                        else:
                            audiotracks = [audiotrack for audiotrack in audiotracks if audiotrack != dtstrackid]
                            remux.append("-a")
                            remux.append(",".join(audiotracks))
                            if args.compress:
                                comp = args.compress
                            for tid in audiotracks:
                                remux.append("--compression")
                                remux.append(tid + ":" + comp)
                    
                    # Add original MKV file, set header compression scheme         
                    remux.append("--compression")
                    remux.append(videotrackid + ":" + comp)
                    remux.append(ford)
                            
                    # If user wants new AC3 as default then add appropriate arguments to command
                    if args.default:
                        remux.append("--default-track")
                        remux.append("0")
                    
                    # Set the language
                    remux.append("--language")
                    remux.append("0:" + dtslang)
                    
                    # If the name was set for the original DTS track set it for the AC3
                    if dtsname:
                        remux.append("--track-name")
                        remux.append("0:\"" + dtsname.rstrip() + "\"")
                    
                    # set delay if there is any
                    if delay:
                        remux.append("--sync")
                        remux.append("0:" + delay.rstrip())
                        
                    # Set track compression scheme and append new AC3
                    remux.append("--compression")
                    remux.append("0:" + comp)
                    remux.append(tempac3file)
                    
                    runcommand(remux)
                    
                    elapsed = (time.time() - remuxtime)
                    minutes = int(elapsed / 60)
                    seconds = int(elapsed) % 60
                    doprint(str(minutes) + "min " + str(seconds) + " sec\n")  

                    if not args.test:
                        #~ replace old mkv with new mkv
                        if args.new:
                            os.rename(tempnewmkvfile, adjacentmkvfile)
                        else:
                            os.remove(ford)
                            os.rename(tempnewmkvfile, ford)

                if not args.test:
                    #~ clean up temp folder
                    if args.keepdts and not args.external:
                        os.rename(tempdtsfile, os.path.join(dirName, fileBaseName + ".dts"))
                        fname = dtsfile
                    else:
                        os.remove(tempdtsfile)
                    if not args.external:
                        os.remove(tempac3file)
                    os.remove(temptcfile)
                    os.rmdir(tempdir)

                #~ print out time taken
                elapsed = (time.time() - starttime)
                minutes = int(elapsed / 60)
                seconds = int(elapsed) % 60
                doprint("  " + fileName + " finished in: " + str(minutes) + " minutes " + str(seconds) + " seconds\n")

                return fname

totalstime = time.time()
for a in args.fileordir:
    for ford in glob.glob(a):
        fname = False
        if os.path.isdir(ford):
            for f in os.listdir(ford):
                process(os.path.join(ford, f))
        else:
            fname = process(ford)
        if args.destdir:
            if not args.moveonlyifsab or (args.moveonlyifsab and sab):
                if fname:
                    (dirName, fileName) = os.path.split(ford)
                    os.rename(os.path.join(dirName, fname), os.path.join(args.destdir, fname))
                else:
                    shutil.move(os.path.abspath(ford), os.path.join(args.destdir, os.path.basename(os.path.normpath(ford))))
            
totaltime = (time.time() - totalstime)
minutes = int(totaltime / 60)
seconds = int(totaltime) % 60
doprint("Total Time: " + str(minutes) + " minutes " + str(seconds) + " seconds")