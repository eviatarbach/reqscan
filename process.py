#!/usr/bin/env python
'''
Copyright 2011--2014 Eviatar Bach

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

import traceback
import os
import subprocess
import datetime
import ConfigParser
import glob
import re
import argparse
from sys import argv
from xml.dom.minidom import parseString

error = 0
failed = 0

parser = argparse.ArgumentParser()
parser.add_argument('--nocolours', action='store_true')
args = parser.parse_args()

def filter_alphanum(string):
    # Strip a string of characters that are not alphanumeric, whitespace, or
    # underscores
    return filter(lambda c: c.isalnum() or c.isspace() or c == '_', string)


def natural_sorted(l):
    # From Mark Byers from StackOverflow question 4836710
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in
                                re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def find_max_index(name, start):
    # Finds the largest suffix for a filename in the current directory
    num = start
    while os.path.exists('{}_{}.pdf'.format(name, num)):
        num += 1
    return num

class Colours:
    # Idea from joeld from StackOverflow question 287871
    if args.nocolours == False:
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
    else:
        OKGREEN = WARNING = FAIL = ENDC = BOLD = ''

FNULL = open(os.devnull, 'w')

try:
    from PIL import Image
    import zbar

    # Defaults
    config = ConfigParser.RawConfigParser(defaults={'cropbox': 'None',
                                                    'datamatrix': 'True',
                                                    'orientation': 'False',
                                                    'symbologies':
                                                     'code39 code128',
                                                    'resize': 0.25})

    try:
        options_file = open('options.txt', 'r+')
        config.readfp(options_file)
        if not config.has_section('Options'):
            raise ConfigParser.NoSectionError
        options_file.close()
    except IOError, ConfigParser.NoSectionError:
        config.add_section('Options')
        options_file = open('options.txt', 'w')
        config.write(options_file)
        options_file.close()

    # Check dependencies
    if config.getboolean('Options', 'datamatrix'):
        if subprocess.call(['which', 'dmtxread'], stdout=FNULL, stderr=FNULL) == 1:
            print('Error: Could not find dmtxread executable')
            error = 1
    if error:
        raise SystemExit

    # Make directory
    d = datetime.datetime.today().date().strftime('%b-%d-%Y')
    if not os.path.exists(d):
        os.makedirs(d)
    os.chdir(d)

    scale = float(config.get('Options', 'resize'))

    if len(glob.glob('out*.tif')) == 0:
        print('{}Error: no scanned files{}'.format(Colours.FAIL,
                                                   Colours.ENDC))
        error = 1

    else:
        for each_file in natural_sorted(glob.glob('out*.tif')):
            data_matrix_done = False

            print('File: ' + each_file)

            image = Image.open(each_file)

            # Barcode stuff
            print('Scanning barcodes...')
            pil = image.convert('L')
            scanner = zbar.ImageScanner()

            # Disable all symbologies, then add desired
            scanner.parse_config('disable')
            symbologies = config.get('Options', 'symbologies').split()
            for symbology in symbologies:
                scanner.parse_config('{}.enable'.format(symbology))

            if not config.get('Options', 'cropbox').split()[0] == 'None':
                cropbox = map(int, config.get('Options', 'cropbox').split())
                pil.crop(cropbox)

            if config.getboolean('Options', 'orientation'):
                try:
                    pil.save('tozbar.png')
                    outstr = subprocess.check_output(['../zbarimg',
                                                      '--xml',
                                                      'tozbar.png'])
                    xmlstr = parseString(outstr).getElementsByTagName('symbol')
                    for index in range(len(xmlstr)):
                        if (xmlstr.item(index).getAttribute('orientation') ==
                            'DOWN'):
                            pil = pil.rotate(180)
                except subprocess.CalledProcessError:
                    pass

            raw = pil.tostring()
            image = zbar.Image(pil.size[0], pil.size[1], 'Y800', raw)
            scanner.scan(image)

            if config.getboolean('Options', 'datamatrix'):
                print('Checking for Data Matrix barcodes...')
                pil.save('todmtx.png')
                try:
                    data_matrix = filter_alphanum(subprocess
                                                  .check_output(['dmtxread',
                                                                 '-N1',
                                                                 '-m3000',
                                                                 'todmtx.png']))
                except subprocess.CalledProcessError:
                    data_matrix = None

                if data_matrix:
                    if not os.path.exists(data_matrix + '.pdf'):
                        dname = data_matrix + '.pdf'
                    else:
                        dname = '{}_{}.pdf'.format(data_matrix,
                                                   find_max_index(data_matrix, 2))

                    pil.resize((int(pil.size[0] * scale),
                                int(pil.size[1] * scale)),
                               Image.ANTIALIAS).save(dname)

                    data_matrix_done = True

            if len(list(image)) == 0 and not data_matrix_done:
                print('{}{} failed. Barcode not '
                      'found.{}'.format(Colours.WARNING, each_file,
                                        Colours.ENDC))
                failed += 1
                suffix = find_max_index('fail', 1)
                pil.resize((int(pil.size[0] * scale),
                            int(pil.size[1] * scale)),
                           Image.ANTIALIAS).save('fail_{}.pdf'.format(suffix))
                os.remove(each_file)
                continue

            for symbol in image:
                if symbol.data:
                    data = filter_alphanum(''.join(symbol.data))
                    if not os.path.exists(data + '.pdf'):
                        name = data + '.pdf'
                    else:
                        # For repeated barcodes
                        name = '{}_{}.pdf'.format(data, find_max_index(data, 2))

                    pil.resize((int(pil.size[0] * scale),
                                int(pil.size[1] * scale)),
                               Image.ANTIALIAS).save(name)

            os.remove(each_file)

    if error == 0 and failed == 0:
        print('{}{}Operation completed successfully.{}'.format(Colours.BOLD,
                                                               Colours.OKGREEN,
                                                               Colours.ENDC))
    elif error == 0 and failed > 0:
        print(('{}{}Operation completed with {} '
               'failed file(s).{}').format(Colours.BOLD, Colours.WARNING,
                                           failed, Colours.ENDC))
    else:
        raise SystemExit

except:
    error = 1
    print(traceback.format_exc())

finally:
    # Handles exiting and cleaning up, even in the case of errors
    for scrap_file in (['tozbar.png', 'todmtx.png']):
        try:
            os.remove(scrap_file)
        except:
            pass
    FNULL.close()
    os.chdir('..')  # Return to original directory
    if error == 1:
        print('{}{}Operation failed.{}'.format(Colours.BOLD, Colours.FAIL,
                                               Colours.ENDC))
