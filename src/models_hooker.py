from utils import *
from load_data import *
from time import *
from gurobipy import *


def model_hooker(prob,Tau, instability):
	start = clock()
	m = Model('hooker')

	cal_P = list(prob.projects.keys())
	cal_G = list(prob.groups.keys())
	grp_ranks={}
	max_rank=0
	for g in list(prob.groups.keys()):
		s=prob.groups[g][0] # we consider only first student, the other must have equal prefs
		grp_ranks[g]=prob.std_ranks[s]
		if len(grp_ranks[g]) > max_rank:
			max_rank=len(grp_ranks[g])

	a=dict() # the size of the group
	for g in list(prob.groups.keys()):
		a[g] = len(prob.groups[g])

	############################################################
	# Create variables
	x = {} ## assignment vars
	for g in list(prob.groups.keys()):
		for p in list(prob.projects.keys()):
			for t in range(len(prob.projects[p])):
				x[g,p,t] = m.addVar(lb=0.0,ub=1.0,
						  vtype=GRB.BINARY,
						  obj=0.0,
						  name='x_%s_%s_%s' % (g, p, t))

	y={} ## is team t of project p used?
	for p in list(prob.projects.keys()):
		for t in range(len(prob.projects[p])):
			y[p,t] = m.addVar(lb=0.0,ub=1.0,
					  vtype=GRB.BINARY,
					  obj=0.0,
					  name='y_%s_%s' % (p,t))
	slack={} ## slack in team t of project p
	for p in list(prob.projects.keys()):
		for t in range(len(prob.projects[p])):
			slack[p,t] = m.addVar(lb=0.0,ub=10.0,
					      vtype=GRB.CONTINUOUS,
					      obj=0.0,
					      name='slack_%s_%s' % (p,t))

	v={} # rank assigned per group
	for g in list(prob.groups.keys()):
		v[g]=m.addVar(lb=0.0,ub=max_rank,
			   vtype=GRB.INTEGER,
			   obj=0.0,
			   name='v_%s' % (g))

	f=m.addVar(lb=-GRB.INFINITY,#lb=0.0,ub=len(prob.std_ranks)*max_rank,
		   vtype=GRB.CONTINUOUS,
		   obj=1.0,
		   name='f')

	M=8
	u={}
	for g in list(prob.groups.keys()):
		u[g]=m.addVar(lb=0,
			       #lb=-GRB.INFINITY,
			       ub=GRB.INFINITY,
			   vtype=GRB.CONTINUOUS,
			   obj=0.0,
			   name='u_%s' % (g))

	xi={}
	for k in list(prob.groups.keys()):
           xi[k]=m.addVar(#lb=0.0,ub=1.0,
		   vtype=GRB.BINARY,
		   obj=0.0,
		   name='xi_%s' % (k))


	#omega=m.addVar(lb=-GRB.INFINITY,ub=+GRB.INFINITY,
	#			vtype=GRB.CONTINUOUS,
	# 			obj=0.0,
	#  	 		name='omega')

	zeta=m.addVar(vtype=GRB.CONTINUOUS, obj=0.0, name='zeta')

    ############################################################
	if instability==True:
		z={} # binary variable to indicate whether there is space left in a team
		q={} # counts if space free in some better project
		for p in list(prob.projects.keys()):
			for t in range(len(prob.projects[p])):
				for g in list(prob.groups.keys()):
					z[g,p,t] = m.addVar(lb=0.0,ub=1.0,
									vtype=GRB.BINARY,
									obj=0.0,
									name='z_%s_%s_%s' % (g,p,t))
					q[g,p,t]=m.addVar(lb=0.0,ub=max_rank,
								 vtype=GRB.CONTINUOUS,
								 obj=0.0,
								 name='q_%s_%s_%s' % (g,p,t))
		# the total instability
		tot_instability=m.addVar(lb=0.0,ub=len(list(prob.groups.keys()))*max_rank,
			   vtype=GRB.CONTINUOUS,
			   obj=1.0,
			   name='tot_instability')
	else:
		instability=0
		W_instability=0
	############################################################
	m.update()
	############################################################
	# Assignment constraints
	#for g in prob.groups.keys():
		#working=[x[g,p,t] for p in prob.projects.keys() for t in range(len(prob.projects[p]))]
		#m.addConstr(quicksum(working) == 1, 'grp_%s' % g)


	# Assignment constraints
	for g in cal_G:
		peek=prob.std_type[prob.groups[g][0]]
		valid_prjs=[x for x in cal_P if prob.projects[x][0][2] in prob.valid_prjtype[peek]]
		#valid_prjs=filter(lambda x: prob.projects[x][0][2]==peek or prob.projects[x][0][2]=='alle', prob.projects.keys())

		working=[x[g,p,t] for p in valid_prjs for t in range(len(prob.projects[p]))]
		m.addConstr(quicksum(working) == 1, 'grp_%s' % g)
		for p in cal_P:
			if not p in valid_prjs:
				for t in range(len(prob.projects[p])):
					m.addConstr(x[g,p,t] == 0, 'ngrp_%s' % g)
			if not p in prob.std_ranks[prob.groups[g][0]]:
				for t in range(len(prob.projects[p])):
					m.addConstr(x[g,p,t] == 0, 'ngrp_%s' % g)

	# Capacity constraints
	for p in list(prob.projects.keys()):
		for t in range(len(prob.projects[p])):
			m.addConstr(quicksum(a[g]*x[g,p,t] for g in list(prob.groups.keys())) + slack[p,t]
				    == prob.projects[p][t][1]*y[p,t], 'ub_%s' % (t))
			m.addConstr(quicksum(a[g]*x[g,p,t] for g in list(prob.groups.keys()))
				    >= prob.projects[p][t][0]*y[p,t], 'lb_%s' % (t))

	# enforce restrictions on number of teams open across different topics:
	for rest in prob.restrictions:
		m.addConstr(quicksum(y[p,t] for p in rest["topics"] for t in range(len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str,rest["topics"])))

	# put in v the rank assigned to the group
	for g in list(prob.groups.keys()):
		m.addConstr(v[g]==
			    quicksum(grp_ranks[g][p] * x[g,p,t] for p in list(grp_ranks[g].keys()) for t in range(len(prob.projects[p]))),
			    'v_%s' % (g))


	# Symmetry breaking on the teams
	for p in list(prob.projects.keys()):
		for t in range(len(prob.projects[p])-1):
			m.addConstr(quicksum(x[g,p,t] for g in list(prob.groups.keys())) >= quicksum(x[g,p,t+1] for g in list(prob.groups.keys()))   )


	############################################################
	# Hooker part
	#for p in prob.projects.keys():
	mm = sum([a[g] for g in prob.groups])
	#m.addConstr(f >= (1-mm) * Tau + mm*(max_rank-zeta) + quicksum(a[g]*u[g] for g in prob.groups.keys()),'f')
	m.addConstr(f >= (1-mm) * Tau + quicksum(a[k]*u[k] for k in list(prob.groups.keys())),'f')
