#! /usr/bin/python3
# coding=utf-8

import sys
import getopt
import os
import codecs
import string
import csv
import json
import pandas as pd
from collections import defaultdict
from collections import OrderedDict
from load_data import Problem


output1 = os.path.join("out", "output1")
output2 = "out/output2.txt"
output3 = "out/output3.csv"
output4 = "out/output4.csv"
output5 = "out/output5.txt"


def read_solution(solfile):
    ass_std2team = {}
    ass_team2std = defaultdict(set)
    with open(solfile) as f:
        lines = f.readlines()
    for l in lines:
        l = l.replace("\n", "")
        parts = l.split("\t")
        ass_std2team[parts[0]] = (int(parts[1]), parts[2])
        ass_team2std[parts[1]+parts[2]].add(parts[0])

    return ass_std2team, ass_team2std


def check_sol(ass_std2team, ass_team2std, prob, max_p):  # tablefile=''):
    isok = True
    for s in prob.student_details.keys():
        if s not in ass_std2team:
            isok = False
            print(s+" not assigned!")
        elif (ass_std2team[s][0] not in prob.priorities[s]):
            isok = False
            print(s+" assigned to smth not in his priorities!")

    groups = {i: g for g in prob.groups for i in prob.groups[g]}

    # verify "same group" constraint is satisfied
    for s1 in list(ass_std2team.keys()):
        for s2 in list(ass_std2team.keys()):
            if (groups[s1] == groups[s2]):
                if (ass_std2team[s1][0] != ass_std2team[s2][0] or ass_std2team[s1][1] != ass_std2team[s2][1]):
                    isok = False
                    print(s1, " and ", s2, "not same group:",
                          ass_std2team[s1][0], ass_std2team[s1][1], ass_std2team[s2][0], ass_std2team[s2][1])

    return isok


def project_table(ass_std2team, ass_team2std, popularity, max_p, prob):
    # start reporting

    # Print per project in std
    # and collect student assigned for later output

    f2 = open(output2, "w")
    studentassignments = []
    project_details = OrderedDict()
    for i in sorted(prob.topics.keys()):
        for j in sorted(prob.topics[i]):
            pID = str(int(i))+j
            project_details[pID] = prob.project_details[pID]
            project_details[pID]["popularity_tot"] = popularity[i][0]
            project_details[pID]["popularity_details"] = str(popularity[i][1:(max_p+1)])
            std_assigned = len(ass_team2std[pID]) if pID in ass_team2std else 0
            project_details[pID]["places_available"] = prob.project_details[pID]["max_cap"]-std_assigned
            if (project_details[pID]["places_available"] < 0):
                sys.exit('project %s has places_available %s ' %
                         (pID, project_details[pID]["places_available"]))
            if std_assigned == 0:
                project_details[pID]["team_status"] = "Not open"
            elif prob.project_details[pID]["max_cap"] > std_assigned:
                project_details[pID]["team_status"] = "Underfull"
            else:
                project_details[pID]["team_status"] = "Full"

            project_details[pID]["assigned"] = []
            if (std_assigned > 0):
                f2.write("%s: %s\n" %
                         (pID,
                          project_details[pID]["title"])
                         )
                for sID in sorted(ass_team2std[pID]):
                    project_details[pID]["assigned"].append(sID)
                    f2.write("%s, %s, %s\n" %
                             (prob.student_details[sID]["email"],
                              # prob.student_details[sID]["Efternavn"],
                              prob.student_details[sID]["full_name"],
                              prob.student_details[sID]["priority_list"]))
                f2.write("\n")

    f2.close()

    with codecs.open(output1+".json",  "w", "utf-8") as filehandle:
        json.dump(project_details, fp=filehandle, sort_keys=True,
                  indent=4, separators=(',', ': '),  ensure_ascii=False)

    table = pd.DataFrame.from_dict(project_details, orient='index')
    table.to_csv(output1+".csv")


