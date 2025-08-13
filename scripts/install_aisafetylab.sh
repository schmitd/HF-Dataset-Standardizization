#!/bin/bash

# Script to install AISafetyLab dependency
set -e

echo "Setting up AISafetyLab dependency..."

# Create deps directory if it doesn't exist
mkdir -p deps

# Navigate to deps directory
cd deps

# Clone the repository if it doesn't exist
if [ ! -d "AISafetyLab" ]; then
    echo "Cloning AISafetyLab repository..."
    git clone git@github.com:thu-coai/AISafetyLab.git
else
    echo "AISafetyLab directory already exists, pulling latest changes..."
    cd AISafetyLab
    git pull
    cd ..
fi

# Install the package in editable mode
echo "Installing AISafetyLab in editable mode..."
cd AISafetyLab
pip install -e .

echo "AISafetyLab installation completed successfully!" 