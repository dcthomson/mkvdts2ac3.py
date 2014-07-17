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

##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# mkvdts2ac3.py is a python script for linux, windows or os x which can be used
# for converting the DTS in Matroska (MKV) files to AC3. It provides you with a
# set of options for controlling the resulting file.

##############################################################################
### OPTIONS                                                                ###

## These options take an argument.

# NZBGet destination directory
#destdir=

# Apply header compression to streams (See mkvmerge's --compression)
#compress=

# Custom AC3 track title
#custom=

# Mark AC3 track as default (True, False).
#default=False

# Leave AC3 track out of file. Does not modify the original matroska file. This overrides '-n' and '-d' arguments (True, False).
#external=False

# Path of ffmpeg (if not in path)
#ffmpegpath=

# Force processing when AC3 track is detected (True, False).
#force=False

# New AC3 track will be first in the file (True, False).
#initial=False

# Keep external DTS track (implies '-n') (True, False).
#keepdts=False

# check md5 of files before removing the original if destination directory is on a different device than the original file (True, False).
#mdfive=False

# Path of mkvextract, mkvinfo and mkvmerge (if not in path)
#mkvtoolnixpath=

# Do not copy over original. Create new adjacent file (True, False).
#new=False

# Do not retain the DTS track (True, False).
#nodts=False

# Remove subtitles (True, False).
#no_subtitles=False

# Overwrite file if already there (True, False).
#overwrite=False

# Make ac3 track stereo instead of 6 channel (True, False).
#stereo=False

# Specify alternate DTS track. If it is not a DTS track it will default to the first DTS track found
#track=

# Specify alternate temporary working directory
#wd=

# Create output in mp4 format (True, False).
#mpfour=False

# Also add aac track (True, False).
#aac=False

# Custom AAC track title
#aaccustom=

# Make aac track stereo instead of 6 channel (True, False).
#aacstereo=False

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

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
import hashlib
import textwrap
import errno

version = "1.1"

sab = False
nzbget = False

# create parser
parser = argparse.ArgumentParser(description='convert matroska (.mkv) video files audio portion from dts to ac3')

