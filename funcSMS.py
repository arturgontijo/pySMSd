#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import gammu
import time
from threading import Thread
import traceback

# pySMSd imports
import Vars as v
import funcLOG as fLOG
import funcCMD as fCMD

# SMS DAEMON
smsd = 0

def tryInitSMS():
    
    # Setting up
    fLOG.myPrint('[ SMSd  ]: Setting up...\n')
    fLOG.writeLOG('[ SMSd  ]: Setting up...\n')

    # Start count [5]
    if(v.SMS_TRYSTART_COUNT < v.SMS_TRYSTART_MAX):
        v.SMS_TRYSTART_COUNT += 1
    else:
        if(v.SMS_TRYSTART_FLAG == 'Ok'):
            v.SMS_TRYSTART_FLAG = 'Fail'
            fLOG.updateConfigs()
            # After 3 fails, set the reboot system flag
            v.REBOOT_ENABLE = True
            fLOG.myPrint('[ SMSd  ]: Fail! - Rebooting...!\n')
            fLOG.writeLOG('[ SMSd  ]: Fail! - Rebooting...!\n')
            return
        else:
            fLOG.myPrint('[ SMSd  ]: USB Fail!\n')
            fLOG.writeLOG('[ SMSd  ]: USB Fail!\n')
            v.SMS_FINISHED = True
            return
    
    # Thread to start pySMSd
    thInitSMS = Thread(target = startThSMS)
    thInitSMS.daemon = True
    thInitSMS.start()
    
    while(v.SMS_STARTED):
        m.time.sleep(1)
    
    v.SMS_FINISHED = True
    return

# Start Thread
def startThSMS():
    
    try:
        subprocess.call(['usb_modeswitch','-W','-c','/etc/usb_modeswitch.conf'],stdout=open(os.devnull,'w'),stderr=subprocess.STDOUT)    
        time.sleep(0.5)
        fLOG.myPrint('[ SMSd  ]: usb-modeswitch OK!\n')
        fLOG.writeLOG('[ SMSd  ]: usb-modeswitch OK!\n')
        
        v.SMS_STARTED = initSMS()        
        v.SMS_USBPORT = 0
        while(v.SMS_USBPORT < v.SMS_USBPORT_MAX):
            if(v.SMS_STARTED):
                v.SMS_TRYSTART_COUNT = 0
                if(v.SMS_TRYSTART_FLAG == 'Falhou'):
                    v.SMS_TRYSTART_FLAG = 'Ok'
                    fLOG.updateConfig()
                return
            else:
                s = '[ SMSd  ]: Fail! Waiting...\n'
                fLOG.myPrint(s)
                fLOG.writeLOG(s)
                time.sleep(2)
                s = '[ SMSd  ]: FAIL! Trying port: ttyUSB{0}\n'.format(str(v.SMS_USBPORT))
                fLOG.myPrint(s)
                fLOG.writeLOG(s)
                editGammuConf('/root/.gammurc',v.SMS_USBPORT)
                v.SMS_USBPORT += 1
                
            v.SMS_STARTED = initSMS()
            
        v.SMS_STARTED = False

    except Exception as e:
        s = '[ SMSd  ]: Error (startThSMS) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        print(traceback.format_exc())

    return

def initSMS():
    
    global smsd
    
    smsd = 0
    try:
        # Object for talking with modem
        smsd = gammu.StateMachine()
        smsd.ReadConfig()
        smsd.Init()
        
        s = '[ SMSd  ]: OK!\n'
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
    
        return True
    
    except Exception as e:
        s = '[ SMSd  ]: Error (initSMS) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        
        return False    

