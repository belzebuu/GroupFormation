#! /usr/bin/python
# coding=utf-8

import sys
import os
import csv
import json
import codecs
import pandas as pd
import numpy as np
from collections import defaultdict
from collections import OrderedDict
from collections import namedtuple
import logging

logger = logging.getLogger("preprocessing")

class Problem:
    def __init__(self, pathname, logdir="./log"):
        if not pathname.exists():
            raise Exception("File or directory does not exists")
        if pathname.is_dir():
            self.name = pathname / "data.xlsx"
        else:
            self.name = pathname
        
        self.logdir=logdir
        os.makedirs(self.logdir, exist_ok=True)
        self.study_programs = set()
        self.student_details, self.similarity_dict, self.features_dict, self.categories, self.groups, self.std_type = self.read_students(
            self.name)
        self.project_details, self.topics, self.projects = self.read_projects(self.name)
        self.check_tot_capacity()
        #self.std_values, self.std_ranks = self.calculate_ranks_values(prioritize_all=True)

        self.study_programs=set()
        # self.minimax_sol = self.minimax_sol(dirname),
        self.valid_prjtype = self.type_compliance(self.name)
        self.restrictions = self.read_restrictions(self.name)
        self.minimax_sol = 0
        # self.__dict__.update(kwds)

    def separate_features(self):
        F_cat = list()
        F_num = list()
        F_sim=list()
        for (index, feat) in sorted(self.features_dict.items(), key=lambda x: x[1]["Priority"]):
            #print(feat, type)
            if feat['Type'] in ['category', 'object', 'str']:
                F_cat.append(feat['Variable'])
            elif feat['Type'] in ['numerical','float64','int64','Int64']:
                F_num.append(feat['Variable'])
            elif feat['Type'] == 'similarity':
                F_sim.append(feat['Variable'])
        return F_cat, F_num, F_sim

    
   
    def check_tot_capacity(self):
        capacity = sum([self.project_details[k]["max_cap"] for k in self.project_details])
        n_stds = len(self.student_details)
        if (capacity < n_stds):
            answer = input(
                "Not enough capacity from all projects\nHandle this by including a dummy project with the needed capacity? (y/n)\n")
            if answer in ['Y', 'y']:
                sys.exit("to implement")
                # file.write(str(len(project_dict)+1)+";;1;"+str(n_stds-capacity)+";"+program+"\n")
                #project_dict[len(project_dict)+1] = n_stds-capacity

    def read_students(self, data_file):
        #students_file = dirname+"/students.csv"
        #dtypes_file = dirname+"/dtypes.csv"
        #print("read ", students_file)
        
        with open(data_file, 'rb') as f:
            features_df = pd.read_excel(f, sheet_name='dtypes', header=0, index_col=None)
            # for x in f:
            #    row = x.split(";")
            #student_dtypes[row[0]] = row[1].strip()
            # print(dtypes)
            features_dict = features_df.to_dict("index", into=dict) #OrderedDict)
            # {0: {'Variable': 'C1', 'Type': 'similarity', 'Priority': 1, 'Heterogeneous': 0}}                
            # print(student_dtypes)
            # dtypes.to_dict("index",into=OrderedDict))
            # dtypes = {'grp_id': 'str', 'group': 'str', 'username': 'str', 'type': 'str', 'email': 'str', 'student_id': 'str',
            #          'full_name': 'str', 'priority_list': 'str'}
            dtypes = {'grp_id': 'str', 'username': 'str', 'type': 'str', 'student_id': 'str'}
            dtypes.update({row['Variable']: "str" if row['Type']=="similarity" else row['Type']
                            for index, row in features_df.iterrows()})
            logger.info(dtypes)
            student_table = pd.read_excel(f, sheet_name="students", header=0, index_col=None,
                                            dtype=dtypes, 
                                            keep_default_na=False) #, decimal=',')
            student_table["username"]=student_table["username"].apply(lambda x: x.lower())
            
            if any(student_table["username"].value_counts()>1):
                logger.warning("Some username repeated")

        logger.info(f'\n{student_table.to_string()}')
        logger.info(f'\n{student_table.dtypes}')

        counters = student_table.groupby(['type']).size().reset_index(name='counts')
        logger.info(f'\n{counters}')
        
        # grp_id;group;username;type;priority_list;student_id;full_name;email;timestamp
        # student_table = pd.read_csv(dirname+"/students.csv", sep=";", dtype=student_dtypes, keep_default_na=False, decimal=',')
        # student_table["username"].apply(lambda x: x.lower())
        # print(student_table)

        # print(student_table.dtypes)
        # Transform the categorical values in integers
        categories = OrderedDict()
        similarity_dict={}
        # for f in student_table.columns:
        for k in features_dict:
            f = features_dict[k]['Variable']
            if features_dict[k]['Type']=='category' and student_table[f].dtype.name == 'category':
                # print(student_table[f].cat.categories,len(student_table[f].cat.categories))
                student_table[f+"_rcat"] = student_table[f].cat.rename_categories(
                    range(len(student_table[f].cat.categories)))
                categories[f+"_rcat"] = {x: i for (i, x)
                                        in enumerate(student_table[f+"_rcat"].cat.categories)}
            elif features_dict[k]['Type']=='similarity':
                with open(data_file, 'rb') as fh:
                    similarity_df = pd.read_excel(fh, sheet_name=f, header=0, index_col=None,
                                              dtype={0:str, 1: str, 2: np.float64}, #let infer  
                                              keep_default_na=False) #, decimal=',')
                similarity_dict[f] = {(row[0],row[1]): np.round(row[2],5) for ind, row in similarity_df.iterrows()}
                

        #print(student_table.loc[:, dtypes.keys()]) # range(9, student_table.shape[1])])
        if any(student_table["student_id"].value_counts()>1):
            logger.critical("Some student_id repeated")
        student_table.index = student_table["student_id"]
        student_details = student_table.to_dict("index", into=OrderedDict)


        filehandle = codecs.open(os.path.join(self.logdir, "students.json"),  "w", "utf-8")
        json.dump(student_details, fp=filehandle, sort_keys=True,
                  indent=4, separators=(',', ': '),  ensure_ascii=False)

        tmp = {u: (student_details[u]["grp_id"], student_details[u]["type"])
               for u in student_details}
        group_ids = {student_details[u]["grp_id"] for u in student_details}
        groups = {g: list(
            filter(lambda u: student_details[u]["grp_id"] == g, student_details.keys())) for g in group_ids}

        student_types = {student_details[u]["type"] for u in student_details}
        logger.info(student_types)
        std_type = {u: student_details[u]["type"] for u in student_details}
        logger.info(std_type)
        return (student_details, similarity_dict, features_dict, categories, groups, std_type)
        

    def read_projects(self, data_file):
        print("Reading group specifications...")
        #projects_file = dirname+"/projects.csv"
        #print("read ", projects_file)
        topics = defaultdict(list)
        # We assume header to be:
        # ID;team;title;min_cap;max_cap;type;prj_id;instit;institute;mini;wl
        # OLD: ProjektNr; Underprojek; Projekttitel; Min; Max;Projekttype; ProjektNr  i BB; Institut forkortelse; Obligatorisk minikursus; Gruppeplacering
        #project_table = pd.read_csv(dirname+"/projects.csv", sep=";")
        
        with open(data_file, 'rb') as f:
            project_table = pd.read_excel(f, sheet_name='projects', dtype={'ID':'str','prj_id':'str','title':'str','team':'str','type':'str'}, header=0, index_col=None)
        project_table.index = project_table["ID"]+project_table["team"].astype(str)
        project_table["type"]=project_table["type"].apply(self.program_transform)
        project_details = project_table.to_dict("index", into=OrderedDict)
        # topics = {x: list(map(lambda p: p["team"], project_details[x])) for x in project_details}
        topics = {k: list(v) for k, v in project_table.groupby('ID')['team']}
        print(topics)
        # OrderedDict(
        # ProjektNr=row[],
        # Undergruppe=line[1],
        # ProjektTitle=line[2].strip("\r\n\""),
        # Min=int(line[3]),
        # Max=int(line[4]),
        # ProjektType=line[5].lower(),
        # MinProjektType=self.program_transform(row["type"]),
        # ProjektNrBB=(len(line)>6 and line[6] or ""),
        # InstitutForkortelse=(len(line) > 6 and line[6] or ""),
        # Institut=(len(line)>6 and line[8] or ""),
        # Minikursus_obl=(len(line) > 6 and line[7] or ""),
        # Minikursus_anb=(len(line)==12 and line[10] or ""),
        # Gruppeplacering=(len(line) > 6 and line[8] or "")
        # Gruppeplacering=(((len(line)>6 and len(line)==12) and line[11]) or (len(line)>6 and line[10]) or "") # to take into account format before 2012
        # )

        filehandle = codecs.open(os.path.join(self.logdir, "projects.json"),  "w", "utf-8")
        json.dump(project_details, fp=filehandle, sort_keys=True,
                  indent=4, separators=(',', ': '),  ensure_ascii=False)

        projects = defaultdict(list)
        print(project_details)
        Team = namedtuple("Team", ("min", "max", "type"))
        for topic in topics:
            for t in topics[topic]:
                id = str(topic)+str(t)
                projects[topic].append(Team(project_details[id]["min_cap"],
                                            project_details[id]["max_cap"],
                                            project_details[id]["type"]
                                            )
                                       )
        return (project_details, topics, projects)



    def read_restrictions(self, data_file):
        """ reads restrictions """
       
        with open(data_file, 'rb') as f:
            restriction_table = pd.read_excel(f, sheet_name='restrictions', header=0, index_col=None)
        
        restrictions = []
        print("Restriction reader not implemented yet!")
        return restrictions
        # TODO handle both readers
        reader = csv.reader(open(dirname+"/restrictions.csv", "r"), delimiter=";")
        
        try:
            for row in reader:
                restrictions += [{"cum": int(row[0]), "topics": [int(row[t])
                                                                 for t in range(1, len(row))]}]
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
        return restrictions

    def program_transform(self, program):
        # study_programs = ["anvendt matematik", "biokemi og molekylær biologi", "biologi", "biomedicin", "datalogi", "farmaci","fysik","kemi", "matematik", "psychology"]
        program = program.lower()
        self.study_programs.add(program)
        # if program not in study_programs:
        #    sys.exit("program not recognized: {}".format(program))
        return program

    def type_compliance(self, data_file):
        """ reads types """        
        try:
            with open(data_file, 'rb') as f:
                topics_table = pd.read_excel(f, sheet_name='types', dtype={'key':'str','type':'str'}, header=0, index_col=None)
        except FileNotFoundError:
            raise Exception("No sheet 'types' found")

        #topics.index = project_table["prj_id"]
        #topics = topics_table.to_dict("records") #, into=OrderedDict)
        # topics = {x: list(map(lambda p: p["team"], project_details[x])) for x in project_details}
        topics_table["key"]=topics_table["key"].apply(lambda x: self.program_transform(x))
        topics_table["type"]=topics_table["type"].apply(self.program_transform)

        valid_prjtypes = {k: list(v) for k, v in topics_table.groupby('key')['type']}

        logger.info(f'\n{valid_prjtypes}')
        return valid_prjtypes
        # TODO handle both readers
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
