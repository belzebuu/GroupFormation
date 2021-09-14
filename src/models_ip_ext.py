from utils import *
from load_data import *
import time
from gurobipy import *
from functools import reduce
import math


def model_ip_ext(prob, config):
    start = time.perf_counter()
    m = Model('leximin')

    F_cat, F_num = prob.separate_features()

    #  create sets of students for each category of each categorical variable
    stds = {}
    for f in F_cat:
        for ell in prob.categories[f+"_rcat"]:
            stds[f, ell] = {
                s for s in prob.student_details if prob.student_details[s][f+"_rcat"] == ell}

    # grp_ranks = {}
    # max_rank = 0
    cal_G = list(prob.groups.keys())
    cal_P = list(prob.projects.keys())
    for g in cal_G:
        s = prob.groups[g][0]  # we consider only first student, the other must have equal prefs
        # grp_ranks[g] = prob.std_ranks[s]
        # if len(grp_ranks[g]) > max_rank:
        #    max_rank = len(grp_ranks[g])

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
                                      vtype=GRB.BINARY,
                                      obj=0.0,
                                      name='x_%s_%s_%s' % (g, p, t))

    y = {}  # is team t of project p used?
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            y[p, t] = m.addVar(lb=0.0, ub=1.0,
                               vtype=GRB.BINARY,
                               obj=0.0,
                               name='y_%s_%s' % (p, t))

    # u = {}  # rank assigned per group
    # for g in cal_G:
    #     u[g] = m.addVar(lb=0.0, ub=max_rank,
    #                     vtype=GRB.INTEGER,
    #                     obj=0.0,
    #                     name='u_%s' % (g))
    #
    # v = m.addVar(lb=0.0, ub=max_rank,
    #              vtype=GRB.INTEGER,
    #              obj=1.0,
    #              name='v_%s' % (g))

    delta_cat_sum = {}
    delta_cat = {}  # var to store if category ell of feature f is used in (p,t)
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            for f in F_cat:
                for ell in prob.categories[f+"_rcat"]:
                    delta_cat[p, t, f, ell] = m.addVar(lb=0.0, ub=1.0,
                                                       vtype=GRB.BINARY,
                                                       obj=0.0,
                                                       name='delta_cat_%s_%s_%s_%s' % (p, t, f, ell))
                delta_cat_sum[p, t, f] = m.addVar(lb=0.0,  # ub=1.0,
                                                  vtype=GRB.CONTINUOUS,
                                                  obj=0.0,
                                                  name='delta_cat_sum_%s_%s_%s' % (p, t, f))
    delta_cat_min = {}
    delta_cat_max = {}
    for f in F_cat:
        delta_cat_min[f] = m.addVar(lb=0.0,  # ub=1.0,
                                    vtype=GRB.CONTINUOUS,
                                    obj=0.0,
                                    name='delta_cat_min_%s' % (f))
        delta_cat_max[f] = m.addVar(lb=0.0,  # ub=1.0,
                                    vtype=GRB.CONTINUOUS,
                                    obj=0.0,
                                    name='delta_cat_max_%s' % (f))

    alpha = {}
    for (g1, g2) in itertools.combinations(cal_G, 2):
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                alpha[g1, g2, p, t] = m.addVar(lb=0.0, ub=1.0,
                                               vtype=GRB.BINARY,
                                               obj=0.0,
                                               name='alpha_%s_%s_%s_%s' % (g1, g2, p, t))
    intra_discrepancy_min = {}
    intra_discrepancy_max = {}
    for f in F_num:
        intra_discrepancy_min[f] = m.addVar(lb=0.0,  # ub=1.0,
                                            vtype=GRB.CONTINUOUS,
                                            obj=0.0,
                                            name='intra_discrepancy_min_%s' % (f))
        intra_discrepancy_max[f] = m.addVar(lb=0.0,  # ub=1.0,
                                            vtype=GRB.CONTINUOUS,
                                            obj=0.0,
                                            name='intra_discrepancy_max_%s' % (f))

    # beta = {}
    # D_s1s2 = {}
    # for (g1, g2) in itertools.combinations(cal_G, 2):
    #     for p in cal_P:
    #         for t in range(len(prob.projects[p])):
    #             D_s1s2[g1, g2, p, t] = m.addVar(lb=0.0,  # ub=1.0,
    #                                             vtype=GRB.CONTINUOUS,
    #                                             obj=0.0,
    #                                             name='D_s1s2_%s_%s_%s_%s' % (g1, g2, p, t))
    #             for f in F_num:
    #                 beta[g1, g2, p, t, f] = m.addVar(lb=0.0,  # ub=1.0,
    #                                                  vtype=GRB.CONTINUOUS,
    #                                                  obj=0.0,
    #                                                  name='beta_%s_%s_%s_%s_%s' % (g1, g2, p, t, f))

    # intra_discrepancy_min = {}
    # inter_discrepancy_max = {}
    # for p in cal_P:
    #     for t in range(len(prob.projects[p])):
    #         intra_discrepancy_min[p, t] = m.addVar(lb=0.0,  # ub=1.0,
    #                                                vtype=GRB.CONTINUOUS,
    #                                                obj=0.0,
    #                                                name='intra_discrepancy_min_%s_%s' % (p, t))
    #         inter_discrepancy[p, t] = m.addVar(lb=0.0,  # ub=1.0,
    #                                            vtype=GRB.CONTINUOUS,
    #                                            obj=0.0,
    #                                            name='inter_discrepancy_%s_%s' % (p, t))
    # intra_discrepancy_min_global = m.addVar(lb=0.0,  # ub=1.0,
    #                                         vtype=GRB.CONTINUOUS,
    #                                         obj=0.0,
    #                                         name='intra_discrepancy_min_global')
    # inter_discrepancy_max_global = m.addVar(lb=0.0,  # ub=1.0,
    #                                         vtype=GRB.CONTINUOUS,
    #                                         obj=0.0,
    #                                         name='inter_discrepancy_max_global')
    m.update()
    ############################################################
    # Assignment constraints
    # for g in prob.groups.keys():
    # working=[x[g,p,t] for p in prob.projects.keys() for t in range(len(prob.projects[p]))]
    # m.addLConstr(quicksum(working) == 1, 'grp_%s' % g)
    print("posting constraints...")

    # Assignment constraints
    for g in cal_G:
        peek = str(prob.std_type[prob.groups[g][0]])
        
        valid_prjs = [x for x in cal_P if prob.projects[x][0].type in prob.valid_prjtype[peek]]
        # valid_prjs=filter(lambda x: prob.projects[x][0][2]==peek or prob.projects[x][0][2]=='alle', prob.projects.keys())
        working = [x[g, p, t] for p in valid_prjs for t in range(len(prob.projects[p]))]
        m.addLConstr(quicksum(working) == 1, 'grp_%s' % g)
        for p in cal_P:
            if not p in valid_prjs:
                for t in range(len(prob.projects[p])):
                    m.addLConstr(x[g, p, t] == 0, 'ngrp_%s_%s' % (g,p))
            # if not p in prob.std_ranks[prob.groups[g][0]]:
            #    for t in range(len(prob.projects[p])):
            #        m.addLConstr(x[g, p, t] == 0, 'ngrp_%s' % g)

    # Capacity constraints
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            m.addLConstr(quicksum(a[g]*x[g, p, t] for g in cal_G) <=
                        prob.projects[p][t][1]*y[p, t], 'ub_%s_%s' % (p,t))
            m.addLConstr(quicksum(a[g]*x[g, p, t] for g in cal_G) >=
                        prob.projects[p][t][0]*y[p, t], 'lb_%s_%s' % (p,t))
            if config.groups == "pre":
                m.addLConstr(quicksum(x[g, p, t] for g in cal_G) <= 1, 'max_one_grp_%s%s' % (p, t))

    # # put in u the rank assigned to the group
    # for g in cal_G:
    #     m.addLConstr(u[g] ==
    #                 quicksum(grp_ranks[g][p] * x[g, p, t] for p in list(grp_ranks[g].keys())
    #                          for t in range(len(prob.projects[p]))),
    #                 'u_%s' % (g))
    #     m.addLConstr(v >= u[g], 'v_%s' % g)

    # enforce restrictions on number of teams open across different topics:
    for rest in prob.restrictions:
        m.addLConstr(quicksum(y[p, t] for p in rest["topics"] for t in range(
            len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str, rest["topics"])))

    # Symmetry breaking on the teams
    for p in cal_P:
        for t in range(len(prob.projects[p])-1):
            m.addLConstr(quicksum(x[g, p, t] for g in cal_G)
                        >= quicksum(x[g, p, t+1] for g in cal_G))

    #### DISCREPANCIES ########################################################
    print("posting discrepancies")
    
    if True:
        for f in F_cat:
            for p in cal_P:
                for t in range(len(prob.projects[p])):
                    for ell in prob.categories[f+"_rcat"]:
                        expr = LinExpr()
                        for s in stds[f, ell]:
                            g = prob.student_details[s]["grp_id"]
                            m.addLConstr(x[g, p, t] <= delta_cat[p, t, f, ell], "delta_cat1")
                            expr += x[g, p, t]
                        m.addLConstr(expr, GRB.GREATER_EQUAL, delta_cat[p, t, f, ell], "delta_cat2")
                        #m.addLConstr(quicksum(x[g, p, t] for g in cal_G) >= delta_cat[p, t, f, ell], "delta_cat")
                    m.addLConstr(delta_cat_sum[p, t, f] == quicksum(delta_cat[p, t, f, ell]
                                                                for ell in prob.categories[f+"_rcat"]), "delta_cat_sum")
                    m.addLConstr(delta_cat_min[f] <= delta_cat_sum[p, t, f])
                    m.addLConstr(delta_cat_max[f] >= delta_cat_sum[p, t, f])

        for p in cal_P:
            for t in range(len(prob.projects[p])):
                for (g1, g2) in itertools.combinations(cal_G, 2):
                    m.addLConstr(x[g1, p, t]+x[g2, p, t]-1 <= alpha[g1, g2, p, t], "alpha_1")
                    m.addLConstr(x[g1, p, t] >= alpha[g1, g2, p, t], "alpha_2")
                    m.addLConstr(x[g2, p, t] >= alpha[g1, g2, p, t], "alpha_3")
                    for f in F_num:
                        m.addLConstr(intra_discrepancy_min[f] <= 10*(1-alpha[g1, g2, p, t])+alpha[g1, g2, p, t]*math.fabs(
                            prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "intra_min_np_%s" % f)
                        m.addLConstr(intra_discrepancy_max[f] >= alpha[g1, g2, p, t]*math.fabs(
                            prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "intra_max_np_%s" % f)

    # for p in cal_P:
    #     for t in range(len(prob.projects[p])):
    #         for (g1, g2) in itertools.combinations(cal_G, 2):
    #             m.addLConstr(x[g1, p, t]+x[g2, p, t]-1 <= alpha[g1, g2, p, t], "alpha_1")
    #             m.addLConstr(x[g1, p, t] >= alpha[g1, g2, p, t], "alpha_2")
    #             m.addLConstr(x[g2, p, t] >= alpha[g1, g2, p, t], "alpha_3")
    #             for f in F_num:
    #                 m.addLConstr(beta[g1, g2, p, t, f] == alpha[g1, g2, p, t]*math.fabs(
    #                     prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "beta_np")
    #             m.addLConstr(D_s1s2[g1, g2, p, t] == quicksum(
    #                 beta[g1, g2, p, t, f] for f in F_num), "D_s1s2")
    #             # m.addLConstr(discrepancy_av == quicksum(D_s1s2[g1, g2, p, t], "discrepancy_av")
    #
    #             m.addLConstr(intra_discrepancy_min[p, t] <=
    #                         D_s1s2[g1, g2, p, t]+100*(1-alpha[g1, g2, p, t]), "intra_min_%s_%s" % (p, t))
    #             m.addLConstr(inter_discrepancy[p, t] >= D_s1s2[g1, g2, p, t], "inter_%s_%s" % (p, t))
    #         m.addLConstr(intra_discrepancy_min_global <=
    #                     intra_discrepancy_min[p, t], "intra_min_global")
    #         m.addLConstr(inter_discrepancy_max_global >= inter_discrepancy[p, t])
    ############################################################
    # Compute optimal solution
    # m.setObjective(intra_discrepancy_min_global, GRB.MAXIMIZE)
    m.ModelSense = GRB.MAXIMIZE
    nfeats = len(prob.features_orddict)
    i = 2*nfeats-1
    for index, feat in prob.features_orddict.items():
        print(feat['Variable'], index, i)
        f = feat['Variable']
        if feat['Type'] == 'category':
            m.setObjectiveN(delta_cat_min[f], index=i, priority=i, weight=1)
            m.setObjectiveN(delta_cat_max[f], index=i-1, priority=i-1, weight=-1)
        elif feat['Type'] not in ['object', 'str']:
            m.setObjectiveN(intra_discrepancy_min[f], index=i, priority=i, weight=1)
            m.setObjectiveN(intra_discrepancy_max[f], index=i-1, priority=i-1, weight=-1)
        i = i-2

    # m.setParam("Presolve", 0)
    m.setParam(GRB.param.TimeLimit, 50) #7200)
    m.write("model_ip_ext.lp")
    m.optimize()
    m.write("model_ip_ext.sol")
   
    assert m.status == GRB.status.OPTIMAL or (m.status==GRB.status.TIME_LIMIT and m.SolCount>0)

    elapsed = (time.perf_counter() - start)
    
    
    # Query number of multiple objectives, and number of solutions
    nSolutions  = m.SolCount
    nObjectives = m.NumObj
    print('Problem has', nObjectives, 'objectives')
    print('Gurobi found', nSolutions, 'solutions')

    # For each solution print value for each objective function
    solutions = []
    for s in range(nSolutions):
        # Set which solution we will query from now on
        m.params.SolutionNumber = s

        # Print objective value of this solution in each objective
        print('Solution', s, ':', end='')
        for o in range(nObjectives):
            # Set which objective we will query
            m.params.ObjNumber = o
            # Query the o-th objective value
            print(' ',m.ObjNVal, end='')

        teams = {}
        topics = {}

        for g in prob.groups:
            for p in cal_P:
                for t in range(len(prob.projects[p])):
                    if x[g, p, t].x > 0:
                        for s in prob.groups[g]:
                            teams[s] = t
                            topics[s] = p
        
        solutions.append(Solution(topics=topics, teams=teams, solved=[elapsed]))
    return solutions

