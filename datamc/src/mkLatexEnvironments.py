#!/usr/bin/env python

import sys,re,os
from optparse import OptionParser
sys.path.append('../common/')
from toolkit import *

mp = OptionParser()
mp.add_option('-s','--size',default=0.95,type='float')
mp.add_option('-b','--block',default=-1,type='int')
mp.add_option('-r','--replace',default=[],type='str',action='callback',callback=optsplitlist)
opts,args = mp.parse_args()


for ai,a in enumerate(args):
    amod = a
    for replacement in opts.replace:
        amod = amod.replace(replacement[0],replacement[1])
    if ai==0 or opts.block==-1: print "\\begin{figure}[htbf]\\centering"
    if opts.block>1: 
        print "\t\\begin{minipage}[t]{%.3f\\textwidth}\\centering"%(0.99/float(opts.block)*opts.size)
        print "\t",
    print "\t\\includegraphics[width=%.3f\\textwidth]{%s}"%(0.999,amod)
    if opts.block>1:
        print "\t\\end{minipage}",
        if (ai+1)%opts.block==0 and not ai==len(args)-1: print "\\vskip 0.5em"
        elif not ai==len(args)-1: print "\\hspace{0.3cm}"
        else: print
    if ai==len(args)-1 or opts.block==-1: 
        print "\t\\caption{}\n\t\\label{}"
        print "\\end{figure}"
            
