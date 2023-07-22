# Jar2src
Get source code of Eclipse IDE from installed JAR files

./jar2src.py --help
usage: jar2src.py [-h] [-e] [-l] [-v] JAR

positional arguments:
  JAR            file name of a the Java archive to process

options:
  -h, --help     show this help message and exit
  -e, --execute  execute the generated script to obtain the source code, otherwise only show the script
  -l, --list     list content of the source code directory, if successfully created, has no effect without --execute
  -v, --verbose  show names and texts the program is using

Parse JAR manifest for location of source code, create script to obtain it and optionally execute script