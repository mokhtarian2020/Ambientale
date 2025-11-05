#!/bin/bash
# HealthTrace Virtual Environment Activation Script
echo "Activating HealthTrace virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Available packages:"
pip list | head -10
echo "..."
echo "Ready to run HealthTrace analytics!"
