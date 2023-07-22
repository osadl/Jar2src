#!/usr/bin/env python

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

import sys
import os
import subprocess
import argparse
import re
import zipfile

def parseargs(argline):
    args = {}
    for arg in argline:
        a = arg.split('=')
        args[a[0]] = a[1];
    return args

def getsourcecode(filename, verbose, execute, listing):
    manifest = ''
    if re.search('\.jar$', filename):
        z = zipfile.ZipFile(filename)
        manifest = z.read('META-INF/MANIFEST.MF').decode('utf-8').replace('\r\n', '\n')
    else:
        manifestname = filename + '/' + 'META-INF/MANIFEST.MF'
        if os.path.isfile(manifestname):
            manifest = open(manifestname, 'r').read().replace('\r\n', '\n')
    if manifest == '':
        return

    if verbose:
        print('Manifest found in "' + filename + '"')

    sourceref = ''
    found = 0
    while True:
        endlinepos = manifest.find('\n')
        line = manifest[0:endlinepos]
        if len(line) == 0:
            break
        if found:
            if line[0] == ' ':
                sourceref += line[1:]
            else:
                break
        if line.find('Eclipse-SourceReferences: ') >= 0:
            sourceref = line[34:]
            found = 1
        manifest = manifest[endlinepos + 1:]
        if len(manifest) == 0:
            break
    if len(sourceref) == 0:
        print('Failure for "' + filename + '":')
        print('  Tag "Eclipse-SourceReferences" not found in META-INF/MANIFEST.MF')
        return

    parts = sourceref.split(';')

    if verbose:
        print('Source reference found:')
        for part in parts:
            print('  ' + part)

    if parts[0].find('pserver:dev.eclipse.org') >= 0:
        print('Failure for "' + filename + '":')
        print('  Outdated source reference "dev.eclipse.org"')
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
    relsrcdir = destdir +  '/' + projdir

    bashscript = '#!/bin/bash\n' +\
    '# Use this script to obtain the source code for "' + filename + '"\n' +\
    'mkdir -p ' + destdir + '\n' +\
    'cd ' + destdir + '\n' +\
    'rm -Rf ' + project + '\n' +\
    'git clone ' + url + '\n' +\
    'cd ' + project + '\n' +\
    'git checkout ' + commit + '\n'
    if execute:
        if verbose:
            os.system(bashscript)
        else:
            subprocess.call(bashscript, shell = True, stdout = open(os.devnull, 'w'), stderr = subprocess.STDOUT)
        if os.path.exists(relsrcdir):
            print('Success for "' + filename + '":')
            print('  Source code is located at "' + relsrcdir + '"')
            if listing:
                os.system('ls -l ' + relsrcdir)
        else:
            print('Failure for "' + filename + '":')
            print('  No source code delivered to "' + relsrcdir + '"')
    else:
        if verbose:
            print()
        print("Script to obtain source code:")
        print(bashscript)
    return

def main(argv):
    parser = argparse.ArgumentParser(prog = 'jar2src.py',
      epilog = 'Parse JAR manifest for location of source code, create script to obtain it and optionally execute script')

    parser.add_argument('filename',
      metavar = 'JAR',
      help = 'file name of a the Java archive to process')
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

    getsourcecode(args.filename, args.verbose, args.execute, args.list)

if __name__ == '__main__':
    main(sys.argv)