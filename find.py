#!/bin/env python3
import re
import os
import queue
import argparse

# defining arguments
argparser = argparse.ArgumentParser(description='Finding tool in StardictDictionaries converted to text format.')
argparser.add_argument('path', help='path to dictionary')
argparser.add_argument('word', help='word you are searching')
argparser.add_argument('field', nargs='?', default=0, help='which field search (e.g. k,r,h...)')
argparser.add_argument('-f', '--full-matching', action='store_true', help='will be searched ^word$')

#TODO epilog
args=argparser.parse_args()

searched=args.word
numberOfFields=-1
delimiter='#'

class BadFormatException(Exception):
    pass

def findLine(line):
    global searched, numberOfFields, delimiter, args
    fields=['']
    escaped=False
    for x in line:
        if escaped:
            escaped=False
            fields[-1]+=x
            continue
        
        if x=='\\':
            escaped=True
            continue
        
        if x==delimiter:
            fields.append('')
            continue

        fields[-1]+=x
    
    if len(fields)!=numberOfFields:
        print(fields)
        raise BadFormatException('Bad format!')

    if args.full_matching and fields[args.field]==searched:
        return fields
    if not args.full_matching and (searched in fields[args.field]):
        return fields
    return None


# tisknout hlavicku pro format, plus nejvetsi zarovnani? Fakt prasarna
# TODO escaping


with open(args.path, 'r') as dict:
    # read headers
    header=dict.readline()
    if header[:12]!='#DICTFORMAT:':
        raise BadFormatException('Bad format!')
    delimiter=header[13]

    headers={}
    for (i,x) in enumerate(header[12:].rstrip().split(delimiter)):
        headers[i]=x
        numberOfFields=len(headers)
        
    try:
        args.field=int(args.field)
    except Exception as e:
        i=0
        while i<len(headers):
            if args.field==headers[i]:
                break
            i+=1

        if i>=len(headers):
            raise BadFormatException("Filed %s not found in the header" % (args.field))
        args.field=i

    # fill the queue
    res=queue.Queue()
    length=[0 for y in range(numberOfFields)]

    for line in dict:
        line=line.rstrip()
        t=findLine(line)

        if t!=None:
            res.put(t)
            for i in range(numberOfFields):
                length[i]=max(length[i], len(t[i]))


    # print the queue
    print('-'*(sum(length)+len(length)*3+1))

    while not res.empty():
        line=res.get()
        print('|', end='')
        for i,rec in enumerate(line):
            print((' {0:<'+ str(length[i]) +'} |').format(rec), end='')   
        print()

    print('-'*(sum(length)+len(length)*3+1))
