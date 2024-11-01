#!/bin/bash

# Parameters

# Directory for JEDI OOPS binaries
jedibin=${HOME}/build/jedi-bundle/bin

# Directory for ECMWF OOPS binaries
#ecbin=${HOME}/build/oops-bundle/bin

# Number of tasks for OOPS
ntasks=4

# Run

# Get test data
#curl https://www.dropbox.com/scl/fi/rs8f8k7xzyy964ocd9ug8/data.tar.gz?rlkey=lg3vguxctuzwuidmx1o0nh7m2 -o data.tar.gz -J -L -k  
tar -xvzf data.tar.gz

# Create grid coordinates
mpirun -n ${ntasks} ${jedibin}/saber_quench_convertstate.x json/grid.json

# Format observations
python python/formatObservations.py

# Format backgrounds
python python/formatBackgrounds.py

# Run HofX for each member
for mem in $(seq -f "%06g" 0 20); do
#  sed -e s/%mem%/${mem}/g json/ec_hofx.json > json/hofx_${mem}.json
#  mpirun -n 1 ${ecbin}/saber_quench_hofx.x json/hofx_${mem}.json
  sed -e s/%mem%/${mem}/g json/hofx.json > json/hofx_${mem}.json
  mpirun -n 1 ${jedibin}/quenchxx_hofx3d.x json/hofx_${mem}.json
  rm -f json/hofx_${mem}.json
done

# Gather HofX
python python/gatherHofX.py

# Run LETKF
mpirun -n ${ntasks} ${jedibin}/quenchxx_letkf.x json/letkf.json

# Format analysis (still very slow)
# python python/formatAnalyses.py