# Check if called from NZBGet
if os.environ.has_key('NZBOP_SCRIPTDIR') and not os.environ['NZBOP_VERSION'][0:5] < '11.0':
    #Logger.info("MAIN: Script triggered from NZBGet (11.0 or later).")

    nzbget = True
    # NZBGet argv: all passed as environment variables.
    # Exit codes used by NZBGet
    POSTPROCESS_PARCHECK=92
    POSTPROCESS_SUCCESS=93
    POSTPROCESS_ERROR=94
    POSTPROCESS_NONE=95

    # Check nzbget.conf options
    status = 0

    if os.environ['NZBOP_UNPACK'] != 'yes':
        #Logger.error("Please enable option \"Unpack\" in nzbget configuration file, exiting")
        sys.exit(POSTPROCESS_ERROR)

    # Check par status
    if os.environ['NZBPP_PARSTATUS'] == '3':
        #Logger.warning("Par-check successful, but Par-repair disabled, exiting")
        sys.exit(POSTPROCESS_NONE)

    if os.environ['NZBPP_PARSTATUS'] == '1':
        #Logger.warning("Par-check failed, setting status \"failed\"")
        status = 1

    # Check unpack status
    if os.environ['NZBPP_UNPACKSTATUS'] == '1':
        #Logger.warning("Unpack failed, setting status \"failed\"")
        status = 1

    if os.environ['NZBPP_UNPACKSTATUS'] == '0' and os.environ['NZBPP_PARSTATUS'] != '2':
        # Unpack is disabled or was skipped due to nzb-file properties or due to errors during par-check

        for dirpath, dirnames, filenames in os.walk(os.environ['NZBPP_DIRECTORY']):
            for file in filenames:
                fileExtension = os.path.splitext(file)[1]

                if fileExtension in ['.rar', '.7z'] or os.path.splitext(fileExtension)[1] in ['.rar', '.7z']:
                    #Logger.warning("Post-Process: Archive files exist but unpack skipped, setting status \"failed\"")
                    status = 1
                    break

                if fileExtension in ['.par2']:
                    #Logger.warning("Post-Process: Unpack skipped and par-check skipped (although par2-files exist), setting status \"failed\"g")
                    status = 1
                    break

        if os.path.isfile(os.path.join(os.environ['NZBPP_DIRECTORY'], "_brokenlog.txt")) and not status == 1:
            #Logger.warning("Post-Process: _brokenlog.txt exists, download is probably damaged, exiting")
            status = 1

        #if not status == 1:
            #Logger.info("Neither archive- nor par2-files found, _brokenlog.txt doesn't exist, considering download successful")

    # Check if destination directory exists (important for reprocessing of history items)
    if not os.path.isdir(os.environ['NZBPP_DIRECTORY']):
        #Logger.error("Post-Process: Nothing to post-process: destination directory %s doesn't exist", os.environ['NZBPP_DIRECTORY'])
        status = 1

    args = parser.parse_args()
    
    args.fileordir = [os.environ['NZBPP_DIRECTORY']]
    
    if not 'NZBPO_AAC' in os.environ:
        raise Exception("mkvdts2ac3.py settings not saved")
        sys.exit(POSTPROCESS_ERROR)
    
    if os.environ['NZBPO_AAC'] == 'False':
        args.aac = False
    else:
        args.aac = True

    if os.environ['NZBPO_AACSTEREO'] == 'False':
        args.aacstereo = False
    else:
        args.aacstereo = True

    args.aaccustom = os.environ['NZBPO_AACCUSTOM']
    
    args.compress = os.environ['NZBPO_COMPRESS']
    
    args.custom = os.environ['NZBPO_CUSTOM']
    
    if os.environ['NZBPO_DEFAULT'] == 'False':
        args.default = False
    else:
        args.default = True 
    
    args.destdir = os.environ['NZBPO_DESTDIR']
    
    if os.environ['NZBPO_EXTERNAL'] == 'False':
        args.external = False
    else:
        args.external = True
    
    args.ffmpegpath = os.environ['NZBPO_FFMPEGPATH']
    
    if os.environ['NZBPO_FORCE'] == 'False':
        args.force = False
    else:
        args.force = True
    
    if os.environ['NZBPO_INITIAL'] == 'False':
        args.initial = False
    else:
        args.initial = True
        
    if os.environ['NZBPO_KEEPDTS'] == 'False':
        args.keepdts = False
    else:
        args.keepdts = True

    if os.environ['NZBPO_MDFIVE'] == 'False':
        args.md5 = False
    else:
        args.md5 = True
        
    args.mkvtoolnixpath = os.environ['NZBPO_MKVTOOLNIXPATH']
    
    if os.environ['NZBPO_NEW'] == 'False':
        args.new = False
    else:
        args.new = True

    if os.environ['NZBPO_NODTS'] == 'False':
        args.nodts = False
    else:
        args.nodts = True

    if os.environ['NZBPO_NO_SUBTITLES'] == 'False':
        args.no_subtitles = False
    else:
        args.no_subtitles = True

    if os.environ['NZBPO_OVERWRITE'] == 'False':
        args.overwrite = False
    else:
        args.overwrite = True

    args.sabdestdir = 'sab'
    
    if os.environ['NZBPO_STEREO'] == 'False':
        args.stereo = False
    else:
        args.stereo = True

    args.track = os.environ['NZBPO_TRACK']
    
    args.wd = os.environ['NZBPO_WD']
    
    if os.environ['NZBPO_MPFOUR'] == 'False':
        args.mp4 = False
    else:
        args.mp4 = True

    args.verbose = 3
    args.recursive = False
    args.test = False
    args.debug = False

# NZBGet config done

