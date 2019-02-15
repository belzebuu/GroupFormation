#! /usr/bin/python3

## Text files required:
## students-enc.txt
## model.tbl
## sol.txt
## projects-quoted.txt
import sys;
import getopt;
import os;
import codecs;
import string;
import csv;

studieretninger=False
### global constants:
studentfile = "students.txt"
projectfile = "projects.txt"
studentfileseparator = ";"
projectfileseparator = ";"
output1 = "out/output1.txt"
output2 = "out/output2.txt"
output3 = "out/output3.csv"
output4 = "out/output4.csv"
output5 = "out/output5.txt"
#solfile = "./sol.txt"

retning2inst={'Biologi':"Biologisk Institut",
                        "Datalogi":'Institut for Matematik og Datalogi',
                        "Matematik":'Institut for Matematik og Datalogi',
                        'Anvendt Matematik':'Institut for Matematik og Datalogi',
                        "BMB":"Institut for Biokemi og Molekylær Biologi",
                        "Biokemi og Molekylær Biologi": "Institut for Biokemi og Molekylær Biologi",
                        "Biomedicin":"Institut for Biokemi og Molekylær Biologi",
                        "Nanobioscience":"Institut for Fysik, Kemi og Farmaci",
                        'Farmaci':"Institut for Fysik, Kemi og Farmaci",
                        'Kemi':"Institut for Fysik, Kemi og Farmaci",
                        'Fysik':"Institut for Fysik, Kemi og Farmaci",
                        'NAT':"Placeholder"};

for k in list(retning2inst.keys()):
        retning2inst.update( {k.lower(): retning2inst[k]} )


ass = {};
assgrpid = {};
prior = {};
groups = {};
topics = {};
project_details={};
student_details={};
type_compatibility={}
popularity={};
max_p=0;

def read_types(dirname):

        reader = csv.reader(open(dirname+"/tmp_types_orig.txt", "r"),delimiter=";")

        try:
                for row in reader:
                        type_compatibility[row[0]]=[row[t] for t in range(1,len(row))]
        except csv.Error as e:
                sys.exit('file %s, line %d: %s' % ("types_orig", reader.line_num, e))
                ##return {'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]}

        ## print type_compatibility


def read_topics(dirname):
        global topics;
        global project_details;

        with open(dirname+"/projects.csv", "r", encoding="utf-8") as f:
                lines=f.readlines();

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
                MinProjektType=parts[5]

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

## reads the solution
## needs two files:
## model.tbl and sol.txt
def scansol(tablefile):
        global ass;
        maps = {};
        f = open(tablefile);
        lines = f.readlines();
        f.close();
        for l in lines:
                l=l.replace("\"","");
                l=l.replace("#","$");
                if l.find("x$")>=0:
                        l=l.replace("\n","");
                        parts=l.split("\t");
                        names=parts[3].split("$");
                        #print parts,names;
                        maps[parts[2].strip()]=[names[1],names[2],names[3]];

        for a in list(maps.keys()):
                assgrpid[maps[a][1]+maps[a][2]]=set();

        f = open("zpl/sol.txt");
        lines = f.readlines();
        f.close();
        for l in lines:
                l=l.replace("#","$");
                parts=l.split();
#                print parts;
                ass[maps[parts[0]][0]]=[maps[parts[0]][1],maps[parts[0]][2]];
                assgrpid[maps[parts[0]][1]+maps[parts[0]][2]].add(maps[parts[0]][0]);




def read_solution(solfile):
        global ass;

        with open(solfile) as f:
                lines = f.readlines();
        for l in lines:
                l=l.replace("\n","");
                parts=l.split("\t");
                ass[parts[0]]=[parts[1],parts[2]];
                if (parts[1]+parts[2]) in assgrpid:
                        assgrpid[parts[1]+parts[2]].add(parts[0]);
                else:
                        assgrpid[parts[1]+parts[2]]=set([parts[0]]);



