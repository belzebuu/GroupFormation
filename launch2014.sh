#! /bin/bash


#
#for i in 2015; do
#    for a in "minimax"; do
#		python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; done
#done
##
#
#
#for i in 2015; do
#    for a in "minimax_instab_weighted"; do
#	#for w in "owa" "identity" "powers"; do
#	for w in "identity"; do
#	    python src/main.py -d data/$i -m $a -W $w | tee res/$i-$a-$w.txt; done
#    done
#done

#
#for i in 2016; do
#    for a in "minimax"; do
#		python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; done
#done
##
#
#
#for i in 2016; do
#    for a in "minimax_instab_weighted"; do
#	#for w in "owa" "identity" "powers"; do
#	for w in "identity"; do
#	    python src/main.py -d data/$i -m $a -W $w | tee res/$i-$a-$w.txt; done
#    done
#done
#


#
#for i in 2017; do
#    for a in "minimax"; do
#	python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; done
#done
#

#
#for i in 2017; do
#    for a in "minimax_instab_weighted"; do
#	for w in "owa"; do # "powers"  "identity"
#	    python src/main.py -d data/$i -m $a -W $w | tee res/$i-$a-$w.txt; done
#    done
#done
#
#
#for i in 2017; do
#    for a in  "minimax_instab_greedy_max"; do
#	python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; 
#    done
#done




#
#for i in 2018; do
#    for a in "minimax"; do
#	python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; done
#done



for i in 2018; do
    for a in "minimax_instab_weighted"; do
	for w in "owa"; do # "powers"  "identity"
	    python src/main.py -d data/$i -m $a -W $w | tee res/$i-$a-$w.txt; done
    done
done
#
#
#for i in 2018; do
#    for a in  "minimax_instab_greedy_max"; do
#	python src/main.py -d data/$i -m $a | tee res/$i-$a.txt; 
#    done
#done
