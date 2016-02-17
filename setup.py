#!/bin/env python3
from distutils.core import setup, Extension

readidx = Extension('readidx',
       sources = ['readidx.c'])

setup (name = 'ReadBinary',
        version = '1.0',
        description = 'This package parse binary data in files',
        ext_modules = [readidx])
