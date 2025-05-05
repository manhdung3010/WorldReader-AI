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
echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing core dependencies first..."
pip install setuptools wheel
pip install six==1.16.0 python-dateutil==2.8.2

# Try to fix the "six.moves" issue by ensuring all dependencies are properly installed
echo "Installing specific dependencies that might be causing issues..."
pip install python-dateutil==2.8.2
pip install six==1.16.0

echo "Installing core numerical and data processing libraries..."
pip install numpy==1.26.4
pip install pandas==2.2.2
pip install scikit-learn==1.5.1
pip install faiss-cpu==1.8.0

echo "Installing remaining requirements..."
pip install flask==2.3.3
pip install pymysql==1.1.1
pip install nltk==3.9.1
pip install packaging==24.1
pip install cryptography==43.0.1
pip install google-generativeai==0.3.0
pip install python-dotenv==1.0.0
pip install PyPDF2==3.0.1
pip install python-docx==0.8.11
pip install textract==1.6.5

echo "Validating installation of six..."
python3 -c "import six; print('Six version:', six.__version__); print('Six.moves available:', 'Yes' if hasattr(six, 'moves') else 'No')"

echo "Starting PM2 process..."
pm2 start ./venv/bin/python --name worldreader-ai -- -m main 3053 