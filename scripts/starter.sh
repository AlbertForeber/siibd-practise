#!/bin/zsh
echo "Test #1 ---------------------------------"
python3 ../main.py ../test_vsf.x
echo "Test #2 ---------------------------------"
python3 ../main.py ../test_vf.xml
echo "Test #3 ---------------------------------"
python3 ../main.py ../vsf/several_levels.xml --script script_demo.txt
echo "Test #4 ---------------------------------"
python3 ../main.py ../vsf/basic.xml --script script_demo.txt
echo "Test #5 ---------------------------------"
python3 ../main.py ../vsf/several_files.xml --script script_demo.txt
