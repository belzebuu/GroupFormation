import sys
import os
from collections import defaultdict
import numpy as np
import itertools
import pandas as pd
import textwrap
import subprocess
from pathlib import Path

pd.options.display.float_format = "{:,.2f}".format

import logging
logger = logging.getLogger("postprocessing")

def check_all_sols(solutions, problem, soldirname, latex = False):
    num_solutions = len(solutions)
    logger.info(f"Num solutions: {num_solutions}")
    logs = []
    for sol in solutions:
        log=[problem.name, sol.solved]
        log += check_sol(sol, problem, num_solutions, soldirname, latex)
        logs += [log]
        num_solutions = num_solutions-1
    report=pd.DataFrame(logs,columns=["Instance","Time [s]","Students","Teams","Unassigned","Underfull","Mistyped","Feasible"])
    logger.info(f'\n{report.to_string(index=True)}')
    return 


def check_sol(sol, problem, sol_id, soldirname: Path, latex=False):

    filename = "sol_%03d" % sol_id
    filepath = soldirname / filename

    excel_writer = pd.ExcelWriter(filepath.with_suffix('.xlsx')) 

    ############################################
    if soldirname != "":                
        with open(filepath.with_suffix("_sol.txt"), "w") as fh:
            for s in problem.std_type:
                if s in sol.topics:
                    if sol.teams[s] == 0 and len(problem.projects[sol.topics[s]]) == 1:
                        fh.write(s + "\t" + str(sol.topics[s]) + "\t" + str(problem.std_type[s]) + "\n")
                    else:
                        fh.write(s + "\t" + str(sol.topics[s]) +
                                "\t" + 'abcdefghi'[sol.teams[s]] +"\t" + str(problem.std_type[s])+ "\n")
            #with pd.ExcelWriter('output.xlsx') as writer:  
    
    students = pd.DataFrame.from_dict(dict(problem.student_details), orient='index')    
    students.set_index("student_id")
    
    students["topics"]=None
    students["teams"]=None
    for index, row in students.iterrows():
        if index in sol.topics:
            if sol.teams[index] == 0 and len(problem.projects[sol.topics[index]]) == 1:
                students.loc[index,"topics"]=sol.topics[index]
                students.loc[index,"teams"]=sol.teams[index]
            else:
                students.loc[index,"topics"]=sol.topics[index]
                students.loc[index,"teams"]=sol.teams[index]
    students.sort_values(by=['topics', 'teams'],inplace=True)
    students.to_markdown(filepath+"_sol.md")
    students.to_excel(excel_writer, sheet_name='assignment')    
    ############################################

    log = []
    members = {}
    unass_students=0
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
        else:
            unass_students+=1
    
    # arrived til here then feasible
    feasible = True if counter_area==0 else False 
    ############################################################
    F_cat, F_num, F_sim = problem.separate_features()
    #nfeats = len(F_cat)+len(F_num)+ # len(problem.features_orddict)
    order_cols = [x['Variable'] for i, x in sorted(problem.features_dict.items(), key=lambda y: y[1]["Priority"])]
    nfeats=len(order_cols)
    logger.debug(f"{order_cols}")
    discrepancy_av = np.empty([len(projects), nfeats])
    discrepancy_min = np.empty([len(projects), nfeats])
    discrepancy_max = np.empty([len(projects), nfeats])

    i = 0

    if latex:
        latexfile = open(filepath.with_suffix(".tex"), encoding="utf-8",mode="w")
        boilerplate = textwrap.dedent("""\
                                      \\documentclass{article}
                                      \\usepackage{booktabs}
                                      \\begin{document}
                                      """)
        latexfile.write(boilerplate)
    for p in sorted(projects):
        M_num = np.empty((len(projects[p]), len(F_num)))
        M_cat = np.empty((len(projects[p]), len(F_cat)))
        M_sim = np.zeros((len(F_sim),len(projects[p]),len(projects[p])))
        #M_rcat = np.empty((len(projects[p]), len(F_cat)), dtype=np.uintc)
        for j in range(len(projects[p])):
            s = projects[p][j]
            # print([problem.student_details[s][f] for f in F_num])
            M_num[j, :] = np.array([problem.student_details[s][f] for f in F_num])
            M_cat[j, :] = np.array([problem.student_details[s][f] for f in F_cat])
        for (s1,s2) in itertools.combinations(range(len(projects[p])),2):
            M_sim[:,s1,s2] = np.array([problem.similarity_dict[f][(projects[p][s1],projects[p][s2])] for f in F_sim])
            #M_rcat[j, :] = np.array([problem.student_details[s][f+"_rcat"] for f in F_cat])
        
        feat_grp = np.hstack([M_num, M_cat])
        feat_grp_df = pd.DataFrame(data=feat_grp, index=list(range(len(projects[p]))), columns=F_num+F_cat)
        #feat_sim_df = pd.DataFrame(data=M_sim, index=list(range(len(projects[p]))), columns=F_sim) # to do does not work with two feats
        #logger.info(feat_sim_df)
        sim_mx_df = pd.DataFrame(np.reshape(M_sim,(len(projects[p])*len(F_sim),len(projects[p]))).T)
        #         
        if latex:
            latexfile.write(feat_grp_df.style.to_latex(hrules=True, caption=f"The features for the groups {p}"))
            latexfile.write(sim_mx_df.style.to_latex(hrules=True, caption=f"The similarities for the groups {p}"))
            #latexfile.write(feat_sim_df.style.to_latex(hrules=True, caption=f"The similarity for the groups {p}"))
        feat_grp_df.to_excel(excel_writer, sheet_name='grp_'+str(p))
        sim_mx_df.to_excel(excel_writer, sheet_name=f'grp_{p}_sim')
        #feat_sim_df.to_excel(excel_writer, sheet_name='grp_sim_'+str(p))
        logger.info(f'\n{sim_mx_df.to_string()}')
        # Dss = [np.linalg.norm(M_num[u, :]-M_num[v, :], 1)
        #      for (u, v) in itertools.combinations(range(len(projects[p])), 2)]
        # print("The norm L_1 of the pairwise discrepancies:",Dss)
        
        tmp_min=[]
        tmp_av=[]
        tmp_max=[]

        if len(F_num)>0:
            pairwise = np.vstack([np.absolute(M_num[u, :]-M_num[v, :])
                            for (u, v) in itertools.combinations(range(len(projects[p])), 2)])
            tmp_min.append(np.min(pairwise, axis=0))
            tmp_av.append(np.average(pairwise, axis=0))
            tmp_max.append(np.max(pairwise, axis=0))

        if len(F_cat)>0:
            counts = np.apply_along_axis(lambda a: len(np.unique(a)), 0, M_cat)
            tmp_min.append(counts)
            tmp_av.append(counts)
            tmp_max.append(counts)
        if len(F_sim)>0:
            tmp_min.append([np.min(M_sim[f,:,:] + np.tril(np.ones_like(M_sim[f,:,:]),0)) for f in range(len(F_sim))])
            tmp_av.append([np.mean(M_sim[f,:,:]) for f in range(len(F_sim))])
            tmp_max.append([np.max(M_sim[f,:,:]) for f in range(len(F_sim))])
        
        discrepancy_min[i, :]=np.concatenate(tmp_min, axis=0) # np.array(tmp_min).reshape(1,nfeats)
        discrepancy_av[i, :]=np.concatenate(tmp_av, axis=0) # np.array(tmp_av).reshape(1,nfeats)
        discrepancy_max[i, :]=np.concatenate(tmp_max, axis=0) # np.array(tmp_max).reshape(1,nfeats)
        #discrepancy_av[i, :] = np.hstack([num_av, counts, sim_av])
    
        i += 1
    # print("The range: ", discrepancy_min,  discrepancy_max, sep="\n")
    summary = np.vstack([np.min(discrepancy_min, axis=0),
                        # np.average(discrepancy_av,axis=0),
                        np.max(discrepancy_max, axis=0)]
                        )
    
    sum_df = pd.DataFrame(data=summary, index=["min", "max"], columns=F_num+F_cat+F_sim)
    #print(sum_df[order_cols])

    sum_df[order_cols].to_excel(excel_writer, sheet_name='overall')    
    

    if latex:
        latexfile.write(sum_df[order_cols].style.to_latex(hrules=True, caption="Overall"))
        latexfile.write("\end{document}")
        latexfile.close()
        subprocess.run(["pdflatex", filename+".tex"], cwd=soldirname, capture_output=False)
    
    
    #sum_df[order_cols].to_markdown(filepath+'.md')
    # Hierarchical indexing (MultiIndex)
    iterables = [order_cols, ["min", "max"]]
    hierarchy = pd.MultiIndex.from_product(iterables, names=["feature", "value"])  
    discrepancy_av = np.empty([len(projects), nfeats])
    f_list = F_num+F_cat+F_sim
    indices = [f_list.index(x) for x in order_cols]
    discrepancy_array=np.empty((len(projects), 2*nfeats))
    for f in range(nfeats):
        discrepancy_array[:,2*f] = discrepancy_min[:,indices[f]]
        discrepancy_array[:,2*f+1] = discrepancy_max[:,indices[f]]
    discrepancy_multiindex_df = pd.DataFrame(discrepancy_array,columns=hierarchy)
    discrepancy_multiindex_df.to_markdown(filepath+'.md')
    with open(filepath+'.txt',"w") as fh:
        fh.write(discrepancy_multiindex_df.to_string())
    
    discrepancy_multiindex_df.to_markdown(filepath+'.csv',index=None)
    logger.info(f'\n{discrepancy_multiindex_df.to_string()}')
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
    
    log += [len(problem.std_type)]
    log += [nteams]
    #log += [len(problem.projects)]
    log += [unass_students]
    log += [underfull]
    log += [counter_area]
    log += [feasible]
    #log += [unstable]
    #log += [tot_util]
    #log += [tot_envy]

    
    excel_writer.close()

    return log
