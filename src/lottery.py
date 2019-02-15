
######################################################################

## Program to assign students to projects in NAT501.

## Usage: python makeGroupVersion3.py > output.

## Author : Rolf Fagerberg, February 2008, IMADA

######################################################################


###### Some design definitions for the program:

### All assignments to projects goes by groups. I.e. single students
### are singleton groups.

### All IDs (projects, groups, students) are strings. I.e. beware of
### whitespace in data files.

### Wishes are indexed starting from 0

### Groups will simply get wishlist and type from first member (sanity
### checks of uniformity within group could be added).

####### ToDos:

### Add sanity checks? E.g. are wishlists without duplets (does this
### matter?), have students in the same group the same wishlist and
### same type.

### Increase robustness by removing whitespace in proper places
### (everywhere besides project titles?)?

######################################################################

import sys, random, csv
from utils import *
from check_sol import *

def Rolfs_greedy(dirname,seed):
	verbose = False
	### global constants:
	studentfile = dirname+"/tmp_students.txt"
	priorityfile = dirname+"/tmp_priorities.txt"
	projectfile = dirname+"/tmp_projects.txt"
	typesfile = dirname+"/tmp_types.txt"
	studentfileseparator = ";"
	projectfileseparator = ";"
	outputfilestudentassignments = "studentassignments.txt"
	
	### global seeding (for repeatability):
	random.seed(seed)
	
	
	### Remove everything after first '#' in a string.
	###
	def uncommentLine(string):
	    return string.split("#",1)[0]
	
	### Read a file, return as list of lines.  Lines have first had ending
	### \n removed, have been uncommented, and then lines with only
	### whitespace have been removed.
	###
	def readFileAndClean(filename):
	    lines = open(filename).readlines()
	    lines2 = [uncommentLine(l[:-1]) for l in lines]
	    return [l for l in lines2 if l.strip()]
	
	
	
	### Read the projectfile.
	###
	### Format is a follows:
	###   pID, sub-pID (if any), title, min participants, max participants, type
	###
	### where sub-pID gives "subtitle" of dublicated projects, and type is
	### some identifier used for deciding legal student and project
	### assignments (so far, only for the benefit of
	### Laegemiddelvidenskab).
	
	# read file
	projectlines = readFileAndClean(projectfile)
	# convert lines into list of parts
	projectlist = [line.rstrip('\r\n').split(projectfileseparator)[0:5] for line in projectlines]
	# add a list of participants
	for p in projectlist:
	    p.append([])
	
	# make dictionary of projects, grouped by same pID (pID is key)
	projects = {}
	for p in projectlist:
	    pID = int(p[0])
	    if not pID in projects:
	        projects[pID] = [p]
	    else:
	        projects[pID].append(p)
	
	
	
	### Read the studentfile.
	###
	### Format is a follows:
	###   Group-ID, Student-ID, type, wishlist (comma-separated)
	###
	### Here, type is some identifier used for deciding legal student and
	### project assignments (so far, only for the benefit of
	### Laegemiddelvidenskab).
	
	
	# read file
	studentlines = readFileAndClean(studentfile)
	# convert lines into list of parts
	studentlist = [line.rstrip('\r\n').split(studentfileseparator)[0:3] for line in studentlines]
	
	prioritylines = readFileAndClean(priorityfile)
	prioritylist = [line.rstrip('\r\n').split(";")[0:4] for line in prioritylines]
	std_ranks = {}
	for row in prioritylist:
		if row[0] in std_ranks:
			std_ranks[row[0]].update(dict([(int(row[2]),row[1])]))
		else:
			std_ranks[row[0]] = dict([(int(row[2]),row[1])])
	
	# make wishlist string into list and store student info in
	# dictionary (sID is key):
	students = {}
	for [gID,sID,type] in studentlist:
		priorities=std_ranks[sID]
		w=[priorities[i] for i in range(1,len(priorities)+1)]			
		students[sID] = [gID,type,w] 
	# make dictionary of groups (gID is key)
	groups = {}
	for sID in students:
	    gID = students[sID][0]
	    if not gID in groups:
	        type = students[sID][1]
	        wishlist = students[sID][2]
	        groups[gID] = [[sID],type,wishlist]
	    else:
	        groups[gID][0].append(sID)
	
	### At this point, print the groups found.
	### First order the groupIDs to our likening (here, we currently
	### assume they are integes)
	groupkeylist = list(groups.keys())
	groupkeylist = list(map(int,groupkeylist))
	groupkeylist.sort()
	groupkeylist = list(map(str,groupkeylist))
	### Then print info for all groups
	if (verbose==True):
		print()
		print(" ** The following groups were found: ** ")
		print()
		for k in groupkeylist:
		    print("GroupID:", k)
		    print("Group type:", groups[k][1])
		    print("Student IDs:", end=' ')
		    for sID in groups[k][0]:
		        print(sID, end=' ')
		    print()
		    print("Wishlist:", end=' ')
		    for w in groups[k][2]:
		        print(w, end=' ')
		    print()
		    print()
		print()
	
	
	
	typelines = readFileAndClean(typesfile)
	typelist = [line.rstrip('\r\n').split(";") for line in typelines]
	valid_prjtypes = {}
	for row in typelist:
		valid_prjtypes[row[0].replace('"','')]=[row[t].replace('"','') for t in range(1,len(row))]

	### Function for testing if a given project type identifier is legal
	### with a given group type identifier.
	def assignmentLegal(projecttype,grouptype):
		return projecttype in valid_prjtypes[grouptype]
	
	
	### start assigning groups to projects:
	
	leftovergroups = {}
	currentWishnumber = 0
	
	# stop loop when groups is empty
	while groups:
	    # Make dictionary of groups collected according to wish number
	    # currentWishnumber. We use "groups.keys()", not just "groups", as
	    # we cannot delete from a dictionary while iterating over it
	    # (while keys() gives a *copy* of the list of keys).
	    currentWishGroups = {}
	    for gID in list(groups.keys()):
	        # if wishlist too short for currentWishnumber, give up on group
	        if len(groups[gID][2]) - 1 < currentWishnumber:
	#            leftovergroups.append([gID,groups[gID]])
	            leftovergroups[gID] = groups[gID]
	            del groups[gID]
	        # else store with other groups having same current wish
	        else:
	            groupWish = int(groups[gID][2][currentWishnumber])
	            groupSize = len(groups[gID][0])
	            if not groupWish in currentWishGroups:
	                currentWishGroups[groupWish] = [[gID,groupSize]]
	            else:
	                currentWishGroups[groupWish].append([gID,groupSize])
	
	    # now assign according to current wish number:
	    for pID in currentWishGroups:
	        # first permute randomly the groups with this wish
	        random.shuffle(currentWishGroups[pID])
	        # then try to assign interested groups in this random order
	        for [gID,groupSize] in currentWishGroups[pID]:
	            # There may be several (sub)projects of same kind.
	            # Try them sequentially until a possible assignment is found.  
	            for subProject in projects[pID]:
	                max = subProject[3]
	                currentParticipants = len(subProject[5])
	                # if asignment possible, sign group up with project,
	                # and remove from groups dict.
	                if ((groupSize <= int(max) - currentParticipants)
	                and assignmentLegal(subProject[4],groups[gID][1])):
	                    newParticipants = groups[gID][0]
	                    subProject[5].extend(newParticipants)
	                    del groups[gID]
	                    break
	
	    currentWishnumber += 1
	
	### End of assignment....
	
	
	### Print the projects with assigned students.
	### First order the projectIDs to our likening (here, we currently
	### assume they are integes)
	projectkeylist = list(projects.keys())
	projectkeylist = list(map(int,projectkeylist))
	projectkeylist.sort()
	##projectkeylist = map(str,projectkeylist)
	### Then print info for all projects
	if verbose:
		print()
		print(" ** The following project assignments were made: ** ")
		print()
		for projectkey in projectkeylist:
		    for p in projects[projectkey]:
		        print("ProjectID:", p[0]+p[1])
		        #print "Project title:", p[2]
		        print("Project type:", p[4])
		        print("Min participants:", p[2])
		        print("Max participants:", p[3])
		        print("Assigned students IDs:")
		        for sID in p[5]:
		            print("  ", sID, list(map(int,students[sID][2])))
		        print("Underfull?", len(p[5]) < int(p[3]) and "YES!" or "No.")
		        print()
		        print()
		print()
		print()
	
	
	
	
	### Print the groups not assigned to any project.
	### First order the groupIDs to our likening (here, we currently
	### assume they are integers)
	leftovergroupkeylist = list(leftovergroups.keys())
	leftovergroupkeylist = list(map(int,leftovergroupkeylist))
	leftovergroupkeylist.sort()
	leftovergroupkeylist = list(map(str,leftovergroupkeylist))
	### Then print info for all groups
	if verbose:
		print()
		print(" ** The following groups were not assigned to any project: ** ")
		print()
		for k in leftovergroupkeylist:
		    print("GroupID:", k)
		    print("Group type:", leftovergroups[k][1])
		    print("Student IDs:", end=' ')
		    for sID in leftovergroups[k][0]:
		        print(sID, end=' ')
		    print()
		    print("Wishlist:", end=' ')
		    for w in leftovergroups[k][2]:
		        print(w, end=' ')
		    print()
		    print()
		print()
		
	
	
	### Now output to a file the info per student
	###
	### Info is:
	###   StudentID, StudentType, ProjectID, ProjectTitle, ProjectType,
	###   isProjectUnderfull?, wishlistOfStudent
	
	studentassignments = []
	for projectkey in projects:
	    for p in projects[projectkey]:
	        pID = p[0]+p[1]
	        #ptitle = p[2]
	        ptype = p[4]
	        assignedstudentIDs = p[5]
	        underfull = len(p[5]) < int(p[2]) and "Underfull" or "Not underfull"
	        for sID in assignedstudentIDs:
	            wishlist = students[sID][2]
	            sType = students[sID][1]
	            studentassignments.append([sID,sType,pID,ptype,
	                                       underfull,wishlist])
	
	### put into sID order (as sID is first element of list for each student):
	studentassignments.sort()
	
	### output:
	f = open(outputfilestudentassignments,"w")
	for [sID,sType,pID,ptype,underfull,wishlist] in studentassignments:
	    wlist = ",".join(wishlist)
	    f.write("%s;%s;%s;%s;%s;%s\n" %
	            (sID,sType,pID,ptype,underfull,wlist))
	f.close()





