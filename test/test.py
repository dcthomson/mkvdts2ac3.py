#!/usr/bin/env python

import os
import shutil
import subprocess
import sys

#wd -- probably want to test this with --debug because it is removed before the
#      script ends
#sabdestdir -- this might be tough to auto test
#debug -- can't auto test, requires user input

# ext device -- since md5 is only checked when copying to a different device than
#               the original, you must set ext to a different device if you want
#               to run the following tests: md5, md5 tree, recursive md5 tree
#
#               examples:
#                   Unix:    ext = "/mnt/othermntpt"
#                   Windows: ext = "F:\\"
ext = False

extdir = False
if ext:
    extdir = os.path.join(ext, "mkvdts2ac3-test")

if os.path.isdir("tests"):
    sys.stdout.write("Removing old tests...")
    shutil.rmtree('tests')
    if ext and os.path.isdir(extdir):
        shutil.rmtree(extdir)
    print "DONE"

os.makedirs("tests")
if extdir:
    os.makedirs(extdir)

mkvdts2ac3cmd = os.path.join("..", "mkvdts2ac3.py")

# compress
test = "compress"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--compress", "zlib", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# custom
test = "custom"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--custom", "custom name", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# default
test = "default"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--default", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# mp4
test = "mp4"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--mp4", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir
test = "destdir"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir mp4
test = "destdir_mp4"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--mp4", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir keepdts
test = "destdir_keepdts"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--keepdts", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir keepdts all-tracks
test = "destdir_keepdts_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--keepdts", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir external
test = "destdir_external"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--external", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir external all-tracks
test = "destdir_external_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--external", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir external aac
test = "destdir_external_aac"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--external", "--aac", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# destdir external aac all-tracks
test = "destdir_external_aac_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
destdir = os.path.join(testdir, "destdir")
os.makedirs(destdir)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--destdir", destdir, "--external", "--aac", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# external
test = "external"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--external", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# external all-tracks
test = "external_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--external", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# force
test = "force"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--force", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
output2 = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output + "\n-------------\n" + output2)
f.close()
print "DONE"

# initial
test = "initial"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--initial", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# keepdts
test = "keepdts"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--keepdts", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# keepdts all-tracks
test = "keepdts_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--keepdts", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

if extdir:
    # md5
    test = "md5"
    sys.stdout.write('Running test "' + test + '"...')
    testdir = os.path.join("tests", test)
    os.makedirs(testdir)
    testfile = os.path.join(testdir, "test.mkv")
    shutil.copyfile("test.mkv", testfile)
    md5extdir = os.path.join(extdir, test)
    os.makedirs(md5extdir)
    cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--md5", "--destdir", md5extdir, testfile]
    output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
    outfile = os.path.join(testdir, "output.txt")
    f = open(outfile, "w")
    f.write(output)
    f.close()
    print "DONE"
    
    # md5 tree
    test = "md5_tree"
    sys.stdout.write('Running test "' + test + '"...')
    testdir = os.path.join("tests", test)
    os.makedirs(testdir)
    dir1 = os.path.join(testdir, test)
    os.makedirs(dir1)
    dir1file = os.path.join(dir1, "test.mkv")
    shutil.copyfile("test.mkv", dir1file)
    dir2 = os.path.join(dir1, "dir2")
    os.makedirs(dir2)
    dir2file = os.path.join(dir2, "test.mkv")
    shutil.copyfile("test.mkv", dir2file)
    cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--md5", "--overwrite", "--destdir", extdir, dir1]
    output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
    outfile = os.path.join(testdir, "output.txt")
    f = open(outfile, "w")
    f.write(output)
    f.close()
    print "DONE"

# new
test = "new"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--new", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# nodts
test = "nodts"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--nodts", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# nodts all-tracks
test = "nodts_all-tracks"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "multidts.mkv")
shutil.copyfile("multidts.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--nodts", "--all-tracks", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# not recursive
test = "not_recursive"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
dir2 = os.path.join(testdir, "dir2")
os.makedirs(dir2)
dir2file = os.path.join(dir2, "test.mkv")
shutil.copyfile("test.mkv", dir2file)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", testdir]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# no_subtitles
test = "no_subtitles"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--no-subtitles", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# recursive
test = "recursive"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
dir2 = os.path.join(testdir, "dir2")
os.makedirs(dir2)
dir2file = os.path.join(dir2, "test.mkv")
shutil.copyfile("test.mkv", dir2file)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--recursive", testdir]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

if extdir:
    # recursive md5 tree
    test = "recursive_md5_tree"
    sys.stdout.write('Running test "' + test + '"...')
    testdir = os.path.join("tests", test)
    os.makedirs(testdir)
    dir1 = os.path.join(testdir, test)
    os.makedirs(dir1)
    dir1file = os.path.join(dir1, "test.mkv")
    shutil.copyfile("test.mkv", dir1file)
    dir2 = os.path.join(dir1, "dir2")
    os.makedirs(dir2)
    dir2file = os.path.join(dir2, "test.mkv")
    shutil.copyfile("test.mkv", dir2file)
    cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--md5", "--recursive", "--overwrite", "--destdir", extdir, dir1]
    output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
    outfile = os.path.join(testdir, "output.txt")
    f = open(outfile, "w")
    f.write(output)
    f.close()
    print "DONE"


# test
test = "test"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("test.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--test", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"

# track
test = "track"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
testfile = os.path.join(testdir, "test.mkv")
shutil.copyfile("multidts.mkv", testfile)
cmdlist = ["python", mkvdts2ac3cmd, "-vvv", "--track", "4", testfile]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
mkvinfo = os.path.join(testdir, "mkvinfo.txt")
f = open(mkvinfo, "w")
f.write(subprocess.check_output(["mkvinfo", testfile]))
f.close()
print "DONE"

# verbose
test = "verbose"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
for verbosity in range(0,4):
    testfile = os.path.join(testdir, "test." + str(verbosity) + ".mkv")
    shutil.copyfile("test.mkv", testfile)
    v = '-'
    for i in range (0, verbosity):
        v += 'v'
    cmdlist = []
    if verbosity == 0:
        cmdlist = ["python", mkvdts2ac3cmd, testfile]
    else:
        cmdlist = ["python", mkvdts2ac3cmd, v, testfile]
    output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
    outfile = os.path.join(testdir, "output." + str(verbosity) + ".txt")
    f = open(outfile, "w")
    f.write(output)
    f.close()
print "DONE"

# version
test = "version"
sys.stdout.write('Running test "' + test + '"...')
testdir = os.path.join("tests", test)
os.makedirs(testdir)
cmdlist = ["python", mkvdts2ac3cmd, "-V"]
output = subprocess.check_output(cmdlist,  stderr=subprocess.STDOUT)
outfile = os.path.join(testdir, "output.txt")
f = open(outfile, "w")
f.write(output)
f.close()
print "DONE"