else:
    # Check if called form sabnzbd
    if len(sys.argv) == 8:
        nzbgroup = sys.argv[6]
        ppstatus = sys.argv[7]
        if ppstatus.isdigit():
            if int(ppstatus) >= 0 and int(ppstatus) <= 3 and "." in nzbgroup:
                sab = True

    # set config file arguments
    configFilename = os.path.join(os.path.dirname(sys.argv[0]), "mkvdts2ac3.cfg")

    if os.path.isfile(configFilename):
        config = ConfigParser.SafeConfigParser()
        config.read(configFilename)
        defaults = dict(config.items("mkvdts2ac3"))
        for key in defaults:
            if key == "verbose":
                defaults["verbose"] = int(defaults["verbose"])

        parser.set_defaults(**defaults)

    parser.add_argument('fileordir', metavar='FileOrDirectory', nargs='+', help='a file or directory (wildcards may be used)')

    parser.add_argument("--aac", help="Also add aac track", action="store_true")
    parser.add_argument("--aacstereo", help="Make aac track stereo instead of 6 channel", action="store_true")
    parser.add_argument("--aaccustom", metavar="TITLE", help="Custom AAC track title")
    parser.add_argument("-c", "--custom", metavar="TITLE", help="Custom AC3 track title")
    parser.add_argument("-d", "--default", help="Mark AC3 track as default", action="store_true")
    parser.add_argument("--destdir", metavar="DIRECTORY", help="Destination Directory")
    parser.add_argument("-e", "--external", action="store_true",
                        help="Leave AC3 track out of file. Does not modify the original matroska file. This overrides '-n' and '-d' arguments")
    parser.add_argument("-f", "--force", help="Force processing when AC3 track is detected", action="store_true")
    parser.add_argument("--ffmpegpath", metavar="DIRECTORY", help="Path of ffmpeg")
    parser.add_argument("-i", "--initial", help="New AC3 track will be first in the file", action="store_true")
    parser.add_argument("-k", "--keepdts", help="Keep external DTS track (implies '-n')", action="store_true")
    parser.add_argument("--md5", help="check md5 of files before removing the original if destination directory is on a different device than the original file", action="store_true")
    parser.add_argument("--mp4", help="create output in mp4 format", action="store_true")
    parser.add_argument("--mkvtoolnixpath", metavar="DIRECTORY", help="Path of mkvextract, mkvinfo and mkvmerge")
    parser.add_argument("-n", "--nodts", help="Do not retain the DTS track", action="store_true")
    parser.add_argument("--new", help="Do not copy over original. Create new adjacent file", action="store_true")
    parser.add_argument("--no-subtitles", help="Remove subtitles", action="store_true")
    parser.add_argument("-o", "--overwrite", help="Overwrite file if already there. This only applies if destdir or sabdestdir is set", action="store_true")
    parser.add_argument("-r", "--recursive", help="Recursively descend into directories", action="store_true")
    parser.add_argument("-s", "--compress", metavar="MODE", help="Apply header compression to streams (See mkvmerge's --compression)", default='none')
    parser.add_argument("--sabdestdir", metavar="DIRECTORY", help="SABnzbd Destination Directory")
    parser.add_argument("--stereo", help="Make ac3 track stereo instead of 6 channel", action="store_true")
    parser.add_argument("-t", "--track", metavar="TRACKID", help="Specify alternate DTS track. If it is not a DTS track it will default to the first DTS track found")
    parser.add_argument("-w", "--wd", metavar="FOLDER", help="Specify alternate temporary working directory")
    parser.add_argument("-v", "--verbose", help="Turn on verbose output. Use more v's for more verbosity. -v will output what it is doing. -vv will also output the command that it is running. -vvv will also output the command output", action="count")
    parser.add_argument("-V", "--version", help="Print script version information", action='version', version='%(prog)s ' + version + ' by Drew Thomson')
    parser.add_argument("--test", help="Print commands only, execute nothing", action="store_true")
    parser.add_argument("--debug", help="Print commands and pause before executing each", action="store_true")

    args = parser.parse_args()

    if not args.verbose:
        args.verbose = 0

def winexe(program):
    if sys.platform == "win32" and not program.endswith(".exe"):
        program += ".exe"
    return program

# set ffmpeg and mkvtoolnix paths
if args.mkvtoolnixpath:
    mkvinfo = os.path.join(args.mkvtoolnixpath, "mkvinfo")
    mkvinfo = winexe(mkvinfo)
    mkvmerge = os.path.join(args.mkvtoolnixpath, "mkvmerge")
    mkvmerge = winexe(mkvmerge)
    mkvextract = os.path.join(args.mkvtoolnixpath, "mkvextract")
    mkvextract = winexe(mkvextract)
if not args.mkvtoolnixpath or not os.path.exists(mkvinfo):
    mkvinfo = "mkvinfo"
if not args.mkvtoolnixpath or not os.path.exists(mkvmerge):
    mkvmerge = "mkvmerge"
if not args.mkvtoolnixpath or not os.path.exists(mkvextract):
    mkvextract = "mkvextract"
   
if args.ffmpegpath:
    ffmpeg = os.path.join(args.ffmpegpath, "ffmpeg")
    ffmpeg = winexe(ffmpeg)
if not args.ffmpegpath or not os.path.exists(ffmpeg):
    ffmpeg = "ffmpeg"


