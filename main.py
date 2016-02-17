#!/bin/env python3
import argparse
import parse
import os
import gzip
import shutil
from exceptions import *

# defining arguments
argparser = argparse.ArgumentParser(description='Parse dictionary is StarDict to user-specified text based format.\nEach dictionary has to contain three files ifo, dict[.gz], idx[.gz] with the same name.', formatter_class=argparse.RawTextHelpFormatter)
argparser.add_argument('dictDir', help='Directory with dictionaries, other files than *.ifo, *.dict[.gz] *.idx[.gz] will be ignored')
argparser.add_argument('format', nargs='?', default='raw', help='''format of output dictionaries, default is "raw"
 * raw - equivalent to k#r
 * string containing flags separated by exactly one delimiter character (e.g. k#p#s)
Flags:
   k - key
   p - pronunciation
   r - whole record with escaped newlines
   ---------------------------------
   following are empty unless present
   h - HTML
   m - pure nonformatted meaning
   t - phonetic utf-8 string
   g - pango syntax
   ---------------------------------
   following are non-empty only if the dictionary is in pango syntax
   s - tag <small>
   i - tag <i>
   b - tag <b>''')
argparser.add_argument('-r', '--recursive', action='store_true', help='search the specified directory recursively')
argparser.add_argument('--dest', dest='dest', default=os.getcwd(), help='directory where will be dictionaries stored, default is current working directory')
argparser.add_argument('--no-header', dest='header', action='store_false', default=os.getcwd(), help='do not print header to output')

flags=['p', 'r', 'k', 'h', 'm', 't', 'g', 's', 'i', 'b']

#TODO epilog
args=argparser.parse_args()

# check format string
if args.format=='raw':
    args.format='k#r'
    
for x in range(1, len(args.format)-2, 2):
    if args.format[x]!=args.format[x+2]:
        raise BadFormatException('format string inappropriately formatted')
for x in range(0, len(args.format), 2):
    if not args.format[x] in flags:
        raise BadFormatException('format string inappropriately formatted')


def readDir(d):
    parser=parse.Parser(args.format, args.header)
    for x in os.listdir(d):
        f=x.split('.')
        if len(f)==2 and f[1]=='ifo':
            print('Reading %s dictionary.' % f[0])

            dictFile=os.path.join(d, (f[0]+'.dict'))
            idxFile=os.path.join(d, (f[0]+'.idx'))
            dictGz=False
            idxGz=False

            #DICT FILE
            if not os.path.isfile(dictFile):
                if os.path.isfile(dictFile+'.dz'):
                    with gzip.open(dictFile+'.dz', 'rb') as r, open(os.path.join(args.dest, f[0]+'.dict'), 'wb') as w:
                        shutil.copyfileobj(r, w)
                    dictFile=os.path.join(args.dest, f[0]+'.dict')
                    dictGz=True
                else:
                    raise IncompleteDictException('Missing dict file')

            #IDX FILE
            if not os.path.isfile(idxFile):
                if os.path.isfile(idxFile+'.gz'):
                    with gzip.open(idxFile+'.gz', 'rb') as r, open(os.path.join(args.dest, f[0]+'.idx'), 'wb') as w:
                        shutil.copyfileobj(r, w)
                    idxFile=os.path.join(args.dest, f[0]+'.idx')
                    idxGz=True
                else:
                    raise IncompleteDictException('Missing dict file')

            parser.parse(os.path.join(d,x), dictFile, idxFile, os.path.join(args.dest, (f[0]+'.txt')))
            if idxGz:
                os.remove(idxFile)
            if dictGz:
                os.remove(dictFile)

        if args.recursive and os.path.isdir(os.path.join(d, x)):
            readDir(os.path.join(d, x))
                
if not os.path.isdir(args.dest):
    os.makedirs(args.dest)
readDir(args.dictDir)
