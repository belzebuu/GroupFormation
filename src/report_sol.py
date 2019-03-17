#! /usr/bin/python3

# Text files required:
# students-enc.txt
# model.tbl
# sol.txt
# projects-quoted.txt
import sys
import getopt
import os
import codecs
import string
import csv
from collections import defaultdict
from load_data import Problem

studieretninger = False
# global constants:
studentfile = "students.txt"
projectfile = "projects.txt"
studentfileseparator = ";"
projectfileseparator = ";"
output1 = "out/output1.txt"
output2 = "out/output2.txt"
output3 = "out/output3.csv"
output4 = "out/output4.csv"
output5 = "out/output5.txt"
# solfile = "./sol.txt"

retning2inst = {'Biologi': "Biologisk Institut",
                "Datalogi": 'Institut for Matematik og Datalogi',
                "Matematik": 'Institut for Matematik og Datalogi',
                'Anvendt Matematik': 'Institut for Matematik og Datalogi',
                "BMB": "Institut for Biokemi og Molekylær Biologi",
                "Biokemi og Molekylær Biologi": "Institut for Biokemi og Molekylær Biologi",
                "Biomedicin": "Institut for Biokemi og Molekylær Biologi",
                "Nanobioscience": "Institut for Fysik, Kemi og Farmaci",
                'Farmaci': "Institut for Fysik, Kemi og Farmaci",
                'Kemi': "Institut for Fysik, Kemi og Farmaci",
                        'Fysik': "Institut for Fysik, Kemi og Farmaci",
                        'NAT': "Placeholder"}

for k in list(retning2inst.keys()):
    retning2inst.update({k.lower(): retning2inst[k]})


# reads the solution
# needs two files:
# model.tbl and sol.txt

# dismissed
def scansol(tablefile):
    maps = {}
    f = open(tablefile)
    lines = f.readlines()
    f.close()
    for l in lines:
        l = l.replace("\"", "")
        l = l.replace("#", "$")
        if l.find("x$") >= 0:
            l = l.replace("\n", "")
            parts = l.split("\t")
            names = parts[3].split("$")
            # print parts,names;
            maps[parts[2].strip()] = [names[1], names[2], names[3]]

    for a in list(maps.keys()):
        ass_team2std[maps[a][1]+maps[a][2]] = set()

    f = open("zpl/sol.txt")
    lines = f.readlines()
    f.close()
    for l in lines:
        l = l.replace("#", "$")
        parts = l.split()
#                print parts;
        ass[maps[parts[0]][0]] = [maps[parts[0]][1], maps[parts[0]][2]]
        ass_team2std[maps[parts[0]][1]+maps[parts[0]][2]].add(maps[parts[0]][0])


def read_solution(solfile):
    ass_std2team = {}
    ass_team2std = defaultdict(set)
    with open(solfile) as f:
        lines = f.readlines()
    for l in lines:
        l = l.replace("\n", "")
        parts = l.split("\t")
        ass_std2team[parts[0]] = [int(parts[1]), parts[2]]
        ass_team2std[parts[1]+parts[2]].add(parts[0])

    return ass_std2team, ass_team2std


