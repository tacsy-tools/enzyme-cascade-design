#!/usr/bin/python

import argparse
import os
# make sure that out directory exists
if not os.path.exists("./out"): os.makedirs("./out")
# get path to home directory
HOME = os.getenv("HOME")
import subprocess
import sys
# set path to libmod
sys.path.insert(0, HOME + "/local/Mod/lib64")
from mod import *

# create command line argument parser object
parser = argparse.ArgumentParser()

# define command line argument --smi
parser.add_argument('-e', '--ext',
                    action = 'store',
                    help = "specify rule file extension",
                    default = '.gml',
                    type = str)
parser.add_argument('-d', '--dir',
                    action = 'store',
                    help = "specify directory with rule files",
                    default = './',
                    type = str)

# parse command line
args = parser.parse_args()

for file in sorted(list(filter(lambda x: x.endswith(args.ext), os.listdir(args.dir)))):
    print(file) 
    ruleGML(file)

post.summarySection("DPO Diagramms of Rule(s)")
for r in inputRules:
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    r.print(p)

post.flushCommands()
subprocess.run([HOME + "/local/Mod/bin/mod_post"])
