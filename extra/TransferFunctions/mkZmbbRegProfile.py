#!/usr/bin/env python

import sys,os,json,re,glob
from optparse import OptionParser,OptionGroup
from array import array
basepath=os.path.split(os.path.abspath(__file__))[0]
sys.path.append(basepath+'/../../common/')

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv

from write_cuts import *
from toolkit import *
from main import main
from math import *

global paves
paves = []

f = TFile.Open("../largefiles/flatZ/