def check_sol(ass_std2team, ass_team2std, prob, popularity, max_p):  # tablefile=''):

    students = list(prob.student_details.keys())
    # print groups

    counter = [0]*50
    prioritized = 0
    unassigned = 0

    for s in students:
        if s not in ass_std2team:
            unassigned = unassigned+1
            continue
        if (ass_std2team[s][0] in prob.priorities[s]):
            counter[prob.priorities[s].index(ass_std2team[s][0])] += 1
        else:
            prioritized += 1
            print("someone assigned to smth not in his priorities!")

    groups = {i: g for g in prob.groups for i in prob.groups[g]}

    # verify "same group" constraint is satisfied
    for s1 in list(ass_std2team.keys()):
        for s2 in list(ass_std2team.keys()):
            if (groups[s1] == groups[s2]):
                if (ass_std2team[s1][0] != ass_std2team[s2][0] or ass_std2team[s1][1] != ass_std2team[s2][1]):
                    print(s1, " and ", s2, "not same group:",
                          ass_std2team[s1][0], ass_std2team[s1][1], ass_std2team[s2][0], ass_std2team[s2][1])

    # start reporting

    # Print per project in std
    # and collect studnet assigned for later output
    f1 = open(output1, "w")
    f2 = open(output2, "w")
    studentassignments = []
    for i in sorted(prob.topics.keys()):
        for j in sorted(prob.topics[i]):
            pID = str(int(i))+j
            s = "ProjectID: "+pID+"\n"
            s = s + "Project title: \""+prob.project_details[pID]["ProjektTitle"]+"\""+"\n"
            s = s + "Popularity: (tot. "+str(popularity[i][0])+") " + \
                str(popularity[i][1:(max_p+1)])+"\n"
            s = s + "Project type: "+prob.project_details[pID]["ProjektType"]+"\n"
            s = s + "Min participants: "+str(prob.project_details[pID]["Min"])+"\n"
            s = s + "Max participants: "+str(prob.project_details[pID]["Max"])+"\n"
            std_assigned = pID in ass_team2std and len(ass_team2std[pID]) or 0
            prob.project_details[pID]["LedigePladser"] = prob.project_details[pID]["Max"]-std_assigned
            s = s + "Available places: "+str(prob.project_details[pID]["LedigePladser"])+"\n"
            if (prob.project_details[pID]["LedigePladser"] < 0):
                sys.exit('project %s has LedigePladser %s ' %
                         (pID, prob.project_details[pID]["LedigePladser"]))
            s = s + "Assigned students IDs:"+"\n"
            if std_assigned == 0:
                prob.project_details[pID]["ProjektStatus"] = "Not open"
            elif prob.project_details[pID]["Min"] > std_assigned:
                prob.project_details[pID]["ProjektStatus"] = "Underfull"
            else:
                prob.project_details[pID]["ProjektStatus"] = "Not underfull"

            f1.write(s)

            if (std_assigned > 0):
                f2.write("%s: %s\n" %
                         (pID,
                          prob.project_details[pID]["ProjektTitle"])
                         )

            if (prob.project_details[pID]["InstitutForkortelse"] == "IMADA"):
                print("\n"+prob.project_details[pID]["ProjektNrBB"] +
                      ": "+prob.project_details[pID]["ProjektTitle"])
                print("Popularity: (tot. "+str(popularity[i]
                                               [0])+") "+str(popularity[i][1:(max_p+1)]))

            if std_assigned > 0:
                for sID in sorted(ass_team2std[pID]):
                    f1.write("   "+sID+" "+str(prob.priorities[sID])+"\n")
                    wishlist = prob.priorities[sID]
                    sType = prob.std_type[sID]
                    f2.write("%s, %s\n" %
                             (prob.student_details[sID]["Navn"],
                              # prob.student_details[sID]["Efternavn"],
                              prob.student_details[sID]["Email"]))
                    if (prob.project_details[pID]["InstitutForkortelse"] == "IMADA"):
                        print(str(prob.student_details[sID]["Navn"])+" "+prob.student_details[sID]
                              ["Email"]+" "+str(prob.student_details[sID]["prob.prioritiesiteringsliste"]))
                # studentassignments.append([sID,sType,pID,ptitle,ptype,
                #                                                   underfull,wishlist])
            f1.write("Underfull? ")
            s = prob.project_details[pID]["Min"] > std_assigned and "Yes" or "No"
            s += (std_assigned > 0 and " " or " (Not open)")
            f1.write(str(s)+"\n")
            f1.write("\n")
            if (std_assigned > 0):
                f2.write("\n")

    f1.close()
    f2.close()
    # Now output to a file the info per student
    #
    # Info is:
    #   StudentID, StudentType, ProjectID, ProjectTitle, ProjectType,
    #   isProjectUnderfull?, wishlistOfStudent

    # put into sID order (as sID is first element of list for each student):
    studentassignments.sort()

    # output:
    f = open(output3, "w")
    #        for [sID,sType,pID,ptitle,ptype,underfull,wishlist] in studentassignments:
    #                wlist = ",".join(wishlist)
    #                f.write("%s;%s;%s;%s;%s;%s;%s\n" %
    #                                (sID,sType,pID,ptitle,ptype,underfull,wlist))
    #        f.close()

    for s in students:  # problem.groups.keys():
        prob.student_details[s]["DerfraIkkeTilladt"] = []
        peek = prob.student_details[s]["StudType"]
        # d={'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]} # which projects for students
        valid_prjs = [x for x in sorted(prob.topics.keys()) if prob.project_details[str(
            x)+prob.topics[x][0]]["MinProjektType"] in prob.valid_prjtype[peek]]
        # valid_prjs=filter(lambda x: prob.project_details[str(x)+prob.topics[x][0]]["MinProjektType"]==peek or prob.project_details[str(x)+prob.topics[x][0]]["ProjektType"]=='alle', sorted(prob.topics.keys()))
        # print set(prob.student_details[s]["prob.prioritiesiteringsliste"])
        diff = set(prob.student_details[s]["PrioriteringsListe"]) - set(valid_prjs)
        if len(diff) > 0:
            tmp = []
            for p in diff:
                tmp.append(p)
            prob.student_details[s]["DerfraIkkeTilladt"] = tmp

    f.write("Brugernavn;StudType;ProjektNr;Undergruppe;ProjektTitel;ProjektType;TildeltPrio;PrioriteringsListe;DerfraIkkeTilladt;Min;Max;")
    f.write("LedigePladser;Navn;Email;GruppeID;Tilmeldingstidspunkt;Institutforkortelse;")
    f.write("Institut;Minikursus obligatorisk;Gruppeplacering\n")
    students.sort()
    for s in students:
        pID = str(int(ass_std2team[s][0]))+ass_std2team[s][1]
        # print pID;
        priolist = prob.student_details[s]["Prioriteringsliste"]
        valgt = [x for x in range(1, len(priolist)+1) if int(priolist[x-1])
                 == int(prob.project_details[pID]["ProjektNr"])]
        gottenprio = '%s' % ', '.join(map(str, valgt))
        f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %
                (
                    prob.student_details[s]["Brugernavn"],
                    prob.student_details[s]["StudType"],
                    prob.project_details[pID]["ProjektNr"],
                    prob.project_details[pID]["Undergruppe"],
                    prob.project_details[pID]["ProjektTitle"],
                    prob.project_details[pID]["ProjektType"],
                    # prob.project_details[pID]["ProjektStatus"],
                    gottenprio,
                    str(prob.student_details[s]["Prioriteringsliste"]),
                    prob.student_details[s]["DerfraIkkeTilladt"],
                    prob.project_details[pID]["Min"],
                    prob.project_details[pID]["Max"],
                    prob.project_details[pID]["LedigePladser"],
                    # prob.project_details[pID]["ProjektNrBB"],
                    # prob.student_details[s]["CprNr"],
                    # prob.student_details[s]["Fornavne"],
                    prob.student_details[s]["Navn"],
                    prob.student_details[s]["Email"],
                    prob.student_details[s]["GruppeID"],
                    prob.student_details[s]["Tilmeldingstidspunkt"],
                    prob.project_details[pID]["InstitutForkortelse"],
                    # prob.project_details[pID]["Institut"],
                    prob.project_details[pID]["Minikursus_obl"],
                    # # prob.project_details[pID]["Minikursus_anb"],
                    prob.project_details[pID]["Gruppeplacering"]))
    f.close()

    # Now summarise
    # in std output
    count_teams = 0
    count_prj = 0

    for i in sorted(prob.topics.keys()):
        prj = 0
        for j in sorted(prob.topics[i]):
            pID = str(int(i))+j
            std_assigned = len(ass_team2std[pID]) if pID in ass_team2std else 0
            if std_assigned > 0:
                count_teams += 1
                prj = 1
        count_prj += prj

    s = "\n\nNumb. of students: "+str(len(students))
    s = s+"\nNumb. of active topics/topics offered: "+str(count_prj)+"/"+str(len(prob.topics))
    s = s+"\nNumb. of active teams/teams offered: " + \
        str(count_teams)+"/"+str(len(prob.project_details))
    s = s+"\nStudents unassigned: "+str(unassigned)
    s = s+"\nStudents assigned outside of preference: "+str(prioritized)+"\n"
    for i in range(max_p):
        out = str(i+1)+". priority: students "+str(counter[i])
        s = s+out+"\n"

    print(s)
    f = open(output1, "a")
    f.write(s)
    f.close()


