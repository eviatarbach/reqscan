#!/usr/bin/env python
'''
Copyright 2011--2013 Eviatar Bach

This file is part of patient-form-scanning.

patient-form-scanning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

patient-form-scanning is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
patient-form-scanning. If not, see http://www.gnu.org/licenses/.

patient-form-scanning is an open-source Python-based electronic medical record
(EMR) system, focusing on automatically digitizing records with barcode
recognition and OCR.'''

import subprocess
import ConfigParser
import os
import datetime
import glob

FNULL = open(os.devnull, 'w')

exit = False
for dep in ['scanimage']:  # Check dependencies
    if subprocess.call(['which', dep], stdout=FNULL, stderr=FNULL) == 1:
        print('Error: Could not find "{}" executable'.format(dep))
        exit = True
if exit:
    raise SystemExit

config = ConfigParser.RawConfigParser(defaults={'dpi': 300,
                                                'source': 'ADF Front'})

try:
    options_file = open('options.txt', 'r+')
    config.readfp(options_file)
    if not config.has_section('Options'):
        raise ConfigParser.NoSectionError
except IOError, ConfigParser.NoSectionError:
    config.add_section('Options')
    options_file = open('options.txt', 'w')
    config.write(options_file)
    options_file.close()

# Make directory

d = datetime.datetime.today().date().strftime('%b-%d-%Y')
if not os.path.exists(d):
    os.makedirs(d)
os.chdir(d)

# Get options

dpi = config.getint('Options', 'dpi')
source = config.get('Options', 'source')

# Find starting index

if len(glob.glob('out*.tif')):
    batch_start = max([int(entry[3:entry.index('.')]) for entry in
                       glob.glob('out*.tif')]) + 1
else:
    batch_start = 1

# Scan

os.system('scanimage --batch --format=tiff --source "{}" --resolution {} '
          '--batch-start {}'.format(source, dpi, batch_start))

os.chdir('..')  # Return to original directory
