#! /usr/bin/python
#import argparse; # only from python 2.7
import sys;
import os;
import csv

# MR = 40


def minimax_sol(dirname):
	d= {'2018':3, '2017':4, '2016':5, '2015':3, '2014': 6, '2013': 7, '2012':  6, '2011': 6, '2010': 3, '2009': 3, '2008': 4, '2018-psy': 5}
	# 2012 6 if with stability
	return d[dirname.split('/')[-1]]

def valid_prjtype(dirname):
	""" reads types """
	reader = csv.reader(open(dirname+"/tmp_types.txt", "r"),delimiter=";")
	valid_prjtypes = {}
	try:
		for row in reader:
			valid_prjtypes[row[0]]=[row[t] for t in range(1,len(row))]
	except csv.Error as e:
		sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
		##return {'biologi': ["alle", "natbidat"],"farmaci": ["alle","farmaci"],"natbidat": ["alle","natbidat"]}
	print(valid_prjtypes)
	return valid_prjtypes


def read_restrictions(dirname):
	""" reads types """
	reader = csv.reader(open(dirname+"/tmp_restrictions.txt", "r"),delimiter=",")
	restrictions = []
	try:
		for row in reader:
			restrictions += [{"cum": int(row[0]), "topics": [int(row[t]) for t in range(1,len(row))]}]
	except csv.Error as e:
		sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
	return restrictions



def read_groups(dirname, group_reg):
	""" reads students' names and organize them in groups"""
	""" reads student type, eg, general nat student or farma std. """

	reader = csv.reader(open(dirname+"/tmp_students.txt", "r"),delimiter=";")

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
	reader = csv.reader(open(dirname+"/tmp_priorities.txt", "r"),delimiter=";")

	std_values = {}
	std_ranks = {}
	try:
		for row in reader:
			if row[0] in std_values:
				std_values[row[0]].update(dict([(int(row[1]),int(row[3]))]))
				std_ranks[row[0]].update(dict([(int(row[1]),int(row[2]))]))
			else:
				std_values[row[0]] = dict([(int(row[1]),int(row[3]))])
				std_ranks[row[0]] = dict([(int(row[1]),int(row[2]))])
	except csv.Error as e:
		sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

	return std_values,std_ranks





def read_projects(dirname):
	""" reads projects, topics and teams """


	reader = csv.reader(open(dirname+"/tmp_projects.txt", "r"),delimiter=';')

	projects = {}
	try:
		for row in reader:
			if int(row[0]) in projects:
				projects[int(row[0])].append((int(row[2]),int(row[3]),row[4]))
			else:
				projects[int(row[0])]=[(int(row[2]),int(row[3]),row[4])]
	except csv.Error as e:
		sys.exit('file %s, line %d: %s' % ("projcet file", reader.line_num, e))

	return projects
