#! /usr/bin/python3
""" Transforms the input files in files that can be read by the assignment program 
"""


__author__ = "Marco Chiarandini"
__copyright__ = "Copyright 2019, Marco Chiarandini"
__credits__ = ["Stefano Gualandi","Rolf Fagerberg"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marco Chiarandini"
__email__ = "marco@imada.sdu.dk"
__status__ = "Prototype"


import sys;
import getopt;
import os;
import string;
from subprocess import *
import random




## Configuration
# anonymize=True;
anonymize=False;
random.seed(2018)



study_programs = ["anvendt matematik", "biokemi og molekylær biologi", "biologi", "biomedicin", "datalogi", "farmaci","fysik","kemi", "matematik", "psychology"]


def identifier(read_name):
    if (anonymize):
        buf = Popen("/home/marco/usr/bin/hashit -k /home/marco/usr/bin/mykey28_2014.bin -w "+read_name, stdout=PIPE, shell=True).stdout.read()
        # print(buf)
        id_hash=buf.split(" = ")[1].strip("\n")
    else:
        id_hash=read_name.lower();
    return id_hash


def program_transform(program):
    program = program.lower()
    return program
    # this is for SDU
    if program=="naturvidenskab, biologi og datalogi":
        program="not_pharma"
    elif program=="alle studier, dog ikke farmaci": # for 2018
        program="not_pharma"
    elif program=="kun farmaci":
        program ="pharma"
    elif program=="farmaci":
        program="pharma"
    elif program=="psychology":
        program="psychology"
    elif program in study_programs:
        program="not_pharma"
    elif program=="alle":
        program="everyone"
    else:
        sys.exit("program not recognized: {}".format(program))
    return program



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



def write_projects(dirname, n_stds):
    print("read projects.csv")
    projects_file=dirname+"/projects.csv"
    f = open(projects_file, "r")
    lines=f.readlines();
    f.close();

    project_dict={}
    file=open(dirname+"/tmp_projects.txt",'w');
    for line in lines:
        if line[0]=="#": continue
        line=line.strip("\r\n");
        parts=line.split(";");
        program = program_transform(parts[5].lower())
        file.write(parts[0]+";"+parts[1]+";"+parts[3]+";"+parts[4]+";"+program+"\n");
        project_dict[parts[0]]=int(parts[4])

    capacity = sum([project_dict[k] for k in project_dict])
    if (capacity < n_stds):
        answer = input("Not enough capacity from all projects\nHandle this by including a dummy project with the needed capacity? (y/n)\n")
        if answer in ['Y','y']:
                file.write(str(len(project_dict)+1)+";;1;"+str(n_stds-capacity)+";"+program+"\n");
                project_dict[len(project_dict)+1]=n_stds-capacity
    file.close();
    print("wrote tmp_projects.txt\n")
    return project_dict


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



def main(argv):
    dirname = "."
    try:
        opts, args = getopt.getopt(argv, "hpd:", ["help", "dir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if (len(opts)==0):
        usage();

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dir"):
            dirname = arg

    n_stds = write_students(dirname);
    prj_dict = write_projects(dirname, n_stds);
    write_priorities(dirname, prj_dict);



def usage():
    print("\nTransforms input data. Needs files in dirname \"./students.csv\" and \"./projects.csv\"");
    print("Usage: [\"help\", \"--dir=\" \"-p\"]");
    print("\tflag -p necessary if all project topics must be prioritized. Implies that we can assign beyond the expressed priority") 
    sys.exit(1);


if __name__ == "__main__":
    main(sys.argv[1:])
