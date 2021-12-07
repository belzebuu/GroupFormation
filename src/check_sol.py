import sys
from collections import defaultdict
import numpy as np
import itertools
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format


def check_all_sols(solutions, problem, soldirname=""):
    num_solutions = len(solutions)
    print("num_solutions: ", num_solutions)
    logs = []
    for sol in solutions:
        log = check_sol(sol, problem, num_solutions, soldirname)
        logs += [log]
        num_solutions = num_solutions-1
    return logs


def check_sol(sol, problem, sol_id, soldirname=""):
    log = []
    unass_students = 0
    members = {}

    #    print(problem.projects)
    projects = defaultdict(list)
    for s in sol.topics:
        projects[(sol.topics[s], sol.teams[s])].append(s)

    for p in problem.projects:
        for t in range(len(problem.projects[p])):
            if p in members:
                members[p].append([x for x in list(sol.topics.keys()) if p ==
                                   sol.topics[x] and t == sol.teams[x]])
            else:
                members[p] = [[x for x in list(sol.topics.keys())
                               if p == sol.topics[x] and t == sol.teams[x]]]

    # students only get projects they ranked
    # for s in problem.std_type:
    #     if s not in sol.topics:
    #         unass_students += 1
    #     elif sol.topics[s] not in list(problem.std_ranks[s].keys()):
    #         print(sol.topics[s], list(problem.std_ranks[s].keys()))
    #         sys.exit("%s student assigned to a project not ranked" % s)

    # group members are assigned to the same teams
    for g in problem.groups:
        for s1 in problem.groups[g]:
            for s2 in problem.groups[g]:
                if s1 in sol.topics and s2 in sol.topics:
                    if (sol.topics[s1] != sol.topics[s2]) or (sol.teams[s1] != sol.teams[s2]):
                        sys.exit("group members assigned in different projects")

    # team creation and cardinality
    nteams = 0
    underfull = 0
    for p in problem.projects:
        for t in range(len(problem.projects[p])):
            nteams += 1
            # print str(len(members[p][t])) +" "+ str(problem.projects[p][t][1])
            assert (len(members[p][t]) <= problem.projects[p][t][1])
            if len(members[p][t]) < problem.projects[p][t][0] and len(members[p][t]) > 0:
                underfull += 1
    # check how many students are not assigned to their area
    counter_area = 0
    for s in problem.std_type:
        if s in sol.topics:
            p = sol.topics[s]
            prj_type = problem.projects[p][0][2]
            if prj_type != problem.std_type[s] and prj_type != "alle":
                counter_area += 1
    # count unstable students
    # unstable = 0
    # for g in problem.groups:
    #     s = problem.groups[g][0]
    #     if s in sol.topics:
    #         rank = problem.std_ranks[s][sol.topics[s]]
    #         for p in list(problem.std_ranks[s].keys()):
    #             if (problem.std_ranks[s][p] < rank):
    #                 for t in range(len(problem.projects[p])):
    #                     if len(members[p][t]) > 0:
    #                         if len(members[p][t])+len(problem.groups[g]) <= problem.projects[p][t][1]:
    #                             print("student " + str(s) + " could go in "+str(p))
    #                             unstable += len(problem.groups[g])
    #                     elif len(problem.groups[g]) >= problem.projects[p][t][0] and (len(problem.groups[g]) <= problem.projects[p][t][1]):
    #                         print("student " + str(s) + " could go in unopened "+str(p))
    #                         unstable += len(problem.groups[g])
    # count classical utility
    # tot_util = 0
    # for s in problem.std_type:
    #     if s in sol.topics:
    #         tot_util += problem.std_ranks[s][sol.topics[s]]
    ############################################################
    # count envy
    # tot_envy = 0
    # for s in problem.std_type:
    #     max_envy = 0
    #     for s1 in problem.std_type:
    #         if s1 != s and s in sol.topics and s1 in sol.topics:
    #             if sol.topics[s1] in problem.std_ranks[s]:
    #                 envy = max(0, problem.std_ranks[s][sol.topics[s]] -
    #                            problem.std_ranks[s][sol.topics[s1]])
    #                 if (envy > max_envy):
    #                     max_envy = envy
    #     tot_envy += max_envy

    # max_rank = 0
    # for s in list(problem.std_ranks.keys()):
    #     if len(problem.std_ranks[s])+1 > max_rank:
    #         max_rank = len(problem.std_ranks[s])+1

