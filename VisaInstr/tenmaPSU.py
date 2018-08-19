# -*- coding: utf-8 -*-
"""
visa control of Tenma PSU
Just basic functionality needed for turning things on/off
Also just the single channel 72-2550 model

Unfortunately NOT a standard visa instrument:
    commands are upper case only
    write must not have a terminator
    read is terminated by \0 and so in python 3
    return values are b'' (byte arrays) not str

                                                          rgr02jul18
"""
import logging

import warnings
from time import sleep
from visa import constants as VC

class TenmaPSU(object):
    def __init__(self,  name='Tenam2550', comm=25): 
        """Encapsulation of commands for FA type code masthead devices"""
        self.name = name
        self.address = comm        # 25 is the lab PC comm port
        self.resource_name = 'ASRL{:n}'.format(comm)
        self.serial = None
        self.settling_time = 0.2   # some commands need time to take effect
        # some items to hold info to hep debug commands 
        self.lastCmd = ''
        self.lastRead = []
        self.flushed = []

    def __repr__(self):
        return 'PSU {:s},{:d}'.format(self.name, self.address)

    def _write(self, message):
        """write the message to the device"""
        # clear up any left over output
        if self.serial.bytes_in_buffer>0:
            self.flushed = self.__read_all()
        self.lastCmd = message
        logging.debug('>> '+message)
        self.serial.write(message.upper(), termination=0)

    def _read(self):
        """read the message from the device,'' if nothing to read"""
        self.lastRead = self.__read_all()
        if len(self.lastRead)==0:
            return ''    # avoid time out error if there is nothing to read
        if len(self.lastRead)>1:
            warnings.warn('unexpected additional return values')
        # just return the value part, can test lastRead to find out more
        ans = self.lastRead[0][0]
        logging.debug('<< '+str(ans))
        return ans

    def __read_all(self):
        # from stack overflow, clear the device keeping read buffer
        handle = self.serial
        data = []
        with handle.ignore_warning(VC.VI_SUCCESS_DEV_NPRESENT, 
                                   VC.VI_SUCCESS_MAX_CNT):
            while handle.bytes_in_buffer>0:
                data.append(handle.visalib.read(handle.session, 
                            handle.bytes_in_buffer)) 
        return data

    def _returnValue(self, value, as_float):
        """optionally convert the string as a float"""
        return float(value) if as_float else value

    def connect(self,vi_resource_manager):
        """connect the device using the visa resource manager"""
        serial = vi_resource_manager.\
                    get_instrument(self.resource_name)
        serial.baud_rate = 9600
        serial.query_delay = 0.05    # 50 mS needed for reliable query
        self.serial = serial
        self.__read_all()   # was self.serial.clear() but unavailable in linux?

    def disconnect(self):
        """disconnect and close the serial resource"""
        self.serial.close()
        self.serial = None

    def query(self, message, delay=None):
        """send a command and receive the reply"""
        # the default delay is obtained from the serial port
        self._write(message)
        delay = self.serial.query_delay if delay is None else delay
        if delay > 0.0:
            sleep(delay)
        return self._read()

    def idn(self):
        """the GP-IB standard idenfification test"""
        return self.query('*IDN?')

    def on(self):
        """turn psu on, uses a mechanical switch so need a pause"""
        logging.info('psu on')
        self._write('OUT1')
        sleep(self.settling_time)

    def off(self):
        """turn psu off, uses a mechanical switch so need a pause"""
        logging.info('psu off')
        self._write('OUT0')
        sleep(self.settling_time)

    def setVoltage(self, v):
        """set the voltage output limit in volts"""
        cmd_str = 'VSET1:{:2.2f}'.format(v)
        self._write(cmd_str)
        sleep(self.settling_time)

    def getVoltage(self, by_value=False):
        """return the set voltage limit in volts"""
        # default is a string, use True to return an int
        return self._returnValue(self.query('VSET1?'), by_value)

    def readVoltage(self, by_value=False):
        """return the actual voltage output in volts"""
        # default is a string, use True to return an int
        return self._returnValue(self.query('VOUT1?'), by_value)

    def setCurrent(self, i):
        """set the current output limit in amps"""
        if i>2:
            warnings.warn('current is set in amps, max=2')
            return
        cmd_str = 'ISET1:{:2.3f}'.format(i)
        self._write(cmd_str)
        sleep(self.settling_time)

    def getCurrent(self, by_value=False):
        """return the set current limit in amps"""
        # default is a string, use True to return an int
        return self._returnValue(self.query('ISET1?'), by_value)

    def readCurrent(self, by_value=False):
        """return the actual current output in amps"""
        # default is a string, use True to return an int
        return self._returnValue(self.query('IOUT1?'), by_value)

if __name__=='__main__':  
    from os import path, sys
    from time import strftime

    logging.basicConfig(
        format='%(module)-12s.%(funcName)-12s:%(levelname)s - %(message)s',
        stream=sys.stdout, level=logging.DEBUG)
    logging.debug('start')
    
    import visa
    psu = TenmaPSU()
    visa.log_to_screen(logging.INFO)
    rm = visa.ResourceManager()
    psu.connect(rm)
    logging.debug('connected')
    # not clear how to test without an actual device set 28v and 0.123mA
    # current threshold then flip on read I and V and flip off
    pause = 0.1
    psu.off()
    psu.setVoltage(28.)
    psu.setCurrent(0.123)
    psu.on()
    vv = psu.getVoltage(True)
    assert vv == 28.00
    print('voltage set', vv)
    ii = psu.getCurrent()
    print('current limit', ii)
