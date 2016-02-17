#!/bin/env python3
import readidx
import os
from exceptions import *
import re

class Parser:
    properties={}
    def __init__(self, dictFormat, header):
        self.dictFormat=dictFormat
        self.delimiter=dictFormat[1]
        self.header=header
        pass

    def parseIfoLine(self, line):
        line=line.rstrip().split("=")
        if len(line)!=2:
            raise BadFormatException("czech-cizi.ifo inappropriately formatted")
        self.properties[line[0]]=line[1]
        return line

    def parse(self, ifo, dictF, idx, txt):
        self.properties={}
        with open(ifo, "r") as r:
            r.readline() # first line is just intro msg
            verN,ver=self.parseIfoLine(r.readline())
            if verN!="version":
                raise BadFormatException("czech-cizi.ifo inappropriately formatted")
            if ver!="2.4.2" and ver!="3.0.0":
                raise BadFormatException("Only stardict version 2.4.2 and 3.0.0 supported")

            for x in r:
                self.parseIfoLine(x)

            if not 'sametypesequence' in self.properties:
                raise NotSupportedFormat("Only dictionaries with specified sametypesequence are supported.")

            supported = ['m', 'g', 'h', 't']

            if not self.properties['sametypesequence'] in supported:
                raise NotSupportedFormat("Dictionaries with sametypesequence=%s are not supported." % (self.properties['sametypesequence']))


        self.idxoffsetbits=32
        if 'idxoffsetbits' in self.properties:
            if self.properties['idxoffsetbits']!='64' and self.properties['idxoffsetbits']!='32':
                raise BadFormatException('Bad value in field idxoffsetbits')

            self.idxoffsetbits=int(self.properties['idxoffsetbits']) # safe, can be 32, 64


        data=os.open(dictF, os.O_RDONLY)
        readidx.startRead(idx, int(self.idxoffsetbits/8)) # in bytes

        if os.path.isfile(txt):
            number=2
            while os.path.isfile(txt[:-4]+str(number)+'.txt'):
                number+=1
            txt=txt[:-4]+str(number)+'.txt'

        with open(txt, 'w') as wDict:
            try:
                if self.header:
                    wDict.write('#DICTFORMAT:%s\n' % (self.dictFormat))

                while True:
                    word,offset,size=readidx.nextRecord()
                    record={}
                    record['r']=os.read(data, size)\
                            .decode('utf-8')
                    record['k']=word

                    # sametypesequence=m,h,t has no other information
                    if self.properties['sametypesequence']=='h':
                        record['h']=record['r']
                    else:
                        record['h']=''

                    if self.properties['sametypesequence']=='m':
                        record['m']=record['r']
                    else:
                        record['m']=''

                    if self.properties['sametypesequence']=='t':
                        record['t']=record['r']
                    else:
                        record['t']=''

                    if self.properties['sametypesequence']=='g':
                        record['g']=record['r']
                    else:
                        record['g']=''

                    record['b']=self.parseTag('b', record['r'])
                    record['i']=self.parseTag('i', record['r'])
                    record['s']=self.parseTag('small', record['r'])

                    for x in range(0, len(self.dictFormat), 2):
                        if self.dictFormat[x] in record:
                            wDict.write(record[self.dictFormat[x]]
                                    .replace('\n', '\\n')\
                                    .replace(self.delimiter, '\\'+self.delimiter))
                        if x+1!=len(self.dictFormat):
                            wDict.write(self.delimiter)

                    wDict.write('\n')
            except StopIteration as e:
                pass

        readidx.stopRead()

    def parseTag(self, tag, text):
        if not self.properties['sametypesequence']=='g':
            return ''

        res=''
        matches=re.findall('<%s>[^<]*</%s>' %(tag, tag), text)
        for x in matches:
            res+=re.sub('<[^>]*>', '', x)
        return res
