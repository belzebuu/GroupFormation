#! /usr/bin/python

from optparse import OptionParser
import os
from time import *
import sys
from load_data import *
from utils import *
from models_ip_ext import *
from check_sol import *


from subprocess import *



def main():

    usage = "usage: %prog [options] DIRNAME"
    parser = OptionParser(usage)
    
    parser.add_option("-g", "--groups", dest="groups", type="string", default="post",
                      metavar="[pre|post]", help="Whether groups are formed pre or post [default: %default]")
   
    (options, args) = parser.parse_args()  # by default it uses sys.argv[1:]

    if not len(args) == 1:
        parser.error("Directory missing")

    dirname = args[0]
    problem = Problem(dirname)

    solutions = model_ip_ext(problem, options)
    stat = check_all_sols(solutions, problem, soldirname="sln")

    model = "discrepancy"
    for st in stat:
        log = ['x']+[model]+solutions[0].solved+[os.path.basename(dirname)]+st
        print('%s' % ' '.join(map(str, log)))



if __name__ == "__main__":
    main()
