#! /usr/bin/python

import argparse
import os
from time import *
import yaml
from prensio.load_data import *
from prensio.utils import *
from prensio.models_ip_ext import *
from prensio.check_sol import *
from pathlib import Path

from subprocess import *
import textwrap
import logging_config

def main():
    s = textwrap.dedent("""\
                        Example:
                        python3 src/main.py -m data/example/ | tee log.txt
                        """)
    parser = argparse.ArgumentParser(description='Exam scheduler.', epilog=s)
    parser.add_argument("-m", "--disallow_merging_groups", dest="disallow_merging_groups", action='store_true', help="To disallow merging of pre-made groups in teams [default: %(default)s]")
    parser.add_argument("-t", "--time_limit", dest="time_limit", action='store', type=int, default=100, help="Time limit [default: %(default)s]")
    parser.add_argument('-L','--logging_dir', metavar='logdir', dest='logdirname', type=Path,
                        action='store', nargs='?', required=False, default=Path.cwd()/"log",
                        help='the name of the directory where to put log files. It checks for existance. [default: %(default)s]')
    #parser.add_argument("-l", "--logging_file", nargs='?', dest="logging_file", metavar="PATH", default=None, type=Path, help="The file where the logging is sent [default: stderr]")
    parser.add_argument("-x", "--latex", dest="latex", action='store_true', help="Include LaTeX output [default: %(default)s]")   
    parser.add_argument('-s','--sol_dir', metavar='soldir', dest='soldirname', type=Path,
                        action='store', nargs='?', required=False, default=Path.cwd()/"sln",
                        help='the name of the directory where to put solution files. It checks for existance. [default: %(default)s]')
    parser.add_argument("input_directory", help="The directory of the input data", type=Path)
    args = parser.parse_args()

    if not args.logdirname.exists():
        os.makedirs(args.logdirname, mode = 0o777)
    if not args.soldirname.exists():
        os.makedirs(args.soldirname, mode = 0o777)

    # Not working
    #if args.logging_file is not None:
    #    # Set Logging level to INFO.
    #    # Argument `filename` can be omitted to output -> stderr
    #    logger.basicConfig(filename=args.logging_file, level=logging.INFO)
    #else:
    #    logger.basicConfig(level=logging.INFO)
    #    #logging.basicConfig(level=logging.ERROR)

    logger.info(f'\n{yaml.dump(args)}')
    ###


    problem = Problem(args.input_directory)

    solutions = model_ip_ext(problem, args.disallow_merging_groups, args.logdirname, args.time_limit)
    check_all_sols(solutions, problem, soldirname=args.soldirname, latex=args.latex)
    
       



if __name__ == "__main__":
    import logging
    logger = logging.getLogger("main")
    main()
