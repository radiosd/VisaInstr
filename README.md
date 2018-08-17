VisaInstr
=========

A package for access and control of instrument using pyvisa.  The PlutoSdr file defines a class for control of 
the hardware.  There is a 2 tone DDS generator built into the Tx firmware and there is a separate file and
class used to define the control of that.  An instance of PlutoSdr automatically creates the DDS 

Getting Started
---------------
Dependancies: pyvisa, changeExt
pyvisa
 - installation is platform dependent
changeExt
 - clone from https://github.com/radiosd/rsdLib.git
 - use setup.py to install

Installation of VisaInstr is via the standard python setup.py install.

Instruments Supported
---------------------
These have varying levels of control, essentially sufficient for my measurement needs. 
 - Tennma PSU (USB using virtual comm port)