def count_popularity(prob):
    f = open(output4, "w")
    popularity = {}
    max_p = 0
    students = list(prob.student_details.keys())
    for s in students:
        if (len(prob.priorities[s]) > max_p):
            max_p = len(prob.priorities[s])
    for i in sorted(prob.topics.keys()):
        popularity[i] = [0]*(max_p+1)
    for s in students:
        for i in range(len(prob.priorities[s])):
            pId = prob.priorities[s][i]
            if pId not in prob.topics:
                continue  # pId = int(prob.priorities[s][i])
            popularity[pId][0] += 1
            popularity[pId][i+1] += 1
    for i in sorted(prob.topics.keys()):
        pID = str(int(i))+prob.topics[i][0]
        f.write(str(i)+";\""+prob.project_details[pID]["ProjektTitle"]+"\";")
        f.write(prob.project_details[pID]["ProjektType"]+";" +
                prob.project_details[pID]["InstitutForkortelse"]+";")
        for j in range(0, (max_p+1)):
            f.write(str(popularity[i][j])+";")
        f.write("\n")
    f.close()
    return popularity, max_p


def institute_wise():
    f = open(output5, "w")
    pIDs_per_institute = {}
    pIDs = []
    for i in sorted(prob.topics.keys()):
        for j in sorted(prob.topics[i]):
            pIDs += [str(int(i))+j]

    institutes = set([prob.project_details[x]["Institut"] for x in pIDs])
    # print institutes
    pIDs_per_institute = {i: [x for x in pIDs if prob.project_details[x]
                              ["Institut"] == i] for i in institutes}
    topics_per_institute = {i: [x for x in sorted(prob.topics.keys()) if prob.project_details[str(
        x)+prob.topics[x][0]]["Institut"] == i] for i in institutes}
    print(pIDs_per_institute)
    print(topics_per_institute)

    for i in sorted(institutes):
        tot_per_institute = 0
        istr = "\n"+"["+i+"] "
        tmp = istr
        f.write("##########################################################################################\n")
        for pID in pIDs_per_institute[i]:
            std_assigned = pID in ass_team2std and len(ass_team2std[pID]) or 0
            if std_assigned > 0:
                s = istr+prob.project_details[pID]["ProjektNrBB"] + \
                    ": "+prob.project_details[pID]["ProjektTitle"]
                # # print "Popularity: (tot. "+str(popularity[i][0])+") "+str(popularity[i][1:(max_p+1)]);
                f.write(s+"\n")
                assigned = 0
                for sID in sorted(ass_team2std[pID]):
                    s = str(prob.student_details[sID]["Brugernavn"])+" " + \
                        str(prob.student_details[sID]["prob.prioritiesiteringsliste"])
                    # f.write(s+"\n")
                    assigned = assigned+1
                    if i != retning2inst[prob.student_details[sID]["Studieretning"]]:
                        tmp += "\nX\t"+sID+" "+pID+" "+prob.student_details[sID]["Studieretning"]
                f.write("Std assigned: "+str(assigned)+"\n")
                tot_per_institute = tot_per_institute+assigned
        f.write(istr + "Tot std assigned: "+str(tot_per_institute)+"\n\n")
        print((tmp + " \nTot std assigned: "+str(tot_per_institute)))
    f.close()        #
    print("Written "+output5)

    # 'Institut for Matematik og Datalogi': [2, 3, 15, 28, 52, 58, 62, 68, 72, 77, 80, 92],
    del topics_per_institute['Institut for Matematik og Datalogi']
    topics_per_institute['IMADA Mat'] = [27, 86, 52, 4, 63, 71, 31, 55, 13, 92]
    topics_per_institute['IMADA Dat'] = [15, 78, 95, 1, 81, 26, 40, 12, 17, 14, 77, 60]
    fields = set([prob.student_details[s]["Studieretning"] for s in prob.student_details])
    # fields=topics_per_institute.keys()
    print(topics_per_institute)
    shorten = {"Biologisk Institut": "Biologi",
               "IMADA Dat": "IMADA-Dat",
               "IMADA Mat": "IMADA-Mat",
               "Institut for Biokemi og Molekylær Biologi": "BMB",
               "Institut for Fysik, Kemi og Farmaci": "FKF",
               "Institut for Sundhedstjenesteforskning": "Sund"}
    students_per_institute = {}

    matrix = {r: {c: 0 for c in list(topics_per_institute.keys())} for r in fields}
    # print(matrix)
    for s in prob.student_details:
        # print prob.student_details[s]["prob.prioritiesiteringsliste"][:3]
        shared = {}
        lshared = {}
        for i in sorted(topics_per_institute.keys()):
            shared[i] = [v for v in topics_per_institute[i]
                         if v in prob.student_details[s]["prob.prioritiesiteringsliste"][:5]]
            lshared[i] = len(shared[i])
            # print s+" "+', '.join(map(str,shared[i]))+" "+i
            # print s+" "+str(len(shared[i]))+" "+i
        m = max([len(shared[x]) for x in shared])
        std_retning = prob.student_details[s]["Studieretning"] if "Studieretning" in prob.student_details[s] else filter(
            lambda x: len(shared[x]) == m, fields)[0]
        # print m,std_retning
        for k in topics_per_institute:
            matrix[std_retning][k] = matrix[std_retning][k]+lshared[k]
        students_per_institute.update({std_retning: {s: lshared}})
    # print students_per_institute
    print(matrix)
    # print map(lambda k: ', '.join(map(lambda x : str(matrix[k][x]), matrix.keys())) ,  matrix.keys())
    f = open("www/data/pref.csv", "w")
    f.write("From,To,count\n")
    for k in fields:
        for c in list(topics_per_institute.keys()):
            # print '\"'+shorten[k]+'\",\"'+shorten[c]+'\",'+str(matrix[k][c])
            f.write('\"'+k+'\",\"'+shorten[c]+'\",'+str(matrix[k][c])+"\n")
    f.close()

    stds_per_retning = {
        f: len([s for s in prob.student_details if prob.student_details[s]["Studieretning"] == f]) for f in fields}
    print(stds_per_retning)


def main(argv):
    dirname = "."
    tablefile = ""
    #
    #        parser = argparse.ArgumentParser(description='Create a file prob.prioritiesities.txt containing weighted prob.prioritiesities.')
    #        parser.add_argument('--dir', dest='dirname', action='store',
    #                                                help='the directory where the data are to be found')
    #
    #        args = parser.parse_args()
    #        print args.dirname()
    #
    try:
        opts, args = getopt.getopt(argv, "hd:t:s:", ["help", "dir=", "tbl=", "sol="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if (len(opts) < 1):
        usage()
    tablefile = ''
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dir"):
            dirname = arg
        elif opt in ("-s", "--sol"):
            solfile = arg
        elif opt in ("-t", "--tbl"):
            tablefile = arg
        else:
            print(opt+" Not recognised\n")
            usage()

    problem = Problem(dirname)
    ass_std2team, ass_team2std = read_solution(solfile)
    popularity, max_p = count_popularity(problem)
    check_sol(ass_std2team, ass_team2std, problem, popularity, max_p)  # tablefile)
    # institute_wise()


def usage():
    print("Check sol and writes three output files\n")
    print("Usage: [\"help\", \"dir=\"]\n")
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
