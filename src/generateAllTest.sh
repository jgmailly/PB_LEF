#!/bin/bash

# you can add or remove elements in each for loops to run all the test. Note after the -o you need to have a valid path (the file will be created, not the folder)

for NUM_AGENTS in 10 20 30 40 50 75 100
do
    for Y in 1 2 3 4 5 6 7 8 9 10
    do
        for PROB in 0.05 0.1 0.2 0.3 0.4 0.5 0.6 0.75 0.9
        do
            py -3.8 instance_generator.py ${NUM_AGENTS} inst_test ER ${PROB}
            for HA in both # agents objects
            do
                for LEF in consequence pairs complement
                do
                    py -3.8 decide_LEF_clean.py inst_test.pref inst_test.soc --LEF ${LEF} -t 150 --partial ${HA} -o graphique/inst_${HA}_${NUM_AGENTS}_${PROB}_${LEF}.txt
                done
            done
        done 
    done
done
