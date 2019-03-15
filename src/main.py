#! /usr/bin/python

from optparse import OptionParser
#from matrix import *
#from dfs_example import dfs
import os
from time import *
import sys
from load_data import *
from utils import *
from models_ip import *
from models_ip_weighted import *
from check_sol import *


from subprocess import *

# sys.path.append("../tags/PA2013/src/")
from lottery import *
from models_ip_instability import *
from models_ip_envyfree import *
from models_hooker import *








def main():
    try:
        usage = "usage: %prog [options] DIRNAME"
        parser = OptionParser(usage)
        parser.add_option("-a", "--allsol", action="store_true", dest="allsol", default=False,
                          help="All solutions")
        #parser.add_option("-r", "--rearrange", action="store_true", dest="rearrange_flag", default=False,
        #                  help="Rearrange")
        parser.add_option("-w","--Wmethod", dest="Wmethod", type="string", default="owa", metavar="[identity|owa|powers]",
                          help="The weighting scheme, eg, \"owa\". [default: %default]")
        #parser.add_option("-n","--number", dest="number", type="int", default=10, metavar="NUMBER",
        #                  help="How many tasks/exercises [default: %default]")
        (options, args) = parser.parse_args() # by default it uses sys.argv[1:]
    except getopt.GetoptError:           
        sys.exit("Parsing error in command line options")                     

    if not len(args)==1:
        parser.error("Directory missing")

    dirname=args[0]
    problem=Problem(dirname)
    solutions=model_ip(problem)[1]

    stat = check_sol(solutions,problem,soldirname="sln")
    for st in stat:
        log = ['x']+[model]+[elapsed]+[os.path.basename(dirname)]+st
        print('%s' % ' '.join(map(str, log)))


    if Wmethod not in ["identity","owa", "powers"]:
        sys.exit("Wmethod not recognized")

    start = clock()
    model=model+"-"+Wmethod
    solutions=model_ip_weighted(problem,Wmethod,True, problem.minimax_sol, options.allsol)[1]

    elapsed = (clock() - start)

    stat = check_sol(solutions,problem,soldirname="sln")
    for st in stat:
        log = ['x']+[model]+[elapsed]+[os.path.basename(dirname)]+st
        print('%s' % ' '.join(map(str, log)))

#print '%s' % ' '.join(map(str, solutions[0].solved))


if __name__ == "__main__":
    main()
