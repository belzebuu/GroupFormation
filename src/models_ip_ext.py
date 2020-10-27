from utils import *
from load_data import *
from time import *
from gurobipy import *
from functools import reduce
import math


def model_ip_ext(prob, config):
    start = clock()
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
            # if not p in prob.std_ranks[prob.groups[g][0]]:
            #    for t in range(len(prob.projects[p])):
            #        m.addConstr(x[g, p, t] == 0, 'ngrp_%s' % g)

    # Capacity constraints
    for p in cal_P:
        for t in range(len(prob.projects[p])):
            m.addConstr(quicksum(a[g]*x[g, p, t] for g in cal_G) <=
                        prob.projects[p][t][1]*y[p, t], 'ub_%s' % (t))
            m.addConstr(quicksum(a[g]*x[g, p, t] for g in cal_G) >=
                        prob.projects[p][t][0]*y[p, t], 'lb_%s' % (t))
            if config.groups == "pre":
                m.addConstr(quicksum(x[g, p, t] for g in cal_G) <= 1, 'max_one_grp_%s%s' % (p, t))

    # # put in u the rank assigned to the group
    # for g in cal_G:
    #     m.addConstr(u[g] ==
    #                 quicksum(grp_ranks[g][p] * x[g, p, t] for p in list(grp_ranks[g].keys())
    #                          for t in range(len(prob.projects[p]))),
    #                 'u_%s' % (g))
    #     m.addConstr(v >= u[g], 'v_%s' % g)

    # enforce restrictions on number of teams open across different topics:
    for rest in prob.restrictions:
        m.addConstr(quicksum(y[p, t] for p in rest["topics"] for t in range(
            len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str, rest["topics"])))

    # Symmetry breaking on the teams
    for p in cal_P:
        for t in range(len(prob.projects[p])-1):
            m.addConstr(quicksum(x[g, p, t] for g in cal_G)
                        >= quicksum(x[g, p, t+1] for g in cal_G))

    #### DISCREPANCIES ########################################################
    for f in F_cat:
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                for ell in prob.categories[f+"_rcat"]:
                    expr = LinExpr()
                    for s in stds[f, ell]:
                        g = prob.student_details[s]["grp_id"]
                        m.addConstr(x[g, p, t] <= delta_cat[p, t, f, ell], "delta_cat1")
                        expr += x[g, p, t]
                    m.addConstr(expr, GRB.GREATER_EQUAL, delta_cat[p, t, f, ell], "delta_cat2")
                    #m.addConstr(quicksum(x[g, p, t] for g in cal_G) >= delta_cat[p, t, f, ell], "delta_cat")
                m.addConstr(delta_cat_sum[p, t, f] == quicksum(delta_cat[p, t, f, ell]
                                                               for ell in prob.categories[f+"_rcat"]), "delta_cat_sum")
                m.addConstr(delta_cat_min[f] <= delta_cat_sum[p, t, f])
                m.addConstr(delta_cat_max[f] >= delta_cat_sum[p, t, f])

    for p in cal_P:
        for t in range(len(prob.projects[p])):
            for (g1, g2) in itertools.combinations(cal_G, 2):
                m.addConstr(x[g1, p, t]+x[g2, p, t]-1 <= alpha[g1, g2, p, t], "alpha_1")
                m.addConstr(x[g1, p, t] >= alpha[g1, g2, p, t], "alpha_2")
                m.addConstr(x[g2, p, t] >= alpha[g1, g2, p, t], "alpha_3")
                for f in F_num:
                    m.addConstr(intra_discrepancy_min[f] <= 10*(1-alpha[g1, g2, p, t])+alpha[g1, g2, p, t]*math.fabs(
                        prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "intra_min_np_%s" % f)
                    m.addConstr(intra_discrepancy_max[f] >= alpha[g1, g2, p, t]*math.fabs(
                        prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "intra_max_np_%s" % f)

    # for p in cal_P:
    #     for t in range(len(prob.projects[p])):
    #         for (g1, g2) in itertools.combinations(cal_G, 2):
    #             m.addConstr(x[g1, p, t]+x[g2, p, t]-1 <= alpha[g1, g2, p, t], "alpha_1")
    #             m.addConstr(x[g1, p, t] >= alpha[g1, g2, p, t], "alpha_2")
    #             m.addConstr(x[g2, p, t] >= alpha[g1, g2, p, t], "alpha_3")
    #             for f in F_num:
    #                 m.addConstr(beta[g1, g2, p, t, f] == alpha[g1, g2, p, t]*math.fabs(
    #                     prob.student_details[prob.groups[g1][0]][f]-prob.student_details[prob.groups[g2][0]][f]), "beta_np")
    #             m.addConstr(D_s1s2[g1, g2, p, t] == quicksum(
    #                 beta[g1, g2, p, t, f] for f in F_num), "D_s1s2")
    #             # m.addConstr(discrepancy_av == quicksum(D_s1s2[g1, g2, p, t], "discrepancy_av")
    #
    #             m.addConstr(intra_discrepancy_min[p, t] <=
    #                         D_s1s2[g1, g2, p, t]+100*(1-alpha[g1, g2, p, t]), "intra_min_%s_%s" % (p, t))
    #             m.addConstr(inter_discrepancy[p, t] >= D_s1s2[g1, g2, p, t], "inter_%s_%s" % (p, t))
    #         m.addConstr(intra_discrepancy_min_global <=
    #                     intra_discrepancy_min[p, t], "intra_min_global")
    #         m.addConstr(inter_discrepancy_max_global >= inter_discrepancy[p, t])
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
    m.write("model_ip_ext.lp")
    m.optimize()
    m.write("model_ip_ext.sol")
    # Print solution
    teams = {}
    topics = {}
    if m.status == GRB.status.OPTIMAL:
        for g in prob.groups:
            for p in cal_P:
                for t in range(len(prob.projects[p])):
                    if x[g, p, t].x > 0:
                        for s in prob.groups[g]:
                            teams[s] = t
                            topics[s] = p
    elapsed = (clock() - start)
    solution = []
    solution.append(Solution(topics=topics, teams=teams, solved=[elapsed]))
    return 1, solution


def lex_ip_procedure(prob, instability):
    MR = 40

    v = model_ip(prob)[0]
    print(v)
    h = int(v)
    z = []
    solved = [0]*(MR+1)
    while h > 0:
        start = clock()
        (z, sol) = model_lex(prob, int(v), h, z, False, instability, "bottomup")
        elapsed = (clock() - start)
        solved[h] = elapsed
        h -= 1
        print(z)

    return [Solution(topics=sol["topics"], teams=sol["teams"], solved=[sum(solved)])]


def greedy_maximum_matching_ip_procedure(prob, minimax, instability):
    MR = 40
    if minimax:
        v = prob.minimax_sol  # model_ip(prob)[0]
    else:
        v = MR
    print(v)
    h = 1
    z = []
    solved = [0]*(MR+1)
    while h < int(v):
        start = clock()
        (z, sol) = model_lex(prob, int(v), h, z, minimax, instability, "topdown")
        elapsed = (clock() - start)
        solved[h] = elapsed
        h += 1
        print(reduce((lambda x, y: x + y), z))
        if reduce((lambda x, y: x + y), z) >= len(list(prob.std_type.keys())): break

    return [Solution(topics=sol["topics"], teams=sol["teams"], solved=[sum(solved)])]


def model_lex(prob, v, h, z, minimax, instability, direction):
    start = clock()
    m = Model('leximin')

    cal_P = list(prob.projects.keys())
    cal_G = list(prob.groups.keys())

    grp_ranks = {}
    max_rank = 0
    grp_x_ranks = {}
    for g in list(prob.groups.keys()):
        s = prob.groups[g][0]  # we consider only first student, the other must have equal prefs
        grp_ranks[g] = prob.std_ranks[s]
        if len(grp_ranks[g]) > max_rank:
            max_rank = len(grp_ranks[g])
        for p in grp_ranks[g]:
            r = grp_ranks[g][p]
            if r in grp_x_ranks:
                grp_x_ranks[r].append((g, p))
            else:
                grp_x_ranks[r] = [(g, p)]

    a = dict()  # the size of the group
    for g in list(prob.groups.keys()):
        a[g] = len(prob.groups[g])

    ############################################################
    # Create variables
    x = {}  # assignment vars
    for g in list(prob.groups.keys()):
        for p in list(prob.projects.keys()):
            for t in range(len(prob.projects[p])):
                x[g, p, t] = m.addVar(lb=0.0, ub=1.0,
                                      vtype=GRB.BINARY,
                                      obj=0.0,
                                      name='x_%s_%s_%s' % (g, p, t))

    y = {}  # is team t of project p used?
    for p in list(prob.projects.keys()):
        for t in range(len(prob.projects[p])):
            y[p, t] = m.addVar(lb=0.0, ub=1.0,
                               vtype=GRB.BINARY,
                               obj=0.0,
                               name='y_%s_%s' % (p, t))

    slack = {}  # slack in team t of project p
    for p in list(prob.projects.keys()):
        for t in range(len(prob.projects[p])):
            slack[p, t] = m.addVar(lb=0.0, ub=10.0,
                                   vtype=GRB.CONTINUOUS,
                                   obj=0.0,
                                   name='slack_%s_%s' % (p, t))

    u = {}  # rank assigned per group
    for g in list(prob.groups.keys()):
        u[g] = m.addVar(lb=0.0, ub=max_rank,
                        vtype=GRB.INTEGER,
                        obj=0.0,
                        name='u_%s' % (g))

    z_h = m.addVar(lb=0.0, ub=len(prob.std_type),
                   vtype=GRB.INTEGER,
                   obj=0.0,
                   name='z_%s' % (h))

    ############################################################
    if instability == True:
        z2 = {}  # binary variable to indicate whether there is space left in a team
        q = {}  # counts if space free in some better project
        for p in list(prob.projects.keys()):
            for t in range(len(prob.projects[p])):
                for g in list(prob.groups.keys()):
                    z2[g, p, t] = m.addVar(lb=0.0, ub=1.0,
                                           vtype=GRB.BINARY,
                                           obj=0.0,
                                           name='z2_%s_%s_%s' % (g, p, t))
                    q[g, p, t] = m.addVar(lb=0.0, ub=max_rank,
                                          vtype=GRB.CONTINUOUS,
                                          obj=0.0,
                                          name='q_%s_%s_%s' % (g, p, t))

        # the total instability
        tot_instability = m.addVar(lb=0.0, ub=len(list(prob.groups.keys()))*max_rank,
                                   vtype=GRB.CONTINUOUS,
                                   obj=1.0,
                                   name='instability')
    else:
        tot_instability = 0
        W_instability = 0

    m.update()
    ############################################################
    # Assignment constraints
    # for g in prob.groups.keys():
    # working=[x[g,p,t] for p in prob.projects.keys() for t in range(len(prob.projects[p]))]
    # m.addConstr(quicksum(working) == 1, 'grp_%s' % g)

    # Assignment constraints
    for g in list(prob.groups.keys()):
        peek = prob.std_type[prob.groups[g][0]]
        valid_prjs = [x for x in list(prob.projects.keys())
                      if prob.projects[x][0][2] in prob.valid_prjtype[peek]]
        # valid_prjs=filter(lambda x: prob.projects[x][0][2]==peek or prob.projects[x][0][2]=='alle', prob.projects.keys())

        working = [x[g, p, t] for p in valid_prjs for t in range(len(prob.projects[p]))]
        m.addConstr(quicksum(working) == 1, 'grp_%s' % g)
        for p in list(prob.projects.keys()):
            if not p in valid_prjs:
                for t in range(len(prob.projects[p])):
                    m.addConstr(x[g, p, t] == 0, 'ngrp_%s' % g)
            if not p in prob.std_ranks[prob.groups[g][0]]:
                for t in range(len(prob.projects[p])):
                    m.addConstr(x[g, p, t] == 0, 'ngrp_%s' % g)

    # Capacity constraints
    for p in list(prob.projects.keys()):
        for t in range(len(prob.projects[p])):
            m.addConstr(quicksum(a[g]*x[g, p, t] for g in list(prob.groups.keys())) + slack[p, t]
                        == prob.projects[p][t][1]*y[p, t], 'ub_%s' % (t))
            m.addConstr(quicksum(a[g]*x[g, p, t] for g in list(prob.groups.keys()))
                        >= prob.projects[p][t][0]*y[p, t], 'lb_%s' % (t))
            m.addConstr(quicksum(x[g, p, t] for g in cal_G) <= 1, 'max_one_grp_%s%s' % (p, t))

    # enforce restrictions on number of teams open across different topics:
    for rest in prob.restrictions:
        m.addConstr(quicksum(y[p, t] for p in rest["topics"] for t in range(
            len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str, rest["topics"])))

    if minimax:
        # u={} # rank assigned per group
        # for g in cal_G:
        #	u[g]=m.addVar(lb=0.0,ub=max_rank,
        #		   vtype=GRB.INTEGER,
        #		   obj=0.0,
        #		   name='u_%s' % (g))
        # f=m.addVar(lb=0.0,ub=len(prob.groups.keys())*max_rank,
        #	   vtype=GRB.CONTINUOUS,
        #	   obj=0.0,
        #	   name='minimax')
        # put in u the rank assigned to the group
        #
        for g in list(prob.groups.keys()):
            m.addConstr(u[g] ==
                        quicksum(grp_ranks[g][p] * x[g, p, t] for p in list(grp_ranks[g].keys())
                                 for t in range(len(prob.projects[p]))),
                        'u_%s' % (g))
            m.addConstr(v >= u[g], 'v_%s' % g)

    if direction == "bootomup":
        l = v
        while l > h:
            # print z,v,l
            m.addConstr(z[v-l] >= quicksum(a[g] * x[g, p, t] for (g, p) in grp_x_ranks[l]
                                           for t in range(len(prob.projects[p]))), 'z_%s' % l)
            l -= 1
        m.addConstr(z_h >= quicksum(a[g] * x[g, p, t] for (g, p) in grp_x_ranks[l]
                                    for t in range(len(prob.projects[p]))), 'z_%s' % h)
    elif direction == "topdown":
        l = 1
        while l < h:
            # print z,v,l
            m.addConstr(z[l-1] <= quicksum(a[g] * x[g, p, t] for (g, p) in grp_x_ranks[l]
                                           for t in range(len(prob.projects[p]))), 'z_%s' % l)
            l += 1
        m.addConstr(z_h <= quicksum(a[g] * x[g, p, t] for (g, p) in grp_x_ranks[l]
                                    for t in range(len(prob.projects[p]))), 'z_%s' % h)
    else:
        sys.exit("something wrong in model_lex")

    # Symmetry breaking on the teams
    for p in list(prob.projects.keys()):
        for t in range(len(prob.projects[p])-1):
            m.addConstr(quicksum(x[g, p, t] for g in list(prob.groups.keys()))
                        >= quicksum(x[g, p, t+1] for g in list(prob.groups.keys())))

    ############################################################
    # instability
    if instability == True:
        for p in cal_P:
            for t in range(len(prob.projects[p])):
                for g in list(prob.groups.keys()):
                    if a[g] <= prob.projects[p][t][1]:
                        m.addConstr(slack[p, t]+1-a[g] <= prob.projects[p][t]
                                    [1]*z2[g, p, t], 'c30_%s_%s_%s' % (g, p, t))
                        m.addConstr(a[g]+1-(1-y[p, t])*prob.projects[p][t][0] <= prob.projects[p][t][1]
                                    * z2[g, p, t]+(prob.projects[p][t][1]+1)*y[p, t], 'c31_%s_%s_%s' % (g, p, t))
                    else:
                        m.addConstr(z2[g, p, t] == 0, 'c3031_%s_%s_%s' % (g, p, t))
        for g in cal_G:
            for p in list(grp_ranks[g].keys()):
                for p2 in list(grp_ranks[g].keys()):
                    if (grp_ranks[g][p2] < grp_ranks[g][p]):
                        for t in range(len(prob.projects[p])):
                            for t2 in range(len(prob.projects[p2])):
                                m.addConstr(q[g, p, t] >= (grp_ranks[g][p] - grp_ranks[g][p2])
                                            * (x[g, p, t] + z2[g, p2, t2] - 1), 'c32_%s_%s_%s' % (g, p, t))
        # m.addConstr(tot_instability >= quicksum(q[g,p,t] for g in prob.groups.keys() for p in prob.projects.keys() for t in range(len(prob.projects[p]) ) ), 'instability')
        m.addConstr(0 == quicksum(q[g, p, t] for g in list(prob.groups.keys()) for p in list(
            prob.projects.keys()) for t in range(len(prob.projects[p]))), 'instability')
        # W_instability = max_rank*len(prob.std_type.keys()) #max_rank*len(prob.groups)*len(prob.groups) ##2^7 * len(prob.groups)*
    ############################################################
    # Compute optimal solution
    if direction == "bootomup":
        m.setObjective(z_h, GRB.MINIMIZE)
    elif direction == "topdown":
        m.setObjective(z_h, GRB.MAXIMIZE)

    m.setParam("MIPGap", 0)
    m.setParam("MIPGapAbs", 0)
    m.setParam("OptimalityTol", 1e-09)
    m.setParam("Threads", 1)
    m.update()
    m.write("model.lp")
    m.optimize()
    # m.write("model-"+str(h)+".lp")
    # Print solution
    teams = {}
    topics = {}
    if m.status == GRB.status.OPTIMAL:
        for g in prob.groups:
            for p in list(prob.projects.keys()):
                for t in range(len(prob.projects[p])):
                    if x[g, p, t].x > 0.5:
                        for s in prob.groups[g]:
                            teams[s] = t
                            topics[s] = p

    z.append(z_h.x)
    return z, dict(topics=topics, teams=teams)
