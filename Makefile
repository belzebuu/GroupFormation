YEAR=2019-bachelor
PROGRAM=python3

publish: 
	/bin/rm -rf /home/marco/WWWpublic/Teaching/FF501/Ekstern/${YEAR}/out
	#/bin/mkdir /home/marco/WWWpublic/Teaching/FF501/Ekstern/${YEAR}
	/bin/cp -rf out /home/marco/WWWpublic/Teaching/FF501/Ekstern/${YEAR}/



# owa"; do # "powers"  "identity"
psy:
	${PROGRAM} src/main.py -d data/2018-psy -m minimax_instab_weighted -W owa | tee res/2018-psy-owa-minimax_instab_weighted.txt; done


2019-bachelor:
	${PROGRAM} src/main.py data/2019-bachelor
	${PROGRAM} src/report_sol_new.py -d data/2019-bachelor -s sln/sol_001.txt
