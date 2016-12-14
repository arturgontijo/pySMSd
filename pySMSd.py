#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
import time

# pySMSd imports
import Vars as v
import funcSMS as fsms

def main():

	v.SMS_ISRUNNING = True
	# While no errors
	while(v.SMS_ISRUNNING):
		'''
        ==============================================================================
        SMSd BLOCK
        ==============================================================================
        '''
        # If started, check for new SMS (received)
        # If not started (or error), try to initialize it
		if(v.SMS_STARTED):
        	# Check for new SMS (separated thread)
			if(not v.SMS_CHECKING):
				thcheckSMS = Thread(target=fsms.checkSMS)
				thcheckSMS.daemon = True
				thcheckSMS.start()
		else:
			if(v.SMS_TRYAGAIN_INIT and v.SMS_FINISHED):
				v.SMS_FINISHED = False
				thInitSMS = Thread(target=fsms.tryInitSMS)
				thInitSMS.daemon = True
				thInitSMS.start()
				v.SMS_TRYAGAIN_INIT = False
				v.SMS_CHECKING = False

		# If pass 2min, reset SMS_TRYAGAIN_INIT flag
		if(not (v.MAIN_COUNTER % v.MAIN_MINUTO*2)):
			v.SMS_TRYAGAIN_INIT = True

		# Sleep for 5 (MAIN_INTERVAL) seconds
		time.sleep(v.MAIN_INTERVAL)
		v.MAIN_COUNTER += 1



if __name__=="__main__":
    main()