#!/bin/bash -l
#PBS -l walltime=17:00:00,nodes=1:ppn=8
#PBS -m abe
#PBS -M levon003@umn.edu
#PBS -N CaringBridge_predictAuthorType_allJournals
#PBS -o /home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type/predict_author_type.stdout
#PBS -e /home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type/predict_author_type.stderr

working_dir="/home/srivbane/levon003/repos/sna-social-support/author_type"
cd $working_dir
echo "In '$working_dir', running script."
python predict_author_type.py
echo "Finished."

