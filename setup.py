#!usr/bin/env python
"""
    setup for code to access and control of instruments via pyvisa
    
                                                        rgr17Aug18
"""

from distutils.core import setup

VERSION_FILE = 'VisaInstr/version.py'
# read version and other information from the package
version = {}
with open(VERSION_FILE) as fin:
    exec(fin.read(), version)

setup(name='VisaInstr',
      version = version['__version__'],
      description = \
         'The library package for access and control of instruments via pyvisa',
      author = 'Richard Ranson',
      scripts = [],   # add name(s) of script(s)
      packages = ['VisaInstr']   # add name(s) of package(s)
      )

# I'm sure there is more to add, but for now ok to install packaged and scripts