def editGammuConf(filename,port):
    
    #[gammu]
    #
    #port = /dev/ttyUSB2
    #model = 
    #connection = at19200
    #synchronizetime = yes
    #logfile = 
    #logformat = nothing
    #use_locking = 
    #gammuloc = 
    
    try: 
        if(os.path.isfile(filename)):
            os.remove(filename)
        
        varconf = []
        varconf.append('[gammu]\n\n')
        varconf.append('port = /dev/ttyUSB{}\n'.format(str(port)))
        varconf.append('model = \n')
        varconf.append('connection = at19200\n')
        varconf.append('synchronizetime = yes\n')
        varconf.append('logfile = \n')
        varconf.append('logformat = nothing\n')
        varconf.append('use_locking = \n')
        varconf.append('gammuloc = \n')
        
        conteudo = ''
        for i in range(0,len(varconf)):
            conteudo += varconf[i]
        
        with open(filename,'w') as myfile:
            myfile.write(conteudo)
                
        return True
    
    except Exception as e:
        s = '[ SMSd  ]: Error (editGammuConf) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)        
        return False 

def getSMSSignal():
    
    try:
        if(not smsd == 0):
            dicSignal = smsd.GetSignalQuality()
            v.SMS_SIGNALQUALITY = '%s%%' % str(dicSignal['SignalPercent'])
        else:
            v.SMS_SIGNALQUALITY = 'Initializing...'
        return v.SMS_SIGNALQUALITY
    except:
        v.SMS_SIGNALQUALITY = 'Modem error!'
        return v.SMS_SIGNALQUALITY
    

def sendSMS(cellnumber,msg):
    
    try:
        # Prepare message data
        # Use first SMSC number stored in modem
        message = {
            'Text': msg,
            'SMSC': {'Location': 1},
            'Number': cellnumber,
        }
        s = '[ SMSd  ]: Sending SMS: %s (len = %s)\n' % (cellnumber,str(len(msg)))
        s += '=======================================================\n'
        s += msg + '\n=======================================================\n'
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        
        # Avoid race condition
        v.SMS_CHECKING =  True

        # Actually send the message
        if(not smsd == 0):
            smsd.SendSMS(message)
            m.time.sleep(2)
        else:
            s = '[ SMSd  ]: Deamon error!\n'
            fLOG.myPrint(s)
            fLOG.writeLOG(s)
            return False
        
        v.SMS_CHECKING =  False
        return True
    
    except Exception as e:
        s = '[ SMSd  ]: Error (sendSMS) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        v.SMS_CHECKING =  False
        return False

def checkSMS():
    
    start = True
    try:
        v.SMS_CHECKING = True
        v.SMS_VALIDMSG = False
        v.SMS_SENT = False

        fLOG.myPrint('[ SMSd  ]: Checking SMS (Signal: %s)\n' % (getSMSSignal()))
        while 1:
            try:
                if start:
                    sms = smsd.GetNextSMS(Start = True, Folder = 0)
                    start = False
                else:
                    sms = smsd.GetNextSMS(Location = sms[0]['Location'], Folder = 0)
            except gammu.ERR_EMPTY:
                break
            
            processSMS(sms)

            smsd.DeleteSMS(Location = sms[0]['Location'], Folder = 0)
        
        #Verifica se tem algum aviso pra enviar, e envia
        if(v.SMS_SENDMSG_FLAG):
            sendSMS(v.SMS_FROM_NUM, v.SMS_SENDMSG_CONTENT)
            v.SMS_SENDMSG_FLAG = False
        
        v.SMS_TRYAGAIN_INIT = False
        v.SMS_CHECKING = False
        return True
            
    except Exception as e:
        s = '[ SMSd  ]: Error (checkSMS) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        v.SMS_CHECKING = False
        v.SMS_STARTED = False
        v.SMS_FINISHED = True
        v.SMS_TRYAGAIN_INIT = True
        return False

