#!/bin/bash
echo "Pulling latest code..."
git pull
echo "Stopping old PM2 process if exists..."
pm2 delete worldreader-ai || true

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 is not installed. Installing..."
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3.11-dev
fi

echo "Removing old virtualenv if exists..."
rm -rf venv

echo "Creating new virtualenv with Python 3.11..."
python3.11 -m venv venv

echo "Activating venv..."
source ./venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing six dependency first..."
pip install six==1.16.0

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting PM2 process..."
pm2 start ./venv/bin/python --name worldreader-ai -- -m main 3053 