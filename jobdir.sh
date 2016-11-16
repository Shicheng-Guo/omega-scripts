#!/usr/bin/env bash 
for j in $(qstat hep | grep $1 | tr . ' ' | awk '{print $1}' ) 
  do checkjob -v $j | grep Output | awk '{print $2}' 
done


 qstat -u shg047 | awk '{print $1,$10}' | grep R | grep local | awk '{print $1}' | xargs -n 1 checkjob
