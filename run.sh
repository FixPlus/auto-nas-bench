#!/usr/bin/bash

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ]; then
  echo "Usage: run.sh <build_dir> <max_threads> <result_file>"
  exit
fi

if [ ! -d $1 ]; then
  echo "$1 is not a directory"
  exit
fi
touch $3
if [ $? -ne 0 ]; then
  echo "Could not create result file"
  exit
fi
#rm $3

export RESULT_FILE=$(realpath $3)
cd $1

for PROG in *; do
  if [ -d $PROG ]; then
    echo "$PROG is a directory, not a programm"
    exit
  fi	  
  if [ ! -x $PROG ]; then
    echo "$PROG is not executable"
    exit
  fi
  echo "Running $PROG..."
  for i in $(seq 1 $2); do
    export OMP_NUM_THREADS=$i
    ./$PROG >result.tmp 
    if [ $? -ne 0 ]; then
      echo "ERROR: $PROG finished with exit code $?"
      rm result.tmp
      exit
    fi
    NUM_THREADS=$(grep "Threads         =" result.tmp | sed "s/Threads         =//" | sed "s/ //")
    TEST_TIME=$(grep "Time in seconds =" result.tmp | sed "s/Time in seconds =//" | sed "s/ //")
    echo "$(basename $1);$PROG;$NUM_THREADS;$TEST_TIME" >>$RESULT_FILE
    rm result.tmp
  done
  echo "Done $PROG..."
done