# 		max_rank=0
# 		array_ranks={}
# 		grp_ranks={}
# 		for g in problem.groups.keys():
# 			s=problem.groups[g][0] # we consider only first student, the other must have equal prefs
# 			grp_ranks[g]=problem.std_ranks[s]
# 			if len(grp_ranks[g])+1 > max_rank:
# 				max_rank=len(grp_ranks[g])+1
#
# 		for g in problem.groups.keys():
# 			values=map(lambda x: max_rank if x not in grp_ranks[g].keys() else grp_ranks[g][x], problem.projects.keys())
# 			array_ranks[g]=dict(zip(problem.projects.keys(),values))
#
# 		tot_envy1=0
# 		values = map(lambda x: problem.std_ranks[problem.groups[x][0]], problem.groups.keys())
# 		grp_rank = dict(zip(problem.groups.keys(), values))
# 		values = map(lambda x: sol.topics[problem.groups[x][0]], problem.groups.keys())
# 		grp_sln = dict(zip(problem.groups.keys(), values))
#
#
# 		for g in problem.groups:
# 			max_envy=0
# 			for g1 in problem.groups:
# 				if g1 != g:
# 					if grp_sln[g1] in grp_rank[g]:
# 						envy = max(0,grp_rank[g][grp_sln[g]] - array_ranks[g][grp_sln[g1]])
# 						if (envy > max_envy):
# 							max_envy=envy
# 			tot_env1y += max_envy*len(problem.groups[g])
# 		assert (tot_envy1==tot_envy)
    ############################################################
    F_cat, F_num = problem.separate_features()
    nfeats = len(problem.features_orddict)
    order_cols = [x['Variable'] for i, x in problem.features_orddict.items()]
    print(order_cols)
    discrepancy_av = np.empty([len(projects), nfeats])
    discrepancy_min = np.empty([len(projects), nfeats])
    discrepancy_max = np.empty([len(projects), nfeats])
    i = 0
    filename = "%s/sol_%03d" % (soldirname, sol_id)
    with pd.ExcelWriter(filename+'.xlsx') as excel_writer:
        for p in sorted(projects):
            M_num = np.empty((len(projects[p]), len(F_num)))
            M_cat = np.empty((len(projects[p]), len(F_cat)), dtype=np.uintc)
            for j in range(len(projects[p])):
                s = projects[p][j]
                # print([problem.student_details[s][f] for f in F_num])
                M_num[j, :] = np.array([problem.student_details[s][f] for f in F_num])
                M_cat[j, :] = np.array([problem.student_details[s][f+"_rcat"] for f in F_cat])
            
            feat_grp = np.hstack([M_num, M_cat])
            feat_grp_df = pd.DataFrame(data=feat_grp, index=list(range(
                len(projects[p]))), columns=F_num+F_cat)
            #print(feat_grp_df[order_cols])
            print("The features for project {}".format(p))
            print(feat_grp_df[order_cols].to_latex(index=True))
            feat_grp_df[order_cols].to_excel(excel_writer, sheet_name='grp_'+str(p))

            # Dss = [np.linalg.norm(M_num[u, :]-M_num[v, :], 1)
            #      for (u, v) in itertools.combinations(range(len(projects[p])), 2)]
            # print("The norm L_1 of the pairwise discrepancies:",Dss)
            pairwise = np.vstack([np.absolute(M_num[u, :]-M_num[v, :])
                                for (u, v) in itertools.combinations(range(len(projects[p])), 2)])
            counts = np.apply_along_axis(lambda a: len(np.unique(a)), 0, M_cat)
            discrepancy_min[i, :] = np.hstack([np.min(pairwise, axis=0), counts])
            discrepancy_av[i, :] = np.hstack([np.average(pairwise, axis=0), counts])
            discrepancy_max[i, :] = np.hstack([np.max(pairwise, axis=0), counts])
            i += 1
        # print("The range: ", discrepancy_min,  discrepancy_max, sep="\n")
        summary = np.vstack([np.min(discrepancy_min, axis=0),
                            # np.average(discrepancy_av,axis=0),
                            np.max(discrepancy_max, axis=0)])
        
        sum_df = pd.DataFrame(data=summary, index=["min", "max"], columns=F_num+F_cat)
        #print(sum_df[order_cols])
        print(sum_df[order_cols].to_latex(index=True))
        sum_df[order_cols].to_excel(excel_writer, sheet_name='overall')
    
    # print("Intra: ", np.min(discrepancy_min, axis=0),
    #      #
    #      np.max(discrepancy_max, axis=0), sep="\n")
    # print("Inter accumulated: min: {0:.3f} average: {1:.3f}".format(np.max(np.absolute(discrepancy_min-np.min(discrepancy_min))),
    #                                                    np.sum(np.absolute(discrepancy_av-np.average(discrepancy_av)))))
    # print("Intra : min: {0:.3f} max: {1:.3f}".format(np.max(np.absolute(discrepancy_min-np.min(discrepancy_min))),
    #                                                    np.sum(np.absolute(discrepancy_av-np.average(discrepancy_av)))))
    # raise SystemExit
    ############################################################
    # if it passed all previous tests then solution is feasible
    print("feasible solution")
    print("Numb. of students: " + str(len(problem.std_type)))
    print("Numb. of groups: " + str(len(problem.groups)))
    print("Numb. of topics: " + str(len(problem.projects)))
    print("\nNumb. of unassigned students: " + str(unass_students))
    print("Numb. of underfull teams: " + str(underfull))
    print("Students assigned outside of their area: ", counter_area)
    #print("\nNumb. of unstable: " + str(unstable))
    #print("Tot. util: " + str(tot_util))
    #print("Tot. envy: " + str(tot_envy))

    log += [len(problem.std_type)]
    log += [nteams]
    log += [len(problem.projects)]
    log += [unass_students]
    log += [underfull]
    #log += [unstable]
    #log += [tot_util]
    #log += [tot_envy]

    ############################################
    # std_group = {x: y for y in problem.groups for x in problem.groups[y]}
    # counter = [0] * (max_rank+1)

    # for s in problem.std_values:
    #     if s in sol.topics:  # used in the paper:  and len(problem.groups[std_group[s]])==3:
    #         rank = problem.std_ranks[s][sol.topics[s]]
    #         counter[rank] += 1

    # s = "\n"
    # for i in range(1, max_rank + 1):
    #     out = str(i) + ". prioritet: " + str(counter[i])
    #     s = s + out + "\n"
    #     log += [counter[i]]
    # print(s)

    ############################################
    if soldirname != "":                
        try:
            f = open(filename+".txt", "w")
        except OSError:
            print(soldirname +" not existing")
            raise SystemError
        for s in problem.std_type:
            if s in sol.topics:
                if sol.teams[s] == 0 and len(problem.projects[sol.topics[s]]) == 1:
                    f.write(s + "\t" + str(sol.topics[s]) + "\t" + str(problem.std_type[s]) + "\n")
                else:
                    f.write(s + "\t" + str(sol.topics[s]) +
                            "\t" + 'abcdefghi'[sol.teams[s]] +"\t" + str(problem.std_type[s])+ "\n")
        #with pd.ExcelWriter('output.xlsx') as writer:  
        

    log += sol.solved
    return log
