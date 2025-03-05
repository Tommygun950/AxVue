"""
This file helps pytest find your project modules by adjusting the Python path.
Place this file in your tests directory.
"""
import os
import sys

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to sys.path to enable imports
sys.path.insert(0, project_root)
