#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

# pySMSd imports
import Vars as v
import funcLOG as fLOG
import funcCMD as fCMD

def processCMD(lst, sentby):

	msg = ''

	s = 'Commands received:'
	fLOG.myPrint(s)
	fLOG.writeLOG(s)
	for cmd in lst:
		fLOG.myPrint(cmd)
		fLOG.writeLOG(cmd)

		# Do your comparisons here:
		# e.g:	if(cmd == 'GET TIME'):
		#			msg = getSysTime()

	return msg

# Get system time (just test)
def getSysTime():
    
    t = float(subprocess.check_output(['/bin/date'], shell=True)[:-1])
    return str(t)