#	m.addConstr(f <= z,'fz')
	for k in prob.groups:
		m.addConstr(Tau * xi[k] + v[k] <= u[k])
		m.addConstr(u[k] <= Tau + v[k])
		m.addConstr((Tau-max_rank)*xi[k] + zeta <= u[k])
		m.addConstr(u[k] <= zeta)

	for k in list(prob.groups.keys()):
		m.addConstr(zeta >= v[k])

#                tmp = sum(map(lambda g: a[g], prob.groups)) - 1
##		m.addConstr(f >= tmp * Tau + quicksum(a[g]*u[g] for g in prob.groups.keys()),'f')
##		for g in prob.groups.keys():
##                        m.addConstr(u[g] >= v[g]-(Tau-M)*delta[g])
##                        m.addConstr(u[g] <= v[g]-(Tau-M) )
##
##                for g in prob.groups.keys():
##                        m.addConstr(u[g] >= omega-Tau*delta[g]   )
##                        m.addConstr(u[g] <= omega  )

	############################################################
	# instability
	if instability==True:
		for p in cal_P:
			for t in range(len(prob.projects[p])):
				for g in list(prob.groups.keys()):
					if a[g]<=prob.projects[p][t][1]:
						m.addConstr(slack[p,t]+1-a[g]<= prob.projects[p][t][1]*z[g,p,t], 'c30_%s_%s_%s' % (g,p,t))
						m.addConstr(a[g]+1-(1-y[p,t])*prob.projects[p][t][0] <= prob.projects[p][t][1]*z[g,p,t]+(prob.projects[p][t][1]+1)*y[p,t], 'c31_%s_%s_%s' % (g,p,t))
					else:
						m.addConstr(z[g,p,t]==0, 'c3031_%s_%s_%s' % (g,p,t))
		for g in cal_G:
			for p in list(grp_ranks[g].keys()):
				for p2 in list(grp_ranks[g].keys()):
					if (grp_ranks[g][p2] < grp_ranks[g][p]):
						for t in range(len(prob.projects[p])):
							for t2 in range(len(prob.projects[p2])):
								m.addConstr(q[g,p,t] >= (grp_ranks[g][p] - grp_ranks[g][p2]) * (x[g,p,t] + z[g,p2,t2] - 1), 'c32_%s_%s_%s' % (g,p,t))
		#m.addConstr(tot_instability >= quicksum(q[g,p,t] for g in prob.groups.keys() for p in prob.projects.keys() for t in range(len(prob.projects[p]) ) ), 'instability')
		m.addConstr(0 == quicksum(q[g,p,t] for g in list(prob.groups.keys()) for p in list(prob.projects.keys()) for t in range(len(prob.projects[p]) ) ), 'instability')
		#W_instability = max_rank*len(prob.std_type.keys()) #max_rank*len(prob.groups)*len(prob.groups) ##2^7 * len(prob.groups)*
	############################################################
	# Compute optimal solution
	#m.setObjective(f + W_instability * instability,GRB.MINIMIZE)
	m.setObjective(f)
#	m.setParam("MIPGap",0)
#	m.setParam("MIPGapAbs",0)
#	m.setParam("OptimalityTol",1e-09)
	m.setParam("Threads",1)
	m.setParam("TimeLimit", 3600)
	#m.setParam("NodefileStart", 2)
	m.update()
	m.write("model.lp")
	m.optimize()
#
#        for var in m.getVars():
#            print var.varName, var.VType, var.getAttr(GRB.Attr.X)
#
#        sys.exit()
##	# Print solution
	teams={}
	topics={}
	if m.status == GRB.status.OPTIMAL or GRB.status.TIME_LIMIT:
		for g in prob.groups:
			for p in list(prob.projects.keys()):
				for t in range(len(prob.projects[p])):
					if x[g,p,t].x > 0.5:
						for s in prob.groups[g]:
							teams[s]=t
							topics[s]=p
	elapsed = (clock() - start)
	solution = []
	solution.append(Solution(topics=topics,teams = teams, solved=[elapsed]))
	return solution
