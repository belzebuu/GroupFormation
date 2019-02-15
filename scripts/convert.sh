#! /bin/bash

convert () {
	mv ${1} ${1}.iso;
	iconv -f ISO-8859-1 -t UTF-8 ${1}.iso > ${1};
}

for f in $1/"projects.csv" $1/"students.csv"; do convert $f; done;