# check paths
def which(program):
    if sys.platform == "win32" and not program.endswith(".exe"):
        program += ".exe"
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

missingprereqs = False
missinglist = []
if not which(mkvextract):
    missingprereqs = True
    missinglist.append("mkvextract")
if not which(mkvinfo):
    missingprereqs = True
    missinglist.append("mkvinfo")
if not which(mkvmerge):
    missingprereqs = True
    missinglist.append("mkvmerge")
if not which(ffmpeg):
    missingprereqs = True
    missinglist.append("ffmpeg")
if missingprereqs:
    sys.stdout.write("You are missing the following prerequisite tools: ")
    for tool in missinglist:
        sys.stdout.write(tool + " ")
    if not args.mkvtoolnixpath and not args.ffmpegpath:
        print "\nYou can use --mkvtoolnixpath and --ffmpegpath to specify the path"
    else:
        print   
    sys.exit(1)

if not args.verbose:
    args.verbose = 0

if args.verbose < 2 and (args.test or args.debug):
    args.verbose = 2

if sab:
    args.fileordir = [args.fileordir[0]]
    args.verbose = 3

if args.debug and args.verbose == 0:
    args.verbose = 1

def doprint(mystr, v=0):
    if args.verbose >= v:
        sys.stdout.write(mystr)

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError, e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def elapsedstr(starttime):
    elapsed = (time.time() - starttime)
    minutes = int(elapsed / 60)
    mplural = 's'
    if minutes == 1:
        mplural = ''
    seconds = int(elapsed) % 60
    splural = 's'
    if seconds == 1:
        splural = ''
    return str(minutes) + " minute" + mplural + " " + str(seconds) + " second" + splural

def getduration(time):
    (hms, ms) = time.split('.')
    (h, m, s) = hms.split(':')
    totalms = int(ms) + (int(s) * 100) + (int(m) * 100 * 60) + (int(h) * 100 * 60 * 60)
    return totalms
   
