#!/usr/bin/env python

import sys

tempargv = sys.argv[:]
sys.argv = []
import ROOT
from ROOT import *
sys.argv = tempargv


# PRINTING #########################################################################################
def l1(text):
	print blue+'\n+ %s'%(text)+plain
def l2(text):
	print purple+'  ++ %s'%(text)+plain
def l3(text):
	print plain+'  ++++ %s'%(text)+plain

# COLORS ########################################################################################## 
red 	= "\033[0;31m"
green	= "\033[0;32m"
yellow	= "\033[0;33m"
blue	= "\033[0;34m"
purple	= "\033[0;35m"
cyan	= "\033[0;36m"
Red		= "\033[1;31m"
Green	= "\033[1;32m"
Yellow	= "\033[1;33m"
Blue	= "\033[1;34m"
Purple	= "\033[1;35m"
Cyan	= "\033[1;36m"
plain	= "\033[m"

# ACCESS FILE CONTENT ##############################################################################
def filecontent(fname):
	f = file(fname,'r')
	content = f.read()
	f.close()
	return content

# RUN inside ROOT ##################################################################################
def inroot(cmd):
	gROOT.ProcessLineSync(cmd)

# SPLIT COMMA SEPARATED OPTION LIST ################################################################
def optsplitlist(option,opt,value,parser):
	if ';' in value: setattr(parser.values, option.dest, [x.split(';') for x in value.split(',')])
	else: setattr(parser.values, option.dest, [value.split(',')])
def optsplit(option,opt,value,parser):
	setattr(parser.values, option.dest, value.split(','))