def greedy(dirname):
	Rolfs_greedy(dirname,1)
	reader = csv.reader(open("studentassignments.txt", "r"),delimiter=";")

	topics = {}
	teams = {}
	teams_letter = 'abcdefghil'
	try:
		for row in reader:
			if row[0] in topics:
				print("smth wrong")
			else:
				nteam=teams_letter.find(row[2][-1])
				if nteam>=0:
					topics[row[0]] = int(row[2][:-1])
					teams[row[0]] = nteam+1
				else:
					topics[row[0]] = int(row[2])
					teams[row[0]] = 1
	except csv.Error as e:
		sys.exit('file %s, line %d: %s' % ("studentassignments.txt", reader.line_num, e))

	return [Solution(topics=topics,teams=teams,solved=[0])]


def repeated_random_greedy(dirname,problem):
	best_p=len(problem.groups)+len(problem.projects)
	best_sol={}
	best_log=[]
	for i in range(200):
		Rolfs_greedy(dirname,i)
		reader = csv.reader(open("studentassignments.txt", "r"),delimiter=";")

		topics = {}
		teams = {}

		teams_letter = 'abcdefghil'
		try:
			for row in reader:
				if row[0] in topics:
					print("smth wrong")
				else:
					nteam=teams_letter.find(row[2][-1])
					if nteam>=0:
						topics[row[0]] = int(row[2][:-1])
						teams[row[0]] = nteam+1
					else:
						topics[row[0]] = int(row[2])
						teams[row[0]] = 1
		except csv.Error as e:
			sys.exit('file %s, line %d: %s' % ("studentassignments.txt", reader.line_num, e))
		sol=[Solution(topics=topics,teams=teams,solved=[0])]
		log=check_sol(sol,problem,"")[0]
		penalties=log[3] +log[4]
		print("p unassigned+underfull: "+str(penalties)+" best: " + str(best_p))
		if (best_p==0):
			for j in range(len(log),5):
				if best_log[j]>log[j]:
					best_sol=sol
					best_p=penalties
					best_log=log			
		elif (penalties<best_p):
			best_sol=sol
			best_log=log
			best_p=penalties

			
	return best_sol
