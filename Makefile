DATA=example
PYTHON=/usr/bin/python3

all:
	mkdir -p log sln
	${PYTHON} src/main.py -g post data/${DATA}


clean: # this will remove the solutions found
	rm -fr log sln