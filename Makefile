DATA=example
PYTHON=python3

all:
	${PYTHON} src/prensio/main.py data/${DATA}


clean: # this will remove the solutions found
	rm -fr log sln