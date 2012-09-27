`mkvdts2ac3.py` is a python script which can be used for converting the DTS in
Matroska (MKV) files to AC3. It provides you with a healthy set of options
for controlling the resulting file.

I just recreated mkvdts2ac3.sh which was created by Jake Wharton and Chris Hoekstra
I Figured that most people are using this with sabnzbd and couchpotato which both 
require python so a non-os specific solution would help people out (as well as myself)

Installation
============

Prerequisites
-------------
Make sure the executables for the following libraries are accessible.

1. [mkvtoolnix](http://www.bunkus.org/videotools/mkvtoolnix/) - Matroska tools
2. [ffmpeg](http://ffmpeg.org/) - Audio conversion tool

*Note: If you are a Mac OS X user you may need to compile these libraries.*

Installation
------------
If you have `git` installed, you can just run
`git clone git://github.com/skooby/mkvdts2ac3.py.git`.

You can download the script directly with wget or curl:
  wget https://raw.github.com/skooby/mkvdts2ac3.py/master/mkvdts2ac3.py
  -or-
  curl -O https://raw.github.com/skooby/mkvdts2ac3.py/master/mkvdts2ac3.py

Otherwise you can click the "Download" link on the GitHub project page and
download an archive and extract its contents.

Optional: If you want easy access to the script from any directory you can copy
or symlink the `mkvdts2ac3.py` file to a directory in your PATH variable or else
append the script's directory to the PATH variable.

Usage
=====

This script was designed to be used in conjunction with sabnzbd. It will search
a directory for the largest matroska file and check if it has a DTS track. If so,
it will convert the first DTS track it finds to AC3 and append it to the file.
If you want the directory contents to be moved to new directory you can edit the
variable at the beginning of the file which looks like:

destinationdirectory = ""

and change it to something like:

destinationdirectory = "C:\hooray\movietime"


Developed By
============
* Drew Thomson - <drewthomson@outlook.com>
* Chris Hoekstra - <chris.hoekstra@gmail.com>

Git repository located at
[github.com/JakeWharton/mkvdts2ac3](http://github.com/JakeWharton/mkvdts2ac3)


Very Special Thanks
-------------------
* Jake Wharton
* Chris Hoekstra

License
=======

	Copyright (C) 2012  Drew Thomson
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	
	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.