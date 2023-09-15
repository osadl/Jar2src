#!/usr/bin/env python

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

# Maintain Python 2.x compatibility
# pylint: disable=consider-using-with,unspecified-encoding

import sys
import os
import subprocess
import argparse
import re
import zipfile

class colors:
    OK = '\033[1;32m'
    WARN = '\033[1;33m'
    FAIL = '\033[1;31m'
    ENDC = '\033[0m'

class nocolors:
    OK = ''
    WARN = ''
    FAIL = ''
    ENDC = ''

def checkparent(parentrelsrcdir, filename, lastsubdir, listing, verbose, inserted, movetrials, c):
    found = False
    if os.path.exists(parentrelsrcdir):
        found = True
        if len(inserted) == 0:
            print(c.WARN + 'Warning (parent directory match) for "' + filename + '":' + c.ENDC)
        else:
            print(c.WARN + 'Warning (parent directory match and needed to insert "' + inserted + '" subdirectory at level -' + str(movetrials) + ') for "' + filename + '":' + c.ENDC)
        print('  Source code may be located below "' + parentrelsrcdir + '", subdir "' + lastsubdir + '" not found')
        if listing:
            os.system('find ' + parentrelsrcdir)
    else:
        if verbose:
            print('Source code directory "' + parentrelsrcdir + '" not found')
    return found

def checkinsert(newrelsrcdir, filename, lastsubdir, listing, verbose, inserted, movetrials, c):
    found = False
    if os.path.exists(newrelsrcdir):
        found = True
        print(c.WARN + 'Warning (needed to insert "' + inserted + '" subdirectory at level -' + str(movetrials) + ') for "' + filename + '":' + c.ENDC)
        print('  Source code is probably located at "' + newrelsrcdir + '"')
        if listing:
            os.system('find ' + newrelsrcdir)
    else:
        if verbose:
            print('Source code directory "' + newrelsrcdir + '" not found')
        found = checkparent(os.path.normpath(newrelsrcdir + '/..'), filename, lastsubdir, listing, verbose, inserted, movetrials, c)
    return found

def parseargs(argline):
    """ Convert the tag=value assignemnts of the argline to an associative array"""
    args = {}
    for arg in argline:
        a = arg.split('=')
        args[a[0]] = a[1]
    return args

