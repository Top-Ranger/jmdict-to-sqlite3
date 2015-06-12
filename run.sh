#!/bin/sh

#Remove database if already existing
if [ -e "JMDict.sqlite3" ]
then
    echo Removing old database
    rm JMDict.sqlite3
fi

python3 -OO jmdict-to-sqlite3.py JMdict JMDict.sqlite3
