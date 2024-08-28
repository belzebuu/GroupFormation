#!/bin/zsh

#instances = 

for i in zhiru-f20  zhiru-e21  zhiru-e21-ds  zhiru-e22-ds  zhiru-e22-ds830  zhiru-e23-ds831;
    do 
        echo $i;
        python3 src/prensio/main.py -t 3600 -s patat/${i}_sol -L patat/${i}_log -x data/private/$i;
    done