def getsourcecode(filename, verbose, execute, listing, c):
    """ Find and optionally obtain a JAR's corresponding source code, if required by the license"""
    manifest = ''
    licensetext = ''
    if re.search(r'\.jar$', filename):
        z = zipfile.ZipFile(filename)
        classfound = 0
        for name in z.namelist():
            if re.search(r'\.class$', name):
                classfound = 1
                break
        if not classfound:
            print(c.WARN + 'Warning for "' + filename + '":' + c.ENDC)
            print('  No files with suffix ".class" found in archive, but other binary files may be included')
            print()
            return

        manifest = z.read('META-INF/MANIFEST.MF').decode('utf-8').replace('\r\n', '\n')
        if 'META-INF' + os.sep + 'LICENSE' in z.namelist():
            licensetext = z.read('META-INF/LICENSE').decode('utf-8').replace('\r\n', '\n')
        else:
            if 'LICENSE' in z.namelist():
                licensetext = z.read('LICENSE').decode('utf-8').replace('\r\n', '\n')
        if licensetext == '':
            for name in z.namelist():
                if name.find('about_files/LICENSE-') >= 0:
                    licensetext += z.read(name).decode('latin_1').replace('\r\n', '\n')
    else:
        classfound = 0
        for file in os.walk(filename):
            if os.path.isfile(file[0]) and re.search(r'\.class$', file[0]):
                classfound = 1
                break
        if not classfound:
            print(c.WARN + 'Warning for "' + filename + '":' + c.ENDC)
            print('  No files with suffix ".class" found in directory, but other binary files may be included')
            print()
            return
        manifestname = filename + '/META-INF/MANIFEST.MF'
        if os.path.isfile(manifestname):
            manifest = open(manifestname, 'r').read().replace('\r\n', '\n')
        licensetextname = filename + '/META-INF/LICENSE'
        if os.path.isfile(licensetextname):
            licensetext = open(licensetextname, 'r').read().replace('\r\n', '\n')
        else:
            licensetextname = filename + '/LICENSE'
            if os.path.isfile(licensetextname):
                licensetext = open(licensetextname, 'r').read().replace('\r\n', '\n')

    if manifest == '':
        print(c.FAIL + 'Failure for "' + filename + '":' + c.ENDC)
        print('  No MANIFEST.MF in META-INF found')
        print()
        return

    if verbose:
        print('Manifest found in "' + filename + '"')

    sourceref = ''
    foundsourceref = 0
    copyright = ''
    foundcopyright = 0
    license = ''
    foundlicense = 0
    while True:
        endlinepos = manifest.find('\n')
        line = manifest[0:endlinepos]
        if len(line) == 0:
            break
        if foundsourceref:
            if line[0] == ' ':
                sourceref += line[1:]
            else:
                break
        if foundcopyright:
            if line[0] == ' ':
                copyright += line[1:]
            else:
                foundcopyright = 0
        if foundlicense:
            if line[0] == ' ':
                license += line[1:]
            else:
                foundlicense = 0
        if line.find('Eclipse-SourceReferences: ') >= 0:
            sourceref = line[34:]
            foundsourceref = 1
        if line.find('Bundle-Copyright: ') >= 0:
            copyright = line[18:]
            foundcopyright = 1
        if line.find('Bundle-License: ') >= 0:
            license = line[16:]
            foundlicense = 1
        manifest = manifest[endlinepos + 1:]
        if len(manifest) == 0:
            break
    if len(sourceref) == 0:
        if license == '' and re.search(r'Apache License\W*Version 2\.0', licensetext) or licensetext.find('SPDX-License-Identifier: Apache-2.0') >= 0:
            license = 'Apache-2.0'
        if licensetext.find('W3C Software License') >= 0:
            if len(license) > 0:
                license += ', '
            license += 'W3C Software License'
        reason = '  Tag "Eclipse-SourceReferences" not found in META-INF/MANIFEST.MF'
        if license.find('www.apache.org/licenses/LICENSE-2.0.txt') >= 0 or copyright.find('www.unicode.org/copyright.html') >= 0 or\
          license.find('Apache-2.0') >= 0 or license.find('http://opensource.org/licenses/apache2.0.php') >= 0 or\
          license.find('mit-license.php') >= 0 or license.find('BSD-3-Clause') >= 0:
            print(c.WARN + 'Warning for "' + filename + '":' + c.ENDC)
            print(reason)
            print('  (License does not impose disclosure obligations)')
        else:
            print(c.FAIL + 'Failure for "' + filename + '":' + c.ENDC)
            print(reason)
        if len(copyright) != 0:
            print('  Copyright: ' + copyright.split(';')[0])
        if len(license) != 0:
            print('  License: ' + license.split(';')[0])
        print()
        return

    parts = sourceref.split(';')

    if verbose:
        print('Source reference found:')
        for part in parts:
            print('  ' + part)

    if parts[0].find('pserver:dev.eclipse.org') >= 0:
        print(c.FAIL + 'Failure for "' + filename + '":' + c.ENDC)
        print('  Outdated source reference "dev.eclipse.org"')
        print()
        return

    url = parts[0]

    if url.find('http://git.eclipse.org/gitroot') >= 0:
        eclipsepart = url.split('/')
        url = 'https://github.com/eclipse/' + eclipsepart[4] + '.git'

    urlparts = url.split('/')
    urlslashes = len(urlparts) - 1
    project = urlparts[urlslashes].replace('.git', '')

    parts.pop(0)
    args = parseargs(parts)

    path = args['path'].replace('"', '')
    pathparts = path.split('/')
    pathslashes = len(pathparts) - 1
    src = pathparts[pathslashes]

    if 'tag' in args.keys():
        tag = args['tag']
    if 'commitId' in args.keys():
        commit = args['commitId']

    destdir = filename + '.srcdir'
    srcdir = path + '/src/' + src.replace('.', '/')
    projdir = project + '/' + srcdir
    relsrcdir = destdir + '/' + projdir

    bashscript = '#!/bin/bash\n' +\
    '# Use this script to obtain the source code for "' + filename + '"\n' +\
    'mkdir -p ' + destdir + '\n' +\
    'cd ' + destdir + '\n' +\
    'rm -Rf ' + project + '\n' +\
    'git clone -q ' + url + '\n' +\
    'retval=$?' + '\n' +\
    'if test $retval = 0' + '\n' +\
    'then' + '\n' +\
    '  cd ' + project + '\n' +\
    '  git checkout -q ' + commit + '\n' +\
    'else' + '\n' +\
    '  echo "  "Git error $retval' + '\n' +\
    'fi' + '\n'

    if execute:
        result = subprocess.run(bashscript, shell = True, capture_output = True, text = True)
        errormessage = '  ' + result.stderr.replace('fatal: ', '').capitalize()
        if len(errormessage.strip()) > 0:
            print(c.FAIL + 'Failure for "' + filename + '":' + c.ENDC)
            print(errormessage, end = '')
        else:
            if os.path.exists(relsrcdir):
                print(c.OK + 'Success for "' + filename + '":' + c.ENDC)
                print('  Source code is located at "' + relsrcdir + '"')
                if listing:
                    os.system('ls -l ' + relsrcdir)
            else:
                if verbose:
                    print('Source code directory "' + relsrcdir + '" not found')
                dirparts = relsrcdir.split('/')
                lastsubdir = dirparts[len(dirparts) - 1]
                inserted = ''
                movetrials = ''
                found = checkparent(os.path.normpath(relsrcdir + '/..'), filename, lastsubdir, listing, verbose, inserted, movetrials, c)
                if not found:
                    for movetrials in list(range(1, 4)):
                        if found:
                            break
                        dirparts = relsrcdir.split('/')
                        lastpart = len(dirparts) - 1
                        movepart = lastpart - movetrials
                        dirparts.append(dirparts[lastpart])
                        for moveup in list(range(lastpart, movepart, -1)):
                            dirparts[moveup] = dirparts[moveup - 1]
                        dirparts[movepart] = 'internal'
                        inserted = dirparts[movepart]
                        newrelsrcdir = ('/').join(dirparts)
                        found = checkinsert(newrelsrcdir, filename, lastsubdir, listing, verbose, inserted, movetrials, c)
                        if not found:
                            inserted = '/internal/provisional/'
                            newrelsrcdir2 = newrelsrcdir.replace('/internal/', inserted)
                            found = checkinsert(newrelsrcdir2, filename, lastsubdir, listing, verbose, inserted, movetrials, c)

                if not found:
                    print(c.FAIL + 'Failure for "' + filename + '":' + c.ENDC)
                    if len(errormessage) > 8:
                        print(errormessage)
                    else:
                        print('  Specified path to source code "' + relsrcdir + '" was not found')
    else:
        if verbose:
            print()
        print("Script to obtain source code:")
        print(bashscript)
    print()
    return

def main(argv):
    parser = argparse.ArgumentParser(prog = 'jar2src.py',
      epilog = 'Parse JAR manifest for location of source code, create script to obtain it and optionally execute script')

    parser.add_argument('filename',
      metavar = 'JAR',
      help = 'file name of a the Java archive to process')
    parser.add_argument('-c', '--colorify',
      action = 'store_true',
      default = False,
      help = 'colorify the output to differently mark success, warning and failure')
    parser.add_argument('-e', '--execute',
      action = 'store_true',
      default = False,
      help = 'execute the generated script to obtain the source code, otherwise only show the script')
    parser.add_argument('-l', '--list',
      action = 'store_true',
      default = False,
      help = 'list content of the source code directory, if successfully created, has no effect without --execute')
    parser.add_argument('-v', '--verbose',
      action = 'store_true',
      default = False,
      help = 'show names and texts the program is using')
    args = parser.parse_args()

    if args.colorify:
        c = colors
    else:
        c = nocolors
    getsourcecode(args.filename, args.verbose, args.execute, args.list, c)

if __name__ == '__main__':
    main(sys.argv)