def check_sol(): #tablefile=''):

        students = list(student_details.keys());
        # print groups

        counter=[0]*50;
        not_prioritized=0;
        unassigned=0;

        for s in students:
                if s not in ass:
                        unassigned=unassigned+1;
                        continue;
                found = 0;
                for i in range(len(prior[s])):
                        if (ass[s][0]==prior[s][i]):
                                found = 1;
                                counter[i]=counter[i]+1;
                                break;
                if (found==0):
                        not_prioritized=not_prioritized+1;
                        print("someone assigned to smth not in his priority!");

        print(groups)
        # verify "same group" constraint is satisfied
        for s1 in list(ass.keys()):
                for s2 in list(ass.keys()):
                        if (groups[s1][0]==groups[s2][0]):
                                if (ass[s1][0]!=ass[s2][0] or ass[s1][1]!=ass[s2][1]):
                                        print(s1," and ",s2,"not same group:",ass[s1][0],ass[s1][1],ass[s2][0],ass[s2][1]);

        # start reporting

        # Print per project in std
        # and collect studnet assigned for later output
        f1 = open(output1,"w")
        f2 = open(output2,"w")
        studentassignments = []
        for i in sorted(topics.keys()):
                for j in sorted(topics[i]):
                        pID=str(int(i))+j;
                        s="ProjectID: "+pID+"\n";
                        s=s+ "Project title: \""+project_details[pID]["ProjektTitle"]+"\""+"\n";
                        s=s+ "Popularity: (tot. "+str(popularity[i][0])+") "+str(popularity[i][1:(max_p+1)])+"\n";
                        s=s+ "Project type: "+project_details[pID]["ProjektType"]+"\n";
                        s=s+ "Min participants: "+str(project_details[pID]["Min"])+"\n";
                        s=s+ "Max participants: "+str(project_details[pID]["Max"])+"\n";
                        std_assigned=pID in assgrpid and len(assgrpid[pID]) or 0
                        project_details[pID]["LedigePladser"]=project_details[pID]["Max"]-std_assigned
                        s=s+ "Available places: "+str(project_details[pID]["LedigePladser"])+"\n";
                        if (project_details[pID]["LedigePladser"]<0): sys.exit('project %s has LedigePladser %s ' % (pID, project_details[pID]["LedigePladser"]));
                        s=s+ "Assigned students IDs:"+"\n";
                        if std_assigned==0:
                                project_details[pID]["ProjektStatus"] = "Not open"
                        elif project_details[pID]["Min"]>std_assigned:
                                project_details[pID]["ProjektStatus"] = "Underfull";
                        else:
                                project_details[pID]["ProjektStatus"] = "Not underfull"

                        f1.write(s);

                        if (std_assigned>0):
                                f2.write("%s: %s\n" %
                                                 (project_details[pID]["ProjektNrBB"],
                                                  project_details[pID]["ProjektTitle"])
                                                 );

                        if (project_details[pID]["Institutforkortelse"]=="IMADA"):
                                print("\n"+project_details[pID]["ProjektNrBB"]+": "+project_details[pID]["ProjektTitle"]);
                                print("Popularity: (tot. "+str(popularity[i][0])+") "+str(popularity[i][1:(max_p+1)]));

                        if std_assigned>0:
                                for sID in sorted(assgrpid[pID]):
                                        f1.write("   "+sID+" "+str(prior[sID])+"\n");
                                        wishlist = prior[sID];
                                        sType = groups[sID][1];
                                        f2.write("%s, %s\n" %
                                                        (student_details[sID]["Navn"],
                                                         #student_details[sID]["Efternavn"],
                                                         student_details[sID]["Email"]));
                                        if (project_details[pID]["Institutforkortelse"]=="IMADA"):
                                                print(str(student_details[sID]["Navn"])+" "+student_details[sID]["Email"]+" "+str(student_details[sID]["Prioriteringsliste"]));
                                #studentassignments.append([sID,sType,pID,ptitle,ptype,
                                #                                                   underfull,wishlist])
                        f1.write("Underfull? ")
                        s=project_details[pID]["Min"]>std_assigned and "Yes" or "No"
                        s+=(std_assigned>0 and " " or " (Not open)")
                        f1.write(str(s)+"\n");
                        f1.write("\n");
                        if (std_assigned>0):
                                f2.write("\n");

        f1.close();
        f2.close();
        # Now output to a file the info per student
        #
        # Info is:
        #   StudentID, StudentType, ProjectID, ProjectTitle, ProjectType,
        #   isProjectUnderfull?, wishlistOfStudent

        # put into sID order (as sID is first element of list for each student):
        studentassignments.sort()

        # output:
        f = open(output3,"w")
        #        for [sID,sType,pID,ptitle,ptype,underfull,wishlist] in studentassignments:
        #                wlist = ",".join(wishlist)
        #                f.write("%s;%s;%s;%s;%s;%s;%s\n" %
        #                                (sID,sType,pID,ptitle,ptype,underfull,wlist))
        #        f.close()

        for s in students: #problem.groups.keys():
                student_details[s]["DerfraIkkeTilladt"]=[]
                peek=student_details[s]["StudType"]
                # d={'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]} # which projects for students
                valid_prjs=[x for x in sorted(topics.keys()) if project_details[str(x)+topics[x][0]]["MinProjektType"] in type_compatibility[peek]]
                # valid_prjs=filter(lambda x: project_details[str(x)+topics[x][0]]["MinProjektType"]==peek or project_details[str(x)+topics[x][0]]["ProjektType"]=='alle', sorted(topics.keys()))
                # print set(student_details[s]["Prioriteringsliste"])
                diff = set(student_details[s]["Prioriteringsliste"]) - set(valid_prjs)
                if len(diff)>0:
                        tmp=[]
                        for p in diff:
                                tmp.append(p)
                        student_details[s]["DerfraIkkeTilladt"]=tmp

        f.write("Brugernavn;StudType;ProjektNr;Undergruppe;ProjektTitel;ProjektType;ProjektStatus;TildeltPrio;Prioriteringsliste;DerfraIkkeTilladt;Min;Max;")
        f.write("LedigePladser;ProjektNrBB;CprNR;Navn;Email;GruppeID;Tilmeldingstidspunkt;Institutforkortelse;")
        f.write("Institut;Minikursus obligatorisk;Gruppeplacering\n")
        students.sort()
        for s in students:
                pID=str(int(ass[s][0]))+ass[s][1];
                ##print pID;
                priolist=student_details[s]["Prioriteringsliste"]
                valgt = [x for x in range(1,len(priolist)+1) if int(priolist[x-1])==int(project_details[pID]["ProjektNr"])]
                gottenprio='%s' % ', '.join(map(str, valgt))
                f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %
                                (
                                student_details[s]["Brugernavn"],
                                student_details[s]["StudType"],
                                project_details[pID]["ProjektNr"],
                                project_details[pID]["Undergruppe"],
                                project_details[pID]["ProjektTitle"],
                                project_details[pID]["ProjektType"],
                                project_details[pID]["ProjektStatus"],
                                gottenprio,
                                str(student_details[s]["Prioriteringsliste"]),
                                student_details[s]["DerfraIkkeTilladt"],
                                project_details[pID]["Min"],
                                project_details[pID]["Max"],
                                project_details[pID]["LedigePladser"],
                                project_details[pID]["ProjektNrBB"],
                                student_details[s]["CprNr"],
                                #student_details[s]["Fornavne"],
                                student_details[s]["Navn"],
                                student_details[s]["Email"],
                                student_details[s]["GruppeID"],
                                student_details[s]["Tilmeldingstidspunkt"],
                                project_details[pID]["Institutforkortelse"],
                                project_details[pID]["Institut"],
                                project_details[pID]["Minikursus_obl"],
                                # # project_details[pID]["Minikursus_anb"],
                                project_details[pID]["Gruppeplacering"]));
        f.close()





        # Now summarise
        # in std output
        count_teams=0
        count_prj=0
        for i in sorted(topics.keys()):
                prj=0
                for j in sorted(topics[i]):
                        pID=str(int(i))+j;
                        std_assigned=pID in assgrpid and len(assgrpid[pID]) or 0
                        if std_assigned>0:
                                count_teams+=1
                                prj=1
                count_prj+=prj

        s= "\n\nNumb. of students: "+str(len(students));
        s=s+"\nNumb. of active teams/teams offered: "+str(count_teams)+"/"+str(len(project_details));
        s=s+"\nNumb. of active topics/topics offered: "+str(count_prj)+"/"+str(len(topics));
        s=s+"\nStudents unassigned: "+str(unassigned);
        s=s+"\nStudents assigned outside of preference: "+str(not_prioritized)+"\n";
        for i in range(max_p):
                out=str(i+1)+". prioritet: "+str(counter[i]);
                s=s+out+"\n";

        print(s)
        f = open(output1,"a")
        f.write(s);
        f.close();


