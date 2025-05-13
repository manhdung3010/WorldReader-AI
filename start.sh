#!/bin/bash
echo "Starting WorldReader-AI application..."

# Check if the virtual environment exists
if [ ! -f "./venv/bin/activate" ]; then
  echo "Virtual environment not found. Creating a new one..."
  python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source ./venv/bin/activate

# Check if PM2 is running the application
pm2 list | grep -q "worldreader-ai"
if [ $? -eq 0 ]; then
  echo "Stopping previous PM2 process..."
  pm2 delete worldreader-ai
fi

# Start the application with PM2
echo "Starting application with PM2..."
pm2 start ./venv/bin/python --name worldreader-ai -- -m main 3053

# Show status
echo "Application status:"
pm2 status worldreader-ai

echo "To view logs, run: pm2 logs worldreader-ai"
echo "Application is now running!" 