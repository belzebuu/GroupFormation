#! /usr/bin/python

import getopt
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








def main(argv):

	try:
		opts, args = getopt.getopt(argv, "hagd:m:T:W:", ["help", "dir=", "model=", "Tau=", "Wmethod=", "[allsol]", "nogroups" ])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	if (len(opts)<2):
		usage();
	Tau=-1
	Wmethod=""
	allsol=False
	group_reg = True
	mallowed=[1,2,"greedy","amortizedgreedy",\
			"minimaxcpset","minimaxcpint", "lexcpint","lexcpset",\
			"minimax","weighted","leximin","envyfree","instability",\
			"instab_leximin","hooker","instab_hooker","instab_weighted","minimax_weighted","minimax_instab_weighted",\
			"greedy_max","minimax_greedy_max","instab_greedy_max","minimax_instab_greedy_max"]
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-d", "--dir"):
			dirname = arg
		elif opt in ("-T", "--Tau"):
			Tau = int(arg)
		elif opt in ("-W", "--Wmethod"):
			Wmethod = arg
		elif opt in ("-a", "--allsol"):
			allsol = True
		elif opt in ("-g", "--nogroups"):
			group_reg = False
		elif opt in ("-m", "--model"):
			if arg in mallowed:
				model = arg
			else:
				print("\nmodel must be one of ",mallowed)
				usage()
		else:
			print(opt+" Not recognised\n");
			usage();

	problem=Problem(projects=read_projects(dirname),
					std_values=read_students(dirname)[0],
					std_ranks=read_students(dirname)[1],
					groups=read_groups(dirname, group_reg)[0],
					std_type=read_groups(dirname, group_reg)[1],
					minimax_sol = minimax_sol(dirname),
					valid_prjtype = valid_prjtype(dirname),
					restrictions=read_restrictions(dirname)
					)


	if model in ["weighted","instab_weighted","minimax_weighted","minimax_instab_weighted"]:
		if Wmethod not in ["identity","owa", "powers"]:
			print("set Wmethod\n")
			usage()

	if model in ["hooker","instab_hooker"]:
		if Tau<0:
			print("set Tau")
			usage()

	start = clock()
	if model==1:
		solutions=model1(problem)
	elif model==2:
		solutions=model2(problem)
	elif model=="minimax":
		solutions=model_ip(problem)[1]
	elif model=="leximin":
		solutions=lex_ip_procedure(problem,False,False)
	elif model=="instab_leximin":
		solutions=lex_ip_procedure(problem,False,True)
	elif model=="greedy_max":
    		solutions=greedy_maximum_matching_ip_procedure(problem,False,False)
	elif model=="minimax_greedy_max":
    		solutions=greedy_maximum_matching_ip_procedure(problem,True,False)
	elif model=="instab_greedy_max":
    		solutions=greedy_maximum_matching_ip_procedure(problem,False,True)
	elif model=="minimax_instab_greedy_max":
    		solutions=greedy_maximum_matching_ip_procedure(problem,True,True)
	elif model=="hooker":
		model=model+"-"+str(Tau)
		solutions=model_hooker(problem,Tau,False)
	elif model=="instab_hooker":
		model=model+"-"+str(Tau)
		solutions=model_hooker(problem,Tau,True)
	elif model=="envyfree":
		solutions=model_ip_envy(problem)[1]
	elif model=="instability":
		solutions=model_ip_instability(problem)[1]
	elif model=="greedy":
		solutions=greedy(dirname)
	elif model=="amortizedgreedy":
		solutions=repeated_random_greedy(dirname,problem)
	elif model=="weighted":
		#solutions=read_from_zimpl(problem)
		model=model+"-"+Wmethod
		solutions=model_ip_weighted(problem,Wmethod,False,-1,allsol)[1]
	elif model=="instab_weighted":
		#solutions=read_from_zimpl(problem)
		model=model+"-"+Wmethod
		solutions=model_ip_weighted(problem,Wmethod,True,-1,allsol)[1]
	elif model=="minimax_weighted":
		#solutions=read_from_zimpl(problem)
		model=model+"-"+Wmethod
		solutions=model_ip_weighted(problem,Wmethod, False, problem.minimax_sol,allsol)[1]
	elif model=="minimax_instab_weighted":
		#solutions=read_from_zimpl(problem)
		model=model+"-"+Wmethod
		solutions=model_ip_weighted(problem,Wmethod,True, problem.minimax_sol, allsol)[1]
	elif model=="minimaxcpint":
		cp_model=cp_model_int
		transform_sol=transform_sol_std
		solutions=minimax_cp_procedure(problem, cp_model, transform_sol)
	elif model=="lexcpint":
		cp_model=cp_model_int
		transform_sol=transform_sol_std
		solutions=lex_cp_procedure(problem, cp_model, transform_sol)
	elif model=="minimaxcpset":
		cp_model=cp_model_set
		transform_sol=transform_sol_grp
		solutions=minimax_cp_procedure(problem, cp_model, transform_sol)
	elif model=="lexcpset":
		#solutions=lex_step(problem,20,2,2)
		cp_model=cp_model_set
		transform_sol=transform_sol_grp
		solutions=lex_cp_procedure(problem, cp_model, transform_sol)
	elapsed = (clock() - start)

	stat = check_sol(solutions,problem,soldirname="sln")
	for st in stat:
		log = ['x']+[model]+[elapsed]+[os.path.basename(dirname)]+st
		print('%s' % ' '.join(map(str, log)))

	#print '%s' % ' '.join(map(str, solutions[0].solved))

def usage():
	print("\n");
	print("Usage: [\"--help\", \"--dir=\" \"--model=\" \"--Tau=\"]\n");
	sys.exit(1);


if __name__ == "__main__":
	main(sys.argv[1:])
