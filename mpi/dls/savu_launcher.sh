#!/bin/bash
module load global/cluster

echo "SAVU_LAUNCHER:: Running Job"

savupath=$SAVUHOME
datafile=$1
processfile=$2
outpath=$3
outname=savu
nNodes=4
nCPUs=20

filepath=$savupath/mpi/dls/savu_mpijob.sh
M=$((nNodes*20))

qsub -N $outname -sync y -j y -o /dls/tmp/savu/ -e /dls/tmp/savu/ -pe openmpi $M -l exclusive -l infiniband -l gpu=1 -q medium.q@@com10 $filepath $savupath $datafile $processfile $outpath $nCPUs > /dls/tmp/savu/$USER.out

echo "SAVU_LAUNCHER:: Job Complete, preparing output..."

filename=`echo $outname.o`
jobnumber=`awk '{print $3}' /dls/tmp/savu/$USER.out | head -n 1`
filename=/dls/tmp/savu/$filename$jobnumber

while [ ! -f $filename ]
do
  sleep 2
done

echo "SAVU_LAUNCHER:: Output ready, spooling now"

cat $filename

echo "SAVU_LAUNCHER:: Process complete"