def student_table(prob):
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
        peek = prob.student_details[s]["type"]
        # d={'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]} # which projects for students
        valid_prjs = [x for x in sorted(prob.topics.keys()) if prob.project_details[str(
            x)+prob.topics[x][0]]["type"] in prob.valid_prjtype[peek]]
        # valid_prjs=filter(lambda x: prob.project_details[str(x)+prob.topics[x][0]]["MinProjektType"]==peek or prob.project_details[str(x)+prob.topics[x][0]]["ProjektType"]=='alle', sorted(prob.topics.keys()))
        # print set(prob.student_details[s]["prob.prioritiesiteringsliste"])
        diff = set(prob.student_details[s]["PrioriteringsListe"]) - set(valid_prjs)
        if len(diff) > 0:
            tmp = []
            for p in diff:
                tmp.append(p)
            prob.student_details[s]["DerfraIkkeTilladt"] = tmp

    f.write("Brugernavn;StudType;ProjektNr;Undergruppe;ProjektTitel;ProjektType;ProjektStatus;TildeltPrio;PrioriteringsListe;DerfraIkkeTilladt;Min;Max;")
    f.write("LedigePladser;Navn;Email;GruppeID;Tilmeldingstidspunkt;Institutforkortelse;")
    f.write("Institut;Minikursus obligatorisk;Gruppeplacering\n")
    students.sort()
    for s in students:
        pID = str(int(ass_std2team[s][0]))+ass_std2team[s][1]
        # print pID;
        priolist = prob.student_details[s]["priority_list"]
        valgt = [x for x in range(1, len(priolist)+1) if int(priolist[x-1])
                 == int(prob.project_details[pID]["ProjektNr"])]
        gottenprio = '%s' % ', '.join(map(str, valgt))
        f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %
                (
                    prob.student_details[s]["Brugernavn"],
                    prob.student_details[s]["StudType"],
                    prob.project_details[pID]["ProjektNr"],
                    prob.project_details[pID]["Undergruppe"],
                    prob.project_details[pID]["ProjektTitle"],
                    prob.project_details[pID]["ProjektType"],
                    prob.project_details[pID]["ProjektStatus"],
                    gottenprio,
                    str(prob.student_details[s]["PrioriteringsListe"]),
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


def summarize(ass_std2team, ass_team2std, max_p, prob):
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

    counter = [0]*max_p
    unprioritized = 0
    unassigned = 0

    for s in prob.student_details.keys():
        if s not in ass_std2team:
            unassigned = unassigned+1
            continue
        if (ass_std2team[s][0] in prob.priorities[s]):
            counter[prob.priorities[s].index(ass_std2team[s][0])] += 1
        else:
            unprioritized += 1

    s = "\n\nNumb. of students: "+str(len(prob.student_details))
    s = s+"\nNumb. of active topics/topics offered: "+str(count_prj)+"/"+str(len(prob.topics))
    s = s+"\nNumb. of active teams/teams offered: " + \
        str(count_teams)+"/"+str(len(prob.project_details))
    s = s+"\nStudents unassigned: "+str(unassigned)
    s = s+"\nStudents assigned outside of preference: "+str(unprioritized)+"\n"
    for i in range(max_p):
        out = str(i+1)+". priority: students "+str(counter[i])
        s = s+out+"\n"

    print(s)
    #f = open(output1, "a")
    # f.write(s)
    # f.close()


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
        f.write(str(i)+";\""+prob.project_details[pID]["title"]+"\";")
        f.write(prob.project_details[pID]["type"]+";" +
                prob.project_details[pID]["instit"]+";")
        for j in range(0, (max_p+1)):
            f.write(str(popularity[i][j])+";")
        f.write("\n")
    f.close()
    return popularity, max_p


def main(argv):
    dirname = "."
    tablefile = ""

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
    if not check_sol(ass_std2team, ass_team2std, problem, max_p):
        sys.exit("Solution infeasible")
    project_table(ass_std2team, ass_team2std, popularity, max_p, problem)
    # institute_wise()
    # student_table(problem)
    summarize(ass_std2team, ass_team2std, max_p, problem)


def usage():
    print("Check sol and writes three output files\n")
    print("Usage: [\"help\", \"dir=\"]\n")
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
