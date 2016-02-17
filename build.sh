#!/bin/env sh
# uncomment to rebuild c module
#./setup.py build
#`cp build/lib*/* .`

# obtain test data
./data/get
./main.py -r --dest res data/ raw
./main.py -r --dest res data/ s#s#h#i#k#r
