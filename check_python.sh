#!/bin/bash
# Check Python version
echo "Python version:"
python3 --version

# Check if six is installed
echo -e "\nChecking if six is installed:"
python3 -m pip list | grep six

# Check dateutil version
echo -e "\nChecking dateutil version:"
python3 -m pip list | grep dateutil

# Check pandas version
echo -e "\nChecking pandas version:"
python3 -m pip list | grep pandas 