def count_popularity():
        f = open(output4,"w")
        global popularity
        global max_p
        students = list(student_details.keys());
        for s in students:
                if (len(prior[s])>max_p):
                        max_p=len(prior[s]);
        for i in sorted(topics.keys()):
                popularity[i]=[0]*(max_p+1);
        for s in students:
                for i in range(len(prior[s])):
                        pId=int(prior[s][i])
                        popularity[pId][0]=popularity[pId][0]+1;
                        popularity[pId][i+1]=popularity[pId][i+1]+1;
        for i in sorted(topics.keys()):
                pID=str(int(i))+topics[i][0];
                f.write(str(i)+";\""+project_details[pID]["ProjektTitle"]+"\";")
                f.write(project_details[pID]["ProjektType"]+";"+project_details[pID]["Institutforkortelse"]+";")
                for j in range(0,(max_p+1)):
                        f.write(str(popularity[i][j])+";")
                f.write("\n")
        f.close();



def institute_wise():
        f = open(output5,"w")
        pIDs_per_institute={}
        pIDs=[]
        for i in sorted(topics.keys()):
                for j in sorted(topics[i]):
                        pIDs+=[str(int(i))+j];

        institutes = set([project_details[x]["Institut"] for x in pIDs])
        #print institutes
        pIDs_per_institute={i: [x for x in pIDs if project_details[x]["Institut"]==i] for i in institutes}
        topics_per_institute={i: [x for x in sorted(topics.keys()) if project_details[str(x)+topics[x][0]]["Institut"]==i] for i in institutes}
        print(pIDs_per_institute)
        print(topics_per_institute)

        for i in sorted(institutes):
                tot_per_institute=0
                istr= "\n"+"["+i+"] "
                tmp=istr
                f.write("##########################################################################################\n")
                for pID in pIDs_per_institute[i]:
                        std_assigned=pID in assgrpid and len(assgrpid[pID]) or 0
                        if std_assigned>0:
                                s=istr+project_details[pID]["ProjektNrBB"]+": "+project_details[pID]["ProjektTitle"];
                                # # print "Popularity: (tot. "+str(popularity[i][0])+") "+str(popularity[i][1:(max_p+1)]);
                                f.write(s+"\n")
                                assigned=0
                                for sID in sorted(assgrpid[pID]):
                                        s = str(student_details[sID]["Brugernavn"])+" "+str(student_details[sID]["Prioriteringsliste"]);
                                        #f.write(s+"\n")
                                        assigned=assigned+1
                                        if i != retning2inst[student_details[sID]["Studieretning"]]:
                                                tmp+="\nX\t"+sID+" "+pID+" "+student_details[sID]["Studieretning"]
                                f.write("Std assigned: "+str(assigned)+"\n");
                                tot_per_institute=tot_per_institute+assigned
                f.write(istr +"Tot std assigned: "+str(tot_per_institute)+"\n\n")
                print((tmp +" \nTot std assigned: "+str(tot_per_institute)))
        f.close()        #
        print("Written "+output5)

        #'Institut for Matematik og Datalogi': [2, 3, 15, 28, 52, 58, 62, 68, 72, 77, 80, 92],
        del topics_per_institute['Institut for Matematik og Datalogi'];
        topics_per_institute['IMADA Mat']=[27, 86, 52, 4, 63, 71, 31, 55, 13, 92]
        topics_per_institute['IMADA Dat']=[15, 78, 95, 1, 81, 26, 40, 12, 17, 14, 77, 60]
        fields = set([student_details[s]["Studieretning"] for s in student_details])
        # fields=topics_per_institute.keys()
        print(topics_per_institute)
        shorten={"Biologisk Institut":"Biologi",
                        "IMADA Dat": "IMADA-Dat",
                        "IMADA Mat":"IMADA-Mat",
                        "Institut for Biokemi og Molekylær Biologi":"BMB",
                        "Institut for Fysik, Kemi og Farmaci":"FKF",
                        "Institut for Sundhedstjenesteforskning":"Sund"}
        students_per_institute={}

        matrix={r: {c: 0 for c in list(topics_per_institute.keys())} for r in fields}
        #print(matrix)
        for s in student_details:
                # print student_details[s]["Prioriteringsliste"][:3]
                shared={}
                lshared={}
                for i in sorted(topics_per_institute.keys()):
                        shared[i] = [v for v in topics_per_institute[i] if v in student_details[s]["Prioriteringsliste"][:5]];
                        lshared[i]=len(shared[i])
                        # print s+" "+', '.join(map(str,shared[i]))+" "+i
                        # print s+" "+str(len(shared[i]))+" "+i
                m=max([len(shared[x]) for x in shared])
                std_retning = student_details[s]["Studieretning"]  if "Studieretning" in student_details[s] else filter(lambda x: len(shared[x])==m, fields)[0]
                # print m,std_retning
                for k in topics_per_institute:
                        matrix[std_retning][k]=matrix[std_retning][k]+lshared[k]
                students_per_institute.update({std_retning : {s:lshared } } )
        # print students_per_institute
        print( matrix)
        # print map(lambda k: ', '.join(map(lambda x : str(matrix[k][x]), matrix.keys())) ,  matrix.keys())
        f=open("www/data/pref.csv","w")
        f.write("From,To,count\n");
        for k in fields:
                for c in list(topics_per_institute.keys()):
                        # print '\"'+shorten[k]+'\",\"'+shorten[c]+'\",'+str(matrix[k][c])
                        f.write('\"'+k+'\",\"'+shorten[c]+'\",'+str(matrix[k][c])+"\n")
        f.close()

        stds_per_retning={f: len([s for s in student_details if student_details[s]["Studieretning"]==f]) for f in fields}
        print(stds_per_retning)




def main(argv):
        dirname = "."
        tablefile=""
        #
        #        parser = argparse.ArgumentParser(description='Create a file priorities.txt containing weighted priorities.')
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

        if (len(opts)<1):
                usage();
        tablefile=''
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
                        print(opt+" Not recognised\n");
                        usage();

        read_topics(dirname);
        read_students(dirname);
        read_types(dirname);
        read_solution(solfile)
        count_popularity();
        check_sol(); #tablefile);
        #institute_wise()



def usage():
        print("Check sol and writes three output files\n");
        print("Usage: [\"help\", \"dir=\"]\n");
        sys.exit(1);


if __name__ == "__main__":
        main(sys.argv[1:])
