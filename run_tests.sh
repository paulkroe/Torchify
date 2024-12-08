#!/bin/bash

conda create -n "Torchify" python=3.11.0
conda activate Torchify
cd compiler
pip install -e .
pip install pytest
pip install torch
pip install torchvision
pip install tqdm
cd ..

python3 compiler/tests/TestPrograms/testprogs.py

# Check if the program ran successfully
if [ $? -ne 0 ]; then
    echo "There was an error running the program."
fi
