from utils import *
from load_data import *
from time import *
from gurobipy import *
from owa import *


def model_ip_weighted(prob, weight_method, instability, minimax, allsol):
    start = clock()
    m = Model('weighted')

    restrictions2016 = False
    Bio2014 = False
    allsolutions = allsol

    cal_P = list(prob.projects.keys())
    cal_G = list(prob.groups.keys())
    array_ranks = {}
    grp_ranks = {}
    max_rank = 0
    for g in cal_G:
        s = prob.groups[g][0]  # we consider only first student, the other must have equal prefs
        grp_ranks[g] = prob.std_ranks[s]
        if len(grp_ranks[g]) > max_rank:
            max_rank = len(grp_ranks[g])

    a = dict()  # the size of the group
    for g in cal_G:
        a[g] = len(prob.groups[g])
    ############################################################
    weights = [0] * (max_rank + 1)
    if weight_method == "identity":
        weights = list(range(max_rank + 1))
        weights[0] = max_rank + 1
    elif weight_method == "owa":
        weights = owa_weights(max_rank)
        # beta=1-0.001 #1.0/max_rank - 0.001
        # f_i = [1 for x in range(1,max_rank+1)] #[1./max_rank*x for x in range(1,max_rank+1)]
        # rescale=1000
        # weights[1] = rescale*f_i[0]*beta**(max_rank-1)/(1+beta)**(max_rank-1)
        # weights[2:] = map(lambda x: rescale*f_i[x-1]*beta**(max_rank-x)/(1+beta)**(max_rank+1-x), range(2,max_rank+1))
        # weights[0] = max(weights[1:])+1
    elif weight_method == "powers":
        weights[1:] = [-2 ** max(8 - x, 0) for x in range(1, max_rank + 1)]
        weights[0] = -1
    ############################################################
    # Create variables
    x = {}  # # assignment vars
    for g in cal_G:
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                x[g, p, t] = m.addVar(lb=0.0, ub=1.0,
                                      vtype=GRB.BINARY,
                                      obj=0.0,
                                      name='x_%s_%s_%s' % (g, p, t))

    y = {}  # # is team t of project p used?
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            y[p, t] = m.addVar(lb=0.0, ub=1.0,
                               vtype=GRB.BINARY,
                               obj=0.0,
                               name='y_%s_%s' % (p, t))

    slack = {}  # # slack in team t of project p
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            slack[p, t] = m.addVar(lb=0.0, ub=10.0,
                                   vtype=GRB.CONTINUOUS,
                                   obj=0.0,
                                   name='slack_%s_%s' % (p, t))

    v = m.addVar(lb=-2 ** 8 * len(list(prob.std_type.keys())),
                 ub=len(list(prob.std_type.keys())) * max_rank, vtype=GRB.CONTINUOUS, obj=1.0, name='v')

    ############################################################
    if instability == True:
        z = {}  # z: binary variable to indicate whether there is space left in a team
        q = {}  # d: counts if space free in some better project
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                for g in list(prob.groups.keys()):
                    z[g, p, t] = m.addVar(lb=0.0, ub=1.0,
                                          vtype=GRB.BINARY,
                                          obj=0.0,
                                          name='z_%s_%s_%s' % (g, p, t))
                    q[g, p, t] = m.addVar(lb=0.0, ub=max_rank,
                                          vtype=GRB.CONTINUOUS,
                                          obj=0.0,
                                          name='q_%s_%s_%s' % (g, p, t))

        # the total instability
        tot_instability = m.addVar(lb=0.0, ub=len(list(prob.groups.keys())) * max_rank,
                                   vtype=GRB.CONTINUOUS,
                                   obj=1.0,
                                   name='tot_instability')
    else:
        tot_instability = 0
        W_instability = 0
    ############################################################
    if minimax >= 0:
        u = {}  # rank assigned per group
        for g in cal_G:
            u[g] = m.addVar(lb=0.0, ub=max_rank, vtype=GRB.INTEGER, obj=0.0, name='u_%s' % (g))
        f = m.addVar(lb=0.0, ub=len(list(prob.groups.keys())) * max_rank,
                     vtype=GRB.CONTINUOUS,
                     obj=0.0,
                     name='minimax')
    else:
        f = 0
        W_f = 0

    ############################################################
    m.update()
    ############################################################
    # Assignment constraints
    # for g in prob.groups.keys():
    # working=[x[g,p,t] for p in prob.projects.keys() for t in range(len(prob.projects[p]))]
    # m.addConstr(quicksum(working) == 1, 'grp_%s' % g)

    # Assignment constraints
    for g in cal_G:
        peek = prob.std_type[prob.groups[g][0]]
        valid_prjs = [x for x in cal_P if prob.projects[x][0].type in prob.valid_prjtype[peek]]
        # valid_prjs=filter(lambda x: prob.projects[x][0][2]==peek or prob.projects[x][0][2]=='alle', prob.projects.keys())

        working = [x[g, p, t] for p in valid_prjs for t in range(len(prob.projects[p]))]
        m.addConstr(quicksum(working) == 1, 'grp_%s' % g)
        for p in cal_P:
            if not p in valid_prjs:
                for t in range(len(prob.projects[p])):
                    m.addConstr(x[g, p, t] == 0, 'ngrp_%s' % g)
            if not p in prob.std_ranks[prob.groups[g][0]]:
                for t in range(len(prob.projects[p])):
                    m.addConstr(x[g, p, t] == 0, 'ngrp_%s' % g)
        if Bio2014:  # 2014: constraint on biology stydents
            if peek == "biologi":
                for p in valid_prjs:  # prob.projects.keys():
                    for t in range(len(prob.projects[p])):
                        m.addConstr(x[g, p, t] <= b[p, t], 'biologi_%s' % g)
            else:
                for p in valid_prjs:  # prob.projects.keys():
                    for t in range(len(prob.projects[p])):
                        m.addConstr(x[g, p, t] <= (1 - b[p, t]), 'nbiologi_%s' % g)
            m.addConstr(x['312', 29, 0] + x['312', 29, 1] == 0, "cheat1")
            # m.addConstr(quicksum(x[g,61,0] for g in prob.groups.keys())>=1,"cheat2")

    # Capacity constraints
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            m.addConstr(quicksum(a[g] * x[g, p, t] for g in list(prob.groups.keys())) + slack[p, t]
                        == prob.projects[p][t][1] * y[p, t], 'ub_%s_%d' % (p, t))
            m.addConstr(quicksum(a[g] * x[g, p, t] for g in list(prob.groups.keys()))
                        >= prob.projects[p][t][0] * y[p, t], 'lb_%s_%d' % (p, t))

    # enforce restrictions on number of teams open across different topics:
    for rest in prob.restrictions:
        m.addConstr(quicksum(y[p, t] for p in rest["topics"] for t in range(
            len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str, rest["topics"])))

    ############################################################
    if restrictions2016:
        morteza = [y[p, t] for p in ['06', '70'] for t in range(len(prob.projects[p]))]
        m.addConstr(quicksum(morteza) <= 2, 'morteza_%s' % g)
        m.addConstr(quicksum(y['04', t]
                             for t in range(len(prob.projects['04']))) <= 0, 'prj4_%s' % g)

    ############################################################
    # Symmetry breaking on the teams

    for p in cal_P:
        for t in range(len(prob.projects[p]) - 1):
            m.addConstr(quicksum(x[g, p, t] for g in list(prob.groups.keys())) >= quicksum(
                x[g, p, t + 1] for g in list(prob.groups.keys())), "symbreak_%s" % (p))

    ############################################################
    # weighted
    m.addConstr(v >= quicksum(weights[grp_ranks[g][p]] * a[g] * x[g, p, t] for g in list(
        prob.groups.keys()) for p in list(grp_ranks[g].keys()) for t in range(len(prob.projects[p]))), 'v')

    ############################################################
    # instability
    if instability == True:
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                for g in list(prob.groups.keys()):
                    if a[g] <= prob.projects[p][t][1]:
                        m.addConstr(slack[p, t] + 1 - a[g] <= prob.projects[p][t]
                                    [1] * z[g, p, t], 'c30_%s_%s_%s' % (g, p, t))
                        m.addConstr(a[g] + 1 - (1 - y[p, t]) * prob.projects[p][t][0] <= prob.projects[p][t][1]
                                    * z[g, p, t] + (prob.projects[p][t][1] + 1) * y[p, t], 'c31_%s_%s_%s' % (g, p, t))
                    else:
                        m.addConstr(z[g, p, t] == 0, 'c3031_%s_%s_%s' % (g, p, t))
        for g in cal_G:
            for p in list(grp_ranks[g].keys()):
                for p2 in list(grp_ranks[g].keys()):
                    if (grp_ranks[g][p2] < grp_ranks[g][p]):
                        for t in range(len(prob.projects[p])):
                            for t2 in range(len(prob.projects[p2])):
                                m.addConstr(q[g, p, t] >= (grp_ranks[g][p] - grp_ranks[g][p2])
                                            * (x[g, p, t] + z[g, p2, t2] - 1), 'c32_%s_%s_%s' % (g, p, t))
        # m.addConstr(tot_instability >= quicksum(q[g,p,t] for g in prob.groups.keys() for p in prob.projects.keys() for t in range(len(prob.projects[p]) ) ), 'instability')
        m.addConstr(0 == quicksum(q[g, p, t] for g in list(prob.groups.keys()) for p in list(
            prob.projects.keys()) for t in range(len(prob.projects[p]))), 'instability')
        # W_instability = max_rank*len(prob.std_type.keys()) #max_rank*len(prob.groups)*len(prob.groups) ##2^7 * len(prob.groups)*
    ############################################################
    # minimax
    if minimax >= 0:
        for g in cal_G:
            m.addConstr(u[g] ==
                        quicksum(grp_ranks[g][p] * x[g, p, t] for p in list(grp_ranks[g].keys())
                                 for t in range(len(prob.projects[p]))),
                        'u_%s' % (g))
            m.addConstr(f >= u[g], 'v_%s' % g)
        m.addConstr(f <= minimax, 'minimax_%s' % minimax)
        # W_f = 1.0 #max_rank*len(prob.std_type.keys())*len(prob.std_type.keys())*1000
    ############################################################
    # Compute optimal solution
    W_v = 1.0
    # m.setObjective(W_v*v + W_instability * instability + W_f * f, GRB.MINIMIZE)
    # m.setObjective(W_v*v + W_f * f, GRB.MINIMIZE)
    m.setObjective(W_v * v, GRB.MINIMIZE)

    m.setParam("MIPGap", 0)
    m.setParam("MIPGapAbs", 0)
    m.setParam("OptimalityTol", 1e-09)
    m.setParam("Threads", 1)
    m.setParam("Method", 4)  # for deterministic behavior
    m.setParam("TimeLimit", 3600)
    m.update()
    m.write("model.lp")
    m.optimize()

    if m.status == GRB.status.INFEASIBLE:  # do IIS
        print('The model is infeasible; computing IIS')
        m.computeIIS()
        m.write(os.path.join("optprj_IIS.ilp"))
        print('\nThe following constraint(s) cannot be satisfied:')
        for c in m.getConstrs():
            if c.IISConstr:
                print(('%s' % c.constrName))
        print("\nSee optexam_IIS.ilp for explicit constraints.\n")
        exit(0)

    # Print solution
    optimal_value = v.x
    solutions = []
    i = 1
    while optimal_value == v.x:
        teams = {}
        topics = {}
        expr = LinExpr()
        for g in prob.groups:
            for p in cal_P:
                for t in range(len(prob.projects[p])):
                    if x[g, p, t].x > 0.5:
                        for s in prob.groups[g]:
                            teams[s] = t
                            topics[s] = p
                        expr += 1 - x[g, p, t]
                    else:
                        expr += x[g, p, t]
        print("solution " + str(i) + " found\n")
        elapsed = (clock() - start)
        solutions.append(Solution(topics=topics, teams=teams, solved=[elapsed]))
        if m.status != GRB.status.OPTIMAL or not allsolutions or elapsed >= 3600:
            break
        m.addConstr(expr, GRB.GREATER_EQUAL, 1.0, "no_good" + str(i))
        m.update()
        m.optimize()
        i += 1

    return optimal_value, solutions
