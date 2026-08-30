#!/bin/bash
set -e

n=1
while [ -d "symulacja_$n" ]; do
    n=$((n + 1))
done

dir="symulacja_$n"
mkdir "$dir"

echo "Uruchamiam symulacje w $dir"
python3 protocols.py "$dir/results.h5"
echo "Zakonczono: $dir/results.h5"