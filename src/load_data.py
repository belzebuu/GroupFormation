#! /usr/bin/python
# import argparse; # only from python 2.7
import sys
import os
import csv
import json
from collections import defaultdict
from collections import OrderedDict

class Problem:
    def __init__(self, dirname, group_reg):
        self.projects=self.read_projects(dirname),
        self.std_values=self.read_students(dirname)[0],
        self.std_ranks=self.read_students(dirname)[1],
        self.groups=self.read_groups(dirname, group_reg)[0],
        self.std_type=self.read_groups(dirname, group_reg)[1],
        #self.minimax_sol = self.minimax_sol(dirname),
        self.valid_prjtype = self.valid_prjtype(dirname),
        self.restrictions=self.read_restrictions(dirname)
        self.minimax_sol = 0
        # self.__dict__.update(kwds)


    def program_transform(self, program):
        study_programs = ["anvendt matematik", "biokemi og molekylær biologi", "biologi", "biomedicin", "datalogi", "farmaci","fysik","kemi", "matematik", "psychology"]
        program = program.lower()
        if program not in study_program:
            sys.exit("program not recognized: {}".format(program))
        return program


    def read_projects(self, dirname):
        projects_file=dirname+"/projects.csv"
        print("read ",projects_file)

        with open(dirname+"/projects.csv", "r", encoding="utf-8") as f:
                lines=f.readlines();

        topics = {}
        project_details = {}
        for line in lines:
            if line[0]=="#": continue
            line=line.rstrip('\r\n');
            parts=line.split(";");
            nid = int(parts[0]);
            if (nid in list(topics.keys())):
                topics[nid]=topics[nid]+[parts[1]];
            else:
                topics[nid]=[parts[1]];
            id=parts[0]+parts[1];

                #MinProjektType="natbidat" if parts[5].lower()=="naturvidenskab, biologi og datalogi" else parts[5].lower()
                #MinProjektType="farmaci" if string.find(MinProjektType.lower(),"farma",0,5) >= 0 else MinProjektType.lower()
            MinProjektType=self.program_transform(parts[5])

            project_details[id]=dict(
                        ProjektNr=parts[0],
                        Undergruppe=parts[1],
                        ProjektTitle=parts[2].strip("\r\n\""),
                        Min=int(parts[3]),
                        Max=int(parts[4]),
                        ProjektType=parts[5].lower(),
                        MinProjektType=MinProjektType,
                        ProjektNrBB=(len(parts)>6 and parts[6] or ""),
                        Institutforkortelse=(len(parts)>6 and parts[7] or ""),
                        Institut=(len(parts)>6 and parts[8] or ""),
                        Minikursus_obl=(len(parts)>6 and parts[9] or ""),
                        # Minikursus_anb=(len(parts)==12 and parts[10] or ""),
                        Gruppeplacering=(((len(parts)>6 and len(parts)==12) and parts[11]) or (len(parts)>6 and parts[10]) or "") # to take into account format before 2012
                        )
        
        capacity = sum([project_dict[k]["Max"] for k in project_dict])
        n_stds=10
        if (capacity < n_stds):
            answer = input("Not enough capacity from all projects\nHandle this by including a dummy project with the needed capacity? (y/n)\n")
        if answer in ['Y','y']:
            sys.exit("to implement")
            file.write(str(len(project_dict)+1)+";;1;"+str(n_stds-capacity)+";"+program+"\n");
            project_dict[len(project_dict)+1]=n_stds-capacity
            
        filehandle = codecs.open( os.path.join("log", "projects.json"),  "w","utf-8")
        json.dump(project_details, fp=filehandle, sort_keys=True, indent=4, separators=(',', ': '),  ensure_ascii=False)
        
        projects = defaultdict(list)
        
        Team = namedtuple("Team",("min","min","type"))
        for topic in topics:
            for t in topics[topic]:
                id = topic+t
                projects[topic].append(Team(project_details[id]["Min"],
                                        project_details[id]["Max"],
                                        project_details[id]["MinProjektType"]
                                        )
        return topics, project_details, projects



def write_projects(dirname, n_stds):


    project_dict={}
    file=open(dirname+"/tmp_projects.txt",'w');
    for line in lines:
        if line[0]=="#": continue
        line=line.strip("\r\n");
        parts=line.split(";");
        program = program_transform(parts[5].lower())
        file.write(parts[0]+";"+parts[1]+";"+parts[3]+";"+parts[4]+";"+program+"\n");
        project_dict[parts[0]]=int(parts[4])


    file.close();
    print("wrote tmp_projects.txt\n")
    return project_dict






def read_students(dirname):
        with open(dirname+"/students.csv", "r") as f:
                lines=f.readlines();

        ## print type_compatibility

        global prior;
        global groups;
        for line in lines:
                if line[0]=="#": continue
                line=line.strip('\r\n');
                parts=line.split(";");
                priorities=parts[3].split(",");
                username=parts[1].lower()
                nid=parts[0]
                studtype=parts[2].lower()
                prior[username]=priorities;
                groups[username]=[nid,studtype];

                student_details[username]=dict(
                        GruppeID=nid,
                        Brugernavn=username,
                        StudType=studtype,
                        Studieretning=studtype,
                        Prioriteringsliste=[int(x) for x in parts[3].split(",")],
                        CprNr=(len(parts)>4 and parts[4] or ""),
                        #Fornavne=(len(parts)>4 and parts[5] or ""),
                        #Efternavn=(len(parts)>4 and parts[6] or ""),
                        Navn=(len(parts)>4 and parts[5] or ""),
                        Email=(len(parts)>4 and parts[6] or ""),
                        Tilmeldingstidspunkt=(len(parts)>4 and parts[7] or "")
                        );

        if studieretninger:
                reader = csv.reader(open(dirname+"/Studieretninger2014.csv", "rb"),delimiter=",")
                rheader=False
                try:
                        for row in reader:
                                if not rheader:
                                        rheader=True
                                        continue;
                                username=row[2].split("@")[0].lower()
                                if username in student_details:
                                        student_details[username]["Studieretning"]=row[3]
                                ## print username,student_details[username];
                except csv.Error as e:
                        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
        elif False:
                for username in student_details:
                        student_details[username]["Studieretning"]="NAT"

def write_students(dirname):
    print("read students.csv")
    students_file=dirname+"/students.csv";
    f = open(students_file, "r")
    lines=f.readlines();
    f.close();

    students_file=dirname+"/tmp_students.txt";
    file=open(students_file,'w');
    for line in lines:
        if line[0] == "#": continue
        line=line.strip('\n\r');
        parts=line.split(";");
        if len(parts)>8: # name separeted from surname
            name = parts[5]+parts[6]
        id=identifier(parts[1])
        program = program_transform(parts[2].lower())
        file.write(parts[0]+";"+id+";"+program+'\n');

    file.close();
    print("wrote tmp_students.txt\n")
    return len(lines)



def write_priorities(dirname, prj_dict, prioritize_all=False):
    print("read students.csv")
    students_file=dirname+"/students.csv";
    f = open(students_file, "r")
    lines=f.readlines();
    f.close();

    priorities_file=dirname+"/tmp_priorities.txt";
    file=open(priorities_file,'w');
    for line in lines:
        if line[0]!= "#":

            line=line.replace("\n","");
            line=line.replace("\r","");
            parts=line.split(";");
            priorities=parts[3].split(",");
            n=len(priorities);
            i=7
            j=1

            id=identifier(parts[1])
            ##print priorities;
            for p in priorities:
                file.write(id+";"+str(int(p))+";"+str(j)+";"+str(2**i)+'\n');
                j+=1
                if i>0:
                    i=i-1;

            ## if we need to ensure feasibility we can insert a low priority for all other projects
            if prioritize_all:
                    prj_set = set(prj_dict.keys()) - set(priorities)
                    prj_set = list(prj_set)
                    prj_list = random.sample( prj_set,k=len(prj_set)  )
                    for p in prj_list:
                            file.write(id+";"+str(int(p))+";"+str(j)+";"+str(2**i)+'\n');
                            j+=1
    print("wrote tmp_priority.txt\n")
    file.close();



def valid_prjtype(dirname):
    """ reads types """
    reader = csv.reader(open(dirname+"/types.csv", "r"), delimiter=";")
    valid_prjtypes = {}
    try:
        for row in reader:
            valid_prjtypes[row[0]] = [row[t] for t in range(1, len(row))]
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
        # return {'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]}
    print(valid_prjtypes)
    return valid_prjtypes


def read_restrictions(dirname):
    """ reads types """
    reader = csv.reader(open(dirname+"/restrictions.csv", "r"), delimiter=";")
    restrictions = []
    try:
        for row in reader:
            restrictions += [{"cum": int(row[0]), "topics": [int(row[t])
                                                             for t in range(1, len(row))]}]
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
    return restrictions


def read_groups(dirname, group_reg):
    """ reads students' names and organize them in groups"""
    """ reads student type, eg, general nat student or farma std. """

    reader = csv.reader(open(dirname+"/tmp_students.txt", "r"), delimiter=";")

    groups = {}
    std_type = {}
    row_number = 1
    try:
        for row in reader:
            if group_reg:
                if row[0] in groups:
                    groups[row[0]].append(row[1])
                else:
                    groups[row[0]] = [row[1]]
            else:
                groups[row_number] = [row[1]]
            row_number = row_number+1
            std_type[row[1]] = row[2]
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    return groups, std_type


def read_students(dirname):
    """ reads students' priorities"""
    reader = csv.reader(open(dirname+"/tmp_priorities.txt", "r"), delimiter=";")

    std_values = {}
    std_ranks = {}
    try:
        for row in reader:
            if row[0] in std_values:
                std_values[row[0]].update(dict([(int(row[1]), int(row[3]))]))
                std_ranks[row[0]].update(dict([(int(row[1]), int(row[2]))]))
            else:
                std_values[row[0]] = dict([(int(row[1]), int(row[3]))])
                std_ranks[row[0]] = dict([(int(row[1]), int(row[2]))])
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    return std_values, std_ranks


