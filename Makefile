DATA=example
PYTHON=python3

all:
	${PYTHON} src/main.py -m data/${DATA}


clean: # this will remove the solutions found
	rm -fr log sln