def runcommand(title, cmdlist):
    if args.debug:
        raw_input("Press Enter to continue...")
    cmdstarttime = time.time()
    if args.verbose >= 1:
        sys.stdout.write(title)
        if args.verbose >= 2:
            cmdstr = ''
            for e in cmdlist:
                cmdstr += e + ' '
            print
            print "    Running command:"
            print textwrap.fill(cmdstr.rstrip(), initial_indent='      ', subsequent_indent='      ')
    if not args.test:
        if args.verbose >= 3:
            subprocess.call(cmdlist)
        elif args.verbose >= 1:
            if "ffmpeg" in cmdlist[0]:
                proc = subprocess.Popen(cmdlist, stderr=subprocess.PIPE)
                line = ''
                duration_regex = re.compile("  Duration: (\d+:\d\d:\d\d\.\d\d),")
                progress_regex = re.compile("size= +\d+.*time=(\d+:\d\d:\d\d\.\d\d) bitrate=")
                duration = False
                while True:
                    if not duration:
                        durationline = proc.stderr.readline()
                        match = duration_regex.match(durationline)
                        if match:
                            duration = getduration(match.group(1))
                    else:
                        out = proc.stderr.read(1)
                        if out == '' and proc.poll() != None:
                            break
                        if out != '\r':
                            line += out
                        else:
                            if 'size= ' in line:
                                match = progress_regex.search(line)
                                if match:
                                    percentage = int(float(getduration(match.group(1)) / float(duration)) * 100)
                                    if percentage > 100:
                                        percentage = 100
                                    sys.stdout.write("\r" + title + str(percentage) + '%')
                            line = ''
                        sys.stdout.flush()
                print "\r" + title + elapsedstr(cmdstarttime)
            else:
                proc = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
                line = ''
                progress_regex = re.compile("Progress: (\d+%)")
                while True:
                    out = proc.stdout.read(1)
                    if out == '' and proc.poll() != None:
                        break
                    if out != '\r':
                        line += out
                    else:
                        if 'Progress: ' in line:
                            match = progress_regex.search(line)
                            if match:
                                percentage = match.group(1)
                                sys.stdout.write("\r" + title + percentage)
                        line = ''
                    sys.stdout.flush()
                print "\r" + title + elapsedstr(cmdstarttime)
        else:
            subprocess.call(cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def find_mount_point(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path

def getmd5(fname, block_size=2**12):
    md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        doprint(fname + ": " + md5.hexdigest() + "\n", 3)
    return md5.hexdigest()

def check_md5tree(orig, dest):
    rt = True
    orig = os.path.abspath(orig)
    dest = os.path.abspath(dest)
    for ofile in os.listdir(orig):
        if rt == True:
            if os.path.isdir(os.path.join(orig, ofile)):
                doprint("dir: " + os.path.join(orig, ofile) + "\n", 3)
                odir = os.path.join(orig, ofile)
                ddir = os.path.join(dest, ofile)
                rt = check_md5tree(odir, ddir)
            else:
                doprint("file: " + os.path.join(orig, ofile) + "\n", 3)
                if getmd5(os.path.join(orig, ofile)) != getmd5(os.path.join(dest, ofile)):
                    rt = False
    return rt

def process(ford):
    if os.path.isdir(ford):
        doprint("    Processing dir:  " + ford + "\n", 3)
        if args.recursive:
            for f in os.listdir(ford):
                process(os.path.join(ford, f))
    else:
        doprint("    Processing file: " + ford + "\n", 3)
        # check if file is an mkv file
        child = subprocess.Popen([mkvmerge, "-i", ford], stdout=subprocess.PIPE)
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
                tempdir = tempfile.mkdtemp()
                tempdir = os.path.join(tempdir, "mkvdts2ac3")
               
            (dirName, fileName) = os.path.split(ford)
            fileBaseName = os.path.splitext(fileName)[0]
           
            doprint("filename: " + fileName + "\n", 1)
           
            dtsfile = fileBaseName + '.dts'
            tempdtsfile = os.path.join(tempdir, dtsfile)
            ac3file = fileBaseName + '.ac3'
            tempac3file = os.path.join(tempdir, ac3file)
            aacfile = fileBaseName + '.aac'
            tempaacfile = os.path.join(tempdir, aacfile)
            tcfile = fileBaseName + '.tc'
            temptcfile = os.path.join(tempdir, tcfile)
            newmkvfile = fileBaseName + '.mkv'
            tempnewmkvfile = os.path.join(tempdir, newmkvfile)
            adjacentmkvfile = os.path.join(dirName, fileBaseName + '.new.mkv')
            mp4file = os.path.join(dirName, fileBaseName + '.mp4')
            fname = fileName
           
            # get dts track id and video track id
            output = subprocess.check_output([mkvmerge, "-i", ford])
            lines = output.split("\n")
            altdtstrackid = False
            videotrackid = False
            alreadygotac3 = False
            audiotracks = []
            dtstracks = []
            for line in lines:
                linelist = line.split(' ')
                trackid = False
                if len(linelist) > 2:
                    trackid = linelist[2]
                    linelist = trackid.split(':')
                    trackid = linelist[0]
                if ' audio (' in line:
                    audiotracks.append(trackid)
                if ' audio (A_DTS)' in line or ' audio (DTS' in line:
                    dtstracks.append(trackid)
                elif ' video (' in line:
                    videotrackid = trackid
                elif ' audio (A_AC3)' in line or ' audio (AC3' in line:
                    alreadygotac3 = True
                if args.track:
                    matchObj = re.match( r'Track ID ' + args.track + r': audio (A?_?DTS', line)
                    if matchObj:
                        altdtstrackid = args.track
            if altdtstrackid:
                dtstracks[:] = []
                dtstracks.append(altdtstrackid)
           
            if not dtstracks:
                doprint("  No DTS tracks found\n", 1)
            elif alreadygotac3 and not args.force:
                doprint("  Already has AC3 track\n", 1)
            else:
                # if args.force = True we process all DTS tracks, otherwise only the first one
                if not args.force:
                    dtstracks = dtstracks[0:1]
                for dtstrackid in dtstracks:
                    # get dtstrack info
                    output = subprocess.check_output([mkvinfo, "--ui-language", "en_US", ford])
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
                   
                    # get ac3 track name
                    ac3name = False
                    if args.custom:
                        ac3name = args.custom
                    else:
                        for line in dtstrackinfo:
                            if "+ Name: " in line:
                                ac3name = line.split("+ Name: ")[-1]
                                ac3name = ac3name.replace("DTS", "AC3")
                                ac3name = ac3name.replace("dts", "ac3")
                                if args.stereo:
                                    ac3name = ac3name.replace("5.1", "Stereo")
                   
                    # get aac track name
                    aacname = False
                    if args.aaccustom:
                        aacname = args.aaccustom
                    else:
                        for line in dtstrackinfo:
                            if "+ Name: " in line:
                                aacname = line.split("+ Name: ")[-1]
                                aacname = aacname.replace("DTS", "AAC")
                                aacname = aacname.replace("dts", "aac")
                                if args.aacstereo:
                                    aacname = aacname.replace("5.1", "Stereo")
                   
                    totaljobs = 4
                    jobnum = 1
                    if args.aac:
                        totaljobs += 1
                    if args.mp4:
                        totaljobs += 1

                    # extract timecodes
                    tctitle = "  Extracting Timecodes  [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                    jobnum += 1
                    tccmd = [mkvextract, "timecodes_v2", ford, dtstrackid + ":" + temptcfile]
                    runcommand(tctitle, tccmd)

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
                    extracttitle = "  Extracting DTS track  [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                    jobnum += 1
                    extractcmd = [mkvextract, "tracks", ford, dtstrackid + ':' + tempdtsfile]
                    runcommand(extracttitle, extractcmd)

                    # convert DTS to AC3
                    converttitle = "  Converting DTS to AC3 [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                    jobnum += 1
                    audiochannels = 6
                    if args.stereo:
                        audiochannels = 2
                    convertcmd = [ffmpeg, "-y", "-i", tempdtsfile, "-acodec", "ac3", "-ac", str(audiochannels), "-ab", "448k", tempac3file]
                    runcommand(converttitle, convertcmd)
                   
                    if args.aac:
                        converttitle = "  Converting DTS to AAC [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                        jobnum += 1
                        audiochannels = 6
                        if args.aacstereo:
                            audiochannels = 2
                        convertcmd = [ffmpeg, "-y", "-i", tempdtsfile, "-acodec", "libfaac", "-ac", str(audiochannels), "-ab", "448k", tempaacfile]
                        runcommand(converttitle, convertcmd)
                        if not os.path.isfile(tempaacfile) or os.path.getsize(tempaacfile) == 0:
                            convertcmd = [ffmpeg, "-y", "-i", tempdtsfile, "-acodec", "libvo_aacenc", "-ac", str(audiochannels), "-ab", "448k", tempaacfile]
                            runcommand(converttitle, convertcmd)
                        if not os.path.isfile(tempaacfile) or os.path.getsize(tempaacfile) == 0:
                            convertcmd = [ffmpeg, "-y", "-i", tempdtsfile, "-acodec", "aac", "-strict", "experimental", "-ac", str(audiochannels), "-ab", "448k", tempaacfile]
                            runcommand(converttitle, convertcmd)
                        if not os.path.isfile(tempaacfile) or os.path.getsize(tempaacfile) == 0:
                            args.aac = False
                            print "ERROR: ffmpeg can't use any aac codecs. Please try to get libfaac, libvo_aacenc, or a newer version of ffmpeg with the experimental aac codec installed"
                           
                    if args.external:
                        if not args.test:
                            shutil.move(tempac3file, os.path.join(dirName, fileBaseName + '.ac3'))
                            fname = ac3file
                    else:
                        # remux
                        remuxtitle = "  Remuxing AC3 into MKV [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                        jobnum += 1
                        # Start to "build" command
                        remux = [mkvmerge]
                        
                        comp = 'none'
                        if args.compress:
                            comp = args.compress
                            
                        # Remove subtitles
                        if args.no_subtitles:
                            remux.append("--no-subtitles")
                       
                        # Puts the AC3 track as the second in the file if indicated as initial
                        if args.initial:
                            remux.append("--track-order")
                            if args.aac:
                                remux.append("1:0,2:0")
                            else:
                                remux.append("1:0")

                        # If user doesn't want the original DTS track drop it
                        if args.nodts or args.keepdts:
                            if len(audiotracks) == 1:
                                remux.append("-A")
                            else:
                                audiotracks = [audiotrack for audiotrack in audiotracks if audiotrack != dtstrackid]
                                remux.append("-a")
                                remux.append(",".join(audiotracks))
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
                            remux.append("0:1")
                       
                        # Set the language
                        remux.append("--language")
                        remux.append("0:" + dtslang)
                       
                        # If the name was set for the original DTS track set it for the AC3
                        if ac3name:
                            remux.append("--track-name")
                            remux.append("0:\"" + ac3name.rstrip() + "\"")
                       
                        # set delay if there is any
                        if delay:
                            remux.append("--sync")
                            remux.append("0:" + delay.rstrip())
                           
                        # Set track compression scheme and append new AC3
                        remux.append("--compression")
                        remux.append("0:" + comp)
                        remux.append(tempac3file)
                       
                        if args.aac:
                            # If the name was set for the original DTS track set it for the AAC
                            if aacname:
                                remux.append("--track-name")
                                remux.append("0:\"" + aacname.rstrip() + "\"")
                               
                            # Set track compression scheme and append new AAC
                            remux.append("--compression")
                            remux.append("0:" + comp)
                            remux.append(tempaacfile)
                       
                        # Declare output file
                        remux.append("-o")
                        remux.append(tempnewmkvfile)
                       
                        runcommand(remuxtitle, remux)

                        #time.sleep(600)

                        if not args.test:
                            if args.mp4:
                                converttitle = "  Converting MKV to MP4 [" + str(jobnum) + "/" + str(totaljobs) + "]..."
                                convertcmd = [ffmpeg, "-i", tempnewmkvfile, "-map", "0", "-vcodec", "copy", "-acodec", "copy", "-c:s", "mov_text", mp4file]
                                runcommand(converttitle, convertcmd)
                                silentremove(ford)
                            else:
                                #~ replace old mkv with new mkv
                                if args.new:
                                    shutil.move(tempnewmkvfile, adjacentmkvfile)
                                else:
                                    silentremove(ford)
                                    shutil.move(tempnewmkvfile, ford)

                    if not args.test:
                        #~ clean up temp folder
                        if args.keepdts and not args.external:
                            shutil.move(tempdtsfile, os.path.join(dirName, fileBaseName + ".dts"))
                            fname = dtsfile
                        else:
                            silentremove(tempdtsfile)
                        if not args.external:
                            silentremove(tempac3file)
                            silentremove(tempaacfile)
                            silentremove(temptcfile)
                        if not os.listdir(tempdir):
                            os.rmdir(tempdir)

                #~ print out time taken
                elapsed = (time.time() - starttime)
                minutes = int(elapsed / 60)
                seconds = int(elapsed) % 60
                doprint("  " + fileName + " finished in: " + str(minutes) + " minutes " + str(seconds) + " seconds\n", 1)

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
        destdir = False
        if args.destdir:
            destdir = args.destdir
        if sab and args.sabdestdir:
            destdir = args.sabdestdir
        if destdir:
            if fname:
                (dirName, fileName) = os.path.split(ford)
                destfile = os.path.join(destdir, fname)
                origfile = os.path.join(dirName, fname)
                if args.md5 and (find_mount_point(dirName) != find_mount_point(destdir)):
                    if os.path.exists(destfile):
                        if args.overwrite:
                            silentremove(destfile)
                            shutil.copyfile(origfile, destfile)
                            if getmd5(origfile) == getmd5(destfile):
                                silentremove(origfile)
                            else:
                                print "MD5's don't match."
                        else:
                            print "File " + destfile + " already exists"
                    else:
                        doprint("copying: " + origfile + " --> " + destfile + "\n", 3)
                        shutil.copyfile(origfile, destfile)
                        if getmd5(origfile) == getmd5(destfile):
                            silentremove(origfile)
                        else:
                            print "MD5's don't match."
                else:
                    if os.path.exists(destfile):
                        if args.overwrite:
                            silentremove(destfile)
                            shutil.move(origfile, destfile)
                        else:
                            print "File " + destfile + " already exists"
                    else:
                        shutil.move(origfile, destfile)
            else:
                origpath = os.path.abspath(ford)
                destpath = os.path.join(destdir, os.path.basename(os.path.normpath(ford)))
                if args.md5 and (find_mount_point(origpath) != find_mount_point(destpath)):
                    if os.path.exists(destpath) and args.overwrite:
                        shutil.rmtree(destpath)
                    elif os.path.exists(destpath):   
                        print "Directory " + destpath + " already exists"
                    else:
                        shutil.copytree(origpath, destpath)
                        if check_md5tree(origpath, destpath):
                            shutil.rmtree(origpath)
                        else:
                            print "MD5's don't match."
                else:
                    shutil.move(origpath, destpath)
                   
if sab or nzbget:
    sys.stdout.write("mkv dts -> ac3 conversion: " + elapsedstr(totalstime))
else:
    doprint("Total Time: " + elapsedstr(totalstime), 1)

if nzbget:
    sys.exit(POSTPROCESS_SUCCESS)
