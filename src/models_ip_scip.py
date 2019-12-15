from utils import *
from load_data import *
from time import *

import pyscipopt as pso
from pyscipopt import Model

from functools import reduce


def model_ip_scip(prob):
    start = clock()
    m = Model('leximin')

    grp_ranks = {}
    max_rank = 0
    cal_G = list(prob.groups.keys())
    cal_P = list(prob.projects.keys())
    for g in cal_G:
        s = prob.groups[g][0]  # we consider only first student, the other must have equal prefs
        grp_ranks[g] = prob.std_ranks[s]
        if len(grp_ranks[g]) > max_rank:
            max_rank = len(grp_ranks[g])

    a = dict()  # the size of the group
    for g in cal_G:
        a[g] = len(prob.groups[g])

    ############################################################
    # Create variables
    x = {}  # assignment vars
    for g in cal_G:
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                x[g, p, t] = m.addVar(lb=0.0, ub=1.0,
                                      vtype="BINARY",
                                      obj=0.0,
                                      name='x_%s_%s_%s' % (g, p, t))

    y = {}  # is team t of project p used?
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            y[p, t] = m.addVar(lb=0.0, ub=1.0,
                               vtype="BINARY",
                               obj=0.0,
                               name='y_%s_%s' % (p, t))

    u = {}  # rank assigned per group
    for g in cal_G:
        u[g] = m.addVar(lb=0.0, ub=max_rank,
                        vtype="INTEGER",
                        obj=0.0,
                        name='u_%s' % (g))

    v = m.addVar(lb=0.0, ub=max_rank,
                 vtype="INTEGER",
                 obj=1.0,
                 name='v_%s' % (g))

    # m.update()
    ############################################################
    # Assignment constraints
    # for g in prob.groups.keys():
    #working=[x[g,p,t] for p in prob.projects.keys() for t in range(len(prob.projects[p]))]
    #m.addConstr(quicksum(working) == 1, 'grp_%s' % g)

    # Assignment constraints
    for g in cal_G:
        peek = prob.std_type[prob.groups[g][0]]
        valid_prjs = [x for x in cal_P if prob.projects[x][0].type in prob.valid_prjtype[peek]]
        #valid_prjs=filter(lambda x: prob.projects[x][0][2]==peek or prob.projects[x][0][2]=='alle', prob.projects.keys())

        working = [x[g, p, t] for p in valid_prjs for t in range(len(prob.projects[p]))]
        m.addCons(quicksum(working) == 1, 'grp_%s' % g)
        for p in cal_P:
            if not p in valid_prjs:
                for t in range(len(prob.projects[p])):
                    m.addCons(x[g, p, t] == 0, 'ngrp_%s' % g)
            if not p in prob.std_ranks[prob.groups[g][0]]:
                for t in range(len(prob.projects[p])):
                    m.addCons(x[g, p, t] == 0, 'ngrp_%s' % g)

    # Capacity constraints
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            m.addCons(quicksum(a[g]*x[g, p, t] for g in cal_G) <=
                      prob.projects[p][t][1]*y[p, t], 'ub_%s' % (t))
            m.addCons(quicksum(a[g]*x[g, p, t] for g in cal_G) >=
                      prob.projects[p][t][0]*y[p, t], 'lb_%s' % (t))

    # put in u the rank assigned to the group
    for g in cal_G:
        m.addCons(u[g] ==
                  quicksum(grp_ranks[g][p] * x[g, p, t] for p in list(grp_ranks[g].keys())
                           for t in range(len(prob.projects[p]))),
                  'u_%s' % (g))
        m.addCons(v >= u[g], 'v_%s' % g)

    # enforce restrictions on number of teams open across different topics:
    for rest in prob.restrictions:
        m.addCons(quicksum(y[p, t] for p in rest["topics"] for t in range(
            len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str, rest["topics"])))

    # Symmetry breaking on the teams
    for p in cal_P:
        for t in range(len(prob.projects[p])-1):
            m.addCons(quicksum(x[g, p, t] for g in cal_G)
                      >= quicksum(x[g, p, t+1] for g in cal_G))

    ############################################################
    # Compute optimal solution
    m.setMinimize()

    # m.write("model_ip.lp")
    m.optimize()

    # Print solution
    teams = {}
    topics = {}
    if m.getStatus() == "optimal":
        for g in prob.groups:
            for p in cal_P:
                for t in range(len(prob.projects[p])):
                    if m.getVal(x[g, p, t]) > 0:
                        for s in prob.groups[g]:
                            teams[s] = t
                            topics[s] = p
    elapsed = (clock() - start)
    solution = []
    solution.append(Solution(topics=topics, teams=teams, solved=[elapsed]))
    return m.getVal(v), solution
