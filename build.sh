#!/bin/bash
echo "Pulling latest code..."
git pull
echo "Stopping old PM2 process if exists..."
pm2 delete worldreader-ai || true
echo "Checking virtualenv..."
if [ ! -f "./venv/bin/activate" ]; then
  python3 -m venv venv
fi
echo "Activating venv..."
source ./venv/bin/activate
echo "Downgrading pip if necessary..."
pip install "pip<24.1"
echo "Installing six dependency first..."
pip install six==1.12.0
echo "Installing requirements..."
pip install -r requirements.txt
echo "Starting PM2 process..."
pm2 start ./venv/bin/python --name worldreader-ai -- -m main 3053 