# Jar2src

## Purpose
Get source code of Eclipse IDE from installed JAR files

## Command line options
```bash
jar2src.py --help
```
```
usage: jar2src.py [-h] [-c] [-e] [-l] [-v] JAR

positional arguments:
  JAR             file name of a the Java archive to process

options:
  -h, --help      show this help message and exit
  -c, --colorify  colorify the output to differently mark success, warning and failure
  -e, --execute   execute the generated script to obtain the source code, otherwise only show the script
  -l, --list      list content of the source code directory, if successfully created, has no effect without --execute
  -v, --verbose   show names and texts the program is using

Parse JAR manifest for location of source code, create script to obtain it and optionally execute script
```
## Examples how to use the software

### Generate bash script, only show, do not execute it
```bash
cd ~/Download/eclipse-installer/plugins/
jar2src.py org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar
```
```
Script to obtain source code:
```
```bash
#!/bin/bash
# Use this script to obtain the source code for "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar"
mkdir -p org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar.srcdir
cd org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar.srcdir
rm -Rf ecf
git clone https://github.com/eclipse/ecf.git
cd ecf
git checkout 3e6a22b424f5ce0925abb3f8ea50c714a6f81628
```
### Generate bash script, silently execute it in background
```bash
jar2src.py -e org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar
```
```
Success for "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar":
  Source code is located at "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar.srcdir/ecf/providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient5/src/org/eclipse/ecf/provider/filetransfer/httpclient5"
```
### Generate bash script, execute it in verbose mode and list the content of the created source code directory
```bash
jar2src.py -e -l -v org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar
```
```
Manifest found in "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar"
Source reference found:
  http://git.eclipse.org/gitroot/ecf/org.eclipse.ecf.git/providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient5
  path="providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient5"
  commitId=3e6a22b424f5ce0925abb3f8ea50c714a6f81628
Cloning into 'ecf'...
remote: Enumerating objects: 164281, done.
remote: Counting objects: 100% (1634/1634), done.
remote: Compressing objects: 100% (629/629), done.
remote: Total 164281 (delta 757), reused 1520 (delta 697), pack-reused 162647
Receiving objects: 100% (164281/164281), 56.76 MiB | 6.67 MiB/s, done.
Resolving deltas: 100% (70867/70867), done.
Note: switching to '3e6a22b424f5ce0925abb3f8ea50c714a6f81628'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at 3e6a22b42 Merge pull request #39 from mdaloia/issue-27-sort-certs
Success for "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar":
  Source code is located at "org.eclipse.ecf.provider.filetransfer.httpclient5_1.1.0.v20230423-0417.jar.srcdir/ecf/providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient5/src/org/eclipse/ecf/provider/filetransfer/httpclient5"
total 68
-rw-rw-r-- 1 carsten carsten  2974 Jul 22 11:45 HttpClientBrowseFileTransferFactory.java
-rw-rw-r-- 1 carsten carsten 14471 Jul 22 11:45 HttpClientFileSystemBrowser.java
-rw-rw-r-- 1 carsten carsten  2136 Jul 22 11:45 HttpClientOptions.java
-rw-rw-r-- 1 carsten carsten  1144 Jul 22 11:45 HttpClientRetrieveFileTransferFactory.java
-rw-rw-r-- 1 carsten carsten 38519 Jul 22 11:45 HttpClientRetrieveFileTransfer.java
```
### Generate bash script, silently execute it in background, colorify output
```bash
jar2src.py -ce org.eclipse.equinox.p2.publisher.eclipse_1.5.0.v20230330-1254.jar
```
<img src="/img/Colorified-jar2src-output.png" alt="Example of a colorified output line">

```
Source code is located at "org.eclipse.equinox.p2.publisher.eclipse_1.5.0.v20230330-1254.jar.srcdir/p2/bundles/org.eclipse.equinox.p2.publisher.eclipse/src/org/eclipse/equinox/p2/publisher/eclipse"
```
