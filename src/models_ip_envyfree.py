from utils import *
from load_data import *
from time import *
from gurobipy import *




def model_ip_envy(prob):
	start = clock()

	grp_ranks={}
	array_ranks={}
	max_rank = 0

	# Insieme di progetti e team
	P = prob.projects.keys()
	T = {}
	for p in P:
		T[p] = range(len(prob.projects[p]))

	# Insieme di gruppi
	G = prob.groups.keys()

	# Definisci i progetti che possono essere assegnati ad un gruppo
	V = {}
	for g in G:
		grp_ranks[g] = prob.std_ranks[prob.groups[g][0]]
		ranked_projects = grp_ranks[g].keys()
		peek=prob.std_type[prob.groups[g][0]]
		V[g]=filter(lambda x: x in ranked_projects and prob.projects[x][0][2] in prob.valid_prjtype[peek], P)

		max_g = 1 + max(map(lambda p: grp_ranks[g][p], V[g]))
		array_ranks[g] = map(lambda p: max_g if p not in V[g] else grp_ranks[g][p], P)
		max_rank = max(max_g, max_rank)

	a=dict() # the size of the group
	for g in G:
		a[g] = len(prob.groups[g])

	############################################################
	m = Model('minsumenvy')

	# Create variables
	x = {}
	for g in G:
		for p in V[g]:
			for t in T[p]:
				x[g,p,t] = m.addVar(vtype=GRB.BINARY, name='x_%s_%s_%s' % (g, p, t))

	y={}
	for p in P:
		for t in T[p]:
			y[p,t] = m.addVar(vtype=GRB.BINARY, name='y_%s_%s' % (p,t))

	e={}
	for g in G:
		e[g]=m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, obj=a[g], name='e_%s' % (g))

	m.update()

	# Assignment constraints
	for g in G:
		m.addConstr(quicksum(x[g,p,t] for p in V[g] for t in T[p]) == 1, 'grp_%s' % g)

	# Capacity constraints
	for p in P:
		# Costruisci il sottoinsieme di gruppi che contengono p
		Gp = filter(lambda g: p in V[g], G)
		# Metti il vincolo
		if Gp:
			for t in T[p]:
				m.addConstr(quicksum(a[g]*x[g,p,t] for g in Gp) <= prob.projects[p][t][1]*y[p,t], 'ub_%s' % (t))
				m.addConstr(quicksum(a[g]*x[g,p,t] for g in Gp) >= prob.projects[p][t][0]*y[p,t], 'lb_%s' % (t))

	# enforce restrictions on number of teams open across different topics:
	for rest in prob.restrictions:
		m.addConstr(quicksum(y[p,t] for p in rest["topics"] for t in range(len(prob.projects[p]))) <= rest["cum"], "rest_%s" % "-".join(map(str,rest["topics"])))


	############################################################
	# impose the envy of each student.
	for g in G:
		for h in G:
			if g != h and len(set(V[g]).intersection(set(V[h]))) > 0:
				m.addConstr(e[g] >=
						quicksum(  grp_ranks[g][p]   * x[g,p,t] for p in V[g] for t in T[p]) -
						quicksum(array_ranks[g][p-1] * x[h,p,t] for p in V[h] for t in T[p]))

	m.update()
	#m.write("envy.lp")

	############################################################
	# Compute optimal solution
	m.setParam("MIPGap",0)
	m.setParam("MIPGapAbs",0)
	m.setParam("OptimalityTol",1e-09)
	m.setParam("Threads",1)
	m.setParam("Method",4) # for deterministic behavior
	m.setParam("TimeLimit", 3600)
	m.update()
	m.optimize()

	# Print solution
	teams={}
	topics={}
	if m.status == GRB.status.OPTIMAL or GRB.status.TIME_LIMIT:
		for g in G:
			for p in V[g]:
				for t in T[p]:
					if x[g,p,t].x > 0.5:
						for s in prob.groups[g]:
							teams[s]  = t
							topics[s] = p

	elapsed = (clock() - start)
	solution = []
	solution.append(Solution(topics=topics, teams=teams, solved=[elapsed]))
	return m.getAttr("ObjVal"), solution