def processSMS(sms):
    
    try:        
        # Convert message from unicode to utf-8 and store phone number
        msg_raw = sms[0]['Text'].encode('utf-8')
        num = sms[0]['Number']
        date = sms[0]['DateTime']
        
        # Store number
        v.SMS_FROM_NUM = num
        
        msg = msg_raw.decode('utf-8')
        
        # Uppercase message (to compare)
        msg = msg.upper()
        
        s = '[ SMSd  ]: SMS from: ' + num + '\n'
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        s = '[ SMSd  ]: SMS date: ' + str(date) + '\n'
        fLOG.myPrint(s)
        fLOG.writeLOG(s)      
        s = '[ SMSd  ]: SMS message: \n=======================================================\n' + msg + '\n=======================================================\n'
        fLOG.myPrint(s)
        fLOG.writeLOG(s)

        # Grava no arquivo de LOG de SMS
        data = '[ SMSd  ]: SMS from: ' + num + '\n'
        data += '[ SMSd  ]: SMS date: ' + str(date) + '\n'
        data += '[ SMSd  ]: SMS message: \n=======================================================\n' + msg + '\n=======================================================\n'
        fLOG.gravaLOG(v.LOG_SMS, data)

        length = len(msg)
        l_CMDs = []
        if(num in v.SMS_CELLNUMBERS or num == v.SMS_CELLNUMBER_MASTER):
            
            # Compare the sms date/time with those of the system
            checkSMSdate(str(date))
            
            # Check SMS, line by line (command by command)
            i = 0
            line = []
            while(i < length):
                if(not msg[i] == '\n'):
                    line.append(msg[i])
                else:
                    l_CMDs.append(''.join(line))
                    line = []
                i += 1
            
            # Get the last line
            l_CMDs.append(''.join(line))
            
            # Remove all empty elements
            l_CMDs = filter(None, l_CMDs)
            
            # Process the command list
            if(num in v.SMS_CELLNUMBERS):
                lista_msg = fCMD.processCMD(l_CMDs,'user')
            elif(num == v.CELLNUMBER_MASTER):
                lista_msg = fCMD.processCMD(l_CMDs,'master')

            msg = formatSMStoSend(lista_msg)

            if(msg == ''):
                msg = u'Invalid Command!'
                
            if(not DEBUG):
                sendSMS(num,msg)
            else:
                s = '[ SMSd  ]: SMS to: %s\n' % num
                fLOG.myPrint(s)
                s = '[ SMSd  ]: SMS messge: %s\n' % msg
                fLOG.myPrint(s)
        else:
            s = '[ SMSd  ]: Number not in DB!\n'
            fLOG.myPrint(s)
            fLOG.writeLOG(s)
            
        return True
            
    except Exception as e:
        s = '[ SMSd  ]: Error (processSMS) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        return -1
  
def formatSMStoSend(lst):
    
    msg = ''
    for i in range(len(lst)):
        if(i == len(lst)-1):
            if(len(lst) > 1):
                msg += '--\n'
            msg += lst[i]
        else:
            lst_um = lst[i].split('\n')
            msg += lst_um[0] + '\n'
    return msg
    
def checkSMSdate(sdate):
    
    # 2015-03-03 15:55:05
    date_hour = sdate.split(' ')
    date_full = date_hour[0].split('-')
    hour_full = date_hour[1].split(':')
    
    year = date_full[0]
    month = date_full[1]
    day = date_full[2]
    
    hour = hour_full[0]
    minutes = hour_full[1]
    seconds = hour_full[2]
    
    date = day + '/' + month + '/' + year + ' - ' + hour + ':' + minutes + ':' + seconds
    
    try:
        # Update the variable
        v.SMS_LASTSMS_TIME = date
        
        ret = m.fdata.compareDate(date)
        if(ret < 0):
            s = '[ SMSd  ]: Updating system date/time...\n'
            fLOG.myPrint(s)
            fLOG.writeLOG(s)
            v.SYS_TIME = date
            m.fdata.setDate(date)
        else:
            s = '[ SMSd  ]: System date/time OK!\n'
            fLOG.myPrint(s)
            fLOG.writeLOG(s)
            v.SYS_TIME = m.fdata.getDate()
            
        return True
    
    except Exception as e:
        s = '[ SMSd  ]: Error (checkSMSdate) = %s\n' % (e)
        fLOG.myPrint(s)
        fLOG.writeLOG(s)
        return False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
