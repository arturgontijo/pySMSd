#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import datetime

# pySMSd imports
import Vars as v
import pySMSd as m

# Console print (debug) 
def myPrint(s):
    
    s = u'[%s]%s' %  (getDate(),s)
    sys.stdout.write(s.encode('utf-8'))
    sys.stdout.flush()

# Write to LOG file
def writeLOG(s):
    
    try:
        s = '[%s]%s' % (getDate(),s)
        with codecs.open(v.LOG_FILE,'a+','utf-8') as myfile:
            myfile.write(s)
        
    except Exception as e:
        s = '[  LOG  ]: Error (baseLOG): %s\n' % (e)
        myPrint(s)
    
    return

def writeFile(filename, s):
    
    try:
        with codecs.open(filename,'a+','utf-8') as myfile:
            myfile.write(s)
            
    except Exception as e:
        s = '[  LOG  ]: Error (writeFile) = %s\n' % (e)
        myPrint(s)
    return

def updateConfig():
    
    try:
        with codecs.open(v.CONFIG_FILE,'a+','utf-8') as myfile:
            s = [ 'CONF_XXX:%s' % (v.CONFIG_FILE),
                  'CONF_YYY:%s' % (v.CONFIG_FILE)
                  ]
            myfile.writelines(s)
            
    except Exception as e:
        s = '[  LOG  ]: Error (updateConfig) = %s\n' % (e)
        myPrint(s)
    return

def getDate():
    
    data_hora = datetime.datetime.now()
    return data_hora.strftime('%d/%m/%Y - %H:%M:%S')
